# Python の軽量バージョンを使用
FROM python:3.11-slim-bullseye

# 必要なパッケージをインストール
RUN apt-get update && apt-get install -y \
    wget \
    unzip \
    curl \
    chromium \
    chromium-driver \
    && rm -rf /var/lib/apt/lists/*

# Python ライブラリのインストール
COPY requirements.txt /app/requirements.txt
WORKDIR /app
RUN pip install --no-cache-dir -r requirements.txt

# 環境変数を設定して Selenium に Chromium を使わせる
ENV CHROMIUM_PATH=/usr/bin/chromium
ENV CHROMEDRIVER_PATH=/usr/bin/chromedriver

# Flask アプリのソースをコピー
COPY . /app

# Gunicorn で Flask を起動する
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "app:app"]
