import requests
from bs4 import BeautifulSoup
import json

URL = "https://lolchess.gg/champions/set18"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 Chrome/131.0 Safari/537.36"
    )
}


def load_lolchess_costs():

    response = requests.get(
        URL,
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
        print("__NEXT_DATA__ 없음")
        return {}

    data = json.loads(script.string)

    cost_map = {}


    # JSON 전체 재귀 탐색
    def walk(obj):

        if isinstance(obj, dict):

            name = obj.get("name")
            cost = obj.get("cost")
            key = obj.get("key")
            ingame_key = obj.get("ingameKey")

            # 챔피언 데이터로 추정
            if (
                name
                and isinstance(cost, list)
                and len(cost) > 0
                and isinstance(cost[0], int)
                and 1 <= cost[0] <= 5
            ):

                unit_cost = cost[0]

                # 이름 기준
                cost_map[name] = unit_cost

                print(
                    f"{name:12} | "
                    f"cost={unit_cost} | "
                    f"key={key} | "
                    f"ingameKey={ingame_key}"
                )

            for value in obj.values():
                walk(value)

        elif isinstance(obj, list):

            for value in obj:
                walk(value)


    walk(data)

    return cost_map


if __name__ == "__main__":

    print("===== 롤체지지 SET18 코스트 로드 =====\n")

    cost_map = load_lolchess_costs()

    print()
    print("==============================")
    print("총 이름:", len(cost_map))
    print("==============================")

    print()
    print("===== 주요 챔피언 확인 =====")

    for name in [
        "라칸",
        "렉사이",
        "다이애나",
        "럭스"
    ]:

        print(
            f"{name:10} -> "
            f"{cost_map.get(name, '없음')}"
        )