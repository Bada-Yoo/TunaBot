# event1.py
import discord

# 프로젝트 공통 팔레트와 맞춤 (s1: #FFAEBC)
PINK = 0xFFAEBC

EVENT_TITLE = "🐟 참치봇 비밀 이벤트 발견!"
EVENT_DESC = (
    "참치봇을 사용해 주셔서 정말 감사합니다!\n"
    "여러분의 관심과 사랑 덕분에, 감사한 마음을 전하고자\n"
    "이런 이벤트를 준비하게 되었습니다.\n\n"
    "💡 **이벤트 안내**\n"
    "**기간:** 2025.08.12 ~ 2025.09.30\n"
    "**조건:** 최소 봇이 아닌 사람 **11명 이상** 있는 서버 *(서버당 한 분 참여 가능)*\n\n"
    "🛠 **참여 방법**\n"
    "1. 참치봇 서포트 페이지 들어오기\n"
    "2. **자신이 포함된 서버 인원**이 보이게 스크린샷 찍기\n"
    "3. 이벤트 페이지에 스샷을 첨부하고 **어떻게 알게 됐는지/ 봇 초대 이유** 적기\n\n"
    "🎁 추첨을 통해, DM을 보내주신 분들 중 **3분**에게 **🍗교촌치킨 기프티콘** 증정!"
)

def build_event1_embed() -> discord.Embed:
    embed = discord.Embed(
        title=EVENT_TITLE,
        description=EVENT_DESC,
        color=PINK
    )
    embed.set_footer(text="참치봇 v1.0.0 오픈 이벤트 🎉")
    return embed


async def send_event1_embed(
    interaction: discord.Interaction,
    *,
    ephemeral: bool = True,
    support_url: str | None = None,
    event_url: str | None = None,
):
    """
    /이벤트 명령어에서 호출하는 전송 함수.
    - ephemeral=True: 발견자에게만 보이도록 숨김 응답
    - support_url, event_url: 버튼으로 링크 노출 (옵션)
    """
    embed = build_event1_embed()

    view = None
    if support_url or event_url:
        view = discord.ui.View()
        if support_url:
            view.add_item(discord.ui.Button(label="서포트 페이지 열기", url=support_url, style=discord.ButtonStyle.link))
        if event_url:
            view.add_item(discord.ui.Button(label="이벤트 페이지 열기", url=event_url, style=discord.ButtonStyle.link))

    if interaction.response.is_done():
        await interaction.followup.send(embed=embed, ephemeral=ephemeral, view=view)
    else:
        await interaction.response.send_message(embed=embed, ephemeral=ephemeral, view=view)
