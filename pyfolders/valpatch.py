import discord
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time

async def send_val_patch_note(ctx):
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=options)
    driver.get("https://playvalorant.com/ko-kr/news/")
    time.sleep(3)

    try:
        news_cards = driver.find_elements(By.CSS_SELECTOR, 'a[href*="/ko-kr/news/"]')

        for card in news_cards:
            try:
                title = card.find_element(By.CSS_SELECTOR, '[data-testid="card-title"]').text.strip()
            except:
                continue

            if "패치 노트" not in title:
                continue

            summary_tag = card.find_element(By.CSS_SELECTOR, '[data-testid="rich-text"]')
            summary = summary_tag.text.strip() if summary_tag else "최신 패치노트를 확인해보세요!"
            thumbnail = card.find_element(By.CSS_SELECTOR, 'img').get_attribute('src')
            link = card.get_attribute('href')

            # 본문 접속 후 날짜 추출
            driver.get(link)
            time.sleep(2)
            date_tag = driver.find_element(By.TAG_NAME, 'time')
            date = date_tag.get_attribute("datetime").split("T")[0]

            driver.quit()

            # Embed 생성
            embed = discord.Embed(
                title=title,
                url=link,
                description=f"🗓️ {date}\n\n{summary}",
                color=discord.Color.brand_red()
            )
            embed.set_image(url=thumbnail)
            embed.set_author(name="🐟TunaBot 패치 정보")
            embed.set_footer(text="🐳 Powered by Data Crawling | tuna.gg")

            await ctx.send(embed=embed)
            return

        driver.quit()
        await ctx.send("❌ 발로란트 패치노트를 찾을 수 없습니다.")

    except Exception as e:
        driver.quit()
        print(f"[VAL 패치노트 오류] {e}")
        await ctx.send("❌ 발로란트 패치노트를 불러오는 중 오류가 발생했습니다.")
