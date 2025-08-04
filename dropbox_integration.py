# dropbox_integration.py

from flask import request, jsonify
import json
import datetime

def log_event(message):
    """ログを表示（将来的にファイル保存などに拡張可）"""
    print(f"[{datetime.datetime.now().isoformat()}] {message}")

def handle_dropbox_webhook():
    """
    Dropbox Webhook エンドポイント（GET確認 + POST通知）
    Render上で https://your-app.onrender.com/dropbox に対応
    """
    if request.method == "GET":
        # 初期Webhook確認用（Dropbox側が challenge を送ってくる）
        challenge = request.args.get("challenge")
        log_event(f"Webhook challenge received: {challenge}")
        return challenge, 200

    elif request.method == "POST":
        # Webhook通知（ファイル更新・追加など）
        try:
            payload = request.get_data(as_text=True)
            log_event(f"Webhook POST payload received:\n{payload}")

            # JSONがあれば表示
            try:
                json_payload = json.loads(payload)
                log_event(f"Parsed JSON payload:\n{json.dumps(json_payload, indent=2)}")
            except json.JSONDecodeError:
                log_event("Payload is not valid JSON.")

            return jsonify({"status": "Webhook received"}), 200

        except Exception as e:
            log_event(f"Error in webhook processing: {e}")
            return jsonify({"error": str(e)}), 500
