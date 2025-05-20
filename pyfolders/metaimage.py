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
options.add_argument('--headless=new')  # 브라우저 창 안 뜨게
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--window-size=1280,3000')  # 해상도 충분히 확보

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

try:
    driver.get("https://lolchess.gg/meta")

    # 조합 카드 요소 로딩 대기
    WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.XPATH, "//div[contains(@class, 'css-1iudmso')]"))
    )
    comps = driver.find_elements(By.XPATH, "//div[contains(@class, 'css-1iudmso')]")
    print(f"🧩 조합 박스 {len(comps)}개 발견됨")

    # 저장 폴더 준비
    output_dir = os.path.join(os.path.dirname(__file__), "meta_images")
    os.makedirs(output_dir, exist_ok=True)

    # 기존 이미지 삭제
    for file in glob.glob(os.path.join(output_dir, "meta_box_*.png")):
        os.remove(file)

    for i, comp in enumerate(comps[2:], start=1):  # 앞 2개 건너뜀
        try:
            driver.execute_script("arguments[0].scrollIntoView(true);", comp)
            time.sleep(0.5)

            # ✅ 조합 내부 유닛 박스 영역만 캡처
            unit_box = comp.find_element(By.XPATH, ".//div[contains(@class, 'Champions')]")
            filename = os.path.join(output_dir, f"meta_box_{i}.png")
            unit_box.screenshot(filename)
            print(f"✅ 저장됨: {filename}")
        except Exception as e:
            print(f"⚠️ 저장 실패 (index={i}): {e}")

finally:
    driver.quit()
