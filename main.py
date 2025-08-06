# 🔼 すでにある import の下に追加（重複なければそのまま）
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import dropbox
import os

# 🔼 LINE Bot & Dropboxの設定
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")
DROPBOX_ACCESS_TOKEN = os.getenv("DROPBOX_ACCESS_TOKEN")

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)
dbx = dropbox.Dropbox(DROPBOX_ACCESS_TOKEN)

# 🔽 Flaskアプリ本体
app = Flask(__name__)

@app.route("/", methods=["GET"])
def health_check():
    return "E.T Code is running."

@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers["X-Line-Signature"]
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except Exception as e:
        print(f"❌ Webhook Error: {e}")
        abort(400)

    return "OK"

# 🔽 Dropboxログ保存関数
def save_log_to_dropbox(filename, content):
    try:
        path = f"/logs/{filename}"
        dbx.files_upload(content.encode(), path, mode=dropbox.files.WriteMode.overwrite)
        return f"✅ ログ保存成功: {filename}"
    except Exception as e:
        return f"❌ 保存失敗: {str(e)}"

# 🔽 LINEメッセージイベントハンドラ
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_msg = event.message.text.strip()

    # ✅ ログ保存コマンド（例：保存:log1.txt 内容:これはテストです）
    if user_msg.startswith("保存:") and "内容:" in user_msg:
        try:
            # メッセージを "保存:ファイル名 内容:ログ内容" の形式で分割
            filename_part, content_part = user_msg.split("内容:", 1)
            filename = filename_part.replace("保存:", "").strip()
            content = content_part.strip()

            # Dropboxに保存実行
            result = save_log_to_dropbox(filename, content)

            # 成功/失敗メッセージをLINEに返信
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=result)
            )
            return
        except Exception as e:
            # フォーマットエラー等の例外処理
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="❌ コマンド形式エラー（保存:ファイル名 内容:内容）で送信してください）")
            )
            return

    # 他の通常メッセージ
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text="📌 コマンドを受信しました。")
    )

# 🔽 サーバー起動
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))