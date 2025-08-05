from flask import Flask, request, jsonify
import os

app = Flask(__name__)

# 自分のコード保存フォルダ（任意で変更可）
CODE_DIR = "received_code"
os.makedirs(CODE_DIR, exist_ok=True)

@app.route("/")
def index():
    return "E.T Code is running."

# 八咫烏から受信するルート
@app.route("/receive-code", methods=["POST"])
def receive_code():
    try:
        data = request.json
        filename = data.get("filename")
        code = data.get("code")

        if not filename or not code:
            return jsonify({"error": "filename and code are required"}), 400

        filepath = os.path.join(CODE_DIR, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(code)

        return jsonify({"message": f"{filename} を受信して保存しました"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)