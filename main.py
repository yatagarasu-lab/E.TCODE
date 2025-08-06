from flask import Flask, request
from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import os
from dropbox_utils import save_log_to_dropbox  # ログ保存用モジュール

# 環境変数からLINE設定を取得
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")

# LINE APIの初期化
line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# Flaskアプリの初期化
app = Flask(__name__)

# Webhookエンドポイント
@app.route("/webhook", methods=["POST"])
def webhook():
    signature = request.headers["X-Line-Signature"]
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except Exception as e:
        return "Error", 400

    return "OK", 200

# メッセージ受信処理
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

            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=result)
            )
            return
        except Exception:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="❌ コマンド形式エラー（保存:ファイル名 内容:内容）で送信してください）")
            )
            return

    # ✅ 通常メッセージ応答（任意でカスタマイズ可能）
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text="ありがとうございます。")
    )

# アプリ起動（Renderでは不要だがローカル動作確認用）
if __name__ == "__main__":
    app.run()