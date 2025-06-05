import discord
import random
from urllib.parse import quote

GITHUB_BASE_URL = "https://raw.githubusercontent.com/Bada-Yoo/TunaBot/refs/heads/main/pyfolders/gun_images/"

weapon_categories = {
    "권총": ["클래식", "쇼티", "프렌지", "고스트", "셰리프"],
    "주무기": [
        "스팅어", "스펙터", "버키", "저지", "불독", "가디언", "팬텀", "밴달",
        "마샬", "오퍼레이터", "아레스", "오딘"
    ]
}

refresh_targets = {}

def choose_random_category():
    return random.choice(["권총", "주무기"])

async def send_random_weapon(ctx, category: str, label: str):
    if category == "랜덤":
        category = choose_random_category()

    names = weapon_categories.get(category)
    name = random.choice(names)
    image_url = f"{GITHUB_BASE_URL}{quote(name)}.avif"

    embed = discord.Embed(
        title=f"🔫 오늘의 랜덤 {label}",
        description=f"**{name}**입니다!",
        color=discord.Color(0x2ECC71)
    )
    embed.set_author(name="🐟 TunaBot 총기 정보")
    embed.set_image(url=image_url)
    embed.set_footer(text="🐳 TunaBot Valorant Info | tuna.gg")

    message = await ctx.send(embed=embed)
    await message.add_reaction("🔁")

    # 리프레시 시 label만 저장 (category는 랜덤 시마다 새로 정함)
    refresh_targets[message.id] = label

async def handle_valorant_refresh(reaction, user, bot):
    if user.bot or str(reaction.emoji) != "🔁":
        return

    message = reaction.message
    if message.id not in refresh_targets:
        return

    label = refresh_targets[message.id]
    category = choose_random_category() if label == "총" else (
        "권총" if label == "권총" else "주무기"
    )

    names = weapon_categories.get(category)
    if not names:
        await message.channel.send("❌ 무기 정보를 불러오는 데 실패했습니다.")
        return

    name = random.choice(names)
    image_url = f"{GITHUB_BASE_URL}{quote(name)}.avif"

    embed = discord.Embed(
        title=f"🔫 오늘의 랜덤 {label}",
        description=f"**{name}**입니다!",
        color=discord.Color(0x2ECC71)
    )
    embed.set_author(name="🐟 TunaBot 총기 정보")
    embed.set_image(url=image_url)
    embed.set_footer(text="🐳 TunaBot Valorant Info | tuna.gg")

    await message.edit(embed=embed)
    await message.clear_reactions()
    await message.add_reaction("🔁")
