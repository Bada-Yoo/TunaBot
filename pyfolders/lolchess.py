import os
import requests
import discord
from urllib.parse import quote
from dotenv import load_dotenv
from collections import Counter

load_dotenv()
RIOT_API_KEY = os.getenv("RIOT_API_KEY")
HEADERS = {"X-Riot-Token": RIOT_API_KEY}

#해당 url에서 롤체 영문이름과 한글이름 매핑을 가져옵니다.
CD_URL = "https://raw.communitydragon.org/latest/cdragon/tft/ko_kr.json"
data = requests.get(CD_URL).json()

CHAMPION_MAP = {}
TRAIT_MAP = {}
AUGMENT_MAP = {}

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

def translate_unit(name):
    return CHAMPION_MAP.get(name, name)

def translate_synergy(name):
    return TRAIT_MAP.get(name, name)

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

# 최근 10판중 최다 사용한 꼬마전설이 아이콘가져오기.. 이번 명령어중 제일 힘들었다.
# 캐릭터 이름이랑 skin id를 가져와야하는데, 캐릭터 이름은 json에서 찾을 수 있지만 skin id는 아무리 찾아도 없었는데, 다른 하위폴더 파일에 연결고리를 찾아서가지고 오게 되었다.
# 아니 가령 뿔보포로면 뿔보포로로 하지 왜 포로랑 번호로 나누어서서 이중삼중으로 찾게 만들어.. 눈 뽀개지는줄 알았다.
def get_companion_icon_url(species: str, skin_id: int):
    json_url = f"https://raw.communitydragon.org/latest/game/data/characters/{species.lower()}/skins/skin{skin_id}.bin.json"
    res = requests.get(json_url)
    if res.status_code != 200:
        return None
    data = res.json()
    if not data:
        return None
    skin_data = next(iter(data.values()))
    icon_path = skin_data.get("iconCircle")
    if not icon_path:
        return None
    icon_url = "https://raw.communitydragon.org/latest/" + icon_path.lower().replace("assets/", "game/assets/").replace(".tex", ".png")
    return icon_url

async def send_tft_stats(ctx, riot_id):
    if "#" not in riot_id:
        await ctx.send("❗ Riot ID는 `닉네임#태그` 형식으로 입력해주세요.")
        return

    game_name, tag_line = riot_id.split("#")
    account = get_puuid_by_riot_id(game_name, tag_line)
    if "puuid" not in account:
        await ctx.send("🤔 Riot ID를 찾을 수 없습니다.")
        return

    puuid = account["puuid"]
    summoner = get_tft_summoner_by_puuid(puuid)
    encrypted_id = summoner.get("id")

    rank_data = get_tft_rank_by_id(encrypted_id)
    solo = next((r for r in rank_data if r["queueType"] == "RANKED_TFT"), None)
    duo = next((r for r in rank_data if r["queueType"] == "RANKED_TFT_DOUBLE_UP"), None)

    #총 판수는 없지만 이기고 진 횟수가 있어서 합계로 총 겜수 적었다.
    def format_rank(r):
        return f'{r["tier"]} {r["rank"]} ({r["wins"] + r["losses"]}판)' if r else "Unranked"

    solo_rank = format_rank(solo)
    duo_rank = format_rank(duo)

    match_ids = get_tft_match_ids(puuid, count=10)
    total_level = 0
    top4_count = 0
    unit_counter = Counter()
    companion_counter = Counter()
    recent5_text = ""

    #각 판당 레벨과 순위, 사용한 유닛과 시너지를 가져온다.
    #최근 5판만 가져온다.
    for match_id in match_ids[:5]:
        match = get_tft_match_detail(match_id)
        info = match["info"]
        me = next(p for p in info["participants"] if p["puuid"] == puuid)

        place = me["placement"]
        level_final = me["level"]
        total_level += level_final
        if place <= 4:
            top4_count += 1

        units = me["units"]
        unit_counter.update([u["character_id"] for u in units])

        units_sorted = sorted(units, key=lambda x: -x.get("rarity", 0))
        top_units = [translate_unit(u["character_id"]) for u in units_sorted[:5]]
        used_units_text = ", ".join(top_units) + ("..." if len(units_sorted) > 5 else "")

        traits = [t for t in me["traits"] if t["tier_current"] > 0]
        traits.sort(key=lambda x: x["tier_current"] * x["num_units"], reverse=True)
        top_traits = [translate_synergy(t["name"]) for t in traits[:3]]

        recent5_text += (
            f"**{place}위**  |  Lv{level_final}  |  시너지: {', '.join(top_traits)}\n"
            f"사용 유닛: {used_units_text}\n"
        )

        companion = me.get("companion")
        if companion:
            key = (companion.get("species"), companion.get("skin_ID"))
            companion_counter[key] += 1

    avg_level = round(total_level / len(match_ids), 2)
    top4_rate = round((top4_count / len(match_ids)) * 100, 1)
    most_units = ", ".join([translate_unit(u) for u, _ in unit_counter.most_common(3)])

    embed = discord.Embed(
        title=f"{game_name}#{tag_line}님's\n롤토체스 전적",
        description=(
            f"**🌊 현 시즌 랭크**\n"
            f"솔로 랭크: {solo_rank} \n더블업: {duo_rank}\n\n"
            f"**🌊 최근 10경기**\n"
            f"평균 최종 레벨: {avg_level}\n"
            f"Top 4 비율: {top4_rate}%\n"
            f"모스트 유닛: {most_units}\n\n"
            f"**🌊 최근 5경기**\n{recent5_text}"
        ),
        color=discord.Color.dark_blue()
    )
    embed.set_author(name="🐟TunaBot 전적 정보")
    embed.set_footer(text="🐬 Powered by Riot API | tuna.gg")

    
    if companion_counter:
        (species, skin_id), _ = companion_counter.most_common(1)[0]
        companion_icon = get_companion_icon_url(species, skin_id)
        if companion_icon:
            embed.set_thumbnail(url=companion_icon)

    await ctx.send(embed=embed)
