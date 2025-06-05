import os
from dotenv import load_dotenv
import discord
import asyncio
from discord import app_commands

from lol import send_lol_stats
from lolwatch import send_lol_live_status, send_lol_opponent_info
from lolpatch import send_lol_patch_note

from tft import send_tft_stats
from tftwatch import send_tft_live_status
from tftpatch import send_tft_patch_note
from tftmeta import send_tft_meta

from valgun import send_random_weapon, handle_valorant_refresh
from valpatch import send_val_patch_note
from valrotate import send_valorant_rotation

from steamgame import send_steam_game_info

from tunaregister import send_tuna_register, send_tuna_unregister
from tunapointcheck import send_tuna_point
from tunacheckin import send_tuna_checkin

from tft_update_meta import crawl_tft_meta, save_meta_json
from tft_update_metadetail import crawl_detail_info
from tft_generate_meta_card import generate_all_meta_cards

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

@client.event
async def on_ready():
    await tree.sync()
    print(f"✅ 봇 로그인 완료: {client.user}")

# 롤 명령어 그룹
class 롤(app_commands.Group):
    @app_commands.command(name="전적", description="롤 전적을 확인합니다.")
    @app_commands.describe(riot_id="Riot ID#태그")
    async def 전적(self, interaction: discord.Interaction, riot_id: str):
        await send_lol_stats(interaction, riot_id)

    @app_commands.command(name="관전", description="롤 라이브 관전을 확인합니다.")
    @app_commands.describe(riot_id="Riot ID#태그")
    async def 관전(self, interaction: discord.Interaction, riot_id: str):
        await send_lol_live_status(interaction, riot_id)

    @app_commands.command(name="상대정보", description="롤 상대팀 정보를 확인합니다.")
    @app_commands.describe(riot_id="Riot ID#태그")
    async def 상대정보(self, interaction: discord.Interaction, riot_id: str):
        await send_lol_opponent_info(interaction, riot_id)

    @app_commands.command(name="패치", description="롤 패치노트를 확인합니다.")
    async def 패치(self, interaction: discord.Interaction):
        await send_lol_patch_note(interaction)

# 롤체 명령어 그룹
class 롤체(app_commands.Group):
    @app_commands.command(name="전적", description="롤체 전적을 확인합니다.")
    @app_commands.describe(riot_id="Riot ID#태그")
    async def 전적(self, interaction: discord.Interaction, riot_id: str):
        await send_tft_stats(interaction, riot_id)

    @app_commands.command(name="관전", description="롤체 관전을 확인합니다.")
    @app_commands.describe(riot_id="Riot ID#태그")
    async def 관전(self, interaction: discord.Interaction, riot_id: str):
        await send_tft_live_status(interaction, riot_id)

    @app_commands.command(name="패치", description="롤체 패치노트를 확인합니다.")
    async def 패치(self, interaction: discord.Interaction):
        await send_tft_patch_note(interaction)

    @app_commands.command(name="메타", description="롤체 메타 정보를 확인합니다.")
    @app_commands.describe(riot_id="전체 | 번호 | 유닛 이름")
    async def 메타(self, interaction: discord.Interaction, riot_id: str):
        await send_tft_meta(interaction, riot_id)

# 발로 명령어 그룹
class 발로(app_commands.Group):
    @app_commands.command(name="권총", description="발로란트 권총 추천")
    async def 권총(self, interaction: discord.Interaction):
        await send_random_weapon(interaction, category="권총", label="권총")

    @app_commands.command(name="주무기", description="발로란트 주무기 추천")
    async def 주무기(self, interaction: discord.Interaction):
        await send_random_weapon(interaction, category="주무기", label="주무기")

    @app_commands.command(name="랜덤", description="발로란트 무기 랜덤 추천")
    async def 랜덤(self, interaction: discord.Interaction):
        await send_random_weapon(interaction, category="랜덤", label="총")

    @app_commands.command(name="패치", description="발로란트 패치노트 확인")
    async def 패치(self, interaction: discord.Interaction):
        await send_val_patch_note(interaction)

    @app_commands.command(name="로테", description="발로란트 로테이션 확인")
    async def 로테(self, interaction: discord.Interaction):
        await send_valorant_rotation(interaction)

# 참치 명령어 그룹
class 참치(app_commands.Group):
    @app_commands.command(name="등록", description="참치봇에 등록합니다.")
    async def 등록(self, interaction: discord.Interaction):
        await send_tuna_register(interaction)

    @app_commands.command(name="삭제", description="참치봇에서 탈퇴합니다.")
    async def 삭제(self, interaction: discord.Interaction):
        await send_tuna_unregister(interaction)

    @app_commands.command(name="포인트", description="포인트를 조회합니다.")
    async def 포인트(self, interaction: discord.Interaction):
        await send_tuna_point(interaction)

    @app_commands.command(name="출첵", description="출석체크를 합니다.")
    async def 출첵(self, interaction: discord.Interaction):
        await send_tuna_checkin(interaction)

# 스팀
@tree.command(name="스팀정보", description="스팀 게임 정보를 조회합니다.")
@app_commands.describe(game_name="게임 이름")
async def slash_steam(interaction: discord.Interaction, game_name: str):
    await send_steam_game_info(interaction, game_name)

# 관리자 전용 명령어
ADMIN_USER_ID = int(os.getenv("DISCORD_ADMIN_ID"))

def is_admin(interaction: discord.Interaction):
    return interaction.user.id == ADMIN_USER_ID

@tree.command(name="롤토체스", description="관리자 전용 메타 카드 패치")
@app_commands.describe(subcommand="메타패치")
@app_commands.check(is_admin)
async def slash_meta_patch(interaction: discord.Interaction, subcommand: str):
    if subcommand in ["메타패치"]:
        await interaction.response.send_message("🔄 롤체 메타 정보를 수집 중입니다. 약 5분가량 소요됩니다.")

        loop = asyncio.get_running_loop()
        data = await loop.run_in_executor(None, crawl_tft_meta)
        await loop.run_in_executor(None, save_meta_json, data)
        await loop.run_in_executor(None, crawl_detail_info)
        await loop.run_in_executor(None, generate_all_meta_cards)

        await interaction.followup.send("✅ 롤체 메타 패치 완료! 최신 카드 이미지가 생성되었습니다.")
    else:
        await interaction.response.send_message("❓ 사용법: `/롤토체스 메타패치`")

# 그룹 등록
@client.event
async def setup_hook():
    tree.add_command(롤(name="롤"))
    tree.add_command(롤체(name="롤체"))
    tree.add_command(발로(name="발로"))
    tree.add_command(참치(name="참치"))
    await tree.sync()

client.run(TOKEN)
