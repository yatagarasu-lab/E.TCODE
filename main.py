from flask import Flask, request, jsonify
from services.dropbox_utils import get_file_list, download_file, upload_file
import os

app = Flask(__name__)

# 環境変数（.env または Render上で設定済）
DROPBOX_TARGET_PATH = "/Apps/yatagarasu_code/"  # 八咫烏のコード保存先

@app.route("/", methods=["GET"])
def index():
    return jsonify({"status": "E.T Code is running"}), 200

# 八咫烏のコード一覧取得（ファイル名リスト）
@app.route("/code/list", methods=["GET"])
def list_files():
    try:
        files = get_file_list(DROPBOX_TARGET_PATH)
        return jsonify({"files": files})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 八咫烏のコード内容を取得（ファイル名指定）
@app.route("/code/read", methods=["POST"])
def read_file():
    data = request.get_json()
    filename = data.get("filename")
    if not filename:
        return jsonify({"error": "filename is required"}), 400
    try:
        content = download_file(DROPBOX_TARGET_PATH + filename)
        return jsonify({"filename": filename, "content": content})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 八咫烏のコードを上書き保存
@app.route("/code/save", methods=["POST"])
def save_file():
    data = request.get_json()
    filename = data.get("filename")
    content = data.get("content")
    if not filename or content is None:
        return jsonify({"error": "filename and content are required"}), 400
    try:
        upload_file(DROPBOX_TARGET_PATH + filename, content)
        return jsonify({"message": f"{filename} saved successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))