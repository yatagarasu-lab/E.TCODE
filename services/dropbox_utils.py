import dropbox
import os

# 環境変数から取得
DROPBOX_APP_KEY = os.environ.get("DROPBOX_APP_KEY")
DROPBOX_APP_SECRET = os.environ.get("DROPBOX_APP_SECRET")
DROPBOX_REFRESH_TOKEN = os.environ.get("DROPBOX_REFRESH_TOKEN")

# Dropbox セッション初期化
def get_dropbox():
    if not DROPBOX_REFRESH_TOKEN or not DROPBOX_APP_KEY or not DROPBOX_APP_SECRET:
        raise Exception("Dropbox環境変数が未設定です。")
    
    oauth_result = dropbox.DropboxOAuth2FlowNoRedirect(
        consumer_key=DROPBOX_APP_KEY,
        consumer_secret=DROPBOX_APP_SECRET
    )
    dbx = dropbox.Dropbox(
        oauth2_refresh_token=DROPBOX_REFRESH_TOKEN,
        app_key=DROPBOX_APP_KEY,
        app_secret=DROPBOX_APP_SECRET
    )
    return dbx

# ファイル一覧を取得（指定フォルダ）
def get_file_list(folder_path):
    dbx = get_dropbox()
    result = dbx.files_list_folder(folder_path)
    return [entry.name for entry in result.entries if isinstance(entry, dropbox.files.FileMetadata)]

# ファイルの内容を取得（テキスト）
def download_file(file_path):
    dbx = get_dropbox()
    metadata, res = dbx.files_download(file_path)
    return res.content.decode("utf-8")

# ファイルをアップロード（テキストで上書き保存）
def upload_file(file_path, content):
    dbx = get_dropbox()
    dbx.files_upload(content.encode("utf-8"), file_path, mode=dropbox.files.WriteMode.overwrite)
