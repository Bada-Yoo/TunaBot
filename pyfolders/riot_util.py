import requests
import os

RIOT_API_KEY = os.getenv("RIOT_LOL_API_KEY")
HEADERS = {"X-Riot-Token": RIOT_API_KEY}

def safe_get(url, params=None):
    response = requests.get(url, headers=HEADERS, params=params)

    if response.status_code == 429:
        retry_after = int(response.headers.get("Retry-After", "60"))
        print(f"🚫 요청량이 많아요! {retry_after}초 후 재시도 부탁드려요~")
        return None

    return response
