import dropbox
import os

DROPBOX_ACCESS_TOKEN = os.getenv("DROPBOX_ACCESS_TOKEN")
dbx = dropbox.Dropbox(DROPBOX_ACCESS_TOKEN)

def save_log_to_dropbox(filename, content, folder_path="/"):
    """Dropboxにテキストを保存する"""
    try:
        path = f"{folder_path}/{filename}"
        dbx.files_upload(content.encode("utf-8"), path, mode=dropbox.files.WriteMode.overwrite)
        return f"✅ 保存完了: {filename}"
    except Exception as e:
        return f"❌ 保存失敗: {str(e)}"

def load_log_from_dropbox(filename, folder_path="/"):
    """Dropboxからテキストを読み込む"""
    path = f"{folder_path}/{filename}"
    try:
        _, res = dbx.files_download(path)
        return res.content.decode("utf-8")
    except Exception as e:
        return f"❌ 読み込み失敗: {str(e)}"

def list_files_in_dropbox(folder_path="/"):
    """Dropbox内のファイル一覧を取得"""
    try:
        result = dbx.files_list_folder(folder_path)
        return [entry.name for entry in result.entries if isinstance(entry, dropbox.files.FileMetadata)]
    except Exception as e:
        return [f"❌ エラー: {str(e)}"]