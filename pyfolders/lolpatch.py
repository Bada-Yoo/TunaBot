import os
import requests
import discord
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()

async def send_lol_patch_note(ctx):
    url = "https://www.leagueoflegends.com/ko-kr/news/tags/patch-notes/"
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        res = requests.get(url, headers=headers)
        soup = BeautifulSoup(res.text, "html.parser")

        # 최신 패치노트 링크 추출
        patch_link_tag = soup.select_one('a[href*="/ko-kr/news/game-updates/patch-"]')
        if not patch_link_tag:
            await ctx.send("❌ 패치노트를 불러올 수 없습니다.")
            return

        link = "https://www.leagueoflegends.com" + patch_link_tag["href"]

        # 개별 패치노트 페이지 접속
        patch_res = requests.get(link, headers=headers)
        patch_soup = BeautifulSoup(patch_res.text, "html.parser")

        title_tag = patch_soup.select_one("h1")
        date_tag = patch_soup.select_one("time")
        thumbnail_tag = patch_soup.select_one("meta[property='og:image']")

        if not (title_tag and date_tag and thumbnail_tag):
            await ctx.send("❌ 패치노트를 불러올 수 없습니다.")
            return

        title = title_tag.text.strip()
        date = date_tag.text.strip()
        thumbnail = thumbnail_tag["content"]
        # 본문 부제목 가져오기기
        summary_tag = patch_soup.select_one('div[data-testid="rich-text-html"]')
        summary = summary_tag.text.strip() if summary_tag else "최신 패치노트를 확인해보세요!"

        embed = discord.Embed(
            title=title,
            url=link,
            description=f"🗓️ {date}\n\n{summary}",
            color=discord.Color.brand_red()
        )
        embed.set_image(url=thumbnail) 
        embed.set_author(name="🐟TunaBot 패치 정보")
        embed.set_footer(text="🐬 Powered by Data Crawling | tuna.gg")

        await ctx.send(embed=embed)

    except Exception as e:
        print(f"[패치노트 오류] {e}")
        await ctx.send("❌ 패치노트를 불러오는 중 오류가 발생했습니다.")

async def lolpatch(ctx):
    await send_lol_patch_note(ctx)
