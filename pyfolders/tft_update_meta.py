from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime
from urllib.parse import urlparse
import json
import os
import time

def extract_item_info(img):
    try:
        src = img.get_attribute("src")
        if not src or "tft-item" not in src:
            return None

        filename = os.path.basename(urlparse(src).path)
        item_name = os.path.splitext(filename)[0].replace("TFT_Item_", "").replace("_", " ")

        return {
            "name": item_name,
            "image": src.strip()
        }
    except:
        return None

def extract_unit_info(unit_elem):
    try:
        # 이름
        name_elem = unit_elem.find_element(By.XPATH, ".//div[contains(@class, 'e9927jh2')]")
        name = name_elem.text.strip()

        # 코스트
        cost_elem = unit_elem.find_element(By.XPATH, ".//div[contains(@class, 'e9927jh3')]")
        cost_text = cost_elem.text.strip()
        cost = int(''.join(filter(str.isdigit, cost_text))) if cost_text else 0

        # 아이콘 (요원 이미지)
        try:
            img_elem = unit_elem.find_element(By.TAG_NAME, "img")
            icon = img_elem.get_attribute("src").strip()
        except:
            icon = ""

        # 아이템 이미지
        items = []
        try:
            item_block = unit_elem.find_element(By.CLASS_NAME, "items")
            item_imgs = item_block.find_elements(By.TAG_NAME, "img")
            for img in item_imgs:
                item = extract_item_info(img)
                if item:
                    items.append(item)
        except:
            pass

        return {
            "name": name,
            "cost": cost,
            "icon": icon,
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
    options.add_argument("--window-size=1920,5000")

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
                #  조합 이름 추출
                name_raw = comp.find_element(By.XPATH, ".//div[contains(@class, 'css-35tzvc')]").text
                name = name_raw.split("\n")[0].strip()

                #  HOT 여부 판단
                hot = False
                try:
                    comp.find_element(By.XPATH, ".//span[contains(@class, 'tag hot')]")
                    hot = True
                except:
                    pass

                #  링크 추출
                url_elem = comp.find_element(By.XPATH, ".//a[contains(@href, '/builder/guide/')]")
                url = url_elem.get_attribute("href")

                #  유닛 추출
                unit_elems = comp.find_elements(By.XPATH, ".//div[contains(@class, 'Champion')]")
                unit_list = []
                added_names = set()
                for ue in unit_elems:
                    try:
                        name_candidate = ue.find_element(By.XPATH, ".//div[contains(@class, 'e9927jh2')]").text.strip()
                        if name_candidate in added_names:
                            continue
                        unit_info = extract_unit_info(ue)
                        if unit_info:
                            unit_list.append(unit_info)
                            added_names.add(unit_info["name"])
                    except:
                        continue

                # 🔹 조합 정보 저장
                meta_data.append({
                    "index": i,
                    "name": name,
                    "url": url,
                    "hot": hot,
                    "units": unit_list
                })

            except Exception as e:
                print(f"⚠️ 조합 파싱 실패 (index={i}): {e}")


        return {
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "meta": meta_data
        }

    finally:
        driver.quit()

def save_meta_json(data):
    save_path = os.path.join(os.path.dirname(__file__), "tft_meta.json")
    with open(save_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"✅ tft_meta.json 저장 완료 ({data['updated_at']} 기준, {len(data['meta'])}개 조합)")

if __name__ == "__main__":
    data = crawl_tft_meta()
    save_meta_json(data)
