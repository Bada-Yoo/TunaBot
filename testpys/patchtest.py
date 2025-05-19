import requests
from bs4 import BeautifulSoup

def get_latest_patch_note():
    url = "https://www.leagueoflegends.com/ko-kr/news/tags/patch-notes/"
    headers = {"User-Agent": "Mozilla/5.0"}

    res = requests.get(url, headers=headers)
    if res.status_code != 200:
        return "❌ 패치노트를 불러올 수 없습니다."

    soup = BeautifulSoup(res.text, "html.parser")

    # 최신 패치노트 링크 추출
    article = soup.select_one('a[href*="/ko-kr/news/game-updates/patch-"]')
    if not article:
        return "❌ 패치노트를 찾을 수 없습니다."

    patch_url = "https://www.leagueoflegends.com" + article["href"]

    # 개별 패치 페이지 접근
    patch_res = requests.get(patch_url, headers=headers)
    patch_soup = BeautifulSoup(patch_res.text, "html.parser")

    title_tag = patch_soup.select_one("h1")
    date_tag = patch_soup.select_one("time")
    thumbnail_tag = patch_soup.select_one("meta[property='og:image']")

    if not (title_tag and date_tag and thumbnail_tag):
        return "❌ 패치노트 정보를 불러올 수 없습니다."

    title = title_tag.text.strip()
    date = date_tag.text.strip()  # ex: "2025. 4. 30."
    thumbnail = thumbnail_tag["content"]

    return {
        "title": title,
        "date": date,
        "url": patch_url,
        "thumbnail": thumbnail
    }

# 테스트
result = get_latest_patch_note()
print(result)
