import os
import dropbox

# Dropbox API に接続するための関数
def get_dropbox_client():
    refresh_token = os.environ.get("DROPBOX_REFRESH_TOKEN")
    app_key = os.environ.get("DROPBOX_APP_KEY")
    app_secret = os.environ.get("DROPBOX_APP_SECRET")

    if not all([refresh_token, app_key, app_secret]):
        raise ValueError("Dropbox 認証情報が不足しています")

    return dropbox.Dropbox(
        app_key=app_key,
        app_secret=app_secret,
        oauth2_refresh_token=refresh_token
    )

# 指定フォルダ内のファイル一覧を取得
def list_files(folder_path="/Apps/slot-data-analyzer"):
    dbx = get_dropbox_client()
    res = dbx.files_list_folder(folder_path)
    return res.entries

# ファイルをダウンロードして内容を返す
def download_file(path):
    dbx = get_dropbox_client()
    _, res = dbx.files_download(path)
    return res.content.decode("utf-8")

# 最も新しいファイルを取得
def get_latest_file_path(folder_path="/Apps/slot-data-analyzer"):
    files = list_files(folder_path)
    if not files:
        return None
    latest = max(files, key=lambda f: f.client_modified)
    return latest.path_display

# WebhookログファイルをDropboxから読み取る（新機能）
def read_log_file(file_path="/logs/webhook_log.txt"):
    try:
        content = download_file(file_path)
        print(f"[log] ログファイル読み取り成功: {file_path}")
        return content
    except Exception as e:
        print(f"[error] ログファイル読み取り失敗: {e}")
        return f"ログ取得エラー: {e}"