from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import os
import json

def crawl_detail_info():
    base_dir = os.path.dirname(__file__)
    meta_path = os.path.join(base_dir, "tft_meta.json")
    detail_path = os.path.join(base_dir, "tft_metadetail.json")

    with open(meta_path, "r", encoding="utf-8") as f:
        meta_data = json.load(f)

    detail_data = {"updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "meta": []}

    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1280,3000")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    for entry in meta_data["meta"]:
        url = entry["url"]
        name = entry["name"]
        print(f"🔍 {name} 세부 정보 크롤링 중...")

        driver.get(url)
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "challenger-comment"))
            )
        except:
            print(f"❌ 타임아웃: {url}")
            continue

        # 난이도
        try:
            difficulty_elem = driver.find_element(By.XPATH, "//h1[contains(text(), '덱 난이도')]/following-sibling::p")
            difficulty = difficulty_elem.text.strip()
        except:
            difficulty = ""

        # 레벨링 추천
        leveling = []
        try:
            p_tags = driver.find_elements(By.XPATH, "//h1[contains(text(), '스테이지별 레벨업 추천')]/following-sibling::p")
            for p in p_tags:
                text = p.get_attribute("innerText").strip()
                if text:
                    lines = text.split("\n")
                    for line in lines:
                        # "(연승 or 연패)" 제거, 다른 괄호는 유지
                        if "(연승 or 연패)" in line:
                            line = line.replace("(연승 or 연패)", "").strip()
                        if line:
                            leveling.append(line)
        except Exception as e:
            print(f"⚠️ 레벨링 정보 없음: {e}")

        # 덱 구성
        try:
            composition_elem = driver.find_element(By.XPATH, "//h1[contains(text(), '덱 구성')]/following-sibling::p")
            composition = composition_elem.text.strip()
        except:
            composition = ""

        detail_data["meta"].append({
            "index": entry["index"],
            "name": name,
            "difficulty": difficulty,
            "leveling": leveling,
            "composition": composition
        })

    driver.quit()

    with open(detail_path, "w", encoding="utf-8") as f:
        json.dump(detail_data, f, ensure_ascii=False, indent=2)
    print(f"✅ metadetail.json 저장 완료 ({detail_data['updated_at']} 기준, {len(detail_data['meta'])}개 조합)")

if __name__ == "__main__":
    crawl_detail_info()
