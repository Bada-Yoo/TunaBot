import discord
import requests
from bs4 import BeautifulSoup
from discord import Interaction

# 현재 경쟁전 맵 로테이션 정보를 가져오는 함수
def get_current_valorant_rotation():
    url = "https://valorant.fandom.com/wiki/Maps"
    headers = {"User-Agent": "Mozilla/5.0"}
    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.text, "html.parser")

    gallery = soup.find("div", id="gallery-0")
    if not gallery:
        return []

    a_tags = gallery.select("div.lightbox-caption a")

    maps = []
    seen = set()

    for a in a_tags:
        name = a.text.strip()
        if name.lower() in seen:
            continue
        if name.lower() in ["quotes", "lore"]:
            continue
        if len(name) > 30 or not name.isalpha():
            continue
        seen.add(name.lower())
        maps.append(name)

    return maps

# Discord Embed 생성 함수
def generate_valorant_rotation_embed():
    maps = get_current_valorant_rotation()

    if not maps:
        return discord.Embed(
            title="❌ 맵 정보를 불러올 수 없습니다.",
            description="잠시 후 다시 시도해주세요.",
            color=discord.Color.red()
        )

    description = "\n".join([f"🗺️ {m}" for m in maps])

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