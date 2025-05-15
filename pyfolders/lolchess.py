import os
import requests
import discord
from urllib.parse import quote
from dotenv import load_dotenv
from collections import Counter

load_dotenv()
RIOT_API_KEY = os.getenv("RIOT_API_KEY")
HEADERS = {"X-Riot-Token": RIOT_API_KEY}

# 한글 번역 JSON 불러오기
CD_URL = "https://raw.communitydragon.org/latest/cdragon/tft/ko_kr.json"
data = requests.get(CD_URL).json()

CHAMPION_MAP = {}
TRAIT_MAP = {}
AUGMENT_MAP = {}

# 유닛/시너지 매핑: setData 내부
for set_entry in data.get("setData", []):
    for category in ["champions", "traits"]:
        for entry in set_entry.get(category, []):
            if not isinstance(entry, dict):
                continue
            api_name = entry.get("apiName")
            name = entry.get("name")
            if api_name and name:
                if category == "champions":
                    CHAMPION_MAP[api_name] = name
                elif category == "traits":
                    TRAIT_MAP[api_name] = name

# 증강 매핑: items에서
for entry in data.get("items", []):
    api_name = entry.get("apiName")
    name = entry.get("name")
    if api_name and name and "Augment" in api_name:
        AUGMENT_MAP[api_name] = name

def translate_unit(name):
    return CHAMPION_MAP.get(name, name)

def translate_synergy(name):
    return TRAIT_MAP.get(name, name)

def translate_augment(name):
    return AUGMENT_MAP.get(name, name)

def get_puuid_by_riot_id(game_name, tag_line):
    url = f"https://asia.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{quote(game_name)}/{quote(tag_line)}"
    return requests.get(url, headers=HEADERS).json()

def get_tft_summoner_by_puuid(puuid):
    url = f"https://kr.api.riotgames.com/tft/summoner/v1/summoners/by-puuid/{puuid}"
    return requests.get(url, headers=HEADERS).json()

def get_tft_rank_by_id(encrypted_id):
    url = f"https://kr.api.riotgames.com/tft/league/v1/entries/by-summoner/{encrypted_id}"
    return requests.get(url, headers=HEADERS).json()

def get_tft_match_ids(puuid, count=10):
    url = f"https://asia.api.riotgames.com/tft/match/v1/matches/by-puuid/{puuid}/ids?count={count}"
    return requests.get(url, headers=HEADERS).json()

def get_tft_match_detail(match_id):
    url = f"https://asia.api.riotgames.com/tft/match/v1/matches/{match_id}"
    return requests.get(url, headers=HEADERS).json()

async def send_tft_stats(ctx, riot_id):
    if "#" not in riot_id:
        await ctx.send("❗ Riot ID는 `닉네임#태그` 형식으로 입력해주세요.")
        return

    game_name, tag_line = riot_id.split("#")
    account = get_puuid_by_riot_id(game_name, tag_line)
    if "puuid" not in account:
        await ctx.send("❌ Riot ID를 찾을 수 없습니다.")
        return

    puuid = account["puuid"]
    summoner = get_tft_summoner_by_puuid(puuid)
    icon_url = f"http://ddragon.leagueoflegends.com/cdn/14.10.1/img/profileicon/{summoner['profileIconId']}"
    encrypted_id = summoner.get("id")

    rank_data = get_tft_rank_by_id(encrypted_id)
    solo = next((r for r in rank_data if r["queueType"] == "RANKED_TFT"), None)
    duo = next((r for r in rank_data if r["queueType"] == "RANKED_TFT_DOUBLE_UP"), None)

    def format_rank(r):
        return f'{r["tier"]} {r["rank"]} ({r["wins"] + r["losses"]}판)' if r else "Unranked"

    solo_rank = format_rank(solo)
    duo_rank = format_rank(duo)

    match_ids = get_tft_match_ids(puuid, count=10)
    total_level = 0
    top4_count = 0
    unit_counter = Counter()
    recent5_text = ""

    for match_id in match_ids[:5]:
        match = get_tft_match_detail(match_id)
        info = match["info"]
        me = next(p for p in info["participants"] if p["puuid"] == puuid)

        place = me["placement"]
        level_final = me["level"]
        total_level += level_final
        if place <= 4:
            top4_count += 1

        units = [u["character_id"] for u in me["units"]]
        unit_counter.update(units)

        traits = [t for t in me["traits"] if t["tier_current"] > 0]
        traits.sort(key=lambda x: x["tier_current"] * x["num_units"], reverse=True)
        top_traits = [translate_synergy(t["name"]) for t in traits[:3]]

        augments = me.get("augments", [])
        augments_text = ", ".join([translate_augment(a) for a in augments]) if augments else "정보 없음"

        three_star_units = [translate_unit(u["character_id"]) for u in me["units"] if u.get("tier") == 3]
        stars_text = ", ".join(three_star_units) if three_star_units else "없음"

        recent5_text += (
            f"{place}위 | Lv{level_final} | 시너지: {', '.join(top_traits)}\n"
            f"       증강: {augments_text}\n"
            f"       3성 유닛: {stars_text}\n"
        )

    avg_level = round(total_level / len(match_ids), 2)
    top4_rate = round((top4_count / len(match_ids)) * 100, 1)
    most_units = ", ".join([translate_unit(u) for u, _ in unit_counter.most_common(3)])

    embed = discord.Embed(
        title=f"{game_name}#{tag_line}님의 롤토체스 전적",
        description=(
            f"🌊 **현 시즌 랭크**\n"
            f"솔로 랭크: {solo_rank} | 더블업: {duo_rank}\n\n"
            f"🌊 **최근 10경기**\n"
            f"평균 최종 레벨: {avg_level}\n"
            f"Top 4 비율: {top4_rate}%\n"
            f"모스트 유닛: {most_units}\n\n"
            f"🌊 **최근 5경기**\n{recent5_text}"
        ),
        color=discord.Color.teal()
    )
    embed.set_author(name="🐟TunaBot TFT 정보", icon_url=icon_url)
    embed.set_footer(text="🐬 Powered by Riot API | tuna.gg")

    await ctx.send(embed=embed)