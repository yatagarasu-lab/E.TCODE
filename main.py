import os
from flask import Flask, request

app = Flask(__name__)

@app.route("/", methods=["GET"])
def index():
    return "LINE × Dropbox × GPT サーバー動作中！", 200

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    print("受信データ:", data)
    return "OK", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # ローカル環境では5000番
    app.run(host="0.0.0.0", port=port)