import json
import os
import time
from datetime import datetime
from urllib.parse import urlparse

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


BASE_URL = "https://lolchess.gg"
META_URL = "https://lolchess.gg/meta"

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


def normalize_url(src):

    if not src:
        return ""

    src = src.strip()

    if src.startswith("//"):
        return "https:" + src

    if src.startswith("/"):
        return BASE_URL + src

    return src


def extract_item(img):

    src = img.get_attribute("src") or ""
    src = normalize_url(src)

    filename = os.path.basename(urlparse(src).path)
    name = filename.replace(".png", "").replace("TFT_Item_", "")

    return {
        "name": name,
        "image": src
    }


def extract_unit(block):

    name = ""
    icon = ""
    items = []

    # 챔피언 이름
    try:
        name = block.find_element(
            By.CSS_SELECTOR,
            "div[class*='e9927jh2']"
        ).text.strip()
    except:
        pass

    # 챔피언 아이콘
    try:
        img = block.find_element(
            By.CSS_SELECTOR,
            "img[src*='champions']"
        )

        icon = normalize_url(
            img.get_attribute("src")
            or img.get_attribute("data-src")
        )

    except:
        pass

    # 아이템
    try:
        item_container = block.find_element(
            By.CSS_SELECTOR,
            "div.items"
        )

        item_imgs = item_container.find_elements(
            By.CSS_SELECTOR,
            "img"
        )

        for img in item_imgs:
            items.append(extract_item(img))

    except:
        pass

    return {
        "name": name,
        "icon": icon,
        "items": items
    }

def crawl_tft_meta():

    options = webdriver.ChromeOptions()

    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,5000")
    

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )

    wait = WebDriverWait(driver, 20)

    try:

        print("meta 페이지 로딩")

        driver.get(META_URL)

        wait.until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "div[class*='Champion']")
            )
        )

        time.sleep(2)

        cards = driver.find_elements(
            By.CSS_SELECTOR,
            "a[href*='builder']"
        )

        meta_list = []

        for a in cards:

            url = normalize_url(a.get_attribute("href"))

            card = a
            for _ in range(6):
                card = card.find_element(By.XPATH, "..")

            name = "unknown"

            try:
                name = card.find_element(
                    By.CSS_SELECTOR,
                    "h2, h3"
                ).text.strip()
            except:
                name = card.text.split("\n")[0]

            unit_blocks = card.find_elements(
                By.CSS_SELECTOR,
                "div[class*='Champion']"
            )

            units = []

            for block in unit_blocks:
                units.append(extract_unit(block))

            meta_list.append({
                "name": name,
                "url": url,
                "units": units
            })

            print("수집:", name)

        return {
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "meta": meta_list
        }

    finally:
        driver.quit()


def save_meta_json(data):

    path = os.path.join(SCRIPT_DIR, "tft_meta.json")

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print("tft_meta.json 저장 완료")