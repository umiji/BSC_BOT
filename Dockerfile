FROM python:3.11-slim-bullseye

# Chrome と ChromeDriver のインストールに必要な依存関係をインストール
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

# Chrome バージョンの取得と対応する ChromeDriver のインストール
RUN CHROME_VERSION=$(google-chrome --version | grep -oP '[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+' | cut -d'.' -f1) && \
    echo "Detected Chrome version: $CHROME_VERSION" && \
    CHROMEDRIVER_VERSION=$(curl -sS https://chromedriver.storage.googleapis.com/LATEST_RELEASE_$CHROME_VERSION) && \
    wget -O /tmp/chromedriver.zip https://chromedriver.storage.googleapis.com/$CHROMEDRIVER_VERSION/chromedriver_linux64.zip && \
    unzip /tmp/chromedriver.zip -d /usr/local/bin/ && \
    rm /tmp/chromedriver.zip && \
    chmod +x /usr/local/bin/chromedriver

# Python ライブラリのインストール
COPY requirements.txt /app/requirements.txt
WORKDIR /app
RUN pip install --no-cache-dir -r requirements.txt

# Flask アプリのソースをコピー
COPY . /app

# Gunicorn で Flask を起動する
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "app:app"]
