# dropbox_auth.py
import os
import json
import requests

def get_dropbox_access_token():
    client_id = os.environ.get("DROPBOX_CLIENT_ID")
    client_secret = os.environ.get("DROPBOX_CLIENT_SECRET")
    refresh_token = os.environ.get("DROPBOX_REFRESH_TOKEN")

    if not all([client_id, client_secret, refresh_token]):
        raise Exception("Dropbox認証情報が環境変数に設定されていません。")

    url = "https://api.dropbox.com/oauth2/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "client_id": client_id,
        "client_secret": client_secret
    }

    response = requests.post(url, headers=headers, data=data)
    if response.status_code != 200:
        raise Exception(f"Dropboxアクセストークンの取得に失敗: {response.text}")

    return response.json()["access_token"]
