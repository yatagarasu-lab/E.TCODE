# etcode_sender.py

import requests

# 🛑 あなたの八咫烏の Render URL に変更してください
RENDER_URL = "https://your-yatagarasu-app.onrender.com/update-code"

def send_code(filename, code):
    payload = {
        "filename": filename,
        "code": code
    }

    try:
        response = requests.post(RENDER_URL, json=payload)

        if response.status_code == 200:
            print(f"[✅ 成功] {filename} を八咫烏に送信しました")
        else:
            print(f"[❌ 失敗] ステータス: {response.status_code}")
            print(response.text)

    except Exception as e:
        print(f"[❗ エラー] {str(e)}")

# ✅ 使用例：main.py を書き換える
if __name__ == "__main__":
    code_to_send = """
print("これは E.T Code から送信された新しいコードです！")
"""
    send_code("main.py", code_to_send)