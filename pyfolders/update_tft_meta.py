from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime
import json
import os
import time

def crawl_tft_meta():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1280,3000")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    try:
        driver.get("https://lolchess.gg/meta")

        # 최소 1개 조합이 뜰 때까지 대기
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'css-1iudmso')]"))
        )

        comps = driver.find_elements(By.XPATH, "//div[contains(@class, 'css-1iudmso')]")
        print(f"🔍 총 조합 {len(comps)}개 발견됨")

        meta_data = []

        for i, comp in enumerate(comps[2:], start=1):  # 앞 2개 제외, index는 1부터 시작
            try:
                name = comp.find_element(By.XPATH, ".//div[contains(@class, 'css-35tzvc')]").text.strip()

                # HOT 여부
                hot = False
                try:
                    comp.find_element(By.XPATH, ".//span[contains(@class, 'tag hot')]")
                    hot = True
                except:
                    pass

                # 상세 빌드 링크
                link_elem = comp.find_element(By.XPATH, ".//a[contains(@href, '/builder/guide/')]")
                href = link_elem.get_attribute("href")

                meta_data.append({
                    "index": i,
                    "name": name,
                    "url": href,
                    "hot": hot
                })

            except Exception as e:
                print(f"⚠️ 조합 파싱 실패 (index={i}): {e}")

        return {
            "updated_at": datetime.now().strftime("%Y-%m-%d"),
            "meta": meta_data
        }

    finally:
        driver.quit()

def save_meta_json(data):
    save_path = os.path.join(os.path.dirname(__file__), "meta.json")
    with open(save_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"✅ meta.json 저장 완료 ({data['updated_at']} 기준, {len(data['meta'])}개 조합)")

if __name__ == "__main__":
    data = crawl_tft_meta()
    save_meta_json(data)
