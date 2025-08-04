from flask import Flask, request, render_template
from apscheduler.schedulers.background import BackgroundScheduler
from yatagarasu import analyze_latest_file
from services.dropbox_handler import handle_dropbox_webhook
import os

app = Flask(__name__)

# Webhook処理
@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/', methods=['POST'])
def webhook():
    if request.headers.get('X-Dropbox-Signature'):
        return handle_dropbox_webhook(request)
    return 'Ignored', 200

# GETアクセスで最新解析結果を確認
@app.route('/analyze', methods=['GET'])
def analyze():
    result = analyze_latest_file()
    return result

# 🕓 定期解析処理（5分ごと）
def scheduled_job():
    print("🕒 [定期実行] 解析開始...")
    result = analyze_latest_file()
    print("📊 [解析結果] ↓↓↓\n", result)

# APSchedulerの設定
scheduler = BackgroundScheduler()
scheduler.add_job(scheduled_job, 'interval', minutes=5)
scheduler.start()

if __name__ == '__main__':
    app.run(debug=True, port=int(os.getenv("PORT", 10000)))