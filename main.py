# main.py に追記
from flask import Flask, request, jsonify
from dropbox_integration import update_yatagarasu_code, write_dropbox_log

app = Flask(__name__)

@app.route("/update-code", methods=["POST"])
def update_code():
    """
    E.T Code から POST で受け取ったコードを八咫烏フォルダに保存し、
    Dropbox にアップロードしてログも残す。
    """
    data = request.get_json()
    filename = data.get("filename", "main.py")
    code = data.get("code", "")

    if not code:
        return jsonify({"error": "コード内容が空です"}), 400

    try:
        update_yatagarasu_code(filename, code)
        write_dropbox_log(f"{filename} を更新しました。")
        return jsonify({"status": "success", "message": f"{filename} を保存しました。"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500