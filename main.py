import os
from flask import Flask, request

app = Flask(__name__)

@app.route("/", methods=["GET"])
def index():
    return "E.TCODE is running!", 200

if __name__ == "__main__":
    # Render環境ではPORTが自動で設定されるので、それを取得
    port = int(os.environ.get("PORT", 5000))  # ローカル実行時は5000番
    app.run(host="0.0.0.0", port=port)