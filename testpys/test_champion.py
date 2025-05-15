import requests

def load_champion_id_map():
    url = "https://ddragon.leagueoflegends.com/cdn/14.10.1/data/ko_KR/champion.json"
    res = requests.get(url)

    if res.status_code != 200 or not res.text.strip():
        print("❌ 챔피언 목록을 불러오지 못했습니다.")
        return {}

    try:
        champ_data = res.json()["data"]
    except Exception as e:
        print("❌ 챔피언 JSON 파싱 오류:", e)
        return {}

    id_map = {}
    for champ in champ_data.values():
        champ_id = int(champ["key"])
        champ_name = champ["name"]
        id_map[champ_id] = champ_name
    return id_map

# 실행 테스트
if __name__ == "__main__":
    champ_map = load_champion_id_map()
    if champ_map:
        print("✅ 챔피언 ID → 이름 매핑 성공!")
        print("예시: 157 →", champ_map.get(157))  # Yasuo
        print("예시: 103 →", champ_map.get(103))  # Ahri
    else:
        print("❌ 챔피언 매핑 실패")
