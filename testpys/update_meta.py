from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

options = webdriver.ChromeOptions()
options.add_argument('--headless=new')
options.add_argument('--ignore-certificate-errors')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

try:
    print("롤체지지 접속 중...")
    driver.get("https://lolchess.gg/meta")

    WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.XPATH, "//div[contains(@class, 'css-35tzvc')]"))
    )

    containers = driver.find_elements(By.XPATH, "//div[contains(@class, 'css-35tzvc')]")

    names = []
    skip_keywords = ["초반 빌드업", "유물별 챔피언"]

    for comp in containers:
        try:
            name_elem = comp.find_element(By.XPATH, "./div[1]")
            name = name_elem.text.strip()

            if not name or any(skip in name for skip in skip_keywords):
                continue

            # 🔥 붙일지 판단
            hot = False
            try:
                comp.find_element(By.XPATH, ".//span[contains(@class, 'tag hot')]")
                hot = True
            except:
                pass

            final_name = f"🔥 {name}" if hot else name
            names.append(final_name)

        except Exception as e:
            print(f"⚠️ 조합 처리 중 에러: {e}")

    print(f"\n✅ 메타 조합 {len(names)}개:")
    for i, name in enumerate(names, 1):
        print(f"{i}. {name}")

finally:
    driver.quit()