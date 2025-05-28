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

async def send_random_weapon(ctx, category):
    names = weapon_categories.get(category)
    if not names:
        await ctx.send(f"❌ 존재하지 않는 카테고리: {category}")
        return

    name = random.choice(names)
    image_url = f"{GITHUB_BASE_URL}{quote(name)}.avif"

    embed = discord.Embed(
        title=f"🔫 오늘의 {category}",
        description=f"**{name}**입니다!",
        color=discord.Color.green()
    )
    embed.set_author(name="🐟 TunaBot 총기 정보")
    embed.set_image(url=image_url)
    embed.set_footer(text="🐳 Powered by Data Crawling | tuna.gg")
    await ctx.send(embed=embed)
