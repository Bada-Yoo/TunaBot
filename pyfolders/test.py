import discord
from discord import app_commands
from discord.ext import commands
import os
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"✅ {bot.user} 로그인 완료 및 슬래시 명령 동기화됨")

# /핑
@bot.tree.command(name="핑", description="퐁!을 반환합니다.")
async def slash_ping(interaction: discord.Interaction):
    await interaction.response.send_message("퐁!")

bot.run(os.getenv("DISCORD_TOKEN"))
