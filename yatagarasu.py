import os
from services.dropbox_utils import get_file_list, download_file
from services.gpt_analyzer import analyze_content

# 解析対象のDropboxフォルダパス（ルート配下）
DROPBOX_TARGET_FOLDER = "/Apps/slot-data-analyzer"

# 最新ファイルを取得して解析
def analyze_latest_file():
    try:
        files = get_file_list(DROPBOX_TARGET_FOLDER)
        if not files:
            return "Dropbox内に解析可能なファイルがありません。"

        # ファイル名で降順ソート（新しい順）
        files.sort(reverse=True)
        latest_file_name = files[0]
        latest_file_path = f"{DROPBOX_TARGET_FOLDER}/{latest_file_name}"

        content = download_file(latest_file_path)
        result = analyze_content(content)
        return f"【ファイル名】{latest_file_name}\n\n【解析結果】\n{result}"
    except Exception as e:
        return f"解析中にエラーが発生しました: {str(e)}"
