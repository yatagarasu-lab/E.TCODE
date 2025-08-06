import os
import hashlib
import dropbox
import openai
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

# 環境変数の読み込み
LINE_CHANNEL_ACCESS_TOKEN = os.environ.get("LINE_CHANNEL_ACCESS_TOKEN")
LINE_CHANNEL_SECRET = os.environ.get("LINE_CHANNEL_SECRET")
DROPBOX_REFRESH_TOKEN = os.environ.get("DROPBOX_REFRESH_TOKEN")
DROPBOX_APP_KEY = os.environ.get("DROPBOX_APP_KEY")
DROPBOX_APP_SECRET = os.environ.get("DROPBOX_APP_SECRET")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

# インスタンス
app = Flask(__name__)
line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# Dropbox セッション生成（Refresh Token 使用）
def create_dropbox_client():
    from dropbox.oauth import DropboxOAuth2FlowNoRedirect
    from dropbox.dropbox_client import create_session

    session = create_session(app_key=DROPBOX_APP_KEY, app_secret=DROPBOX_APP_SECRET)
    token = session.refresh_access_token(DROPBOX_REFRESH_TOKEN)
    return dropbox.Dropbox(oauth2_access_token=token.access_token)

# GPT要約関数
def summarize_with_gpt(content):
    openai.api_key = OPENAI_API_KEY
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "以下の内容を1〜2行でわかりやすく要約してください。"},
                {"role": "user", "content": content}
            ],
            temperature=0.5,
            max_tokens=150
        )
        return response.choices[0].message["content"].strip()
    except Exception as e:
        return f"❌ 要約に失敗しました: {str(e)}"

# Dropbox保存処理
def save_log_to_dropbox(filename, content):
    try:
        dbx = create_dropbox_client()
        path = f"/Apps/slot-data-analyzer/{filename}"
        dbx.files_upload(content.encode(), path, mode=dropbox.files.WriteMode("overwrite"))
        return f"✅ 保存成功: {filename}"
    except Exception as e:
        return f"❌ Dropbox保存失敗: {str(e)}"

# ファイル読み込み（要約用）
def read_file_from_dropbox(filename):
    try:
        dbx = create_dropbox_client()
        path = f"/Apps/slot-data-analyzer/{filename}"
        metadata, res = dbx.files_download(path)
        return res.content.decode()
    except Exception as e:
        return None

# LINE メッセージ受信
@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers["X-Line-Signature"]
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return "OK"

# メッセージイベント処理
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

            # 要約を生成して返信
            summary = summarize_with_gpt(content)
            reply_text = f"{result}\n\n📝 要約:\n{summary}"
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_text))
            return
        except Exception as e:
            # フォーマットエラー等の例外処理
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="❌ コマンド形式エラー（保存:ファイル名 内容:内容）で送信してください）")
            )
            return

    # その他のメッセージ（未対応）
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text="✅ メッセージ受信しました"))

# アプリ起動
if __name__ == "__main__":
    app.run()