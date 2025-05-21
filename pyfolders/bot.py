import os
from dotenv import load_dotenv
import discord    
from discord.ext import commands
from lol import send_lol_stats
from tft import send_tft_stats
from lolwatch import send_lol_live_status, send_lol_opponent_info
from tftwatch import send_tft_live_status
from lolpatch import send_lol_patch_note
from tftpatch import send_tft_patch_note
from tftmeta import send_tft_meta
#from valorant import send_valorant_stats

# 토큰 불러오기
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# 디스코드 봇 설정
intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True
bot = commands.Bot(command_prefix='!', intents=intents) 

@bot.event
async def on_ready():
    print(f'✅ 봇 로그인 완료: {bot.user}')


@bot.command()
async def ping(ctx):
    await ctx.send('퐁!')

# !롤 전적 [RiotID]
@bot.command(name="롤", aliases=["ㄹ"])
async def lol_command(ctx, subcommand: str = None, *, riot_id: str = None):
    if subcommand in ["전적", "ㅈㅈ"]:
        await send_lol_stats(ctx, riot_id)
    elif subcommand in ["관전", "ㄱㅈ"]:
        await send_lol_live_status(ctx, riot_id)
    elif subcommand in ["상대정보", "ㅅㄷ"]:  
        await send_lol_opponent_info(ctx, riot_id)
    elif subcommand in ["패치", "ㅍㅊ"]:
        await send_lol_patch_note(ctx)
    else:
        await ctx.send("🤔 지원하지 않는 명령어입니다.")

# !롤체 전적 [RiotID]
@bot.command(name="롤체", aliases=["ㄹㅊ"])
async def tft_command(ctx, subcommand: str = None, *, riot_id: str = None):
    if subcommand in ["전적", "ㅈㅈ"]:
        await send_tft_stats(ctx, riot_id)
    elif subcommand in ["관전", "ㄱㅈ"]:
        await send_tft_live_status(ctx, riot_id)
    elif subcommand in ["패치", "ㅍㅊ"]:
        await send_tft_patch_note(ctx)
    elif subcommand in ["메타", "ㅁㅌ"]:
        await send_tft_meta(ctx)
    else:
        await ctx.send("🤔 지원하지 않는 명령어입니다.")

# !참치 도움
@bot.command(name="참치")
async def tuna(ctx, subcommand = None):
    if subcommand == "help":
        await ctx.send("""
🐟 **참치봇 사용 가이드**

🌊 **롤 전적 및 라이브**
- `!롤 전적 닉#태그` 또는 `!ㄹ ㅈㅈ 닉#태그` : 소환사 전적 확인
- `!롤 관전 닉#태그` 또는 `!ㄹ ㄱㅈ 닉#태그` : 현재 롤 정보 확인
- `!롤 상대정보 닉#태그` 또는 `!ㄹ ㅅㄷ 닉#태그` : 상대 팀 티어/모스트 분석
- `!롤 패치` 또는 `!ㄹ ㅍㅊ` : 최신 패치노트 확인

🌊 **롤체(TFT)**
- `!롤체 전적 닉#태그` 또는 `!ㄹㅊ ㅈㅈ 닉#태그` : 소환사 전적 확인
- `!롤체 관전 닉#태그` 또는 `!ㄹㅊ ㄱㅈ 닉#태그` : 현재 롤체 정보 확인
- `!롤체 패치` 또는 `!ㄹㅊ ㅍㅊ` : 최신 TFT 패치노트 확인
- `!롤체 메타` 또는 `!ㄹㅊ ㅁㅌ` : 현재 TFT 메타 추천 조합 확인

🐬 모든 명령어는 줄임말로도 사용 가능합니다!
""")
    else:
        await ctx.send("🤔 지원하지 않는 명령어입니다.")

# !잘못된 명령어
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("🤔 지원하지 않는 명령어입니다.")
    else:
        raise error  # 다른 오류는 디버깅을 위해 그대로 발생시킴


# 예시 확장 가능:
# @bot.command(name="발로")
# async def valorant_command(ctx, subcommand, *, riot_id):
#     if subcommand == "전적":
#         await send_valorant_stats(ctx, riot_id)

#🌊 **즐겨찾기 기능**
#- `!등록 닉#태그` : 즐겨찾는 Riot ID 등록
#- `!내전적` / `!내현재` : 등록된 Riot ID로 전적/관전 확인

bot.run(TOKEN)
