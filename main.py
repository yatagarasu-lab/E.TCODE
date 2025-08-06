from flask import Flask, request, jsonify
import os

app = Flask(__name__)

@app.route("/", methods=["GET"])
def index():
    return "✅ E.T Code Flask App is running!"

@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        data = request.json
        print("📩 Webhook Received:", data)
        return jsonify({"status": "received", "data": data}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/check-endpoint", methods=["GET"])
def check_endpoint():
    endpoint = os.environ.get("ET_CODE_ENDPOINT", "❌ Not Set")
    return jsonify({"ET_CODE_ENDPOINT": endpoint})

if __name__ == "__main__":
    # ← この部分が重要です！
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)