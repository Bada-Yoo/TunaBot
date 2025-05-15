import requests

def get_companion_icon_url(species: str, skin_id: int):
    # 1. JSON 경로 생성
    json_url = f"https://raw.communitydragon.org/latest/game/data/characters/{species.lower()}/skins/skin{skin_id}.bin.json"
    print("📦 JSON 경로:", json_url)

    # 2. JSON 가져오기
    response = requests.get(json_url)
    if response.status_code != 200:
        print("❌ JSON 로드 실패")
        return None

    data = response.json()
    if not data:
        print("❌ JSON 데이터 없음")
        return None

    # 3. 첫 key의 iconCircle 필드 찾기
    skin_data = next(iter(data.values()))
    icon_path = skin_data.get("iconCircle")
    if not icon_path:
        print("❌ iconCircle 항목이 없음")
        return None

    # 4. .tex → .png 경로 변환
    icon_url = "https://raw.communitydragon.org/latest/" + icon_path.lower().replace("assets/", "game/assets/").replace(".tex", ".png")

    return icon_url


# ▶️ 테스트 실행
species = "PetPoro"
skin_id = 7

url = get_companion_icon_url(species, skin_id)
if url:
    print("✅ 아이콘 URL:", url)
    # 존재 여부 테스트
    check = requests.get(url)
    if check.status_code == 200:
        print("🖼️ 이미지 확인 성공!")
    else:
        print("⚠️ 이미지 URL은 형식은 맞지만 실제 이미지가 없을 수 있음.")
