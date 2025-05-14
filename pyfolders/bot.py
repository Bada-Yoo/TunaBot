import os
from dotenv import load_dotenv
import discord    
from discord.ext import commands
from lol import send_lol_stats
#from lolchess import send_tft_stats
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
#    elif cmd == "롤체전적":
#        await send_tft_stats(ctx, name)
#    elif cmd == "발로전적":
#        await send_valorant_stats(ctx, name)
    else:
        await ctx.send("지원하지 않는 명령어입니다.")




import requests

RIOT_API_KEY = "RGAPI-7a9876f6-e68d-4907-aa0e-502b39ebc6ae"
summoner_name = "바다속참치"
encoded_name = requests.utils.quote(summoner_name)
url = f"https://kr.api.riotgames.com/lol/summoner/v4/summoners/by-name/{encoded_name}"

headers = {
    "X-Riot-Token": RIOT_API_KEY
}

res = requests.get(url, headers=headers)

print("🔍 요청 URL:", url)
print("🔍 응답 코드:", res.status_code)
print("🔍 응답 내용:", res.text)











bot.run(TOKEN)
