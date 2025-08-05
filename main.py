# main.py（E.T Code 側の送信スクリプト）

import requests
import json

# 八咫烏（Render側）のURLをここにセット（例は仮）
RENDER_URL = "https://your-render-url.onrender.com/update-code"

def send_code(filename, code):
    """指定したファイル名とコードを八咫烏に送信する"""
    payload = {
        "filename": filename,
        "code": code
    }

    try:
        response = requests.post(RENDER_URL, json=payload)
        if response.status_code == 200:
            print(f"[成功] {filename} を八咫烏に送信しました")
        else:
            print(f"[失敗] ステータス: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"[エラー] 送信中に問題が発生しました: {e}")

if __name__ == "__main__":
    # 🔁 書き換えたいコードをここに記述（例：main.py）
    filename_to_update = "main.py"
    code_to_send = """
print("これはE.T Codeから送信されたコードです！")
"""

    send_code(filename_to_update, code_to_send)