import discord
import random
from urllib.parse import quote
from discord.ext import commands
from debug import log_reaction_simple, handle_raw_reaction_add


# 총기 이미지 경로 (GitHub raw)
GITHUB_BASE_URL = "https://raw.githubusercontent.com/Bada-Yoo/TunaBot/refs/heads/main/pyfolders/gun_images/"

# 무기 목록
weapon_categories = {
    "권총": ["클래식", "쇼티", "프렌지", "고스트", "밴딧", "셰리프"],
    "주무기": [
        "스팅어", "스펙터", "버키", "저지", "불독", "가디언", "팬텀", "밴달",
        "마샬", "오퍼레이터", "아레스", "오딘"
    ]
}

# 메시지 ID: label 저장
refresh_targets = {}

# 무기 카테고리 무작위 선택
def choose_random_category():
    return random.choice(["권총", "주무기"])


# 무기 임베드 전송 함수
async def send_random_weapon(interaction: discord.Interaction, category: str, label: str):
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

    await interaction.response.send_message(embed=embed)
    message = await interaction.original_response()
    await message.add_reaction("🔁")

    refresh_targets[message.id] = label


# 리액션으로 새 무기 갱신
async def handle_valorant_refresh(reaction, user, bot):
    if user.bot or str(reaction.emoji) != "🔁":
        return

    message = reaction.message
    if message.id not in refresh_targets:
        print("[DEBUG] 메시지 ID가 refresh_targets에 없음")
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

    try:
        await message.edit(embed=embed)
        await message.clear_reactions()
        await message.add_reaction("🔁")
    except discord.NotFound:
        print("[DEBUG] 메시지를 찾을 수 없음 (삭제되었거나 webhook 만료됨)")


# 봇 설정 (intents 필수)
intents = discord.Intents.default()
intents.messages = True
intents.reactions = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_reaction_add(reaction, user):
    log_reaction_simple(reaction, user)
    await handle_valorant_refresh(reaction, user, bot)

@bot.event
async def on_raw_reaction_add(payload: discord.RawReactionActionEvent):
    await handle_raw_reaction_add(bot, payload, refresh_cb=handle_valorant_refresh)

