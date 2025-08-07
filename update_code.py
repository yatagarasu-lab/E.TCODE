import requests

# 📍 Render の実行URL（例: https://your-app.onrender.com）
RENDER_URL = "https://your-app.onrender.com"
UPDATE_ENDPOINT = "/update-code"

# 🔄 送りたいコード（main.py全文を文字列で読み込む）
with open("main.py", "r", encoding="utf-8") as f:
    code = f.read()

res = requests.post(RENDER_URL + UPDATE_ENDPOINT, data=code)

if res.ok:
    print("✅ アップデート成功:", res.text)
else:
    print("❌ アップデート失敗:", res.status_code, res.text)