# 使用するベースイメージ
FROM python:3.11-slim

# 作業ディレクトリを作成
WORKDIR /app

# 依存関係ファイルをコピー
COPY requirements.txt .

# ライブラリをインストール
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションファイルをコピー
COPY . .

# アプリケーション起動コマンド（Render用）
CMD ["gunicorn", "--bind", "0.0.0.0:${PORT}", "main:app"]