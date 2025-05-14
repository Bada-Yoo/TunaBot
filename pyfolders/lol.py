import discord
import requests
import os
from dotenv import load_dotenv
import urllib.parse #깨질까봐

load_dotenv()
RIOT_API_KEY = os.getenv("RIOT_API_KEY")
HEADERS = {"X-Riot-Token": RIOT_API_KEY}

# 큐 이름 매핑
QUEUE_TYPES = {
    420: "솔로랭크",
    430: "일반 게임",
    440: "자유랭크",
    450: "칼바람 나락",
    900: "URF",
    700: "격전",
    1700: "아레나"
}

# Riot API 요청 함수들
def get_summoner_data(summoner_name):
    encoded_name = urllib.parse.quote(summoner_name)
    url = f"https://kr.api.riotgames.com/lol/summoner/v4/summoners/by-name/{encoded_name}"
    res = requests.get(url, headers=HEADERS)

    print("🔍 요청 URL:", url)
    print("🔍 응답 코드:", res.status_code)
    print("🔍 응답 내용:", res.text)

    return res.json()

def get_rank_data(encrypted_summoner_id):
    url = f"https://kr.api.riotgames.com/lol/league/v4/entries/by-summoner/{encrypted_summoner_id}"
    return requests.get(url, headers=HEADERS).json()

def get_match_ids(puuid, count=5):
    url = f"https://asia.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?start=0&count={count}"
    return requests.get(url, headers=HEADERS).json()

def get_match_detail(match_id):
    url = f"https://asia.api.riotgames.com/lol/match/v5/matches/{match_id}"
    return requests.get(url, headers=HEADERS).json()

# 디스코드 메시지 함수
async def send_lol_stats(ctx, summoner_name):
    summoner = get_summoner_data(summoner_name)
    if "id" not in summoner:
        await ctx.send("❌ 소환사를 찾을 수 없습니다.")
        return

    profile_icon_id = summoner["profileIconId"]
    level = summoner["summonerLevel"]
    icon_url = f"http://ddragon.leagueoflegends.com/cdn/14.10.1/img/profileicon/{profile_icon_id}.png"

    rank_data = get_rank_data(summoner["id"])
    solo = next((r for r in rank_data if r["queueType"] == "RANKED_SOLO_5x5"), None)

    if solo:
        tier = solo["tier"]
        rank = solo["rank"]
        wins = solo["wins"]
        losses = solo["losses"]
        total = wins + losses
        winrate = round(wins / total * 100, 1)
        rank_info = f"{tier} {rank} / {wins}승 {losses}패 / 승률 {winrate}%"
    else:
        rank_info = "솔로랭크 정보 없음"

    match_ids = get_match_ids(summoner["puuid"], count=5)
    match_lines = []
    for i, mid in enumerate(match_ids):
        match = get_match_detail(mid)
        me = next(p for p in match["info"]["participants"] if p["puuid"] == summoner["puuid"])
        champ = me["championName"]
        k, d, a = me["kills"], me["deaths"], me["assists"]
        win = "승" if me["win"] else "패"
        queue = QUEUE_TYPES.get(match["info"].get("queueId", -1), "기타")
        match_lines.append(f"{i+1}. {champ} / {k}/{d}/{a} / {win} / {queue}")

    embed = discord.Embed(
        title=f"{summoner_name} 님의 롤 전적",
        description=f"📊 레벨: {level}\n🏆 {rank_info}",
        color=discord.Color.blue()
    )
    embed.set_thumbnail(url=icon_url)
    embed.add_field(name="최근 5경기", value="\n".join(match_lines), inline=False)

    await ctx.send(embed=embed)
