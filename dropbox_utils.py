import dropbox
import os

# Dropbox設定
DROPBOX_REFRESH_TOKEN = os.environ["DROPBOX_REFRESH_TOKEN"]
DROPBOX_APP_KEY = os.environ["DROPBOX_APP_KEY"]
DROPBOX_APP_SECRET = os.environ["DROPBOX_APP_SECRET"]

# 認証
dbx = dropbox.Dropbox(
    app_key=DROPBOX_APP_KEY,
    app_secret=DROPBOX_APP_SECRET,
    oauth2_refresh_token=DROPBOX_REFRESH_TOKEN
)

def save_log_to_dropbox(filename, content):
    """ログをDropboxに保存する"""
    path = f"/{filename}" if not filename.startswith("/") else filename
    try:
        dbx.files_upload(content.encode("utf-8"), path, mode=dropbox.files.WriteMode.overwrite)
        return f"✅ 保存成功: {filename}"
    except Exception as e:
        return f"❌ 保存エラー: {str(e)}"

def load_log_from_dropbox(filename):
    """Dropboxからログファイルの内容を読み込む"""
    path = f"/{filename}" if not filename.startswith("/") else filename
    try:
        metadata, res = dbx.files_download(path)
        return res.content.decode("utf-8")
    except Exception as e:
        return f"❌ 読み込みエラー: {str(e)}"