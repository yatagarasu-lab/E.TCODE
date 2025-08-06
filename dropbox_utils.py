import os
import dropbox
from datetime import datetime
from dropbox.exceptions import ApiError, AuthError

# Dropboxにログを保存する関数
def save_log_to_dropbox(filename: str, content: str) -> str:
    try:
        # 環境変数から認証情報を取得
        app_key = os.getenv("DROPBOX_APP_KEY")
        app_secret = os.getenv("DROPBOX_APP_SECRET")
        refresh_token = os.getenv("DROPBOX_REFRESH_TOKEN")

        if not all([app_key, app_secret, refresh_token]):
            return "❌ Dropbox認証情報が不足しています（環境変数を確認してください）"

        # Dropboxクライアントを初期化
        dbx = dropbox.Dropbox(
            oauth2_refresh_token=refresh_token,
            app_key=app_key,
            app_secret=app_secret
        )

        # 保存するファイルパス（タイムスタンプ付き）
        now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        dropbox_path = f"/E.T.Code/logs/{now}_{filename}"

        # アップロード処理（文字列 → バイト列に変換）
        dbx.files_upload(
            content.encode("utf-8"),
            dropbox_path,
            mode=dropbox.files.WriteMode("overwrite")
        )

        return f"✅ Dropboxに保存しました：{dropbox_path}"

    except AuthError:
        return "❌ Dropbox認証エラーが発生しました（トークンが無効または期限切れの可能性があります）"
    except ApiError as e:
        return f"❌ Dropbox APIエラー: {e}"
    except Exception as e:
        return f"❌ 保存処理で予期せぬエラーが発生しました: {str(e)}"