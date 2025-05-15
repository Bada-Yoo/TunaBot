import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()
RIOT_API_KEY = os.getenv("RIOT_API_KEY")
HEADERS = {"X-Riot-Token": RIOT_API_KEY}

def get_puuid_by_riot_id(game_name, tag_line):
    url = f"https://asia.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{game_name}/{tag_line}"
    return requests.get(url, headers={"X-Riot-Token": RIOT_API_KEY}).json().get("puuid")

def get_match_ids(puuid, count=1):
    url = f"https://asia.api.riotgames.com/tft/match/v1/matches/by-puuid/{puuid}/ids?count={count}"
    return requests.get(url, headers=HEADERS).json()

def get_match_detail(match_id):
    url = f"https://asia.api.riotgames.com/tft/match/v1/matches/{match_id}"
    return requests.get(url, headers=HEADERS).json()

# 테스트 실행
game_name = "바다속참치"
tag_line = "는못참치"

puuid = get_puuid_by_riot_id(game_name, tag_line)
match_ids = get_match_ids(puuid, count=1)
match = get_match_detail(match_ids[0])

# 전체 match['info'] 출력 (예쁘게 보기)
print("✅ match['info'] 전체 구조:")
print(json.dumps(match["info"], indent=2, ensure_ascii=False))
