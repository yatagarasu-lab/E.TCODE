import os
from flask import jsonify
from datetime import datetime
from dropbox_utils import get_dropbox_client, get_latest_file_path, download_file

LAST_FILE_PATH = "last_notified.txt"

def load_last_notified():
    if os.path.exists(LAST_FILE_PATH):
        with open(LAST_FILE_PATH, "r", encoding="utf-8") as f:
            return f.read().strip()
    return ""

def save_last_notified(path):
    with open(LAST_FILE_PATH, "w", encoding="utf-8") as f:
        f.write(path)

def handle_check_dropbox():
    try:
        latest_path = get_latest_file_path()
        if not latest_path:
            return jsonify({"status": "no files found"})

        last_notified = load_last_notified()
        if latest_path == last_notified:
            return jsonify({"status": "no new files", "latest": latest_path})

        # ✅ 新ファイル → 内容読み取り
        content = download_file(latest_path)

        # 🔄 通知処理（ここにLINE/GPT処理を後で追加可能）
        print(f"[{datetime.now().isoformat()}] 新ファイル: {latest_path}")
        print("内容（冒頭100文字）:", content[:100])

        save_last_notified(latest_path)

        return jsonify({
            "status": "new file detected",
            "file": latest_path,
            "preview": content[:100]
        })

    except Exception as e:
        return jsonify({"error": str(e)})
