# Dockerfile
FROM python:3.11-slim-buster

# Chrome と ChromeDriver のインストールに必要な依存関係
RUN apt-get update && apt-get install -y \
    wget \
    unzip \
    gnupg \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Google の署名キー追加
RUN curl -fsSL https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -

# Google Chrome リポジトリの追加
RUN echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list

RUN apt-get update && apt-get install -y \
    google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

# ChromeDriver のバージョンを Chrome に合うよう適宜修正
RUN wget -O /tmp/chromedriver.zip https://chromedriver.storage.googleapis.com/114.0.5735.90/chromedriver_linux64.zip \
    && unzip /tmp/chromedriver.zip -d /usr/local/bin/ \
    && rm /tmp/chromedriver.zip \
    && chmod +x /usr/local/bin/chromedriver

# Python ライブラリのインストール
COPY requirements.txt /app/requirements.txt
WORKDIR /app
RUN pip install --no-cache-dir -r requirements.txt

# Flask アプリのソースをコピー
COPY . /app

# Gunicorn で Flask を起動する
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "app:app"]
