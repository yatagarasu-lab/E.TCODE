from flask import Flask, request
import requests
import dropbox
import os
import hashlib
from linebot import LineBotApi
from linebot.models import TextSendMessage
import openai

# --- 環境変数 ---
DROPBOX_REFRESH_TOKEN = os.getenv("DROPBOX_REFRESH_TOKEN")
DROPBOX_APP_KEY = os.getenv("DROPBOX_APP_KEY")
DROPBOX_APP_SECRET = os.getenv("DROPBOX_APP_SECRET")
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
LINE_USER_ID = os.getenv("LINE_USER_ID")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PARTNER_UPDATE_URL = os.getenv("PARTNER_UPDATE_URL")

# --- 初期化 ---
app = Flask(__name__)
dbx = dropbox.Dropbox(
    oauth2_refresh_token=DROPBOX_REFRESH_TOKEN,
    app_key=DROPBOX_APP_KEY,
    app_secret=DROPBOX_APP_SECRET
)
line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
openai.api_key = OPENAI_API_KEY

# --- グローバル変数 ---
PROCESSED_HASHES = set()
DROPBOX_FOLDER_PATH = "/"  # Dropboxのルートディレクトリ

# --- Dropbox ファイル一覧取得 ---
def list_files(folder_path=DROPBOX_FOLDER_PATH):
    try:
        result = dbx.files_list_folder(folder_path)
        return result.entries
    except Exception as e:
        print(f"[ファイル一覧取得エラー] {e}")
        return []

# --- Dropbox ファイルダウンロード ---
def download_file(path):
    try:
        _, res = dbx.files_download(path)
        return res.content
    except Exception as e:
        print(f"[ファイルDLエラー] {e}")
        return None

# --- ハッシュ生成 ---
def file_hash(content):
    return hashlib.sha256(content).hexdigest()

# --- GPT要約処理 ---
def summarize_text(text):
    prompt = f"以下のテキストを要約してください:\n\n{text}"
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"[GPT要約失敗] {e}"

# --- LINE 通知送信 ---
def send_line(text):
    try:
        msg = TextSendMessage(text=text)
        line_bot_api.push_message(LINE_USER_ID, messages=msg)
    except Exception as e:
        print(f"[LINE通知失敗] {e}")

# --- 新規ファイル処理 ---
def process_new_files():
    files = list_files()
    for file in files:
        fname = file.name
        path = f"{DROPBOX_FOLDER_PATH}/{fname}"
        content = download_file(path)
        if not content:
            continue
        h = file_hash(content)
        if h in PROCESSED_HASHES:
            print(f"[スキップ] 重複ファイル → {fname}")
            continue
        PROCESSED_HASHES.add(h)

        text = content.decode("utf-8", errors="ignore")
        summary = summarize_text(text)
        send_line(f"【要約】{fname}\n{summary}")

# --- Webhook 受信（Dropbox用） ---
@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        challenge = request.args.get("challenge")
        if challenge:
            print("[Webhook認証] challenge を返します")
            return challenge, 200
        return "No challenge", 400

    if request.method == "POST":
        print("[Webhook受信] 新ファイルチェック実行")
        process_new_files()

        # パートナー側へも通知（必要なら）
        if PARTNER_UPDATE_URL:
            try:
                requests.post(PARTNER_UPDATE_URL, timeout=3)
                print("[通知] 相手へ update-code 通知済")
            except Exception as e:
                print(f"[通知エラー] {e}")
        return "", 200

# --- update-code 受信（手動/相互連携） ---
@app.route("/update-code", methods=["POST"])
def update_code():
    print("[受信] update-code")
    process_new_files()
    return "OK", 200

# --- ステータス確認ページ ---
@app.route("/", methods=["GET"])
def home():
    files = list_files()
    return "<h2>E.T Code BOT 稼働中</h2><br>" + "<br>".join([f.name for f in files])

# --- 実行エントリーポイント ---
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)