import os
import requests
import discord
from urllib.parse import quote
from dotenv import load_dotenv
import time

versions = requests.get("https://ddragon.leagueoflegends.com/api/versions.json").json()
latest_version = versions[0]

load_dotenv()
RIOT_API_KEY = os.getenv("RIOT_LOL_API_KEY")
HEADERS = {"X-Riot-Token": RIOT_API_KEY}

# 큐 ID → 게임 모드 이름 매핑
QUEUE_TYPES = {
    400: "일반",
    420: "솔로 랭크",
    430: "일반",
    440: "자유 랭크",
    450: "칼바람 나락",
    700: "격전",
    900: "우르프",
    1020: "단일 챔피언 모드",
    1700: "아레나",
}

def get_puuid_by_riot_id(game_name, tag_line):
    url = f"https://asia.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{quote(game_name)}/{quote(tag_line)}"
    res = requests.get(url, headers=HEADERS)
    if res.status_code == 200:
        return res.json().get("puuid")
    return None

def get_live_game_by_puuid(puuid):
    url = f"https://kr.api.riotgames.com/lol/spectator/v5/active-games/by-summoner/{puuid}"
    res = requests.get(url, headers=HEADERS)
    if res.status_code == 200 and res.text.strip():
        try:
            return res.json()
        except Exception as e:
            print("❌ 라이브 게임 파싱 실패:", e)
            return None
    return None

def load_champion_id_map():
    url = f"https://ddragon.leagueoflegends.com/cdn/{latest_version}/data/ko_KR/champion.json"
    res = requests.get(url)
    if res.status_code != 200:
        print("❌ 챔피언 목록 로딩 실패")
        return {}
    try:
        data = res.json()["data"]
    except Exception as e:
        print("❌ 파싱 실패:", e)
        return {}

    id_map = {}
    for champ in data.values():
        id_map[int(champ["key"])] = champ["name"]
    return id_map

CHAMPION_ID_MAP = load_champion_id_map()

def load_champion_eng_name_map():
    url = f"https://ddragon.leagueoflegends.com/cdn/{latest_version}/data/en_US/champion.json"
    res = requests.get(url)
    if res.status_code != 200:
        print("❌ 챔피언 영문 목록 로딩 실패")
        return {}
    try:
        data = res.json()["data"]
    except Exception as e:
        print("❌ 파싱 실패:", e)
        return {}

    id_map = {}
    for eng_name, champ in data.items():
        champ_id = int(champ["key"])
        id_map[champ_id] = eng_name
    return id_map

CHAMPION_ENG_NAME_MAP = load_champion_eng_name_map()

#롤 전적 함수
async def send_lol_live_status(ctx, riot_id):
    if "#" not in riot_id:
        await ctx.send("❗ Riot ID는 `닉네임#태그` 형식으로 입력해주세요.")
        return

    game_name, tag_line = riot_id.split("#")
    puuid = get_puuid_by_riot_id(game_name, tag_line)
    if not puuid:
        await ctx.send("🤔 Riot ID를 찾을 수 없습니다.")
        return

    live_game = get_live_game_by_puuid(puuid)
    if not live_game:
        await ctx.send(f"{game_name}#{tag_line}님은 현재 게임 중이 아닙니다.")
        return

    queue_id = live_game.get("gameQueueConfigId", -1)
    game_mode = QUEUE_TYPES.get(queue_id, f"알 수 없음 (큐 ID: {queue_id})")

    game_start = live_game.get("gameStartTime")
    now = int(time.time() * 1000)
    duration_ms = now - game_start
    duration_min = duration_ms // 60000
    duration_sec = (duration_ms % 60000) // 1000
    game_time_str = f"{duration_min}분 {duration_sec}초"

    champ_id = None
    for p in live_game["participants"]:
        if p["puuid"] == puuid:
            champ_id = p["championId"]
            break

    champ_eng = CHAMPION_ENG_NAME_MAP.get(champ_id)
    champ_name = CHAMPION_ID_MAP.get(champ_id, f"챔피언 ID {champ_id}")

    embed = discord.Embed(
        title=f"{game_name}#{tag_line}님's\n현재 게임 정보",
        description=(
            f"**🌊 게임 모드:** {game_mode}\n"
            f"**🌊 진행 시간:** {game_time_str}\n"
            f"**🌊 사용 챔피언:** {champ_name}"
        ),
        color=discord.Color.dark_blue()
    )
    embed.set_author(name="🐟TunaBot 라이브 정보")
    embed.set_footer(text="🐬 Powered by Riot API | tuna.gg")

    # 챔피언 썸네일 (영문 이름 기준)
    if champ_eng:
        img_url = f"https://ddragon.leagueoflegends.com/cdn/{latest_version}/img/champion/{champ_eng}.png"
        embed.set_thumbnail(url=img_url)

    await ctx.send(embed=embed)

# 상대정보 분석 함수
from collections import defaultdict

def get_summoner_by_puuid(puuid):
    url = f"https://kr.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/{puuid}"
    res = requests.get(url, headers=HEADERS)
    return res.json() if res.status_code == 200 else None

def get_rank_by_id(encrypted_id):
    url = f"https://kr.api.riotgames.com/lol/league/v4/entries/by-summoner/{encrypted_id}"
    res = requests.get(url, headers=HEADERS)
    if res.status_code != 200:
        return "Unranked"
    for entry in res.json():
        if entry["queueType"] in ["RANKED_SOLO_5x5", "RANKED_FLEX_SR"]:
            return f"{entry['tier'].title()} {entry['rank']}"
    return "Unranked"

def get_recent_match_ids(puuid, count=2):
    url = f"https://asia.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?count={count}"
    res = requests.get(url, headers=HEADERS)
    return res.json() if res.status_code == 200 else []

def get_match_detail(match_id):
    url = f"https://asia.api.riotgames.com/lol/match/v5/matches/{match_id}"
    res = requests.get(url, headers=HEADERS)
    return res.json() if res.status_code == 200 else None

def format_kda_line(me):
    champ_id = me.get("championId")
    champ_name = CHAMPION_ID_MAP.get(champ_id, me.get("championName", "알 수 없음"))
    k, d, a = me["kills"], me["deaths"], me["assists"]
    win = "승" if me["win"] else "패"
    return f"{champ_name} {k}/{d}/{a} ({win})"


async def send_lol_opponent_info(ctx, riot_id):
    if "#" not in riot_id:
        await ctx.send("❗ Riot ID는 `닉네임#태그` 형식으로 입력해주세요.")
        return

    game_name, tag_line = riot_id.split("#")
    url = f"https://asia.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{quote(game_name)}/{quote(tag_line)}"
    res = requests.get(url, headers=HEADERS)
    if res.status_code != 200:
        await ctx.send("❌ Riot ID를 찾을 수 없습니다.")
        return
    puuid = res.json().get("puuid")

    live_game = get_live_game_by_puuid(puuid)
    if not live_game:
        await ctx.send(f"{riot_id}님은 현재 게임 중이 아닙니다.")
        return

    queue_id = live_game.get("gameQueueConfigId")
    queue_name = QUEUE_TYPES.get(queue_id)
    if queue_id not in [420, 440]:
        await ctx.send(f"🎮 현재 게임 모드({queue_name})는 상대 분석을 지원하지 않습니다.")
        return

    my_team = None
    for p in live_game["participants"]:
        if p["puuid"] == puuid:
            my_team = p["teamId"]
            break

    if my_team is None:
        await ctx.send("❌ 참가자 팀 정보를 찾을 수 없습니다.")
        return

    enemies = [p for p in live_game["participants"] if p["teamId"] != my_team]

    embed = discord.Embed(
        title=f"{game_name}#{tag_line}님's 현재 상대",
        description="",
        color=discord.Color.dark_blue()
    )
    embed.set_author(name="🐟TunaBot 상대 정보")
    embed.set_footer(text="🐬 Powered by Riot API | tuna.gg")

    for i, enemy in enumerate(enemies, start=1):
        riot_name = enemy.get("riotId") or enemy.get("summonerName")
        enemy_puuid = enemy["puuid"]
        enemy_summoner = get_summoner_by_puuid(enemy_puuid)
        encrypted_id = enemy_summoner.get("id") if enemy_summoner else None
        rank = get_rank_by_id(encrypted_id) if encrypted_id else "Unranked"

        match_ids = get_recent_match_ids(enemy_puuid, count=2)
        kda_lines = []
        for match_id in match_ids:
            detail = get_match_detail(match_id)
            if not detail:
                continue
            participants = detail["info"]["participants"]
            me = next((p for p in participants if p["puuid"] == enemy_puuid), None)
            if me:
                kda_lines.append(format_kda_line(me))

        champ_id = enemy.get("championId")
        champ_name = CHAMPION_ID_MAP.get(champ_id, f"챔피언 ID {champ_id}")

        body = f"🌊 **{riot_name}** ({rank})\n지금 챔피언: {champ_name}"
        if kda_lines:
            body += f"\n최근 2판: {', '.join(kda_lines)}"
        embed.add_field(name="\u200b", value=body, inline=False)

    await ctx.send(embed=embed)
