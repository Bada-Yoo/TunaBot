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

def extract_unit_info(unit_elem):
    try:
        # 이름
        name = unit_elem.find_element(By.XPATH, ".//div[contains(@class, 'e9927jh2')]").text.strip()

        # 코스트
        cost_text = unit_elem.find_element(By.XPATH, ".//div[contains(@class, 'e9927jh3')]").text.strip()
        cost = int(''.join(filter(str.isdigit, cost_text))) if cost_text else 0

        # 아이템
        items = []
        item_imgs = unit_elem.find_elements(By.XPATH, ".//div[contains(@class, 'items')]//img")
        for img in item_imgs:
            alt = img.get_attribute("alt")
            src = img.get_attribute("src")
            if alt and alt != "item":
                items.append({
                    "name": alt.strip(),
                    "image": src.strip()
                })

        return {
            "name": name,
            "cost": cost,
            "items": items
        }

    except Exception as e:
        print(f"⚠️ 유닛 파싱 실패: {e}")
        return None

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

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'css-1iudmso')]"))
        )

        comps = driver.find_elements(By.XPATH, "//div[contains(@class, 'css-1iudmso')]")
        print(f"🔍 총 조합 {len(comps)}개 발견됨")

        meta_data = []

        for i, comp in enumerate(comps[2:], start=1):  # 앞 2개 제외
            try:
                name = comp.find_element(By.XPATH, ".//div[contains(@class, 'css-35tzvc')]").text.strip()

                # HOT 여부
                hot = False
                try:
                    comp.find_element(By.XPATH, ".//span[contains(@class, 'tag hot')]")
                    hot = True
                except:
                    pass

                # 링크
                url_elem = comp.find_element(By.XPATH, ".//a[contains(@href, '/builder/guide/')]")
                url = url_elem.get_attribute("href")

                # 유닛 목록
                unit_elems = comp.find_elements(By.XPATH, ".//div[contains(@class, 'Champion')]")
                units = []
                for ue in unit_elems:
                    unit_info = extract_unit_info(ue)
                    if unit_info:
                        units.append(unit_info)

                meta_data.append({
                    "index": i,
                    "name": name,
                    "url": url,
                    "hot": hot,
                    "units": units
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
