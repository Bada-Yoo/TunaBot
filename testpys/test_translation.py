import json
import requests

# 링크에서 JSON 가져오기
url = "https://raw.communitydragon.org/latest/cdragon/tft/ko_kr.json"  # 여기에 실제 링크 삽입
data = requests.get(url).json()

# JSON 구조상 최상단 key가 "items"일 경우
for entry in data.get("items", []):
    api_name = entry.get("apiName")
    name = entry.get("name")
    if api_name and name:
        print(f"{api_name} → {name}")
print("---------------------------------------------------------")
for set_entry in data.get("setData", []):
    for category in ["augments", "champions", "traits"]:
        for entry in set_entry.get(category, []):
            if not isinstance(entry, dict):  # ✅ 여기가 중요!
                continue

            api_name = entry.get("apiName")
            name = entry.get("name")
            if api_name and name:
                print(f"{api_name} → {name}")
