import os
import requests
import json
from dotenv import load_dotenv

# API 키 로드
load_dotenv()
RIOT_API_KEY = os.getenv("RIOT_API_KEY")
HEADERS = {"X-Riot-Token": RIOT_API_KEY}

# Riot ID → PUUID
def get_puuid_by_riot_id(game_name, tag_line):
    url = f"https://asia.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{game_name}/{tag_line}"
    return requests.get(url, headers=HEADERS).json().get("puuid")

# Match ID → 상세 데이터
def get_tft_match_ids(puuid, count=1):
    url = f"https://asia.api.riotgames.com/tft/match/v1/matches/by-puuid/{puuid}/ids?count={count}"
    return requests.get(url, headers=HEADERS).json()

def get_tft_match_detail(match_id):
    url = f"https://asia.api.riotgames.com/tft/match/v1/matches/{match_id}"
    return requests.get(url, headers=HEADERS).json()

# 입력
game_name = "꽃온수"
tag_line = "kr1"

puuid = get_puuid_by_riot_id(game_name, tag_line)
match_ids = get_tft_match_ids(puuid, count=1)
match = get_tft_match_detail(match_ids[0])

# 전체 경기 info 출력 (예쁘게)
print("🧾 match['info'] 전체 내용:")
print(json.dumps(match["info"], indent=2, ensure_ascii=False))
