from flask import Flask, request, jsonify
from dropbox_integration import handle_dropbox_webhook
from dropbox_utils import read_log_file  # ← 追加

app = Flask(__name__)

@app.route("/")
def index():
    return "Dropbox Webhook Bot is running!"

# Dropbox Webhook用ルート
@app.route("/dropbox", methods=["GET", "POST"])
def dropbox_webhook():
    return handle_dropbox_webhook()

# Dropboxログ読み取り用エンドポイント
@app.route("/read-log", methods=["GET"])
def read_log():
    file_path = request.args.get("path", "/logs/webhook_log.txt")
    content = read_log_file(file_path)
    return jsonify({
        "file": file_path,
        "content": content
    })

if __name__ == "__main__":
    print("Flask app 起動")
    app.run(host="0.0.0.0", port=10000)
    print("完了")