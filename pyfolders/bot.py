import os
from dotenv import load_dotenv
import discord    
from discord.ext import commands
from lol import send_lol_stats
from lolchess import send_tft_stats
from lolwatch import send_lol_live_status
#from valorant import send_valorant_stats

# 토큰 불러오기
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# 디스코드 봇 설정
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents) 

@bot.event
async def on_ready():
    print(f'✅ 봇 로그인 완료: {bot.user}')


@bot.command()
async def ping(ctx):
    await ctx.send('퐁!')

# !롤 전적 [RiotID]
@bot.command(name="롤")
async def lol_command(ctx, subcommand, *, riot_id):
    if subcommand == "전적":
        await send_lol_stats(ctx, riot_id)
    elif subcommand == "현재":
        await send_lol_live_status(ctx, riot_id)
    else:
        await ctx.send("지원하지 않는 명령어입니다.")

# !롤체 전적 [RiotID]
@bot.command(name="롤체")
async def tft_command(ctx, subcommand, *, riot_id):
    if subcommand == "전적":
        await send_tft_stats(ctx, riot_id)
    else:
        await ctx.send("지원하지 않는 명령어입니다.")

# 예시 확장 가능:
# @bot.command(name="발로")
# async def valorant_command(ctx, subcommand, *, riot_id):
#     if subcommand == "전적":
#         await send_valorant_stats(ctx, riot_id)


bot.run(TOKEN)
