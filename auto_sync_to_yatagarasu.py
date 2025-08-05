# E.T Code 側：auto_sync_to_yatagarasu.py
import os
import requests

# 八咫烏のエンドポイント（環境変数で管理）
YATAGARASU_ENDPOINT = os.environ.get("YATAGARASU_ENDPOINT")  # 例: https://yatagarasu.onrender.com/receive-code

SCRIPTS_DIR = "scripts"

def send_file_to_yatagarasu(filename: str, code: str):
    try:
        response = requests.post(
            YATAGARASU_ENDPOINT,
            json={"filename": filename, "code": code},
            timeout=10
        )
        print(f"[✓] {filename} を送信 → {response.status_code}")
    except Exception as e:
        print(f"[✗] {filename} の送信に失敗: {e}")

def sync_all_scripts():
    for fname in os.listdir(SCRIPTS_DIR):
        path = os.path.join(SCRIPTS_DIR, fname)
        if not os.path.isfile(path) or not fname.endswith(".py"):
            continue

        with open(path, "r", encoding="utf-8") as f:
            code = f.read()
            send_file_to_yatagarasu(fname, code)

if __name__ == "__main__":
    sync_all_scripts()
