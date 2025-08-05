# main.py（E.T Code）

from flask import Flask, request
from update_code import handle_code_update

app = Flask(__name__)

@app.route("/")
def index():
    return "E.T Code is running!"

# 八咫烏からコードを受信するエンドポイント
@app.route("/update-code", methods=["POST"])
def update_code():
    return handle_code_update()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)