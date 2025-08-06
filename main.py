from flask import Flask
from receive_code import receive_code_bp

app = Flask(__name__)

# Blueprint登録（コード受信処理）
app.register_blueprint(receive_code_bp)

# 動作確認用のトップエンドポイント
@app.route("/")
def hello():
    return "✅ E.T Code Flask Server is running"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)