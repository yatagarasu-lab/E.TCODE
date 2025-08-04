import os
from flask import Flask, request, jsonify
from linebot import LineBotApi, WebhookHandler
from linebot.models import TextSendMessage
import openai
import dropbox

# Flask初期化
app = Flask(__name__)

# 環境変数取得
DROPBOX_APP_KEY = os.getenv("DROPBOX_APP_KEY")
DROPBOX_APP_SECRET = os.getenv("DROPBOX_APP_SECRET")
DROPBOX_REFRESH_TOKEN = os.getenv("DROPBOX_REFRESH_TOKEN")
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
LINE_USER_ID = os.getenv("LINE_USER_ID")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# LINE Bot初期化
line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# Dropbox クライアント初期化
dbx = dropbox.Dropbox(
    oauth2_refresh_token=DROPBOX_REFRESH_TOKEN,
    app_key=DROPBOX_APP_KEY,
    app_secret=DROPBOX_APP_SECRET
)

# OpenAI初期化
openai.api_key = OPENAI_API_KEY

@app.route("/", methods=["GET"])
def home():
    return "YATAGARASU is alive!"

@app.route("/webhook/dropbox", methods=["POST"])
def dropbox_webhook():
    # WebhookからDropboxファイル変化通知を受信
    print("✅ Dropbox webhook received")
    send_line_message("📦 Dropboxでファイル変更を検知しました！")
    return "", 200

@app.route("/webhook/line", methods=["POST"])
def line_webhook():
    # LINEからのWebhookを処理
    signature = request.headers["X-Line-Signature"]
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except Exception as e:
        print(f"❌ LINE Webhook Error: {e}")
        return "Error", 400

    return "OK", 200

@app.route("/run_yatagarasu", methods=["POST"])
def run_yatagarasu():
    try:
        print("🕊️ 八咫烏を起動します...")
        send_line_message("🕊️ 八咫烏が起動しました。処理を開始します。")
        # ==== ここに八咫烏のメイン処理を書く ====
        # 例：
        # analyze_slot_data()
        # predict_setting()
        # summarize_results()
        # ===============================
        return jsonify({"status": "八咫烏起動OK"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def send_line_message(message):
    try:
        line_bot_api.push_message(LINE_USER_ID, TextSendMessage(text=message))
    except Exception as e:
        print(f"❌ LINE送信エラー: {e}")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)