import os
from flask import Flask, request, jsonify
import subprocess

app = Flask(__name__)

@app.route('/create_event', methods=['POST'])
def create_event():
    data = request.json
    date_list = data.get("dates", [])

    # 調整さんを操作してイベント作成
    result = subprocess.run(["python3", "chouseisan_bot.py", *date_list], capture_output=True, text=True)
    
    return jsonify({"event_url": result.stdout.strip()})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
