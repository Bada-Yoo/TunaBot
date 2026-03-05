from PIL import Image, ImageDraw, ImageFont
import os
import requests
from io import BytesIO
import math
import json

# ===== 설정 =====
SEASON_PREFIX = "TFT16"

# ===== 경로 =====
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
FONT_PATH = os.path.join(SCRIPT_DIR, "fonts", "NanumSquareRoundB.ttf")

# ===== 폰트 =====
def get_font(size=13):
    try:
        return ImageFont.truetype(FONT_PATH, size)
    except:
        return ImageFont.load_default()

FONT = get_font(13)

# ===== 코스트 색 =====
COST_COLOR = {
    1: (132,137,153),
    2: (17,178,136),
    3: (32,122,199),
    4: (196,64,218),
    5: (255,185,59)
}

# ===== 카드 설정 =====
UNIT_SIZE = 100
ITEM_SIZE = UNIT_SIZE // 3
PADDING = 10
MAX_COLS = 5

# ===== 코스트 데이터 =====
def load_cost_data():

    url = "https://raw.communitydragon.org/latest/cdragon/tft/ko_kr.json"

    try:
        data = requests.get(url,timeout=10).json()
    except:
        print("코스트 데이터 로드 실패")
        return {}

    cost_map = {}

    for setdata in data.get("setData",[]):

        for champ in setdata.get("champions",[]):

            api = champ.get("apiName")
            cost = champ.get("cost")

            if not api or cost is None:
                continue

            cost_map[api] = cost

    return cost_map

COST_MAP = load_cost_data()

# ===== 아이콘에서 챔피언 이름 추출 =====
def get_champion_api_name(icon_url):

    if not icon_url:
        return None

    try:

        filename = icon_url.split("/")[-1]

        name = filename.split("-")[-1].replace(".jpg","")

        return f"{SEASON_PREFIX}_{name}"

    except:
        return None

# ===== 이미지 로딩 =====
def load_image_from_url(url,size=None,rounded=False):

    try:
        r = requests.get(url,timeout=10)
        img = Image.open(BytesIO(r.content)).convert("RGBA")
    except:
        img = Image.new("RGBA",(UNIT_SIZE,UNIT_SIZE),(200,200,200,255))

    if size:
        img = img.resize(size,Image.Resampling.LANCZOS)

    if rounded:

        mask = Image.new("L",img.size,0)
        draw = ImageDraw.Draw(mask)
        draw.rounded_rectangle([(0,0),img.size],radius=12,fill=255)
        img.putalpha(mask)

    return img

# ===== 테두리 =====
def draw_unit_border(draw,box,cost):

    color = COST_COLOR.get(cost,(0,0,0))

    draw.rounded_rectangle(
        box,
        outline=color,
        width=3,
        radius=12
    )

# ===== 이름 =====
def draw_unit_name_inside(card,x,y,name):

    draw = ImageDraw.Draw(card)

    text_x = x+4
    text_y = y+UNIT_SIZE-20

    for dx,dy in [(-1,0),(1,0),(0,-1),(0,1)]:
        draw.text((text_x+dx,text_y+dy),name,fill="black",font=FONT)

    draw.text((text_x,text_y),name,fill="white",font=FONT)

# ===== 아이템 =====
def get_item_url(item):

    if isinstance(item,str):
        return item

    if isinstance(item,dict):
        return item.get("image")

    return None

# ===== 카드 생성 =====
def generate_meta_card(meta_data,index,output_dir="tft_meta_images"):

    units = meta_data.get("units",[])

    rows = math.ceil(len(units)/MAX_COLS)

    card_width = MAX_COLS*(UNIT_SIZE+PADDING)+PADDING
    unit_block_height = UNIT_SIZE+ITEM_SIZE+PADDING
    card_height = rows*unit_block_height+PADDING*2

    card = Image.new(
        "RGBA",
        (card_width,card_height),
        (255,255,255,255)
    )

    draw = ImageDraw.Draw(card)

    for i,unit in enumerate(units):

        row = i//MAX_COLS
        col = i%MAX_COLS

        x = PADDING + col*(UNIT_SIZE+PADDING)
        y = PADDING + row*unit_block_height

        icon = unit.get("icon")

        unit_img = load_image_from_url(
            icon,
            size=(UNIT_SIZE,UNIT_SIZE),
            rounded=True
        )

        card.paste(unit_img,(x,y),unit_img)

        # ===== cost lookup =====

        api_name = get_champion_api_name(icon)

        cost = COST_MAP.get(api_name,0)

        draw_unit_border(
            draw,
            (x,y,x+UNIT_SIZE,y+UNIT_SIZE),
            cost
        )

        draw_unit_name_inside(
            card,
            x,
            y,
            unit.get("name","?")
        )

        # 아이템
        items = unit.get("items",[])

        for j,item in enumerate(items[:3]):

            url = get_item_url(item)

            if not url:
                continue

            item_img = load_image_from_url(
                url,
                size=(ITEM_SIZE,ITEM_SIZE)
            )

            item_x = x + j*ITEM_SIZE
            item_y = y + UNIT_SIZE + 2

            card.paste(item_img,(item_x,item_y),item_img)

    # 저장
    full_output_dir = os.path.join(SCRIPT_DIR,output_dir)
    os.makedirs(full_output_dir,exist_ok=True)

    output_path = os.path.join(
        full_output_dir,
        f"meta_card_{index}.png"
    )

    card.save(output_path)

    print(f"카드 생성: {output_path}")

    return output_path
def clean_meta_data(meta_list):

    # 1️⃣ 앞 두개 메타 제거
    meta_list = meta_list[2:]

    cleaned_meta = []

    for meta in meta_list:

        units = meta.get("units", [])

        seen = set()
        unique_units = []

        for unit in units:

            name = unit.get("name")

            if not name:
                continue

            if name in seen:
                continue

            seen.add(name)
            unique_units.append(unit)

        meta["units"] = unique_units
        cleaned_meta.append(meta)

    return cleaned_meta

# ===== 전체 생성 =====
def generate_all_meta_cards():

    json_path = os.path.join(SCRIPT_DIR,"tft_meta.json")
    output_dir = os.path.join(SCRIPT_DIR,"tft_meta_images")

    if os.path.exists(output_dir):

        for file in os.listdir(output_dir):

            if file.startswith("meta_card_") and file.endswith(".png"):

                os.remove(os.path.join(output_dir,file))

    with open(json_path,encoding="utf-8") as f:
        data = json.load(f)

    meta_list = data.get("meta", [])

    # 🔧 meta.json 정리
    meta_list = clean_meta_data(meta_list)

    for i,meta in enumerate(meta_list,start=1):

        generate_meta_card(meta,i)

# ===== 실행 =====
if __name__ == "__main__":
    generate_all_meta_cards()