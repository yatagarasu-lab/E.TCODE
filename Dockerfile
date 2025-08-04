# Pythonベースの軽量イメージ
FROM python:3.11-slim

# 作業ディレクトリ
WORKDIR /app

# 必要ファイルを全てコピー
COPY . .

# ライブラリのインストール
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Renderの環境変数でPORT指定されるので、それに従う
ENV PORT=10000

# Flaskをこのポートで起動する
CMD ["gunicorn", "--bind", "0.0.0.0:$PORT", "main:app"]
