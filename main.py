import os
import dropbox
from dropbox import exceptions
from flask import Flask, request, abort

from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

# ✅ 環境変数からトークンなどを取得
LINE_CHANNEL_ACCESS_TOKEN = os.environ.get("LINE_CHANNEL_ACCESS_TOKEN")
LINE_CHANNEL_SECRET = os.environ.get("LINE_CHANNEL_SECRET")
DROPBOX_ACCESS_TOKEN = os.environ.get("DROPBOX_ACCESS_TOKEN")

# ✅ Dropbox と LINE API 初期化
dbx = dropbox.Dropbox(DROPBOX_ACCESS_TOKEN)
line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# ✅ Flask アプリケーション
app = Flask(__name__)

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

# ✅ ログ読み出し関数（Dropboxから取得）
def read_log_from_dropbox(filename: str) -> str:
    """
    Dropbox内の指定されたログファイル（/logs/{filename}）を読み込んで返す。
    """
    try:
        path = f"/logs/{filename}"
        metadata, res = dbx.files_download(path)
        content = res.content.decode("utf-8")
        print(f"✅ ログ '{filename}' 読み込み成功")
        return content
    except exceptions.HttpError as e:
        print(f"❌ Dropboxログ読み出しエラー: {e}")
        return f"読み込みエラー: {filename}"

# ✅ LINE Webhook エンドポイント
@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers["X-Line-Signature"]
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return "OK"

# ✅ メッセージイベント処理
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_msg = event.message.text.strip()

    # ✅ ログ保存コマンド例：
    # 保存:sample.txt 内容:これはテストログです
    if user_msg.startswith("保存:") and "内容:" in user_msg:
        try:
            filename_part, content_part = user_msg.split("内容:", 1)
            filename = filename_part.replace("保存:", "").strip()
            content = content_part.strip()
            result = save_log_to_dropbox(filename, content)
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=result))
            return
        except Exception as e:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="❌ コマンド形式エラー"))
            return

    # ✅ ログ読込コマンド例：
    # 読込:sample.txt
    if user_msg.startswith("読込:"):
        filename = user_msg.replace("読込:", "").strip()
        result = read_log_from_dropbox(filename)
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=result))
        return

    # 既定の応答
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text="ありがとうございます"))

# ✅ サーバー起動
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 1000))
    app.run(host="0.0.0.0", port=port)