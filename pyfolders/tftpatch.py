import requests
import discord
from bs4 import BeautifulSoup
from discord import Interaction

BASE_URL = "https://teamfighttactics.leagueoflegends.com"

async def send_tft_patch_note(interaction: Interaction):
    url = f"{BASE_URL}/ko-kr/news/tags/patch-notes/"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    try:
        # 패치노트 목록 페이지
        res = requests.get(url, headers=headers, timeout=10)
        res.raise_for_status()

        soup = BeautifulSoup(res.text, "html.parser")

        # 최신 패치 카드
        patch_link_tag = soup.select_one(
            'a[data-testid="articlefeaturedcard-component"]'
        )

        if not patch_link_tag:
            await interaction.response.send_message(
                "❌ 최신 TFT 패치노트를 찾을 수 없습니다.",
                ephemeral=True
            )
            return

        href = patch_link_tag.get("href")

        if not href:
            await interaction.response.send_message(
                "❌ 패치 링크를 찾을 수 없습니다.",
                ephemeral=True
            )
            return

        link = href if href.startswith("http") else BASE_URL + href

        print(f"[TFT] 최신 패치 링크: {link}")

        # 실제 패치노트 페이지
        patch_res = requests.get(link, headers=headers, timeout=10)
        patch_res.raise_for_status()

        patch_soup = BeautifulSoup(patch_res.text, "html.parser")

        title_tag = patch_soup.select_one("h1")
        date_tag = patch_soup.select_one("time")
        thumbnail_tag = patch_soup.select_one(
            "meta[property='og:image']"
        )

        summary_tag = patch_soup.select_one(
            'div[data-testid="rich-text-html"]'
        )

        if not title_tag:
            await interaction.response.send_message(
                "❌ 패치 제목을 불러올 수 없습니다.",
                ephemeral=True
            )
            return

        title = title_tag.get_text(strip=True)
        date = (
            date_tag.get_text(strip=True)
            if date_tag else "날짜 정보 없음"
        )

        thumbnail = (
            thumbnail_tag.get("content")
            if thumbnail_tag else None
        )

        if summary_tag:
            summary = summary_tag.get_text(
                separator=" ",
                strip=True
            )
            summary = summary[:500]
        else:
            summary = "최신 TFT 패치노트를 확인해보세요!"

        embed = discord.Embed(
            title=title,
            url=link,
            description=f"🗓️ {date}\n\n{summary}",
            color=discord.Color.brand_red()
        )

        if thumbnail:
            embed.set_image(url=thumbnail)

        embed.set_author(name="🐟 TunaBot TFT 패치 정보")
        embed.set_footer(text="🐧 TunaBot TFT Info | tuna.gg")

        await interaction.response.send_message(embed=embed)

    except Exception as e:
        print(f"[TFT 패치노트 오류] {e}")

        await interaction.response.send_message(
            "❌ TFT 패치노트를 불러오는 중 오류가 발생했습니다.",
            ephemeral=True
        )


async def tftpatch(interaction: Interaction):
    await send_tft_patch_note(interaction)