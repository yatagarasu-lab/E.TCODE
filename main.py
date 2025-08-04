from flask import Flask, request, jsonify
import os
from services.gpt_editor import edit_yatagarasu_code  # GPTによる八咫烏コード編集
from services.dropbox_sync import ensure_dropbox_sync  # Dropbox連携の準備（未使用ならスキップ可能）

app = Flask(__name__)

@app.route("/", methods=["GET"])
def index():
    return "E.T Code is running!"

@app.route("/edit", methods=["POST"])
def edit_yatagarasu():
    data = request.json
    if not data or "instructions" not in data:
        return jsonify({"error": "No instructions provided"}), 400

    instructions = data["instructions"]
    result = edit_yatagarasu_code(instructions)
    return jsonify(result)

if __name__ == "__main__":
    # 必要なら Dropbox同期を初期化（スキップ可能）
    # ensure_dropbox_sync()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))