from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

from dropbox_auth import get_dropbox_access_token
import dropbox
import os

app = Flask(__name__)

# LINE Messaging API
LINE_CHANNEL_SECRET = os.environ.get("LINE_CHANNEL_SECRET")
LINE_CHANNEL_ACCESS_TOKEN = os.environ.get("LINE_CHANNEL_ACCESS_TOKEN")

if not LINE_CHANNEL_SECRET or not LINE_CHANNEL_ACCESS_TOKEN:
    raise Exception("LINEの環境変数が設定されていません")

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# Dropbox認証（リフレッシュトークン対応）
DROPBOX_ACCESS_TOKEN = get_dropbox_access_token()
dbx = dropbox.Dropbox(DROPBOX_ACCESS_TOKEN)

# ルート確認用
@app.route("/")
def home():
    return "✅ LINE × Dropbox × GPT BOT 起動中"

# Webhook受信
@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers["X-Line-Signature"]
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return "OK"

# メッセージ受信処理
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_msg = event.message.text.strip()

    # ✅ 通常の挨拶応答
    if user_msg.lower() in ["こんにちは", "hello"]:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="こんにちは！ご用件は何ですか？"))
        return

    # ✅ ログ保存コマンド（例：保存:log1.txt 内容:これはテストです）
    if user_msg.startswith("保存:") and "内容:" in user_msg:
        try:
            filename_part, content_part = user_msg.split("内容:", 1)
            filename = filename_part.replace("保存:", "").strip()
            content = content_part.strip()

            result = save_log_to_dropbox(filename, content)

            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=result))
            return
        except Exception as e:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="❌ コマンド形式エラー（保存:ファイル名 内容:内容）で送信してください）")
            )
            return

    # ✅ 未対応メッセージ
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text="❌ 未対応のメッセージです"))

# Dropboxにテキスト保存
def save_log_to_dropbox(filename, content):
    try:
        dbx.files_upload(content.encode("utf-8"), f"/{filename}", mode=dropbox.files.WriteMode.overwrite)
        return f"✅ Dropboxに保存しました: {filename}"
    except Exception as e:
        return f"❌ Dropbox保存エラー: {str(e)}"

if __name__ == "__main__":
    app.run()