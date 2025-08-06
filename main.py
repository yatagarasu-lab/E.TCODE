from flask import Flask, request, jsonify
import os

app = Flask(__name__)

# 例：ルートエンドポイント
@app.route('/')
def index():
    return '✅ Flask is running successfully on Render!'

# 例：テスト用POSTエンドポイント
@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    print("📩 Webhook received:", data)
    return jsonify({'status': 'received'}), 200

# Renderで必要なポートバインド設定
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 1000))  # Renderが割り当てたPORTを使用
    app.run(host='0.0.0.0', port=port)