import os
import requests
import discord
from urllib.parse import quote
from dotenv import load_dotenv
from collections import Counter, defaultdict


load_dotenv()
RIOT_API_KEY = os.getenv("RIOT_LOL_API_KEY")
HEADERS = {"X-Riot-Token": RIOT_API_KEY}

match_id = "KR_7646709819"  # 원하는 match ID

url = f"https://asia.api.riotgames.com/lol/match/v5/matches/{match_id}"
response = requests.get(url, headers=HEADERS)

# 응답 JSON 출력
try:
    data = response.json()
    if "info" in data:
        print(f"✅ match_id {match_id} 정보 조회 성공")
        print(data["info"])  # 전체 info 출력
    else:
        print(f"❌ match_id {match_id} 응답 이상:")
        print(data)
except Exception as e:
    print("⚠️ JSON 파싱 실패 또는 연결 오류:", e)
