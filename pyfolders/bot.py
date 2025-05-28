import os
from dotenv import load_dotenv
import discord    
import asyncio

from discord.ext import commands
from lol import send_lol_stats
from tft import send_tft_stats
from lolwatch import send_lol_live_status, send_lol_opponent_info
from tftwatch import send_tft_live_status
from lolpatch import send_lol_patch_note
from tftpatch import send_tft_patch_note
from tftmeta import send_tft_meta
from valgun import send_random_weapon
from steamgame import send_steam_game_info

from tft_update_meta import crawl_tft_meta, save_meta_json
from tft_update_metadetail import crawl_detail_info
from tft_generate_meta_card import generate_all_meta_cards


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

# !롤 
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

# !롤체 
@bot.command(name="롤체", aliases=["ㄹㅊ"])
async def tft_command(ctx, subcommand: str = None, *, riot_id: str = None):
    if subcommand in ["전적", "ㅈㅈ"]:
        await send_tft_stats(ctx, riot_id)
    elif subcommand in ["관전", "ㄱㅈ"]:
        await send_tft_live_status(ctx, riot_id)
    elif subcommand in ["패치", "ㅍㅊ"]:
        await send_tft_patch_note(ctx)
    elif subcommand in ["메타", "ㅁㅌ"]:
        await send_tft_meta(ctx, riot_id)
    else:
        await ctx.send("🤔 지원하지 않는 명령어입니다.")

# !발로
@bot.command(name="발로", aliases=["ㅂㄹ"])
async def valorant_command(ctx, subcommand: str = None):
    if subcommand in ["ㄱㅊ", "권총"]:
        await send_random_weapon(ctx, category="권총")
    elif subcommand in ["ㅈㅁㄱ", "주무기"]:
        await send_random_weapon(ctx, category="주무기")
    elif subcommand in ["ㄹㄷ", "랜덤"]:
        # 주무기 + 권총 통합해서 랜덤
        import random
        category = random.choice(["권총", "주무기"])
        await send_random_weapon(ctx, category=category)
    else:
        await ctx.send("🤔 지원하지 않는 명령어입니다.")

@bot.command(name="스팀")
async def steam_command(ctx, subcommand: str = None, *, game_name: str = None):
    if subcommand == "정보" and game_name:
        await send_steam_game_info(ctx, game_name)
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
- `!롤체 관전 닉#태그` 또는 `!ㄹㅊ ㄱㅈ 닉#태그` : 현재 게임 관전
- `!롤체 패치` 또는 `!ㄹㅊ ㅍㅊ` : 최신 TFT 패치노트 확인
- `!롤체 메타 전체` : 현재 메타 조합 목록 출력
- `!롤체 메타 [번호]` : 해당 번호의 메타 + 상세정보 확인
   예) `!롤체 메타 2`
- `!롤체 메타 [유닛이름]` : 특정 유닛이 포함된 메타 리스트 출력
   예) `!롤체 메타 유미`

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

#관리자 명령어
@bot.command(name="롤토체스")
async def tft_meta_patch(ctx, subcommand: str = None):
    if subcommand in ["메타패치"]:
        await ctx.send("🔄 롤체 메타 정보를 수집 중입니다. 약 5분가량 소요됩니다./n 오래 걸릴경우 관리자 `pal_tak`에게 문의 주세요!")

        loop = asyncio.get_running_loop()

        # 1. 메타 정보 수집 및 저장
        data = await loop.run_in_executor(None, crawl_tft_meta)
        await loop.run_in_executor(None, save_meta_json, data)

        # 2. 세부 정보 수집
        await loop.run_in_executor(None, crawl_detail_info)

        # 3. 카드 이미지 생성
        await loop.run_in_executor(None, generate_all_meta_cards)

        await ctx.send("✅ 롤체 메타 패치 완료! 최신 카드 이미지가 생성되었습니다.")
    else:
        await ctx.send("❓ 사용법: `!롤체 메타 패치`")



bot.run(TOKEN)
