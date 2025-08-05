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
