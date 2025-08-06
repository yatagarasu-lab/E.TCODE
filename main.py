from flask import Flask, request, jsonify
import os
import dropbox
import datetime

app = Flask(__name__)

# Dropbox アクセストークン（環境変数）
DROPBOX_ACCESS_TOKEN = os.getenv("DROPBOX_ACCESS_TOKEN")

@app.route("/", methods=["GET"])
def home():
    return "E.T Codelabo Server is Running!"

@app.route("/receive-code", methods=["POST"])
def receive_code():
    try:
        data = request.get_json()
        user_id = data.get("user_id")
        message = data.get("message")
        timestamp = datetime.datetime.now().isoformat()

        # Dropbox保存パス
        file_path = f"/Apps/slot-data-analyzer/{timestamp}_{user_id}.txt"

        # 内容をDropboxにアップロード
        dbx = dropbox.Dropbox(DROPBOX_ACCESS_TOKEN)
        dbx.files_upload(message.encode(), file_path, mute=True)

        return jsonify({"status": "success", "path": file_path}), 200

    except Exception as e:
        return jsonify({"status": "error", "error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)