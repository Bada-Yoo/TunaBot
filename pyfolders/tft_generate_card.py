from PIL import Image, ImageDraw, ImageFont
import os
import requests
from bs4 import BeautifulSoup
from io import BytesIO
import math
import json

# ===== 설정 =====
LOLCHESS_SET = "set18"
LOLCHESS_CHAMPION_URL = f"https://lolchess.gg/champions/{LOLCHESS_SET}"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 Chrome/131.0 Safari/537.36"
    )
}

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
    1: (132, 137, 153),
    2: (17, 178, 136),
    3: (32, 122, 199),
    4: (196, 64, 218),
    5: (255, 185, 59)
}

# ===== 카드 설정 =====
UNIT_SIZE = 100
ITEM_SIZE = UNIT_SIZE // 3
PADDING = 10
MAX_COLS = 5

TRIM_OFFSET = 2


# =========================================================
# 롤체지지 SET18 코스트 데이터
# =========================================================
def load_cost_data():

    print(f"롤체지지 {LOLCHESS_SET.upper()} 코스트 데이터 로드 중...")

    try:

        response = requests.get(
            LOLCHESS_CHAMPION_URL,
            headers=HEADERS,
            timeout=20
        )

        response.raise_for_status()

        soup = BeautifulSoup(
            response.text,
            "html.parser"
        )

        script = soup.find(
            "script",
            id="__NEXT_DATA__"
        )

        if not script:
            print("❌ __NEXT_DATA__를 찾을 수 없습니다.")
            return {}

        data = json.loads(script.string)

    except Exception as e:

        print("❌ 롤체지지 코스트 데이터 로드 실패")
        print(e)

        return {}


    cost_map = {}


    # ===== JSON 재귀 탐색 =====
    def walk(obj):

        if isinstance(obj, dict):

            name = obj.get("name")
            key = obj.get("key")
            cost = obj.get("cost")

            # 챔피언 데이터인지 확인
            if (
                isinstance(name, str)
                and isinstance(key, str)
                and isinstance(cost, list)
                and len(cost) > 0
                and isinstance(cost[0], int)
                and 1 <= cost[0] <= 5
            ):

                # set18 페이지 내부에 포함된
                # 이전 Set17 데이터 제외
                if not key.startswith("Set17"):

                    clean_name = name.strip()
                    unit_cost = cost[0]

                    cost_map[clean_name] = unit_cost

            # 하위 데이터 탐색
            for value in obj.values():
                walk(value)

        elif isinstance(obj, list):

            for value in obj:
                walk(value)


    walk(data)

    print(
        f"✅ {LOLCHESS_SET.upper()} "
        f"코스트 데이터 {len(cost_map)}개 로드"
    )

    return cost_map


# 프로그램 시작 시 한 번만 로드
COST_MAP = load_cost_data()


# =========================================================
# 이미지 로딩
# =========================================================
def load_image_from_url(url, size=None, rounded=False):

    try:

        r = requests.get(
            url,
            headers=HEADERS,
            timeout=10
        )

        r.raise_for_status()

        img = Image.open(
            BytesIO(r.content)
        ).convert("RGBA")

    except Exception as e:

        print(f"⚠️ 이미지 로드 실패: {url}")
        print(e)

        img = Image.new(
            "RGBA",
            (UNIT_SIZE, UNIT_SIZE),
            (200, 200, 200, 255)
        )

    if size:

        img = img.resize(
            size,
            Image.Resampling.LANCZOS
        )

    if rounded:

        mask = Image.new(
            "L",
            img.size,
            0
        )

        draw = ImageDraw.Draw(mask)

        draw.rounded_rectangle(
            [(0, 0), img.size],
            radius=12,
            fill=255
        )

        img.putalpha(mask)

    return img


# =========================================================
# 유닛 테두리
# =========================================================
def draw_unit_border(draw, box, cost):

    color = COST_COLOR.get(
        cost,
        (0, 0, 0)
    )

    draw.rounded_rectangle(
        box,
        outline=color,
        width=3,
        radius=12
    )


# =========================================================
# 유닛 이름
# =========================================================
def draw_unit_name_inside(card, x, y, name):

    draw = ImageDraw.Draw(card)

    text_x = x + 4
    text_y = y + UNIT_SIZE - 20

    # 검은 외곽선
    for dx, dy in [
        (-1, 0),
        (1, 0),
        (0, -1),
        (0, 1)
    ]:

        draw.text(
            (text_x + dx, text_y + dy),
            name,
            fill="black",
            font=FONT
        )

    # 흰 글씨
    draw.text(
        (text_x, text_y),
        name,
        fill="white",
        font=FONT
    )


# =========================================================
# 아이템 URL
# =========================================================
def get_item_url(item):

    if isinstance(item, str):
        return item

    if isinstance(item, dict):
        return item.get("image")

    return None


# =========================================================
# 카드 생성
# =========================================================
def generate_meta_card(
    meta_data,
    index,
    output_dir="tft_meta_images"
):

    units = meta_data.get(
        "units",
        []
    )

    rows = math.ceil(
        len(units) / MAX_COLS
    )

    card_width = (
        MAX_COLS
        * (UNIT_SIZE + PADDING)
        + PADDING
    )

    unit_block_height = (
        UNIT_SIZE
        + ITEM_SIZE
        + PADDING
    )

    card_height = (
        rows
        * unit_block_height
        + PADDING * 2
    )

    card = Image.new(
        "RGBA",
        (
            card_width,
            card_height
        ),
        (
            255,
            255,
            255,
            255
        )
    )

    draw = ImageDraw.Draw(card)


    # =====================================================
    # 유닛 생성
    # =====================================================
    for i, unit in enumerate(units):

        row = i // MAX_COLS
        col = i % MAX_COLS

        x = (
            PADDING
            + col
            * (UNIT_SIZE + PADDING)
        )

        y = (
            PADDING
            + row
            * unit_block_height
        )

        # ===== 유닛 이름 =====

        name = unit.get(
            "name",
            ""
        ).strip()

        # ===== 유닛 이미지 =====

        icon = unit.get("icon")

        unit_img = load_image_from_url(
            icon,
            size=(
                UNIT_SIZE,
                UNIT_SIZE
            ),
            rounded=True
        )

        card.paste(
            unit_img,
            (x, y),
            unit_img
        )


        # =================================================
        # 코스트 조회
        # =================================================

        cost = COST_MAP.get(
            name,
            0
        )

        if cost == 0:

            print(
                f"⚠️ 코스트 찾기 실패: {name}"
            )


        # ===== 코스트 테두리 =====

        draw_unit_border(
            draw,
            (
                x,
                y,
                x + UNIT_SIZE,
                y + UNIT_SIZE
            ),
            cost
        )


        # ===== 유닛 이름 =====

        draw_unit_name_inside(
            card,
            x,
            y,
            name or "?"
        )


        # =================================================
        # 아이템
        # =================================================

        items = unit.get(
            "items",
            []
        )

        for j, item in enumerate(
            items[:3]
        ):

            url = get_item_url(item)

            if not url:
                continue

            item_img = load_image_from_url(
                url,
                size=(
                    ITEM_SIZE,
                    ITEM_SIZE
                )
            )

            item_x = (
                x
                + j * ITEM_SIZE
            )

            item_y = (
                y
                + UNIT_SIZE
                + 2
            )

            card.paste(
                item_img,
                (
                    item_x,
                    item_y
                ),
                item_img
            )


    # =====================================================
    # 저장
    # =====================================================

    full_output_dir = os.path.join(
        SCRIPT_DIR,
        output_dir
    )

    os.makedirs(
        full_output_dir,
        exist_ok=True
    )

    output_path = os.path.join(
        full_output_dir,
        f"meta_card_{index}.png"
    )

    card.save(output_path)

    print(
        f"카드 생성: {output_path}"
    )

    return output_path


# =========================================================
# 메타 데이터 정리
# =========================================================
def clean_meta_data(meta_list):

    # 앞 두 개 메타 제거
    meta_list = meta_list[TRIM_OFFSET:]

    cleaned_meta = []

    for meta in meta_list:

        units = meta.get("units", [])

        # 첫 번째 유닛 제거
        units = units[1:]

        valid_units = []

        for unit in units:

            name = unit.get("name")

            if not name:
                continue

            # 중복 유닛은 그대로 유지
            valid_units.append(unit)

        meta["units"] = valid_units
        cleaned_meta.append(meta)

    return cleaned_meta


# =========================================================
# 전체 카드 생성
# =========================================================
def generate_all_meta_cards():

    json_path = os.path.join(
        SCRIPT_DIR,
        "tft_meta.json"
    )

    output_dir = os.path.join(
        SCRIPT_DIR,
        "tft_meta_images"
    )


    # ===== 기존 카드 삭제 =====

    if os.path.exists(
        output_dir
    ):

        for file in os.listdir(
            output_dir
        ):

            if (
                file.startswith(
                    "meta_card_"
                )
                and file.endswith(
                    ".png"
                )
            ):

                os.remove(
                    os.path.join(
                        output_dir,
                        file
                    )
                )


    # ===== 메타 JSON 로드 =====

    with open(
        json_path,
        encoding="utf-8"
    ) as f:

        data = json.load(f)


    meta_list = data.get(
        "meta",
        []
    )


    # ===== 메타 정리 =====

    meta_list = clean_meta_data(
        meta_list
    )


    # ===== 카드 생성 =====

    for i, meta in enumerate(
        meta_list,
        start=1
    ):

        generate_meta_card(
            meta,
            i
        )


# =========================================================
# 실행
# =========================================================
if __name__ == "__main__":

    generate_all_meta_cards()