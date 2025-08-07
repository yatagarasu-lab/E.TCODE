import os
import hashlib
import dropbox
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import openai

# --- 認証情報 ---
LINE_CHANNEL_ACCESS_TOKEN = os.environ.get("LINE_CHANNEL_ACCESS_TOKEN")
LINE_CHANNEL_SECRET = os.environ.get("LINE_CHANNEL_SECRET")
DROPBOX_REFRESH_TOKEN = os.environ.get("DROPBOX_REFRESH_TOKEN")
DROPBOX_APP_KEY = os.environ.get("DROPBOX_APP_KEY")
DROPBOX_APP_SECRET = os.environ.get("DROPBOX_APP_SECRET")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")  # ← ✅ OpenAIのAPIキー

# --- 初期化 ---
app = Flask(__name__)
line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)
openai.api_key = OPENAI_API_KEY

def get_dropbox():
    return dropbox.Dropbox(
        oauth2_refresh_token=DROPBOX_REFRESH_TOKEN,
        app_key=DROPBOX_APP_KEY,
        app_secret=DROPBOX_APP_SECRET
    )

dbx = get_dropbox()

# --- 基本応答 ---
@app.route('/')
def home():
    return '✅ 自動解析BOT 起動中（八咫烏＆E.T Code）'

# --- ファイル操作 ---
def save_log_to_dropbox(filename, content):
    path = f"/{filename}"
    dbx.files_upload(content.encode(), path, mode=dropbox.files.WriteMode.overwrite)
    return f"✅ 保存完了: {filename}"

def read_log_from_dropbox(filename):
    path = f"/{filename}"
    try:
        metadata, res = dbx.files_download(path)
        return res.content.decode()
    except Exception:
        return "❌ 読み込み失敗（ファイルが存在しません）"

def list_dropbox_files():
    try:
        result = dbx.files_list_folder("")
        files = [entry.name for entry in result.entries]
        return "📄 ファイル一覧:\n" + "\n".join(files) if files else "📂 ファイルは存在しません。"
    except Exception:
        return "❌ 一覧取得失敗"

def delete_dropbox_file(filename):
    path = f"/{filename}"
    try:
        dbx.files_delete_v2(path)
        return f"🗑️ 削除完了: {filename}"
    except Exception:
        return "❌ 削除失敗（ファイルが存在しない可能性）"

# --- ファイル解析 ---
def analyze_file_with_gpt(filename):
    path = f"/{filename}"
    try:
        _, res = dbx.files_download(path)
        content = res.content.decode()

        prompt = f"以下のファイル内容を要約・分析し、スロット設定予測や重要ポイントをまとめてください:\n\n{content}"

        response = openai.ChatCompletion.create(
            model="gpt-4-1106-preview",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5
        )
        result = response.choices[0].message.content.strip()
        return f"📊 {filename} の解析結果:\n{result}"
    except Exception as e:
        return f"❌ 解析失敗: {str(e)}"

# --- LINE Webhook ---
@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers["X-Line-Signature"]
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return "OK"

# --- メッセージ処理 ---
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_msg = event.message.text.strip()

    if user_msg.startswith("保存:") and "内容:" in user_msg:
        try:
            filename_part, content_part = user_msg.split("内容:", 1)
            filename = filename_part.replace("保存:", "").strip()
            content = content_part.strip()
            result = save_log_to_dropbox(filename, content)
        except Exception:
            result = "❌ コマンド形式エラー（保存:ファイル名 内容:内容）"
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=result))
        return

    if user_msg.startswith("読み込み:"):
        filename = user_msg.replace("読み込み:", "").strip()
        result = read_log_from_dropbox(filename)
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=result))
        return

    if user_msg.startswith("削除:"):
        filename = user_msg.replace("削除:", "").strip()
        result = delete_dropbox_file(filename)
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=result))
        return

    if user_msg == "一覧":
        result = list_dropbox_files()
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=result))
        return

    if user_msg.startswith("解析:"):
        filename = user_msg.replace("解析:", "").strip()
        result = analyze_file_with_gpt(filename)
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=result[:3000]))  # LINE制限
        return

    line_bot_api.reply_message(event.reply_token, TextSendMessage(text="❌ コマンドが不明です。"))

# --- コードアップデートエンドポイント ---
@app.route("/update-code", methods=["POST"])
def update_code():
    try:
        new_code = request.data.decode("utf-8")
        script_path = os.path.realpath(__file__)
        with open(script_path, "w", encoding="utf-8") as f:
            f.write(new_code)
        return "✅ コード更新完了（再起動で反映されます）"
    except Exception as e:
        return f"❌ コード更新失敗: {str(e)}", 500

# --- アプリ起動（Renderでは無効） ---
if __name__ == "__main__":
    app.run()