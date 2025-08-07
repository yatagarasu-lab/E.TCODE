import time
import os
import dropbox
import openai
from linebot import LineBotApi
from linebot.models import TextSendMessage

# --- 環境変数から認証情報取得 ---
DROPBOX_REFRESH_TOKEN = os.environ.get("DROPBOX_REFRESH_TOKEN")
DROPBOX_APP_KEY = os.environ.get("DROPBOX_APP_KEY")
DROPBOX_APP_SECRET = os.environ.get("DROPBOX_APP_SECRET")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
LINE_CHANNEL_ACCESS_TOKEN = os.environ.get("LINE_CHANNEL_ACCESS_TOKEN")
LINE_USER_ID = os.environ.get("LINE_USER_ID")  # 固定通知先ユーザーID（例：Uxxxx）

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

# --- ファイル一覧取得 ---
def list_files():
    try:
        res = dbx.files_list_folder("")
        return [entry.name for entry in res.entries]
    except Exception as e:
        print("❌ Dropbox一覧取得エラー:", e)
        return []

# --- GPT解析処理 ---
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

        # 解析結果をDropboxに保存
        log_name = f"{filename}_result.txt"
        dbx.files_upload(result.encode(), f"/{log_name}", mode=dropbox.files.WriteMode.overwrite)

        # LINE通知
        if LINE_USER_ID:
            line_bot_api.push_message(LINE_USER_ID, TextSendMessage(text=f"📊 {filename} を解析しました:\n\n{result[:3000]}"))

        print(f"✅ {filename} 解析・通知完了")
    except Exception as e:
        print(f"❌ {filename} の解析失敗:", e)

# --- メインループ ---
def main_loop():
    print("🌀 自動解析BOT起動中...")
    while True:
        try:
            files = list_files()
            for f in files:
                if f.startswith("auto_") and f not in CHECKED_FILES:
                    analyze_file_with_gpt(f)
                    CHECKED_FILES.add(f)
        except Exception as e:
            print("❌ ループエラー:", e)

        time.sleep(60)  # 1分ごとにチェック

if __name__ == "__main__":
    main_loop()
