from flask import Flask, request, jsonify
import os

app = Flask(__name__)

@app.route("/")
def hello_world():
    return "Yatagarasu Flask app is running"

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    print("Received webhook data:", data)
    return jsonify({"status": "received"})

# ✅ 「print("完了")」を main.py に追記する自動処理
def edit_main_py_append_completion():
    yatagarasu_path = "/mnt/data/yatagarasu_code/main.py"  # ← 対象ファイルのパス
    try:
        # ファイル内容読み込み
        with open(yatagarasu_path, "r", encoding="utf-8") as f:
            content = f.read()

        # すでに含まれていないか確認してから追記
        if 'print("完了")' not in content:
            content += '\n\nprint("完了")\n'
            with open(yatagarasu_path, "w", encoding="utf-8") as f:
                f.write(content)
            print('main.py に "print(完了)" を追記しました。')
        else:
            print('"print(完了)" は既に含まれています。')

    except Exception as e:
        print("main.py 書き込み時にエラー:", str(e))

# ✅ アプリ起動 & 自動実行
if __name__ == "__main__":
    # Dropbox連携など不要な処理はスキップ（必要なら別途有効化）
    # ensure_dropbox_sync()

    # 八咫烏コードに "print(完了)" を追記
    edit_main_py_append_completion()

    # Flask起動
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))