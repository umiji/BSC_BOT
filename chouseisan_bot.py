# chouseisan_bot.py
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import sys

dates = sys.argv[1:]  # 例: ["2025-03-09", "2025-03-16"]

options = webdriver.ChromeOptions()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(options=options)
driver.get("https://chouseisan.com/")

# 仮のイベント名
EVENT_NAME = "Cloud Run Test Event"

# 入力
driver.find_element(By.ID, "name").send_keys(EVENT_NAME)
date_str = "\n".join(dates)
driver.find_element(By.ID, "kouho").send_keys(date_str)

# 作成
driver.find_element(By.ID, "createBtn").click()
time.sleep(5)

# URL 取得
try:
    event_url = driver.find_element(By.ID, "listUrl").get_attribute("value")
except:
    event_url = ""

driver.quit()

print(event_url)
