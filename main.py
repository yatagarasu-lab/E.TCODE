import os
import dropbox
from datetime import datetime
from requests.auth import HTTPBasicAuth
import requests

# --- 環境変数からDropbox認証情報を取得 ---
DROPBOX_REFRESH_TOKEN = os.environ.get("DROPBOX_REFRESH_TOKEN")
DROPBOX_CLIENT_ID = os.environ.get("DROPBOX_CLIENT_ID")
DROPBOX_CLIENT_SECRET = os.environ.get("DROPBOX_CLIENT_SECRET")

# --- アクセストークンの取得 ---
def get_access_token():
    url = "https://api.dropbox.com/oauth2/token"
    data = {
        "grant_type": "refresh_token",
        "refresh_token": DROPBOX_REFRESH_TOKEN,
    }
    auth = HTTPBasicAuth(DROPBOX_CLIENT_ID, DROPBOX_CLIENT_SECRET)
    res = requests.post(url, data=data, auth=auth)
    return res.json()["access_token"]

# --- Dropbox APIインスタンスの取得 ---
def get_dbx():
    access_token = get_access_token()
    return dropbox.Dropbox(access_token)

# --- ログファイルのパス ---
LOG_FILE_PATH = "webhook_log.txt"

# --- ログをDropbox上のファイルとして保存 ---
def log_event(message):
    timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    log_line = f"{timestamp} {message}\n"
    with open(LOG_FILE_PATH, "a", encoding="utf-8") as f:
        f.write(log_line)

# --- Dropboxログファイルの読み取り ---
def read_log_file(path="/logs/webhook_log.txt"):
    try:
        dbx = get_dbx()
        _, res = dbx.files_download(path)
        content = res.content.decode("utf-8")
        return content
    except Exception as e:
        return f"ログファイルの読み取りに失敗しました: {e}"

# --- E.T Code から送られたコードをDropboxに保存 ---
def save_code_to_dropbox(filename, code):
    try:
        dbx = get_dbx()
        path = f"/Apps/slot-data-analyzer/{filename}"
        dbx.files_upload(
            code.encode("utf-8"),
            path,
            mode=dropbox.files.WriteMode("overwrite"),
            mute=True
        )
        log_event(f"Dropboxに {filename} を保存しました。パス: {path}")
        return True, f"{filename} をDropboxに保存しました。"
    except Exception as e:
        log_event(f"Dropbox保存エラー: {e}")
        return False, str(e)