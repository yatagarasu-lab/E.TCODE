from flask import Flask, request
import os
import requests
import dropbox
from openai import OpenAI
from linebot import LineBotApi
from linebot.models import TextSendMessage
import hashlib

# GitHub 連携
from github_utils import commit_text

# --- 環境変数 ---
DROPBOX_REFRESH_TOKEN = os.getenv("DROPBOX_REFRESH_TOKEN")
DROPBOX_APP_KEY       = os.getenv("DROPBOX_APP_KEY")
DROPBOX_APP_SECRET    = os.getenv("DROPBOX_APP_SECRET")
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
LINE_USER_ID          = os.getenv("LINE_USER_ID")
OPENAI_API_KEY        = os.getenv("OPENAI_API_KEY")
PARTNER_UPDATE_URL    = os.getenv("PARTNER_UPDATE_URL")

# 要約通知の可否（"1"で通知、デフォルト=OFF）
NOTIFY_SUMMARY = os.getenv("NOTIFY_SUMMARY", "0") == "1"

# --- 初期化 ---
app = Flask(__name__)
dbx = dropbox.Dropbox(
    oauth2_refresh_token=DROPBOX_REFRESH_TOKEN,
    app_key=DROPBOX_APP_KEY,
    app_secret=DROPBOX_APP_SECRET
)
line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
client = OpenAI(api_key=OPENAI_API_KEY)

# --- GitHub heartbeat 手動エンドポイント ---
@app.route("/push-github", methods=["POST"])
def push_github():
    try:
        summary = "Auto update: service heartbeat and last-run OK\n"
        msg = commit_text(
            repo_path="ops/last_run.log",
            text=summary,
            commit_message="chore: auto heartbeat push"
        )
        return msg, 200
    except Exception as e:
        return f"❌ GitHub push failed: {e}", 500

# --- グローバル ---
PROCESSED_HASHES = set()
DROPBOX_FOLDER_PATH = ""  # ルート監視（空文字がDropbox APIの正）

# --- Dropbox: ファイル一覧 ---
def list_files(folder_path=DROPBOX_FOLDER_PATH):
    try:
        folder = "" if folder_path in ("", "/") else folder_path
        result = dbx.files_list_folder(folder)
        return result.entries
    except Exception as e:
        print(f"[ファイル一覧取得エラー] {e}")
        return []

# --- Dropbox: ダウンロード ---
def download_file(path):
    try:
        _, res = dbx.files_download(path)
        return res.content
    except Exception as e:
        print(f"[ファイルDLエラー] {e}")
        return None

# --- ハッシュ ---
def file_hash(content: bytes) -> str:
    return hashlib.sha256(content or b"").hexdigest()

# --- GPT要約 ---
def summarize_text(text: str) -> str:
    try:
        resp = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "以下のテキストを日本語で簡潔に要約してください。"},
                {"role": "user", "content": text}
            ],
            temperature=0.5,
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        return f"[GPT要約失敗] {e}"

# --- LINE 送信（必要な時のみ） ---
def send_line(text: str):
    try:
        line_bot_api.push_message(LINE_USER_ID, TextSendMessage(text=text))
    except Exception as e:
        print(f"[LINE通知失敗] {e}")

# --- 新規ファイル処理 ---
def process_new_files():
    files = list_files()
    for entry in files:
        fname = entry.name
        # ルート監視時も必ず "/filename" 形式でダウンロード
        path = f"/{fname}" if DROPBOX_FOLDER_PATH in ("", "/") \
               else f"{DROPBOX_FOLDER_PATH.rstrip('/')}/{fname}"

        content = download_file(path)
        if not content:
            continue

        h = file_hash(content)
        if h in PROCESSED_HASHES:
            print(f"[スキップ] 重複 → {fname}")
            continue
        PROCESSED_HASHES.add(h)

        # テキスト化（バイナリは無視してOK）
        text = content.decode("utf-8", errors="ignore")
        summary = summarize_text(text)

        if NOTIFY_SUMMARY:
            send_line(f"【要約】{fname}\n{summary}")
        else:
            # 通知OFF時はログだけ
            print(f"[要約完了/通知OFF] {fname} -> {summary[:80]}...")

# --- Dropbox Webhook ---
@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        challenge = request.args.get("challenge")
        if challenge:
            print("[Webhook認証] challenge を返します")
            return challenge, 200
        return "No challenge", 400

    # POST
    print("[Webhook受信] 新ファイルチェック実行")
    process_new_files()

    if PARTNER_UPDATE_URL:
        try:
            requests.post(PARTNER_UPDATE_URL, timeout=3)
            print("[通知] 相手へ update-code 通知済")
        except Exception as e:
            print(f"[通知エラー] {e}")

    return "", 200

# --- 手動/相互連携トリガー ---
@app.route("/update-code", methods=["POST"])
def update_code():
    print("[受信] update-code")
    process_new_files()
    return "OK", 200

# --- ステータス ---
@app.route("/", methods=["GET"])
def home():
    files = list_files()
    return "<h2>E.T Code BOT 稼働中</h2><br>" + "<br>".join([f.name for f in files])

# --- 実行 ---
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)