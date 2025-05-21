import discord
import json
import os
from discord.ext import commands
from dotenv import load_dotenv

# .env 파일에서 토큰 불러오기
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# 디스코드 봇 설정
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ 봇 로그인 완료: {bot.user}")

@bot.command(name="롤체", aliases=["ㄹㅊ"])
async def tft_command(ctx, subcommand=None):
    if subcommand in ["메타", "ㅁㅌ"]:
        await send_tft_meta(ctx)
    else:
        await ctx.send("❓ 사용 가능한 하위 명령어: `메타`")

async def send_tft_meta(ctx):
    try:
        path = os.path.join(os.path.dirname(__file__), "meta.json")
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        await ctx.send("❌ 메타 정보가 없습니다. 먼저 `update_tft_meta.py`를 실행하세요.")
        return

    meta_list = data.get("meta", [])
    updated_at = data.get("updated_at", "알 수 없음")

    if not meta_list:
        await ctx.send("⚠️ 메타 조합이 비어 있습니다.")
        return

    image_folder = os.path.join(os.path.dirname(__file__), "meta_images")

    for meta in meta_list:
        index = meta["index"]
        name = meta["name"].replace("\nHOT", "").strip()
        is_hot = meta.get("hot", False)
        title = f"{index}. {'🔥' if is_hot else ''}{name}"

        embed = discord.Embed(title=title, color=0x5CD1E5)
        embed.set_footer(text=f"🗓️ 갱신일: {updated_at} | Powered by lolchess.gg")

        image_path = os.path.join(image_folder, f"meta_box_{index}.png")
        if os.path.exists(image_path):
            file = discord.File(image_path, filename=f"meta_{index}.png")
            embed.set_image(url=f"attachment://meta_{index}.png")
            await ctx.send(file=file, embed=embed)
        else:
            await ctx.send(embed=embed)

    await ctx.send(f"✅ 총 {len(meta_list)}개 조합 표시 완료.")

bot.run(TOKEN)