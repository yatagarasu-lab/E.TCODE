from flask import Flask, request
import os
import requests
import dropbox
from openai import OpenAI
from linebot import LineBotApi
from linebot.models import TextSendMessage
import hashlib
from threading import Thread
from datetime import datetime, timezone

# GitHub 連携（commit_text が無ければ try/except 内で握りつぶす）
from github_utils import commit_text

# --- 環境変数 ---
DROPBOX_REFRESH_TOKEN      = os.getenv("DROPBOX_REFRESH_TOKEN")
DROPBOX_APP_KEY            = os.getenv("DROPBOX_APP_KEY")
DROPBOX_APP_SECRET         = os.getenv("DROPBOX_APP_SECRET")
LINE_CHANNEL_ACCESS_TOKEN  = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
LINE_USER_ID               = os.getenv("LINE_USER_ID")
OPENAI_API_KEY             = os.getenv("OPENAI_API_KEY")
PARTNER_UPDATE_URL         = os.getenv("PARTNER_UPDATE_URL")

# 要約通知の可否（"1" で通知、既定 OFF）
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

# --- Health check（Render 用） ---
@app.route("/healthz", methods=["GET"])
def healthz():
    return "ok", 200

# --- GitHub heartbeat 手動エンドポイント ---
@app.route("/push-github", methods=["POST"])
def push_github():
    try:
        return commit_last_run(note="manual-ping"), 200
    except Exception as e:
        return f"❌ GitHub push failed: {e}", 500

# --- グローバル ---
PROCESSED_HASHES = set()
DROPBOX_FOLDER_PATH = ""  # ルート監視（空文字が Dropbox API の正）

# --- GitHub: ops/last_run.log を作成/更新 ---
def commit_last_run(note: str = "heartbeat") -> str:
    """
    ops/last_run.log に UTC タイムスタンプとメモを書き込み（追記ではなく置換）。
    commit_text が未設定/失敗でも例外を外に投げないようにする。
    """
    try:
        ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S %Z")
        body = f"[{ts}] {note}\n"
        msg = commit_text(
            repo_path="ops/last_run.log",
            text=body,
            commit_message=f"chore: {note}"
        )
        print(f"[GitHub] last_run.log updated: {msg}")
        return msg
    except Exception as e:
        print(f"[GitHub更新スキップ] {e}")
        return f"skip: {e}"

# --- Dropbox: ファイル一覧（ページング対応） ---
def list_files(folder_path=DROPBOX_FOLDER_PATH):
    entries = []
    try:
        folder = "" if folder_path in ("", "/") else folder_path
        res = dbx.files_list_folder(folder)
        entries.extend(res.entries)
        while res.has_more:
            res = dbx.files_list_folder_continue(res.cursor)
            entries.extend(res.entries)
    except Exception as e:
        print(f"[ファイル一覧取得エラー] {e}")
    return entries

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
            model="gpt-4o",  # 料金抑えるなら "gpt-4o-mini"
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
        # ルート監視時も必ず "/filename"
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

        # バイナリは無視（必要になったら拡張）
        text = content.decode("utf-8", errors="ignore")
        summary = summarize_text(text)

        if NOTIFY_SUMMARY:
            send_line(f"【要約】{fname}\n{summary}")
        else:
            print(f"[要約完了/通知OFF] {fname} -> {summary[:80]}...")

# --- 非同期実行（webhook タイムアウト回避） ---
def _handle_async():
    try:
        process_new_files()
        if PARTNER_UPDATE_URL:
            try:
                requests.post(PARTNER_UPDATE_URL, timeout=3)
                print("[通知] 相手へ update-code 通知済")
            except Exception as e:
                print(f"[通知エラー] {e}")
    except Exception as e:
        print(f"[非同期処理エラー] {e}")
    finally:
        # 処理の最後に heartbeat を GitHub へ
        commit_last_run(note="webhook-processed")

# --- Dropbox Webhook ---
@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        challenge = request.args.get("challenge")
        if challenge:
            print("[Webhook認証] challenge を返します")
            return challenge, 200
        return "No challenge", 400

    # POST: すぐ 200 を返して裏で処理
    print("[Webhook受信] 非同期処理開始")
    Thread(target=_handle_async, daemon=True).start()
    return "", 200

# --- 手動/相互連携トリガー ---
@app.route("/update-code", methods=["POST"])
def update_code():
    print("[受信] update-code（非同期処理開始）")
    Thread(target=_handle_async, daemon=True).start()
    return "OK", 200

# --- ステータス ---
@app.route("/", methods=["GET"])
def home():
    files = list_files()
    return "<h2>E.T Code BOT 稼働中</h2><br>" + "<br>".join([f.name for f in files])

# --- 実行 ---
if __name__ == "__main__":
    # 起動時にも heartbeat を1回実施（存在しなければ自動で作られる）
    commit_last_run(note="service-start")
    port = int(os.getenv("PORT", "10000"))
    app.run(host="0.0.0.0", port=port)