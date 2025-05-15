import requests
import os
from urllib.parse import quote
from dotenv import load_dotenv

load_dotenv()
RIOT_API_KEY = os.getenv("RIOT_API_KEY")
HEADERS = {"X-Riot-Token": RIOT_API_KEY}

def get_puuid(game_name, tag_line):
    url = f"https://asia.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{quote(game_name)}/{quote(tag_line)}"
    res = requests.get(url, headers=HEADERS)
    if res.status_code == 200:
        return res.json().get("puuid")
    print("❌ puuid 요청 실패:", res.status_code, res.text)
    return None

def get_live_game_by_puuid(puuid):
    url = f"https://kr.api.riotgames.com/lol/spectator/v5/active-games/by-summoner/{puuid}"
    res = requests.get(url, headers=HEADERS)
    print(f"📡 요청: {url}")
    print(f"🔁 상태 코드: {res.status_code}")
    if res.status_code == 200 and res.text.strip():
        return res.json()
    return None
def load_champion_id_map():
    url = "https://ddragon.leagueoflegends.com/cdn/14.10.1/data/ko_KR/champion.json"
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


# ▶️ 실행
game_name = "헬로하로"
tag_line = "KR1"

puuid = get_puuid(game_name, tag_line)
print("🔍 PUUID:", puuid)
champion_map = load_champion_id_map()

live_game = get_live_game_by_puuid(puuid)
if live_game:
    print("🎮 현재 게임 중입니다.")
    for p in live_game["participants"]:
        if p["puuid"] == puuid:
            champ_id = p["championId"]
            champ_name = champion_map.get(champ_id, f"챔피언 ID {champ_id}")
            print(f"✅ 사용 중인 챔피언: {champ_name} (ID: {champ_id})")
else:
    print("❌ 현재 게임 정보를 불러올 수 없습니다.")
