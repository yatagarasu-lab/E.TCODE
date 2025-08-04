from flask import Flask, request, jsonify
import os
import json
import datetime

app = Flask(__name__)

# ログ保存関数
def log_event(message):
    timestamp = datetime.datetime.now().isoformat()
    log_text = f"[{timestamp}] {message}"
    print(log_text)

    try:
        os.makedirs("logs", exist_ok=True)
        with open("logs/webhook_log.txt", "a", encoding="utf-8") as f:
            f.write(log_text + "\n")
    except Exception as e:
        print(f"[{timestamp}] ログファイル保存エラー: {e}")

# Dropbox Webhook エンドポイント処理
@app.route("/dropbox", methods=["GET", "POST"])
def dropbox_webhook():
    if request.method == "GET":
        challenge = request.args.get("challenge")
        log_event(f"Webhook challenge received: {challenge}")
        return challenge, 200

    elif request.method == "POST":
        try:
            payload = request.get_data(as_text=True)
            log_event(f"Webhook POST payload received:\n{payload}")

            try:
                json_payload = json.loads(payload)
                log_event(f"Parsed JSON payload:\n{json.dumps(json_payload, indent=2)}")
            except json.JSONDecodeError:
                log_event("Payload is not valid JSON.")

            return jsonify({"status": "Webhook received"}), 200

        except Exception as e:
            log_event(f"Error in webhook processing: {e}")
            return jsonify({"error": str(e)}), 500

# ログファイル読み取りエンドポイント
@app.route("/read-log", methods=["GET"])
def read_log():
    file_path = request.args.get("path", "logs/webhook_log.txt")
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        return jsonify({"file": file_path, "content": content})
    except Exception as e:
        return jsonify({"error": f"ログ取得エラー: {str(e)}"}), 500

# 動作確認用
@app.route("/")
def index():
    return "Dropbox Webhook Bot is running!"

if __name__ == "__main__":
    print("Flask app 起動")
    app.run(host="0.0.0.0", port=10000)
    print("完了")