# main.py

from flask import Flask
from dropbox_integration import handle_dropbox_webhook

app = Flask(__name__)

@app.route("/")
def index():
    return "Dropbox Webhook Bot is running!"

@app.route("/dropbox", methods=["GET", "POST"])
def dropbox_webhook():
    return handle_dropbox_webhook()

if __name__ == "__main__":
    print("Flask app 起動")
    app.run(host="0.0.0.0", port=10000)  # Renderが自動で PORT を割り当てるのでこの値は無視される
    print("完了")  # 起動完了ログ（Renderログで確認用）