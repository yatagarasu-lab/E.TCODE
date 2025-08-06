from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from dropbox_utils import save_log_to_dropbox, load_log_from_dropbox, list_files_in_dropbox

import os

app = Flask(__name__)

# 環境変数からLINEチャネルの情報を取得
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers["X-Line-Signature"]
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return "OK"

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_msg = event.message.text.strip()

    # ✅ ログ保存コマンド（例：保存:log1.txt 内容:これはテストです）
    if user_msg.startswith("保存:") and "内容:" in user_msg:
        try:
            filename_part, content_part = user_msg.split("内容:", 1)
            filename = filename_part.replace("保存:", "").strip()
            content = content_part.strip()
            result = save_log_to_dropbox(filename, content)
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=result))
            return
        except Exception:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="❌ コマンド形式エラー（保存:ファイル名 内容:内容）で送信）"))
            return

    # ✅ ログ読み込みコマンド（例：読み込み:log1.txt）
    if user_msg.startswith("読み込み:"):
        try:
            filename = user_msg.replace("読み込み:", "").strip()
            content = load_log_from_dropbox(filename)
            if len(content) <= 4000:
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text=content))
            else:
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text="✅ 読み込み成功（内容が長いため省略）"))
            return
        except Exception:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="❌ 読み込み失敗（ファイルが存在しない可能性）"))
            return

    # ✅ 一覧コマンド
    if user_msg == "一覧":
        try:
            files = list_files_in_dropbox()
            if files:
                reply = "📂 Dropboxファイル一覧:\n" + "\n".join(f"- {f}" for f in files)
            else:
                reply = "📂 ファイルが存在しません。"
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))
            return
        except Exception:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="❌ ファイル一覧取得に失敗しました"))
            return

    # デフォルト応答
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text="ありがとうございます"))