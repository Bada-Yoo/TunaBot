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
        src = (
            img.get_attribute("src")
            or img.get_attribute("data-src")
            or img.get_attribute("lazy-src")
            or ""
        )
        if not src or "/items/" not in src:
            return None

        filename = os.path.basename(urlparse(src).path)
        item_name = os.path.splitext(filename)[0].replace("TFT_Item_", "").replace("_", " ")
        return {"name": item_name, "image": src.strip()}
    except Exception as e:
        print(f"⚠️ 아이템 파싱 실패: {e}")
        return None


def extract_unit_info(unit_elem):
    try:
        name = ""
        cost = 0
        icon = ""

        try:
            name_elem = unit_elem.find_element(By.XPATH, ".//div[contains(@class, 'e9927jh2')]")
            name = name_elem.text.strip()
        except:
            pass

        try:
            cost_elem = unit_elem.find_element(By.XPATH, ".//div[contains(@class, 'e9927jh3')]")
            cost_text = cost_elem.text.strip()
            cost = int("".join(filter(str.isdigit, cost_text))) if cost_text else 0
        except:
            pass

        try:
            img_elem = unit_elem.find_element(By.TAG_NAME, "img")
            icon = (
                img_elem.get_attribute("src")
                or img_elem.get_attribute("data-src")
                or img_elem.get_attribute("lazy-src")
                or ""
            ).strip()
        except:
            pass

        return {"name": name, "cost": cost, "icon": icon, "items": []}

    except Exception as e:
        print(f"⚠️ 유닛 파싱 실패: {e}")
        return None


def crawl_tft_meta():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-webgl")
    options.add_argument("--disable-software-rasterizer")
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    options.add_argument("--log-level=3")
    options.add_argument("--window-size=1920,5000")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    try:
        driver.get("https://lolchess.gg/meta")
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'Champion')]"))
        )

        # 스크롤로 lazy load 방지
        last_height = 0
        for _ in range(10):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1)
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

        comps = driver.find_elements(By.XPATH, "//div[contains(@class, 'css-1iudmso')]")
        print(f"🔍 총 조합 {len(comps)}개 발견됨")

        meta_data = []

        for i, comp in enumerate(comps[1:], start=1):
            try:
                name_raw = ""
                try:
                    name_raw = comp.find_element(By.XPATH, ".//div[contains(@class, 'css-35tzvc')]").text
                except:
                    pass
                name = name_raw.split("\n")[0].strip() if name_raw else f"조합{i}"

                hot = bool(comp.find_elements(By.XPATH, ".//span[contains(@class, 'tag hot')]"))

                url_elem = comp.find_element(By.XPATH, ".//a[contains(@href, '/builder/guide/')]")
                url = url_elem.get_attribute("href")

                # 유닛 수집
                unit_elems = comp.find_elements(By.XPATH, ".//div[contains(@class, 'Champion')]")
                unit_list, added_names = [], set()
                for ue in unit_elems:
                    unit_info = extract_unit_info(ue)
                    if unit_info and unit_info["name"] not in added_names:
                        unit_list.append(unit_info)
                        added_names.add(unit_info["name"])

                # 아이템 블록 전체 수집
                all_item_blocks = comp.find_elements(By.XPATH, ".//div[contains(@class,'items')]")

                for item_block in all_item_blocks:
                    item_imgs = item_block.find_elements(By.TAG_NAME, "img")
                    parsed_items = []
                    for img in item_imgs:
                        item = extract_item_info(img)
                        if item:
                            parsed_items.append(item)

                    # 아이템 블록의 상위 Champion 탐색
                    assigned = False
                    parent = item_block
                    for _ in range(5):  # 최대 5단계 위로
                        parent = parent.find_element(By.XPATH, "..")
                        if "Champion" in (parent.get_attribute("class") or ""):
                            # 가장 가까운 Champion에만 연결
                            try:
                                name_elem = parent.find_element(By.XPATH, ".//div[contains(@class,'e9927jh2')]")
                                champ_name = name_elem.text.strip()
                                for u in unit_list:
                                    if u["name"] == champ_name:
                                        u["items"] = parsed_items
                                        assigned = True
                                        break
                            except:
                                pass
                            break

                    # Champion 상위에 못 붙은 items → 공통 아이템 처리
                    if not assigned and parsed_items:
                        for u in unit_list:
                            if not u["items"]:
                                u["items"] = parsed_items

                meta_data.append({
                    "index": i,
                    "name": name,
                    "url": url,
                    "hot": hot,
                    "units": unit_list,
                })

            except Exception as e:
                print(f"⚠️ 조합 파싱 실패 (index={i}): {e}")

        return {
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "meta": meta_data,
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
