from PIL import Image, ImageDraw, ImageFont
import os
import requests
from io import BytesIO
import math
import json

# 유닛 테두리 색상 (코스트 기준)
COST_COLOR = {
    1: (132, 137, 153),
    2: (17, 178, 136),
    3: (32, 122, 199),
    4: (196, 64, 218),
    5: (255, 185, 59),
}

# 설정
UNIT_SIZE = 100
ITEM_SIZE = UNIT_SIZE // 3
PADDING = 10
MAX_COLS = 5
FONT_PATH = "C:/Windows/Fonts/malgun.ttf"  # 윈도우 기본 한글 폰트
FONT = ImageFont.truetype(FONT_PATH, 13)

def load_image_from_url(url, size=None, rounded=False):
    response = requests.get(url)
    img = Image.open(BytesIO(response.content)).convert("RGBA")
    if size:
        img = img.resize(size, Image.Resampling.LANCZOS)
    if rounded:
        mask = Image.new("L", img.size, 0)
        draw = ImageDraw.Draw(mask)
        draw.rounded_rectangle([(0, 0), img.size], radius=12, fill=255)
        img.putalpha(mask)
    return img

def draw_unit_border(draw, box, cost):
    color = COST_COLOR.get(cost, (0, 0, 0))
    draw.rounded_rectangle(box, outline=color, width=3, radius=12)

def draw_unit_name_inside(card, x, y, name):
    draw_overlay = ImageDraw.Draw(card)

    # 좌하단 위치 기준 (텍스트 높이 13~15 기준)
    text_x = x + 4
    text_y = y + UNIT_SIZE - 20

    # 테두리 효과 (4방향)
    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        draw_overlay.text((text_x + dx, text_y + dy), name, fill="black", font=FONT)

    # 중심 흰 텍스트
    draw_overlay.text((text_x, text_y), name, fill="white", font=FONT)


def generate_meta_card(meta_data, output_dir="meta_images"):
    units = meta_data["units"]
    index = meta_data["index"]

    rows = math.ceil(len(units) / MAX_COLS)
    card_width = MAX_COLS * (UNIT_SIZE + PADDING) + PADDING
    unit_block_height = UNIT_SIZE + ITEM_SIZE + PADDING
    card_height = rows * unit_block_height + PADDING * 2

    card = Image.new("RGBA", (card_width, card_height), (255, 255, 255, 255))
    draw = ImageDraw.Draw(card)

    for i, unit in enumerate(units):
        row = i // MAX_COLS
        col = i % MAX_COLS
        x = PADDING + col * (UNIT_SIZE + PADDING)
        y = PADDING + row * unit_block_height

        unit_img = load_image_from_url(unit["icon"], size=(UNIT_SIZE, UNIT_SIZE), rounded=True)
        card.paste(unit_img, (x, y), unit_img)
        draw_unit_border(draw, (x, y, x + UNIT_SIZE, y + UNIT_SIZE), unit["cost"])
        draw_unit_name_inside(card, x, y, unit["name"])

        for j, item in enumerate(unit.get("items", [])[:3]):
            item_img = load_image_from_url(item["image"], size=(ITEM_SIZE, ITEM_SIZE))
            item_x = x + j * ITEM_SIZE
            item_y = y + UNIT_SIZE + 2
            card.paste(item_img, (item_x, item_y), item_img)

    script_dir = os.path.dirname(os.path.abspath(__file__))
    full_output_dir = os.path.join(script_dir, output_dir)
    os.makedirs(full_output_dir, exist_ok=True)

    output_path = os.path.join(full_output_dir, f"meta_card_{index}.png")
    card.save(output_path)
    print(f"✅ 저장 완료: {output_path}")
    return output_path

def generate_all_meta_cards():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(script_dir, "meta.json")

    with open(json_path, encoding="utf-8") as f:
        data = json.load(f)

    for meta in data["meta"]:
        generate_meta_card(meta)

if __name__ == "__main__":
    generate_all_meta_cards()
