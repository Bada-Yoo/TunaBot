import os
import requests
from dotenv import load_dotenv

load_dotenv()

# 각각의 API 키 분리
LOL_API_KEY = os.getenv("RIOT_LOL_API_KEY")
TFT_API_KEY = os.getenv("RIOT_TFT_API_KEY")

LOL_HEADERS = {"X-Riot-Token": LOL_API_KEY}
TFT_HEADERS = {"X-Riot-Token": TFT_API_KEY}


def lol_safe_get(url, params=None):
    response = requests.get(url, headers=LOL_HEADERS, params=params)
    
    if response.status_code == 429:
        retry_after = int(response.headers.get("Retry-After", "60"))
        print(f"🚫 [LoL] 요청량이 많아요! {retry_after}초 후 재시도 부탁드려요~")
        return None, retry_after
    return response, None



def tft_safe_get(url, params=None):
    response = requests.get(url, headers=TFT_HEADERS, params=params)
    if response.status_code == 429:
        retry_after = int(response.headers.get("Retry-After", "60"))
        print(f"🚫 [TFT] 요청량이 많아요! {retry_after}초 후 재시도 부탁드려요~")
        return None
    return response
