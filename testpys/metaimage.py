from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import os
import time
import glob

# 드라이버 옵션 설정
options = webdriver.ChromeOptions()
options.add_argument('--headless=new')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--window-size=1920,5000')  # ✅ 해상도 업그레이드

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
driver.set_window_size(1920, 5000)  # ✅ 추가 안전 조치

try:
    driver.get("https://lolchess.gg/meta")

    WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.XPATH, "//div[contains(@class, 'css-1iudmso')]"))
    )
    comps = driver.find_elements(By.XPATH, "//div[contains(@class, 'css-1iudmso')]")
    print(f"🧩 조합 박스 {len(comps)}개 발견됨")

    output_dir = os.path.join(os.path.dirname(__file__), "meta_images")
    os.makedirs(output_dir, exist_ok=True)

    for file in glob.glob(os.path.join(output_dir, "meta_box_*.png")):
        os.remove(file)

    for i, comp in enumerate(comps[2:], start=1):  # 앞 2개 제외
        try:
            driver.execute_script("arguments[0].scrollIntoView(true);", comp)
            time.sleep(0.5)
            unit_box = comp.find_element(By.XPATH, ".//div[contains(@class, 'Champions')]")
            filename = os.path.join(output_dir, f"meta_box_{i}.png")
            unit_box.screenshot(filename)
            print(f"✅ 저장됨: {filename}")
        except Exception as e:
            print(f"⚠️ 저장 실패 (index={i}): {e}")

finally:
    driver.quit()
