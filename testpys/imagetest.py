import requests

# 테스트용 companion ID
item_id = 52037  # 예: PetBunny

# 이미지 URL 생성
icon_url = f"https://raw.communitydragon.org/latest/game/assets/loadouts/companions/icons/companion_icon_{item_id}.png"

# 이미지 존재 여부 확인
response = requests.get(icon_url)

if response.status_code == 200:
    print("✅ 이미지 URL:", icon_url)
else:
    print("❌ 이미지를 찾을 수 없습니다.")
