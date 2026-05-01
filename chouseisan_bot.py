import sys
import json
import os
import datetime
import urllib.request

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

# ── 翌月の年・月を計算 ────────────────────────────────────────────────────
today = datetime.date.today()
next_year  = today.year + (1 if today.month == 12 else 0)
next_month = 1 if today.month == 12 else today.month + 1

# ── イベント名・候補日の決定 ─────────────────────────────────────────────
if len(sys.argv) > 1:
    # 旧Cloud Run モード：引数でJSON渡し
    input_data = json.loads(sys.argv[1])
    event_name = input_data.get("event_name", "イベント名未設定")
    date_list  = "\n".join(input_data.get("dates", []))
else:
    # GitHub Actions モード：翌月の土日を自動生成
    dates = []
    for day in range(1, 32):
        try:
            d = datetime.date(next_year, next_month, day)
        except ValueError:
            break
        if d.weekday() in (5, 6):  # 5=土, 6=日
            dates.append(d.strftime("%Y-%m-%d"))

    event_name = f"{next_year}年{next_month}月の勉強会日程調整"
    date_list  = "\n".join(dates)

# ── 環境変数 ─────────────────────────────────────────────────────────────
LINE_TOKEN    = os.environ.get("LINE_TOKEN", "")
LINE_GROUP_ID = os.environ.get("LINE_GROUP_ID", "")

# ── Selenium セットアップ ────────────────────────────────────────────────
options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-gpu")

# CHROMIUM_PATH が設定されている場合のみ明示指定（Cloud Run用）
# GitHub Actions では setup-chrome が自動でパスを通すため不要
chromium_path = os.environ.get("CHROMIUM_PATH", "")
if chromium_path:
    options.binary_location = chromium_path

chromedriver_path = os.environ.get("CHROMEDRIVER_PATH", "")
service = Service(chromedriver_path) if chromedriver_path else Service()

# ── 調整さんでイベント作成 ───────────────────────────────────────────────
event_url = None
driver = webdriver.Chrome(service=service, options=options)
try:
    driver.get("https://chouseisan.com/")
    driver.find_element("id", "name").send_keys(event_name)
    driver.find_element("id", "kouho").send_keys(date_list)
    driver.find_element("id", "createBtn").click()

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "listUrl"))
    )
    event_url = driver.find_element("id", "listUrl").get_attribute("value")
    print(f"生成されたURL: {event_url}")

except Exception as e:
    print(f"[ERROR] 調整さんイベント作成に失敗しました: {e}")
    raise
finally:
    driver.quit()

# ── LINE グループに投稿 ──────────────────────────────────────────────────
if event_url and LINE_TOKEN and LINE_GROUP_ID:
    message = (
        f"📅{next_year}年{next_month}月の日程調整📅\n"
        "空いている日を以下のリンクから入力してください！\n\n"
        f"{event_url}"
    )

    body = json.dumps({
        "to": LINE_GROUP_ID,
        "messages": [{"type": "text", "text": message}]
    }).encode("utf-8")

    req = urllib.request.Request(
        "https://api.line.me/v2/bot/message/push",
        data=body,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {LINE_TOKEN}",
        },
        method="POST",
    )
    with urllib.request.urlopen(req) as resp:
        print(f"LINE送信完了: HTTP {resp.status}")
else:
    if not event_url:
        print("[SKIP] event_url が未取得のためLINE送信をスキップ")
    else:
        print("[SKIP] LINE_TOKEN / LINE_GROUP_ID が未設定のためLINE送信をスキップ")
