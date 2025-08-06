import dropbox
import os

# 環境変数からDropbox設定を取得
DROPBOX_CLIENT_ID = os.getenv("DROPBOX_CLIENT_ID")
DROPBOX_CLIENT_SECRET = os.getenv("DROPBOX_CLIENT_SECRET")
DROPBOX_REFRESH_TOKEN = os.getenv("DROPBOX_REFRESH_TOKEN")

# Dropboxフルアクセス用スコープとリフレッシュトークンで認証
def get_dropbox_client():
    from dropbox.oauth import DropboxOAuth2FlowNoRedirect

    if not (DROPBOX_CLIENT_ID and DROPBOX_CLIENT_SECRET and DROPBOX_REFRESH_TOKEN):
        raise Exception("❌ Dropboxの認証情報が不足しています。")

    from dropbox.oauth import DropboxOAuth2FlowNoRedirect
    from dropbox import Dropbox, DropboxOAuth2FlowNoRedirect

    from dropbox.oauth import OAuth2AccessToken
    from dropbox.common import new_session

    session = new_session()
    oauth2_access_token, _ = session.refresh_access_token(
        client_id=DROPBOX_CLIENT_ID,
        client_secret=DROPBOX_CLIENT_SECRET,
        refresh_token=DROPBOX_REFRESH_TOKEN
    )

    return dropbox.Dropbox(oauth2_access_token)

# ログをDropboxに保存する関数
def save_log_to_dropbox(filename: str, content: str) -> str:
    try:
        dbx = get_dropbox_client()
        dropbox_path = f"/E.T Code Logs/{filename}"

        dbx.files_upload(content.encode(), dropbox_path, mode=dropbox.files.WriteMode.overwrite)
        return f"✅ 保存完了：{filename}"
    except Exception as e:
        return f"❌ 保存失敗: {str(e)}"