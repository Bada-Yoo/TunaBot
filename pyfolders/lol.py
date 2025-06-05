import os
import requests
import discord
from urllib.parse import quote
from dotenv import load_dotenv
from collections import Counter, defaultdict
from riot_util import lol_safe_get

# 최신 버전으로
versions = requests.get("https://ddragon.leagueoflegends.com/api/versions.json").json()
latest_version = versions[0]

load_dotenv()
RIOT_API_KEY = os.getenv("RIOT_LOL_API_KEY")
HEADERS = {"X-Riot-Token": RIOT_API_KEY}

QUEUE_TYPES = {
    420: "솔로 랭크",
    430: "일반 게임",
    440: "자유랭크",
    450: "칼바람 나락",
    700: "격전",
    900: "우르프",
    1700: "아레나",
    1710: "아레나"
}

def get_puuid_by_riot_id(game_name, tag_line):
    url = f"https://asia.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{quote(game_name)}/{quote(tag_line)}"
    response, retry_after = lol_safe_get(url)
    if response is None:
        return None, retry_after
    if response.status_code == 404:
        return {}, retry_after
    return response.json(), retry_after

def get_summoner_by_puuid(puuid):
    url = f"https://kr.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/{puuid}"
    return requests.get(url, headers=HEADERS).json()

def get_rank_data(encrypted_summoner_id):
    url = f"https://kr.api.riotgames.com/lol/league/v4/entries/by-summoner/{encrypted_summoner_id}"
    return requests.get(url, headers=HEADERS).json()

def get_match_ids(puuid, count=10):
    url = f"https://asia.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?start=0&count={count}"
    return requests.get(url, headers=HEADERS).json()

def get_match_detail(match_id):
    url = f"https://asia.api.riotgames.com/lol/match/v5/matches/{match_id}"
    return requests.get(url, headers=HEADERS).json()

async def send_lol_stats(interaction, riot_id):
    try:
        if "#" not in riot_id:
            await interaction.response.send_message("❗ Riot ID는 `닉네임#태그` 형식으로 입력해주세요.", ephemeral=True)
            return

        await interaction.response.defer()

        game_name, tag_line = riot_id.split("#")
        account, retry_after = get_puuid_by_riot_id(game_name, tag_line)

        if account is None:
            retry_text = f"{retry_after}초 후 다시 시도해주세요." if retry_after else "잠시 후 다시 시도해주세요."
            await interaction.followup.send(embed=discord.Embed(
                title="🚫 요청 실패",
                description=f"Riot API 요청량이 많습니다.\n{retry_text}",
                color=discord.Color.red()
            ))
            return

        if "puuid" not in account:
            await interaction.followup.send("🤔 Riot ID를 찾을 수 없습니다.")
            return

        puuid = account["puuid"]
        summoner = get_summoner_by_puuid(puuid)
        encrypted_id = summoner["id"]
        level = summoner["summonerLevel"]
        profile_icon_id = summoner["profileIconId"]
        icon_url = f"http://ddragon.leagueoflegends.com/cdn/{latest_version}/img/profileicon/{profile_icon_id}.png"

        rank_data = get_rank_data(encrypted_id)
        solo = next((r for r in rank_data if r["queueType"] == "RANKED_SOLO_5x5"), None)
        rank_info = solo["tier"] + " " + solo["rank"] if solo else "Unranked"

        match_ids = get_match_ids(puuid, count=10)

        champion_pool = []
        queue_counter = defaultdict(list)
        recent_games_text = ""

        for i, match_id in enumerate(match_ids):
            match = get_match_detail(match_id)

            if "info" not in match:
                print(f"❗ 'info' 누락된 match: {match_id}")
                continue

            queue_id = match["info"].get("queueId", -1)
            me = next(p for p in match["info"]["participants"] if p["puuid"] == puuid)

            champ = me["championName"]
            k, d, a = me["kills"], me["deaths"], me["assists"]
            win = me["win"]
            champion_pool.append(champ)

            queue_counter[queue_id].append(win)

            if i < 5:
                queue_name = QUEUE_TYPES.get(queue_id, "이벤트 모드")
                result = "🏆 승" if win else "💀 패"
                recent_games_text += f"{champ} | {k}/{d}/{a} | {result} | {queue_name}\n"

        most_common = Counter(champion_pool).most_common(3)
        most_used = ", ".join([c for c, _ in most_common]) if most_common else "정보 없음"

        queue_lines = []
        for qid, games in queue_counter.items():
            name = QUEUE_TYPES.get(qid, "이벤트 모드")
            if games:
                total = len(games)
                wins = sum(games)
                winrate = round(wins / total * 100, 1)
                queue_lines.append(f"{name}: {total}판 ({winrate}%)")
        queue_summary_text = " | ".join(queue_lines) if queue_lines else "분석된 경기 없음"

        embed = discord.Embed(
            title=f"{game_name}#{tag_line}님의 롤 전적",
            description=(
                f"레벨: {level} | 현 시즌 랭크: {rank_info}\n\n"
                f"**🌊 최근 5경기 (KDA & 결과)**\n"
                f"{recent_games_text}\n"
                f"**🌊 최근 10경기 (판수 & 승률)**\n"
                f"모스트 챔피언: {most_used}\n"
                f"{queue_summary_text}"
            ),
            color=discord.Color.dark_blue()
        )
        embed.set_author(name="🐟TunaBot 전적 정보")
        embed.set_thumbnail(url=icon_url)
        embed.set_footer(text="🐬 Powered by Riot API | tuna.gg")

        await interaction.followup.send(embed=embed)

    except Exception as e:
        await interaction.followup.send(f"❌ 오류 발생: {str(e)}")
