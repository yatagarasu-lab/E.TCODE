from flask import Flask, request, jsonify
import os
from services.gpt_editor import edit_yatagarasu_code  # GPTによる八咫烏コード編集
from services.dropbox_sync import ensure_dropbox_sync  # Dropbox連携の準備（未使用ならスキップ可能）

app = Flask(__name__)

@app.route("/", methods=["GET"])
def index():
    return "E.T Code is running!"

@app.route("/edit", methods=["POST"])
def edit_yatagarasu():
    data = request.json
    if not data or "instructions" not in data:
        return jsonify({"error": "No instructions provided"}), 400

    instructions = data["instructions"]
    result = edit_yatagarasu_code(instructions)
    return jsonify(result)

if __name__ == "__main__":
    # 必要なら Dropbox同期を初期化（スキップ可能）
    # ensure_dropbox_sync()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
    import os

def edit_main_py_append_completion():
    yatagarasu_path = "/mnt/data/yatagarasu_code/main.py"

    try:
        # 既存内容の読み込み
        with open(yatagarasu_path, "r", encoding="utf-8") as f:
            content = f.read()

        # すでに含まれていないか確認してから追記
        if "print(\"完了\")" not in content:
            content += "\n\nprint(\"完了\")\n"

            # 上書き保存
            with open(yatagarasu_path, "w", encoding="utf-8") as f:
                f.write(content)

            print("main.py に 'print(\"完了\")' を追記しました。")
        else:
            print("既に 'print(\"完了\")' が含まれています。追記はスキップしました。")

    except Exception as e:
        print("main.py 書き込み時にエラー:", str(e))


# 起動時に自動実行（Flaskのmain.py内で呼び出し）
edit_main_py_append_completion()