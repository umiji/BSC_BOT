from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time
import sys

# Selenium のオプションを設定（Cloud Run 用）
options = Options()
options.binary_location = "/usr/bin/chromium"  # Chromium のパスを指定
options.add_argument("--headless")  # ヘッドレスモード
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

# ChromeDriver のパスを指定
service = Service("/usr/bin/chromedriver")
driver = webdriver.Chrome(service=service, options=options)

driver.get("https://chouseisan.com/")

# イベント作成処理
event_name = "2025年の調整"
date_list = "\n".join(sys.argv[1:])

driver.find_element("id", "name").send_keys(event_name)
driver.find_element("id", "kouho").send_keys(date_list)
driver.find_element("id", "createBtn").click()
time.sleep(3)

# 作成されたイベントURLを取得
event_url = driver.find_element("id", "listUrl").get_attribute("value")
driver.quit()

print(event_url)
