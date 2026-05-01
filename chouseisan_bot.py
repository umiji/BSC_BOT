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
GAS_WEBHOOK_URL = os.environ.get("GAS_WEBHOOK_URL", "")

# ── Selenium セットアップ ────────────────────────────────────────────────
options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-gpu")

# ── 調整さんでイベント作成 ───────────────────────────────────────────────
event_url = None
driver = webdriver.Chrome(options=options)
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

# ── GASへ通知（LINE送信はGAS側で実施） ──────────────────────────────────
if event_url and GAS_WEBHOOK_URL:
    body = json.dumps({
        "type": "github_actions_chouseisan",
        "url": event_url,
        "year": next_year,
        "month": next_month
    }).encode("utf-8")

    req = urllib.request.Request(
        GAS_WEBHOOK_URL,
        data=body,
        headers={
            "Content-Type": "application/json"
        },
        method="POST",
    )
    with urllib.request.urlopen(req) as resp:
        print(f"GASへの通知完了: HTTP {resp.status}")
else:
    if not event_url:
        print("[SKIP] event_url が未取得のためGASへの通知をスキップ")
    else:
        print("[SKIP] GAS_WEBHOOK_URL が未設定のためGASへの通知をスキップ")
