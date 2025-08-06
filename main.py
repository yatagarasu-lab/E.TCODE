import datetime
import os
from dropbox import Dropbox, exceptions

# Dropbox 初期化（ET_CODE_DROPBOX_TOKEN はすでに登録済み前提）
DROPBOX_TOKEN = os.getenv("ET_CODE_DROPBOX_TOKEN")
dbx = Dropbox(DROPBOX_TOKEN)

def save_log_to_dropbox(log_text: str, prefix: str = "gpt_log") -> str:
    """
    会話ログをDropboxに保存する（ファイル名にタイムスタンプ付き）
    """
    now = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"{prefix}_{now}.txt"
    dropbox_path = f"/logs/{filename}"

    try:
        dbx.files_upload(log_text.encode('utf-8'), dropbox_path, mode=dropbox.files.WriteMode("add"))
        print(f"✅ ログをDropboxに保存しました: {dropbox_path}")
        return filename
    except exceptions.ApiError as e:
        print(f"❌ Dropboxアップロード失敗: {e}")
        return ""