from flask import Flask, request, jsonify, render_template
import os

app = Flask(__name__)

# ✅ アプリのトップページ（ステータス用）
@app.route('/')
def index():
    return "E.T Code Flask App is running."

# ✅ LINE BOTなどのWebhook受信エンドポイント（必要に応じて）
@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.get_json()
        print("Received Webhook:", data)
        return jsonify({"status": "success", "data": data}), 200
    except Exception as e:
        print("Error:", str(e))
        return jsonify({"status": "error", "message": str(e)}), 500

# ✅ ローカルテスト用：手動でAPIを叩けるエンドポイント
@app.route('/api/test', methods=['GET'])
def test_api():
    return jsonify({
        "message": "This is a test endpoint for E.T Code project.",
        "status": "ok"
    })

# ✅ 起動コマンド（Renderなどでは自動実行）
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)