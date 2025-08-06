from flask import Flask, request, jsonify
import os

app = Flask(__name__)

# 動作確認用のエンドポイント
@app.route("/", methods=["GET"])
def index():
    return "✅ E.T Code Flask App is running!"

# 受信テスト用エンドポイント（POST確認用）
@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        data = request.json
        print("📩 Webhook Received:", data)

        return jsonify({"status": "received", "data": data}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ET_CODE_ENDPOINT を受け取って応答するための確認用
@app.route("/check-endpoint", methods=["GET"])
def check_endpoint():
    endpoint = os.environ.get("ET_CODE_ENDPOINT", "❌ Not Set")
    return jsonify({"ET_CODE_ENDPOINT": endpoint})

# 必要ならここにさらにルートを追加できます

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)