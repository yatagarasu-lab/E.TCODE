from flask import Flask, request, jsonify
import os

app = Flask(__name__)

@app.route("/update-code", methods=["POST"])
def update_code():
    data = request.json
    filename = data.get("filename")
    code = data.get("code")

    if not filename or not code:
        return jsonify({"error": "filename または code が不足しています"}), 400

    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(code)

        return jsonify({"message": f"{filename} を正常に更新しました"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)