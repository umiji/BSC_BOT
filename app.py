# app.py
from flask import Flask, request, jsonify
import subprocess

app = Flask(__name__)

@app.route("/create_event", methods=["POST"])
def create_event():
    data = request.json
    date_list = data.get("dates", [])

    # Python のサブプロセスで Selenium スクリプト呼び出し
    result = subprocess.run(
        ["python3", "chouseisan_bot.py", *date_list],
        capture_output=True, text=True
    )

    # 標準出力にイベントURLが入っている想定
    event_url = result.stdout.strip()

    return jsonify({"event_url": event_url})

@app.route("/")
def root():
    return "Hello from Cloud Run Docker - Selenium!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
