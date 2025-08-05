from flask import Flask, request, jsonify
from dropbox_integration import handle_dropbox_webhook
from dropbox_utils import read_log_file, save_code_to_dropbox  # ← 追加

app = Flask(__name__)

# 起動確認
@app.route("/")
def index():
    return "Dropbox Webhook Bot is running!"

# Dropbox Webhookエンドポイント
@app.route("/dropbox", methods=["GET", "POST"])
def dropbox_webhook():
    return handle_dropbox_webhook()

# ログの読み取りエンドポイント
@app.route("/read-log", methods=["GET"])
def read_log():
    file_path = request.args.get("path", "/logs/webhook_log.txt")
    content = read_log_file(file_path)
    return jsonify({
        "file": file_path,
        "content": content
    })

# E.T Code からのコード受信 & Dropbox保存エンドポイント
@app.route("/update-code", methods=["POST"])
def update_code():
    data = request.json
    filename = data.get("filename", "unknown.py")
    code = data.get("code", "")

    success, message = save_code_to_dropbox(filename, code)
    if success:
        return jsonify({"status": "success", "message": message}), 200
    else:
        return jsonify({"status": "error", "message": message}), 500

# ローカル確認用（Renderではport無視）
if __name__ == "__main__":
    print("Flask app 起動")
    app.run(host="0.0.0.0", port=10000)
    print("完了")