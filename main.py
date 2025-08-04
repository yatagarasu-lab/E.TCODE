import os
from flask import Flask, request
from dropbox_integration import handle_dropbox_webhook

app = Flask(__name__)

# Dropbox環境変数の読み込み（未連携なら空でも動作OK）
DROPBOX_APP_KEY = os.getenv("DROPBOX_APP_KEY")
DROPBOX_APP_SECRET = os.getenv("DROPBOX_APP_SECRET")
DROPBOX_REFRESH_TOKEN = os.getenv("DROPBOX_REFRESH_TOKEN")

@app.route("/", methods=["GET"])
def health_check():
    print("Health check accessed.")
    return "Yatagarasu is live!", 200

@app.route("/webhook", methods=["POST"])
def webhook():
    print("Webhook received.")
    return handle_dropbox_webhook()

if __name__ == "__main__":
    print("アプリ起動中")
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

print("完了")