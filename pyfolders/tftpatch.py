import os
import requests
import discord
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from discord import Interaction

async def send_tft_patch_note(interaction: Interaction):
    url = "https://www.leagueoflegends.com/ko-kr/news/tags/teamfight-tactics/"
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        res = requests.get(url, headers=headers)
        soup = BeautifulSoup(res.text, "html.parser")

        patch_link_tag = soup.select_one('a[href*="teamfight-tactics-patch-"]')
        if not patch_link_tag:
            await interaction.response.send_message("❌ TFT 패치노트를 불러올 수 없습니다.", ephemeral=True)
            return

        href = patch_link_tag["href"]
        link = href if href.startswith("http") else "https://teamfighttactics.leagueoflegends.com" + href

        patch_res = requests.get(link, headers=headers)
        patch_soup = BeautifulSoup(patch_res.text, "html.parser")

        title_tag = patch_soup.select_one("h1")
        date_tag = patch_soup.select_one("time")
        thumbnail_tag = patch_soup.select_one("meta[property='og:image']")
        summary_tag = patch_soup.select_one('div[data-testid="rich-text-html"]')

        if not (title_tag and date_tag and thumbnail_tag):
            await interaction.response.send_message("❌ 패치노트 정보를 불러올 수 없습니다.", ephemeral=True)
            return

        title = title_tag.text.strip()
        date = date_tag.text.strip()
        thumbnail = thumbnail_tag["content"]
        summary = summary_tag.text.strip() if summary_tag else "최신 패치노트를 확인해보세요!"

        embed = discord.Embed(
            title=title,
            url=link,
            description=f"🗓️ {date}\n\n{summary}",
            color=discord.Color.brand_red()
        )
        embed.set_image(url=thumbnail)
        embed.set_author(name="🐟TunaBot 패치 정보")
        embed.set_footer(text="🐳 TunaBot TFT Info | tuna.gg")

        await interaction.response.send_message(embed=embed)

    except Exception as e:
        print(f"[TFT 패치노트 오류] {e}")
        await interaction.response.send_message("❌ TFT 패치노트를 불러오는 중 오류가 발생했습니다.", ephemeral=True)

async def tftpatch(interaction: Interaction):
    await send_tft_patch_note(interaction)

