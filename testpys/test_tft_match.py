import requests

RIOT_API_KEY = "RGAPI-3df29f5c-0b93-4ac7-b5e0-3d94bc178aa0"
HEADERS = {"X-Riot-Token": RIOT_API_KEY}

match_id = "KR_7640460191" 

url = f"https://asia.api.riotgames.com/tft/match/v1/matches/{match_id}"
res = requests.get(url, headers=HEADERS)

print("🔍 응답 코드:", res.status_code)
try:
    print("🔍 응답 내용:", res.json())
except Exception as e:
    print("❌ JSON 파싱 실패:", e)
