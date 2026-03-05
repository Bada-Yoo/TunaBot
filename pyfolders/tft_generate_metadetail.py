import os
import json
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


META_JSON = os.path.join(SCRIPT_DIR, "tft_meta.json")
OUTPUT_JSON = os.path.join(SCRIPT_DIR, "tft_metadetail.json")


def create_driver():

    chrome_options = Options()

    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")

    driver = webdriver.Chrome(options=chrome_options)

    return driver


def crawl_meta_detail(driver, url):

    driver.get(url)

    time.sleep(2)

    try:

        h1 = driver.find_element(By.XPATH, "//h1[contains(text(),'개요')]")

        p = h1.find_element(By.XPATH, "following-sibling::p")

        text = p.text.strip()

        return text

    except:

        return ""


def generate_meta_detail():

    with open(META_JSON, encoding="utf-8") as f:
        data = json.load(f)

    meta_list = data.get("meta", [])

    driver = create_driver()

    result = []

    for meta in meta_list:

        name = meta.get("name")
        url = meta.get("url")

        print(f"메타 가이드 수집: {name}")

        text = crawl_meta_detail(driver, url)

        result.append({
            "name": name,
            "url": url,
            "overview": text
        })

    driver.quit()

    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:

        json.dump(
            {"meta_detail": result},
            f,
            ensure_ascii=False,
            indent=2
        )

    print("메타 상세 저장 완료")


if __name__ == "__main__":

    generate_meta_detail()