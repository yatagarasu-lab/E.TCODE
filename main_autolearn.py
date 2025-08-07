import time
import os
import dropbox
import openai
from linebot import LineBotApi
from linebot.models import TextSendMessage

# --- 環境変数 ---
DROPBOX_REFRESH_TOKEN = os.environ.get("DROPBOX_REFRESH_TOKEN")
DROPBOX_APP_KEY = os.environ.get("DROPBOX_APP_KEY")
DROPBOX_APP_SECRET = os.environ.get("DROPBOX_APP_SECRET")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
LINE_CHANNEL_ACCESS_TOKEN = os.environ.get("LINE_CHANNEL_ACCESS_TOKEN")
LINE_USER_ID = os.environ.get("LINE_USER_ID")

# --- 初期化 ---
line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
openai.api_key = OPENAI_API_KEY

def get_dropbox():
    return dropbox.Dropbox(
        oauth2_refresh_token=DROPBOX_REFRESH_TOKEN,
        app_key=DROPBOX_APP_KEY,
        app_secret=DROPBOX_APP_SECRET
    )

dbx = get_dropbox()
CHECKED_FILES = set()

# --- ファイル一覧 ---
def list_files():
    try:
        res = dbx.files_list_folder("")
        return [entry.name for entry in res.entries]
    except Exception as e:
        print("❌ Dropbox一覧取得エラー:", e)
        return []

# --- GPT解析 ---
def analyze_file_with_gpt(filename):
    try:
        path = f"/{filename}"
        _, res = dbx.files_download(path)
        content = res.content.decode()

        prompt = f"以下のファイル内容を要約・分析し、スロット設定予測や重要ポイントをまとめてください:\n\n{content}"

        response = openai.ChatCompletion.create(
            model="gpt-4-1106-preview",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5
        )
        result = response.choices[0].message.content.strip()

        log_name = f"{filename}_result.txt"
        dbx.files_upload(result.encode(), f"/{log_name}", mode=dropbox.files.WriteMode.overwrite)

        if LINE_USER_ID:
            line_bot_api.push_message(LINE_USER_ID, TextSendMessage(text=f"📊 {filename} を解析しました:\n\n{result[:3000]}"))

        print(f"✅ {filename} 解析・通知完了")
    except Exception as e:
        print(f"❌ {filename} の解析失敗:", e)

# --- コード自動アップデート ---
def check_for_update():
    update_filename = "update_main_autolearn.py"
    try:
        _, res = dbx.files_download(f"/{update_filename}")
        new_code = res.content.decode()

        script_path = os.path.realpath(__file__)
        with open(script_path, "w", encoding="utf-8") as f:
            f.write(new_code)

        if LINE_USER_ID:
            line_bot_api.push_message(LINE_USER_ID, TextSendMessage(
                text=f"🛠️ 自動アップデート完了！\n次回起動時に新しいコードが反映されます。\n\n{update_filename}"
            ))
        print("🔄 自動アップデート実行完了")
        return True
    except dropbox.exceptions.ApiError:
        return False
    except Exception as e:
        print("❌ アップデート失敗:", e)
        return False

# --- メインループ ---
def main_loop():
    print("🌀 自動解析BOT（自動アップデート対応）起動中...")
    while True:
        if check_for_update():
            print("🚀 新コードへアップデート済み。再起動で反映されます。")
            break  # 自動停止してRenderが再起動（または手動起動）

        try:
            files = list_files()
            for f in files:
                if f.startswith("auto_") and f not in CHECKED_FILES:
                    analyze_file_with_gpt(f)
                    CHECKED_FILES.add(f)
        except Exception as e:
            print("❌ メイン処理エラー:", e)

        time.sleep(60)

if __name__ == "__main__":
    main_loop()