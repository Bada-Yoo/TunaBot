import requests
import discord
from bs4 import BeautifulSoup
from discord import Interaction


async def send_lol_patch_note(interaction: Interaction):
    url = "https://www.leagueoflegends.com/ko-kr/news/tags/patch-notes/"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    try:
        await interaction.response.defer()

        # 패치노트 목록 페이지
        res = requests.get(url, headers=headers, timeout=10)
        res.raise_for_status()

        soup = BeautifulSoup(res.text, "html.parser")

        # 최신 패치 카드 찾기
        cards = soup.select(
            'a[data-testid="articlefeaturedcard-component"]'
        )

        link = None

        for card in cards:
            href = card.get("href", "")

            if (
                "league-of-legends-patch" in href
                and "notes" in href
            ):
                link = (
                    href
                    if href.startswith("http")
                    else "https://www.leagueoflegends.com" + href
                )
                break

        if not link:
            await interaction.followup.send(
                "❌ 최신 패치노트를 찾을 수 없습니다."
            )
            return

        print(f"[LOL] 최신 패치 링크: {link}")

        # 실제 패치노트 페이지
        patch_res = requests.get(
            link,
            headers=headers,
            timeout=10
        )
        patch_res.raise_for_status()

        patch_soup = BeautifulSoup(
            patch_res.text,
            "html.parser"
        )

        title_tag = patch_soup.select_one("h1")
        date_tag = patch_soup.select_one("time")
        thumbnail_tag = patch_soup.select_one(
            "meta[property='og:image']"
        )
        summary_tag = patch_soup.select_one(
            'div[data-testid="rich-text-html"]'
        )

        if not title_tag:
            await interaction.followup.send(
                "❌ 패치노트 정보를 불러올 수 없습니다."
            )
            return

        title = title_tag.get_text(strip=True)

        date = (
            date_tag.get_text(strip=True)
            if date_tag
            else "날짜 정보 없음"
        )

        thumbnail = (
            thumbnail_tag.get("content")
            if thumbnail_tag
            else None
        )

        if summary_tag:
            summary = summary_tag.get_text(
                separator=" ",
                strip=True
            )
            summary = summary[:500]
        else:
            summary = "최신 패치노트를 확인해보세요!"

        embed = discord.Embed(
            title=title,
            url=link,
            description=f"🗓️ {date}\n\n{summary}",
            color=discord.Color.dark_purple()
        )

        if thumbnail:
            embed.set_image(url=thumbnail)

        embed.set_author(
            name="🐟 TunaBot 패치 정보"
        )

        embed.set_footer(
            text="🐬 TunaBot LOL Info | tuna.gg"
        )

        await interaction.followup.send(
            embed=embed
        )

    except Exception as e:
        print(f"[LOL 패치노트 오류] {e}")

        await interaction.followup.send(
            "❌ 패치노트를 불러오는 중 오류가 발생했습니다."
        )


async def lolpatch(interaction: Interaction):
    await send_lol_patch_note(interaction)