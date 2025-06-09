import discord
import requests
from bs4 import BeautifulSoup
from discord import Interaction

async def send_val_patch_note(interaction: Interaction):
    try:
        url = "https://playvalorant.com/ko-kr/news/game-updates/"
        headers = {"User-Agent": "Mozilla/5.0"}

        # 메인 페이지 요청
        res = requests.get(url, headers=headers)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, "html.parser")

        # 첫 번째 뉴스 카드 선택
        card = soup.select_one('a[data-testid="articlefeaturedcard-component"][href*="/ko-kr/news/game-updates/"]')
        if not card:
            await interaction.response.send_message("❌ 발로란트 패치노트를 찾을 수 없습니다.", ephemeral=True)
            return

        # 상세 페이지 링크
        link = "https://playvalorant.com" + card["href"]

        # 제목
        title_tag = card.select_one('[data-testid="card-title"]')
        title = title_tag.get_text(strip=True) if title_tag else "제목 없음"

        # 요약
        summary_tag = card.select_one('[data-testid="rich-text"]')
        summary = summary_tag.get_text(strip=True) if summary_tag else "요약 정보가 없습니다."

        # 날짜
        date_tag = card.select_one("time")
        date = (
            date_tag["datetime"].split("T")[0]
            if date_tag and date_tag.has_attr("datetime")
            else "날짜 없음"
        )

        # 🎯 뉴스 상세페이지 요청 → og:image 썸네일 추출
        detail_res = requests.get(link, headers=headers)
        detail_soup = BeautifulSoup(detail_res.text, "html.parser")
        og_img_tag = detail_soup.select_one('meta[property="og:image"]')
        thumbnail = og_img_tag["content"] if og_img_tag and og_img_tag.has_attr("content") else None

        print(f"[DEBUG] 썸네일 URL: {thumbnail}")

        # Discord Embed 생성
        embed = discord.Embed(
            title=title,
            url=link,
            description=f"🗓️ {date}\n\n{summary}",
            color=discord.Color.brand_red()
        )
        if thumbnail and thumbnail.startswith("http"):
            embed.set_image(url=thumbnail)
        embed.set_author(name="🐟 TunaBot 패치 정보")
        embed.set_footer(text="🐳 TunaBot Valorant Info | tuna.gg")

        await interaction.response.send_message(embed=embed)

    except Exception as e:
        print(f"[VAL 패치노트 오류] {e}")
        await interaction.response.send_message("❌ 발로란트 패치노트를 불러오는 중 오류가 발생했습니다.")
