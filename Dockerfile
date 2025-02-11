FROM python:3.11-slim-bullseye

# Chrome と ChromeDriver のインストールに必要な依存関係
RUN apt-get update && apt-get install -y \
    wget \
    unzip \
    gnupg \
    curl \
    libxss1 \
    libappindicator3-1 \
    fonts-liberation \
    libnss3 \
    libasound2 \
    xvfb \
    && rm -rf /var/lib/apt/lists/*

# Google の署名キー追加（apt-key は非推奨のため、公式の方法を使用）
RUN mkdir -p /etc/apt/keyrings && \
    curl -fsSL https://dl.google.com/linux/linux_signing_key.pub | tee /etc/apt/keyrings/google-chrome.asc > /dev/null

# Google Chrome リポジトリの追加
RUN echo "deb [signed-by=/etc/apt/keyrings/google-chrome.asc] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list

RUN apt-get update && apt-get install -y \
    google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

# Chrome のバージョンを取得し、適した ChromeDriver をインストール
RUN CHROME_VERSION=$(google-chrome --version | awk '{print $3}' | cut -d'.' -f1) && \
    CHROMEDRIVER_VERSION=$(curl -sS https://chromedriver.storage.googleapis.com/LATEST_RELEASE_$CHROME_VERSION) && \
    wget -O /tmp/chromedriver.zip https://chromedriver.storage.googleapis.com/$CHROMEDRIVER_VERSION/chromedriver_linux64.zip && \
    unzip /tmp/chromedriver.zip -d /usr/local/bin/ && \
    rm /tmp/chromedriver.zip && \
    chmod +x /usr/local/bin/chromedriver

# 環境変数を設定（明示的に `chromedriver` のパスを指定）
ENV PATH="/usr/local/bin:${PATH}"
ENV DISPLAY=:99

# Python ライブラリのインストール
COPY requirements.txt /app/requirements.txt
WORKDIR /app
RUN pip install --no-cache-dir -r requirements.txt

# Flask アプリのソースをコピー
COPY . /app

# Gunicorn で Flask を起動する
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "app:app"]
