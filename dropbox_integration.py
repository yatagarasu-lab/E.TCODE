# dropbox_integration.py に追加
import os
import dropbox
from datetime import datetime
from requests.auth import HTTPBasicAuth
import requests

# 認証（統一）
def get_access_token():
    url = "https://api.dropbox.com/oauth2/token"
    data = {
        "grant_type": "refresh_token",
        "refresh_token": os.getenv("DROPBOX_REFRESH_TOKEN")
    }
    auth = HTTPBasicAuth(os.getenv("DROPBOX_CLIENT_ID"), os.getenv("DROPBOX_CLIENT_SECRET"))
    res = requests.post(url, data=data, auth=auth)
    return res.json()["access_token"]

def get_dbx():
    return dropbox.Dropbox(get_access_token())

# コードをDropboxにアップロード
def update_yatagarasu_code(filename, code_str):
    path = f"/Apps/yatagarasu/code/{filename}"
    dbx = get_dbx()
    dbx.files_upload(code_str.encode("utf-8"), path, mode=dropbox.files.WriteMode.overwrite)

# ログをDropboxに追記保存
def write_dropbox_log(message):
    log_path = "/Apps/yatagarasu/logs/" + datetime.now().strftime("%Y%m%d") + "_log.txt"
    timestamp = datetime.now().isoformat()
    dbx = get_dbx()

    try:
        # 既存ログ読み込み
        _, res = dbx.files_download(log_path)
        existing = res.content.decode("utf-8")
    except dropbox.exceptions.ApiError:
        existing = ""

    new_log = existing + f"[{timestamp}] {message}\n"
    dbx.files_upload(new_log.encode("utf-8"), log_path, mode=dropbox.files.WriteMode.overwrite)