from flask import Blueprint, request, jsonify
import os

receive_code_bp = Blueprint("receive_code", __name__)

CODE_DIR = "received_code"
os.makedirs(CODE_DIR, exist_ok=True)

@receive_code_bp.route("/receive-code", methods=["POST"])
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