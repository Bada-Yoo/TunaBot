import requests

CD_URL = "https://raw.communitydragon.org/latest/cdragon/tft/ko_kr.json"
data = requests.get(CD_URL).json()

CHAMPION_MAP = {}
TRAIT_MAP = {}
AUGMENT_MAP = {}

# 유닛/시너지: setData 안에 있음
for set_entry in data.get("setData", []):
    for category in ["champions", "traits"]:
        for entry in set_entry.get(category, []):
            if not isinstance(entry, dict):
                continue
            api_name = entry.get("apiName")
            name = entry.get("name")
            if api_name and name:
                if category == "champions":
                    CHAMPION_MAP[api_name] = name
                elif category == "traits":
                    TRAIT_MAP[api_name] = name

# 증강: items에 있음
for entry in data.get("items", []):
    api_name = entry.get("apiName")
    name = entry.get("name")
    if api_name and name and "Augment" in api_name:
        AUGMENT_MAP[api_name] = name

# 매핑 함수
def translate_unit(name): return CHAMPION_MAP.get(name, "❌ 못찾음")
def translate_synergy(name): return TRAIT_MAP.get(name, "❌ 못찾음")
def translate_augment(name): return AUGMENT_MAP.get(name, "❌ 못찾음")

# 테스트
print("✅ 유닛 테스트:")
print("TFT14_Leona ➝", translate_unit("TFT14_Leona"))
print("TFT14_Xayah ➝", translate_unit("TFT14_Xayah"))

print("\n✅ 시너지 테스트:")
print("TFT14_AnimaSquad ➝", translate_synergy("TFT14_AnimaSquad"))
print("TFT14_Bruiser ➝", translate_synergy("TFT14_Bruiser"))

print("\n✅ 증강 테스트:")
print("TFT14_Augment_BruiserCirclet ➝", translate_augment("TFT14_Augment_BruiserCirclet"))
print("TFT14_Augment_HedgeFund ➝", translate_augment("TFT14_Augment_HedgeFund"))
