import os
import dropbox
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

# 環境変数から認証情報を取得
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")
DROPBOX_REFRESH_TOKEN = os.getenv("DROPBOX_REFRESH_TOKEN")
DROPBOX_APP_KEY = os.getenv("DROPBOX_APP_KEY")
DROPBOX_APP_SECRET = os.getenv("DROPBOX_APP_SECRET")

# Flask アプリ初期化
app = Flask(__name__)
line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# ✅ Dropboxクライアント作成
def get_dropbox():
    return dropbox.Dropbox(
        oauth2_refresh_token=DROPBOX_REFRESH_TOKEN,
        app_key=DROPBOX_APP_KEY,
        app_secret=DROPBOX_APP_SECRET
    )

# ✅ 保存処理
def save_log_to_dropbox(filename, content):
    try:
        dbx = get_dropbox()
        path = f"/{filename}"
        dbx.files_upload(content.encode(), path, mode=dropbox.files.WriteMode.overwrite)
        return f"✅ 保存完了: {filename}"
    except Exception as e:
        return f"❌ 保存失敗: {e}"

# ✅ 読み出し処理
def read_log_from_dropbox(filename):
    try:
        dbx = get_dropbox()
        path = f"/{filename}"
        _, res = dbx.files_download(path)
        return res.content.decode()
    except Exception:
        return "❌ 読み込み失敗（ファイルが存在しません）"

# ✅ 一覧取得
def list_dropbox_files():
    try:
        dbx = get_dropbox()
        result = dbx.files_list_folder("")
        files = [entry.name for entry in result.entries]
        return "📄 ファイル一覧:\n" + "\n".join(files) if files else "📂 ファイルは存在しません。"
    except Exception as e:
        return f"❌ 一覧取得失敗: {e}"

# ✅ 削除処理
def delete_dropbox_file(filename):
    try:
        dbx = get_dropbox()
        path = f"/{filename}"
        dbx.files_delete_v2(path)
        return f"🗑️ 削除完了: {filename}"
    except Exception:
        return "❌ 削除失敗（ファイルが存在しない可能性）"

# ✅ LINE Webhookエンドポイント
@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers["X-Line-Signature"]
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return "OK"

# ✅ LINEメッセージ処理
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_msg = event.message.text.strip()

    # 保存コマンド（保存:log1.txt 内容:これはテスト）
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

    # 読み込みコマンド
    if user_msg.startswith("読み込み:"):
        filename = user_msg.replace("読み込み:", "").strip()
        result = read_log_from_dropbox(filename)
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=result))
        return

    # 削除コマンド
    if user_msg.startswith("削除:"):
        filename = user_msg.replace("削除:", "").strip()
        result = delete_dropbox_file(filename)
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=result))
        return

    # 一覧コマンド
    if user_msg == "一覧":
        result = list_dropbox_files()
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=result))
        return

    # 不明コマンド
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text="❌ コマンドが不明です。"))

# ✅ Flaskアプリ起動（Renderなどで使用）
if __name__ == "__main__":
    app.run()