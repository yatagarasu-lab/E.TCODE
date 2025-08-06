from flask import Blueprint, request, jsonify
import os

receive_code_bp = Blueprint("receive_code", __name__)

RECEIVED_FOLDER = "received_code"

@receive_code_bp.route("/receive_code", methods=["POST"])
def receive_code():
    data = request.get_json()
    filename = data.get("filename")
    code = data.get("code")

    if not filename or not code:
        return jsonify({"status": "error", "message": "Missing filename or code"}), 400

    os.makedirs(RECEIVED_FOLDER, exist_ok=True)
    file_path = os.path.join(RECEIVED_FOLDER, filename)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(code)

    return jsonify({"status": "success", "message": f"{filename} received and saved"})
