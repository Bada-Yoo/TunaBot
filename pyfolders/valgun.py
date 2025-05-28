import discord
import random
import os

# 카테고리 분류
weapon_categories = {
    "권총": [
        {"name": "클래식", "file": "클래식.avif"},
        {"name": "쇼티", "file": "쇼티.avif"},
        {"name": "프렌지", "file": "프렌지.avif"},
        {"name": "고스트", "file": "고스트.avif"},
        {"name": "셰리프", "file": "셰리프.avif"},
    ],
    "주무기": [
        {"name": "스팅어", "file": "스팅어.avif"},
        {"name": "스펙터", "file": "스펙터.avif"},
        {"name": "버키", "file": "버키.avif"},
        {"name": "저지", "file": "저지.avif"},
        {"name": "불독", "file": "불독.avif"},
        {"name": "가디언", "file": "가디언.avif"},
        {"name": "팬텀", "file": "팬텀.avif"},
        {"name": "밴달", "file": "밴달.avif"},
        {"name": "마샬", "file": "마샬.avif"},
        {"name": "오퍼레이터", "file": "오퍼레이터.avif"},
        {"name": "아레스", "file": "아레스.avif"},
        {"name": "오딘", "file": "오딘.avif"},
        {"name": "근접무기", "file": "근접무기.avif"},  # 칼
    ]
}

# 무기 출력 함수
async def send_random_weapon(ctx, category):
    weapons = weapon_categories.get(category)
    if not weapons:
        await ctx.send(f"❌ 존재하지 않는 무기 카테고리입니다: `{category}`")
        return

    weapon = random.choice(weapons)
    image_path = os.path.join("pyfolders", "gun_images", weapon["file"])

    if not os.path.exists(image_path):
        await ctx.send(f"⚠️ 이미지 파일이 존재하지 않습니다: `{weapon['file']}`")
        return

    file = discord.File(image_path, filename=weapon["file"])
    embed = discord.Embed(
        title=f"🔫 오늘의 {category}",
        description=f"**{weapon['name']}**",
        color=discord.Color.red()
    )
    embed.set_image(url=f"attachment://{weapon['file']}")
    embed.set_author(name="🐟TunaBot 총기 정보")
    embed.set_footer(text="🐳 Powered by Data Crawling | tuna.gg")


    await ctx.send(file=file, embed=embed)
