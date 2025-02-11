from flask import Flask, request, jsonify
import subprocess
import logging

app = Flask(__name__)

# ログレベル設定
logging.basicConfig(level=logging.DEBUG)

@app.route('/')
def home():
    logging.info("Root endpoint accessed")
    return "Cloud Run is running", 200

@app.route('/create_event', methods=['POST'])
def create_event():
    logging.info("Received request at /create_event")

    try:
        data = request.json
        logging.debug(f"Request JSON: {data}")

        date_list = data.get("dates", [])
        logging.debug(f"Received dates: {date_list}")

        if not date_list:
            logging.error("No dates provided")
            return jsonify({"error": "No dates provided"}), 400

        # 調整さんを操作してイベント作成
        result = subprocess.run(["python3", "chouseisan_bot.py", *date_list], capture_output=True, text=True)

        logging.debug(f"Subprocess output: {result.stdout.strip()}")
        logging.error(f"Subprocess error: {result.stderr.strip()}") if result.stderr else None

        return jsonify({"event_url": result.stdout.strip()})

    except Exception as e:
        logging.exception("Error in /create_event")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080)
