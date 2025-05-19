from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

options = webdriver.ChromeOptions()
# 일단 headless는 끄자 (눈으로 확인)
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

driver.get("https://lolchess.gg/meta")
time.sleep(10)
driver.save_screenshot("debug.png")
driver.quit()
