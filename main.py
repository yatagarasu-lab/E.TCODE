from flask import Flask, request, jsonify
import os
import datetime
import requests

app = Flask(__name__)

# Dropbox App Credentials
CLIENT_ID = os.getenv("DROPBOX_CLIENT_ID")
CLIENT_SECRET = os.getenv("DROPBOX_CLIENT_SECRET")
REFRESH_TOKEN = os.getenv("DROPBOX_REFRESH_TOKEN")

# アクセストークンを取得する関数
def get_access_token():
    url = "https://api.dropbox.com/oauth2/token"
    data = {
        "grant_type": "refresh_token",
        "refresh_token": REFRESH_TOKEN,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
    }

    response = requests.post(url, data=data)
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        raise Exception("Dropboxのアクセストークン取得に失敗しました: " + response.text)

@app.route("/", methods=["GET"])
def home():
    return "E.T Codelabo Server is Running!"

@app.route("/receive-code", methods=["POST"])
def receive_code():
    try:
        data = request.get_json()
        user_id = data.get("user_id")
        message = data.get("message")
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

        # 保存パス（Dropbox上）
        dropbox_path = f"/Apps/slot-data-analyzer/{timestamp}_{user_id}.txt"
        access_token = get_access_token()

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/octet-stream",
            "Dropbox-API-Arg": str({
                "path": dropbox_path,
                "mode": "add",
                "autorename": True,
                "mute": True
            }).replace("'", '"')  # Dropbox APIはJSON文字列を要求
        }

        res = requests.post(
            "https://content.dropboxapi.com/2/files/upload",
            headers=headers,
            data=message.encode()
        )

        if res.status_code == 200:
            return jsonify({"status": "success", "path": dropbox_path}), 200
        else:
            return jsonify({"status": "error", "dropbox_error": res.text}), 500

    except Exception as e:
        return jsonify({"status": "error", "exception": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)