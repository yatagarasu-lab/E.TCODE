from flask import Flask, request
from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from linebot.exceptions import InvalidSignatureError
import dropbox
import os

# Flask アプリケーション
app = Flask(__name__)

# LINE Messaging API設定
LINE_CHANNEL_SECRET = os.environ.get("LINE_CHANNEL_SECRET")
LINE_CHANNEL_ACCESS_TOKEN = os.environ.get("LINE_CHANNEL_ACCESS_TOKEN")
line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# Dropbox 認証
DROPBOX_ACCESS_TOKEN = os.environ.get("DROPBOX_ACCESS_TOKEN")
dbx = dropbox.Dropbox(DROPBOX_ACCESS_TOKEN)


# ✅ ログ読み出し関数
def read_log_from_dropbox(filename: str) -> str:
    """
    Dropbox内の指定されたログファイル（/logs/{filename}）を読み出して返します。
    """
    try:
        path = f"/logs/{filename}"
        metadata, res = dbx.files_download(path)
        content = res.content.decode("utf-8")
        print(f"✅ ログ '{filename}' 読み込み成功")
        return content
    except dropbox.exceptions.HttpError as e:
        print(f"❌ Dropboxログ読み出しエラー: {e}")
        return f"読み込みエラー：{filename}"


# ✅ LINE Webhook エンドポイント
@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers["X-Line-Signature"]
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        return "Invalid signature", 400
    return "OK", 200


# ✅ LINEメッセージ受信時の処理
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_msg = event.message.text.strip()
    
    # ✅ 例：ログ読み取りコマンド
    if user_msg.startswith("ログ:"):
        filename = user_msg.replace("ログ:", "").strip()
        content = read_log_from_dropbox(filename)
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=content))
    else:
        # 通常返信
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="ありがとうございます"))


# ✅ Renderで起動するための設定
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))  # Renderでは10000番ポート
    app.run(host="0.0.0.0", port=port)
    # ✅ ログ保存関数（Dropboxに書き込み）
def save_log_to_dropbox(filename: str, content: str) -> str:
    """
    指定された内容（content）をDropboxの /logs/{filename} に保存する。
    """
    try:
        path = f"/logs/{filename}"
        dbx.files_upload(
            content.encode("utf-8"),
            path,
            mode=dropbox.files.WriteMode("overwrite")
        )
        print(f"✅ ログ '{filename}' 保存成功")
        return f"保存成功: {filename}"
    except dropbox.exceptions.ApiError as e:
        print(f"❌ Dropboxログ保存エラー: {e}")
        return f"保存エラー: {filename}"