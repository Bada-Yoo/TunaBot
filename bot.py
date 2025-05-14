import os
from dotenv import load_dotenv
import discord
from discord.ext import commands

# .env 파일 불러오기
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'✅ 봇 로그인 완료: {bot.user}')

@bot.command()
async def ping(ctx):
    await ctx.send('퐁!')

bot.run(TOKEN)
