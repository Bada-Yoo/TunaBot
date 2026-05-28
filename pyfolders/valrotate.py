import discord
import re
import requests
from bs4 import BeautifulSoup
from discord import Interaction

MAP_TRANSLATIONS = {
    "ascent": "어센트",
    "breeze": "브리즈",
    "fracture": "프랙처",
    "haven": "헤이븐",
    "lotus": "로터스",
    "pearl": "펄",
    "split": "스플릿",
    "abyss": "어비스",
    "bind": "바인드",
    "corrode": "코로드",
    "icebox": "아이스박스",
    "sunset": "선셋",
}


def translate_map_name(name):
    translated = MAP_TRANSLATIONS.get(name.lower())
    if translated and translated.lower() != name.lower():
        return f"{name} ({translated})"
    return name


# 현재 경쟁전 맵 로테이션 정보를 가져오는 함수
def get_current_valorant_rotation():
    urls = [
        "https://valorant.fandom.com/wiki/Maps",
        "https://valorant.fandom.com/api.php?action=parse&page=Maps&prop=text&format=json"
    ]
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9"
    }

    for url in urls:
        try:
            res = requests.get(url, headers=headers, timeout=10)
            res.raise_for_status()

            if "api.php" in url:
                data = res.json()
                html = data.get("parse", {}).get("text", {}).get("*", "")
            else:
                html = res.text

            soup = BeautifulSoup(html, "html.parser")
            gallery = soup.find("div", id="gallery-0")
            if not gallery:
                continue

            a_tags = gallery.select("div.lightbox-caption a")
            maps = []
            seen = set()

            for a in a_tags:
                name = a.text.strip()
                if not name:
                    continue
                low = name.lower()
                if low in seen or low in ["quotes", "lore"]:
                    continue
                if any(char.isdigit() for char in name):
                    continue
                if len(name) > 40:
                    continue
                if not re.fullmatch(r"[A-Za-z]+", name):
                    continue
                seen.add(low)
                maps.append(name)

            if maps:
                return maps
        except Exception:
            continue

    return []

# Discord Embed 생성 함수
def generate_valorant_rotation_embed():
    maps = get_current_valorant_rotation()

    if not maps:
        return discord.Embed(
            title="❌ 맵 정보를 불러올 수 없습니다.",
            description="잠시 후 다시 시도해주세요.",
            color=discord.Color.red()
        )

    description = "\n".join([f"🗺️ {translate_map_name(m)}" for m in maps])

    embed = discord.Embed(
        title="발로란트 경쟁전 맵 로테이션",
        description=description,
        color=discord.Color.green()
    )
    embed.set_author(name="🐟 TunaBot 로테이션 정보")
    embed.set_footer(text="🐳 TunaBot Valorant Info | tuna.gg")

    return embed

# Interaction 슬래시 명령어용 함수
async def send_valorant_rotation(interaction: Interaction):
    embed = generate_valorant_rotation_embed()
    await interaction.response.send_message(embed=embed)