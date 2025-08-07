from flask import Flask, request, jsonify
import requests
import dropbox
import os
import hashlib
from linebot import LineBotApi
from linebot.models import TextSendMessage
import openai

app = Flask(__name__)

# --- 環境変数の取得 ---
DROPBOX_ACCESS_TOKEN = os.getenv("DROPBOX_ACCESS_TOKEN")
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
LINE_USER_ID = os.getenv("LINE_USER_ID")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PARTNER_UPDATE_URL = os.getenv("PARTNER_UPDATE_URL")

# --- 初期設定 ---
dbx = dropbox.Dropbox(DROPBOX_ACCESS_TOKEN)
line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
openai.api_key = OPENAI_API_KEY

# --- ファイル一覧を取得 ---
def list_files(folder_path="/Apps/slot-data-analyzer"):
    result = dbx.files_list_folder(folder_path)
    return result.entries

# --- ファイルダウンロード ---
def download_file(path):
    _, res = dbx.files_download(path)
    return res.content

# --- ファイル要約 ---
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
        return f"[要約エラー] {str(e)}"

# --- LINE通知 ---
def send_line_message(text):
    try:
        message = TextSendMessage(text=text)
        line_bot_api.push_message(LINE_USER_ID, messages=message)
    except Exception as e:
        print("[LINE通知エラー]", e)

# --- ファイルのハッシュ（重複チェック） ---
def file_hash(content):
    return hashlib.sha256(content).hexdigest()

# --- 自動解析処理 ---
def auto_analyze():
    seen_hashes = {}
    files = list_files()

    for file in files:
        path = file.path_display
        content = download_file(path)
        hash_val = file_hash(content)

        if hash_val in seen_hashes:
            print(f"重複検出 → {path} はスキップ")
            continue

        seen_hashes[hash_val] = path

        try:
            decoded = content.decode('utf-8')
            summary = summarize_text(decoded)
            send_line_message(f"[解析結果]\n{file.name}:\n{summary}")
        except Exception as e:
            send_line_message(f"[解析失敗] {file.name}\n{str(e)}")

# --- Dropbox Webhook受信（認証兼POST処理） ---
@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        return request.args.get("challenge")
    elif request.method == "POST":
        print("[Webhook通知] Dropboxから更新通知を受信")
        auto_analyze()

        # 相互アップデート連携
        if PARTNER_UPDATE_URL:
            try:
                requests.post(PARTNER_UPDATE_URL, timeout=3)
                print("[連携通知] 相手サーバーにPOST済み")
            except Exception as e:
                print("[連携失敗]", e)

        return "OK"

# --- コード更新通知エンドポイント（相手からの連携用） ---
@app.route("/update-code", methods=["POST"])
def update_code():
    print("[アップデート通知] 相手からupdate-codeが呼ばれました")
    auto_analyze()
    return "Update received and processed."

# --- 簡易テスト用ルート ---
@app.route("/")
def home():
    return "E.T Code is running."

# --- 実行 ---
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)