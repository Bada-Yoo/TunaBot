
import os
from dotenv import load_dotenv
import discord
import asyncio
from discord import app_commands

from anonymous import send_anonymous_channel, send_anonymous_dm, handle_anonymous_reply

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

from tft_update_meta import crawl_tft_meta, save_meta_json
from tft_update_metadetail import crawl_detail_info
from tft_generate_meta_card import generate_all_meta_cards

from event0 import EVENT_TITLE, EVENT_TEXT
import datetime
from debug import log_reaction_simple, handle_raw_reaction_add

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
ADMIN_USER_ID = int(os.getenv("DISCORD_ADMIN_ID"))

intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True
intents.messages = True
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

@client.event
async def on_ready():
    await tree.sync()
    await client.change_presence(
        activity=discord.Game(name="🎣TunaBot| 궁금할땐 /도움말")
    )
    print(f"✅ 봇 로그인 완료: {client.user}")


def extract_options(options):
    if not isinstance(options, list):
        return ""
    extracted = []
    for opt in options:
        name = opt.get("name")
        value = opt.get("value")
        if value is None and "options" in opt:
            nested = extract_options(opt["options"])
            extracted.append(f"{name} {nested}".strip())
        elif name and value is not None:
            extracted.append(f"{name}={value}")
    return " ".join(extracted)

@client.event
async def on_interaction(interaction: discord.Interaction):
    if interaction.type == discord.InteractionType.application_command:
        try:
            admin = await client.fetch_user(ADMIN_USER_ID)
            user = interaction.user
            command_name = interaction.command.name if interaction.command else "Unknown"
            group_name = interaction.command.parent.name if interaction.command and interaction.command.parent else None
            options = interaction.data.get("options", [])
            args_text = extract_options(options)
            full_command = f"/{group_name + ' ' if group_name else ''}{command_name} {args_text}".strip()
            await admin.send(f"🐳 {user} ({user.id})\n{full_command}")
        except Exception as e:
            print(f"⚠️ 관리자 DM 전송 실패: {e}")

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
    @app_commands.describe(type="전체 | 번호 | 유닛 이름")
    async def 메타(self, interaction: discord.Interaction, type: str):
        await send_tft_meta(interaction, type)

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

# 익명 명령어 그룹
class 익명(app_commands.Group):
    @app_commands.command(name="채널", description="현재 채널에 익명 메시지를 보냅니다.")
    @app_commands.describe(message="보낼 메시지 내용")
    async def 채널(self, interaction: discord.Interaction, message: str):
        await send_anonymous_channel(interaction, message)

    @app_commands.command(name="갠디", description="특정 유저에게 익명 DM을 보냅니다.")
    @app_commands.describe(
        target="서버 내 유저 선택",
        message="보낼 메시지 내용"
    )
    async def 갠디(
        self,
        interaction: discord.Interaction,
        target: discord.User,
        message: str
    ):
        await send_anonymous_dm(interaction, target, message)

    @app_commands.command(name="답장", description="받은 익명 DM에 답장합니다.")
    @app_commands.describe(
        token="익명 DM에 포함된 토큰",
        message="답장할 내용"
    )
    async def 답장(
        self,
        interaction: discord.Interaction,
        token: str,
        message: str
    ):
        await handle_anonymous_reply(interaction, token, message)

    @app_commands.command(name="개발자", description="개발자에게 익명 건의사항을 보냅니다.")
    @app_commands.describe(
        message="보낼 메시지 내용"
    )
    async def 개발자(self, interaction: discord.Interaction, message: str):
        try:
            admin = await interaction.client.fetch_user(ADMIN_USER_ID)
            await send_anonymous_dm(interaction, admin, message)
        except Exception as e:
            await interaction.response.send_message("⚠️ 전송 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요.", ephemeral=True)
            print(f"익명 개발자 DM 오류: {e}")



# 반응 이모지 이벤트
@client.event
async def on_raw_reaction_add(payload: discord.RawReactionActionEvent):
    # 필요하면 발로란트 새로고침 콜백 연결
    await handle_raw_reaction_add(client, payload, refresh_cb=handle_valorant_refresh)



# 스팀 명령어
@tree.command(name="스팀정보", description="스팀 게임 정보를 조회합니다.")
@app_commands.describe(game_name="게임 이름(영문)")
async def slash_steam(interaction: discord.Interaction, game_name: str):
    await send_steam_game_info(interaction, game_name)

# 관리자 전용 명령어
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

@tree.command(name="도움말", description="참치봇의 전체 기능을 안내합니다.")
async def slash_help(interaction: discord.Interaction):
    help_text = """
**🎣 참치봇**  
게임 전적부터 무기 추천, 스팀 검색, 익명 메시지까지!  
게이머를 위한 디스코드 올인원 유틸리티 봇입니다.

---

**✏️ 소개**  
**참치봇**은 LoL, TFT, VALORANT, Steam 기반의 전적/정보 조회 기능과  
익명 메시지 시스템을 제공하는 다기능 디스코드 봇입니다.

---

**🛠️ 기능 명령어 안내**

**🐬 League of Legends (롤)**  
`/롤 전적 소환사명` – 소환사 전적을 확인합니다.  
`/롤 관전 소환사명` – 라이브 게임 상태를 확인합니다.  
`/롤 상대정보 소환사명` – 상대팀 정보를 확인합니다.  
`/롤 패치` – 최신 패치노트를 확인합니다.

**🐬 Teamfight Tactics (롤토체스)**  
`/롤체 전적 소환사명` – TFT 전적을 확인합니다.  
`/롤체 관전 소환사명` – TFT 라이브 게임 상태를 확인합니다.  
`/롤체 메타 전체|숫자|챔피언이름` – 메타 티어표를 확인합니다.  
예: `/롤체 메타 전체`, `/롤체 메타 3`, `/롤체 메타 모르가나`  
`/롤체 패치` – TFT 패치노트를 확인합니다.

**🐳 VALORANT**  
`/발로 권총` – 권총을 랜덤으로 추천합니다.  
`/발로 랜덤` – 무기를 랜덤으로 추천합니다.  
`/발로 주무기` – 주무기를 랜덤으로 추천합니다.  
`/발로 로테` – 경쟁전 맵 로테이션을 확인합니다.  
`/발로 패치` – 발로란트 패치노트를 확인합니다.

**🦈 Steam**  
`/스팀정보 게임이름` – 입력한 게임의 스팀 정보를 조회합니다.  
(※ 게임 이름은 **영문**으로 입력해주세요.)

**🪸 익명 메시지**  
`/익명 채널 메시지` – 현재 채널에 익명 메시지를 보냅니다.  
`/익명 갠디 유저 메시지` – 특정 유저에게 익명 DM을 보냅니다.  
`/익명 답장 토큰 메세지` – 받은 익명 DM에 답장합니다.
`/익명 개발자 메세지` – 개발자에게 문의사항이나 하고싶은 익명 메세지를 보냅니다.(답장이 올지도?)

**🎣 참치**  
`/참치 서버` – 현재 참치봇의 서버와 유저수를 알 수 있습니다.  

---

> 🤝 새로운 기능 아이디어가 있다면 언제든지 제안해주세요!  
> 📎 **참치봇 초대하기**: https://discord.com/oauth2/authorize?client_id=1372049356659626104&scope=bot&permissions=337984
"""
    await interaction.response.send_message(help_text, ephemeral=True)

@tree.command(name="서버", description="봇이 들어가 있는 서버 목록과 인원수를 확인합니다.")
@app_commands.check(is_admin)
async def slash_server_info(interaction: discord.Interaction):
    guilds = sorted(
    interaction.client.guilds,
    key=lambda g: g.me.joined_at or datetime.datetime.min
)

    if not guilds:
        await interaction.response.send_message("🤖 봇이 현재 어떤 서버에도 들어가 있지 않습니다.", ephemeral=True)
        return

    chunk_size = 25
    for i in range(0, len(guilds), chunk_size):
        chunk = guilds[i:i + chunk_size]
        embed = discord.Embed(
            title=f"📂 현재 접속 중인 서버 목록 ({i + 1}~{i + len(chunk)} / {len(guilds)})",
            color=discord.Color.blurple()
        )

        for g in chunk:
            owner = g.owner
            owner_text = (
                f"`{g.owner_id}`" if not g.owner
                else f"{g.owner.name}#{g.owner.discriminator} (`{g.owner.id}`)"
            )
            joined_at = g.me.joined_at.strftime("%Y-%m-%d %H:%M") if g.me.joined_at else "알 수 없음"
            embed.add_field(
                name=g.name,
                value=(
                    f"👥 **{g.member_count}명**\n"
                    f"👑 {owner_text}\n"
                    f"⏱ {joined_at}"
                ),
                inline=False
            )

        if i == 0:
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            await interaction.followup.send(embed=embed, ephemeral=True)




@tree.command(
    name="이벤트",
    description="현재 이벤트"
)
async def slash_event(interaction: discord.Interaction):
    embed = discord.Embed(
        title=EVENT_TITLE,
        description=EVENT_TEXT,
        color=discord.Color.pink()
    )
    embed.set_footer(text="참치봇 이벤트 🎉")

    await interaction.response.send_message(embed=embed, ephemeral=True)

class 참치(app_commands.Group):
    @app_commands.command(name="서버", description="참치봇이 들어간 서버 수와 총 유저 수를 확인합니다.")
    async def 서버(self, interaction: discord.Interaction):
        guilds = interaction.client.guilds
        total_servers = len(guilds)
        total_members = sum(g.member_count for g in guilds)

        embed = discord.Embed(
            description=(
                f"• 서버 수: **{total_servers}개**\n"
                f"• 총 유저 수: **{total_members:,}명**"
            ),
            color=discord.Color.pink()
        )
        embed.set_author(name="🐟 TunaBot 서버 정보")
        embed.set_footer(text="🎣 TunaBot Server | tuna.gg")

        await interaction.response.send_message(embed=embed, ephemeral=False)



# 그룹 등록
@client.event
async def setup_hook():
    tree.add_command(롤(name="롤"))
    tree.add_command(롤체(name="롤체"))
    tree.add_command(발로(name="발로"))
    tree.add_command(익명(name="익명")) 
    tree.add_command(참치(name="참치"))
    await tree.sync()

client.run(TOKEN)

# 🔒 참치 관련 기능 임시 비활성화
# from tunaregister import send_tuna_register, send_tuna_unregister
# from tunapointcheck import send_tuna_point
# from tunacheckin import send_tuna_checkin


# 🔒 참치 명령어 그룹 (비활성화)
# class 참치(app_commands.Group):
#     @app_commands.command(name="등록", description="참치봇에 등록합니다.")
#     async def 등록(self, interaction: discord.Interaction):
#         await send_tuna_register(interaction)

#     @app_commands.command(name="삭제", description="참치봇에서 탈퇴합니다.")
#     async def 삭제(self, interaction: discord.Interaction):
#         await send_tuna_unregister(interaction)

#     @app_commands.command(name="포인트", description="포인트를 조회합니다.")
#     async def 포인트(self, interaction: discord.Interaction):
#         await send_tuna_point(interaction)

#     @app_commands.command(name="출첵", description="출석체크를 합니다.")
#     async def 출첵(self, interaction: discord.Interaction):
#         await send_tuna_checkin(interaction)

