import os
import requests
import discord
from urllib.parse import quote
from dotenv import load_dotenv
import datetime

load_dotenv()
RIOT_API_KEY = os.getenv("RIOT_API_KEY")
HEADERS = {"X-Riot-Token": RIOT_API_KEY}

# 큐 Id → TFT 모드 이름 매핑
QUEUE_TYPES_TFT = {
    1090: "롤토체스 일반",
    1100: "롤토체스 랭크",
    1210: "배불뚝이 보물 모드"
}

def get_puuid(game_name, tag_line):
    url = f"https://asia.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{quote(game_name)}/{quote(tag_line)}"
    res = requests.get(url, headers=HEADERS)
    if res.status_code == 200:
        return res.json().get("puuid")
    
    return None

def get_tft_live_game_by_puuid(puuid):
    url = f"https://kr.api.riotgames.com/lol/spectator/tft/v5/active-games/by-puuid/{puuid}"
    res = requests.get(url, headers=HEADERS)
    if res.status_code == 200:
        return res.json()
    elif res.status_code == 404:
        return None
    print("❌ 라이브 게임 요청 실패:", res.status_code, res.text)
    return None

async def send_tft_live_status(ctx, riot_id):
    if "#" not in riot_id:
        await ctx.send("❗ Riot ID는 `닉네임#태그` 형식으로 입력해주세요.")
        return

    game_name, tag_line = riot_id.split("#")
    riot_id_display = f"{game_name}#{tag_line}"

    puuid = get_puuid(game_name, tag_line)
    if not puuid:
        await ctx.send("🤔 Riot ID를 찾을 수 없습니다.")
        return

    live_game = get_tft_live_game_by_puuid(puuid)
    if not live_game:
        await ctx.send(f"{riot_id_display}님은 현재 게임 중이 아닙니다.")
        return

    queue_id = live_game.get("gameQueueConfigId", -1)
    game_mode = QUEUE_TYPES_TFT.get(queue_id, "이벤트 게임")

    # 시작 시간 & 경과 시간 계산
    game_start = live_game.get("gameStartTime", 0)
    start_dt = datetime.datetime.fromtimestamp(game_start / 1000)
    start_str = start_dt.strftime("%Y-%m-%d %H:%M:%S")

    game_length = live_game.get("gameLength", 0)
    minutes, seconds = divmod(game_length, 60)
    duration_str = f"{minutes}분 {seconds}초"

    # 썸네일: 참가자 중 내가 누구인지 찾고 프로필 아이콘 사용
    participants = live_game.get("participants", [])
    player = next((p for p in participants if p["puuid"] == puuid), None)
    icon_url = None
    if player and "profileIconId" in player:
        icon_id = player["profileIconId"]
        icon_url = f"http://ddragon.leagueoflegends.com/cdn/14.10.1/img/profileicon/{icon_id}.png"

    # Embed 생성
    embed = discord.Embed(
        title=f"{riot_id_display}님's\n현재 게임 정보",
        description=(
            f"**🌊 게임 모드:** {game_mode}\n"
            f"**🌊 시작 시간:** {start_str}\n"
            f"**🌊 진행 시간:** {duration_str}"
        ),
        color=discord.Color.teal()
    )
    embed.set_author(name="🐟TunaBot 롤토체스 라이브 정보")
    if icon_url:
        embed.set_thumbnail(url=icon_url)
    embed.set_footer(text="🐬 Powered by Riot API | tuna.gg")

    await ctx.send(embed=embed)
