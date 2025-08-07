from flask import Flask, request
import requests
import dropbox
import os
import hashlib
from linebot import LineBotApi
from linebot.models import TextSendMessage
import openai

# --- 環境変数 ---
DROPBOX_ACCESS_TOKEN = os.getenv("DROPBOX_ACCESS_TOKEN")
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
LINE_USER_ID = os.getenv("LINE_USER_ID")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PARTNER_UPDATE_URL = os.getenv("PARTNER_UPDATE_URL")

app = Flask(__name__)

# --- 初期化 ---
dbx = dropbox.Dropbox(DROPBOX_ACCESS_TOKEN)
line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
openai.api_key = OPENAI_API_KEY

def list_files(folder_path="/Apps/slot-data-analyzer"):
    result = dbx.files_list_folder(folder_path)
    return result.entries

def download_file(path):
    _, res = dbx.files_download(path)
    return res.content

def file_hash(content):
    return hashlib.sha256(content).hexdigest()

def summarize_text(text):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "以下のテキストを簡潔に要約してください。"},
                {"role": "user", "content": text}
            ]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"[要約エラー] {e}"

def send_line_message(text):
    try:
        msg = TextSendMessage(text=text)
        line_bot_api.push_message(LINE_USER_ID, messages=msg)
    except Exception as e:
        print("[LINE通知エラー]", e)

def auto_analyze():
    seen_hashes = {}
    files = list_files()
    for file in files:
        path = file.path_display
        content = download_file(path)
        h = file_hash(content)
        if h in seen_hashes:
            print(f"重複検出 → {path} はスキップ")
            continue
        seen_hashes[h] = path
        summary = summarize_text(content.decode("utf‑8", errors="ignore"))
        send_line_message(f"[解析結果]\n{file.name}:\n{summary}")

@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        challenge = request.args.get("challenge")
        return (challenge or ""), 200

    if request.method == "POST":
        print("[Webhook通知] DropboxからのPOST受信")
        auto_analyze()
        if PARTNER_UPDATE_URL:
            try:
                requests.post(PARTNER_UPDATE_URL, timeout=3)
                print("[連携通知] パートナーに送信済み")
            except Exception as e:
                print("[連携通知失敗]", e)
        return "OK", 200

    return "Method Not Allowed", 405

@app.route("/update-code", methods=["POST"])
def update_code():
    print("[相互アップデート通知] 受信")
    auto_analyze()
    return "Update processed", 200

@app.route("/", methods=["GET"])
def home():
    return "八咫烏 BOT 正常稼働中", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)