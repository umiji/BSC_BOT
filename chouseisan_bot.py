from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import sys
import logging

# ログ設定
logging.basicConfig(level=logging.DEBUG)

logging.info("Starting Selenium WebDriver")
options = webdriver.ChromeOptions()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(options=options)

try:
    driver.get("https://chouseisan.com/")
    logging.info("Opened chouseisan.com")

    event_name = "2025年の調整"
    date_list = "\n".join(sys.argv[1:])

    logging.debug(f"Setting event name: {event_name}")
    logging.debug(f"Setting event dates: {date_list}")

    driver.find_element(By.ID, "name").send_keys(event_name)
    driver.find_element(By.ID, "kouho").send_keys(date_list)
    driver.find_element(By.ID, "createBtn").click()
    time.sleep(3)

    # イベントURLの取得
    event_url = driver.find_element(By.ID, "listUrl").get_attribute("value")
    logging.info(f"Event URL: {event_url}")

    print(event_url)  # ここで Cloud Run に渡される

except Exception as e:
    logging.exception("Error while creating event")
    print("")  # Cloud Run に空の値を渡すと event_url が "" になる
finally:
    driver.quit()
