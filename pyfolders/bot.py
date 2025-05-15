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

@bot.command(name="참치")
async def tuna(ctx, cmd, *, name):
    if cmd == "롤전적":
        await send_lol_stats(ctx, name)
    elif cmd == "롤체전적":
        await send_tft_stats(ctx, name)
    elif cmd == "롤현재":
        await send_lol_live_status(ctx, name)
#    elif cmd == "발로전적":
#        await send_valorant_stats(ctx, name)
    else:
        await ctx.send("지원하지 않는 명령어입니다.")


bot.run(TOKEN)
