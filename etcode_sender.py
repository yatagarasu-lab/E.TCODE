# etcode_sender.py（E.T Code 側の送信スクリプト）

import requests
import json

# あなたのRender URLをここに
RENDER_URL = "https://your-render-url.onrender.com/update-code"

def send_code(filename, code):
    payload = {
        "filename": filename,
        "code": code
    }

    response = requests.post(RENDER_URL, json=payload)

    if response.status_code == 200:
        print(f"[成功] {filename} を八咫烏に送信しました")
    else:
        print(f"[失敗] ステータス: {response.status_code}")
        print(response.text)

# 例：main.py を書き換えたいとき
if __name__ == "__main__":
    code_to_send = """
print("これはE.T Codeから送信されたコードです！")
"""
    send_code("main.py", code_to_send)
