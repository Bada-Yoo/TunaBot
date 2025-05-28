# steamgame.py
import requests
import discord
from urllib.parse import quote

def search_game_on_steam(game_name):
    encoded_name = quote(game_name)
    url = f"https://steamcommunity.com/actions/SearchApps/{encoded_name}"
    response = requests.get(url)
    if response.ok:
        results = response.json()
        if results:
            return results[0]['appid']
    return None

def get_game_details(appid):
    url = f"https://store.steampowered.com/api/appdetails?appids={appid}&cc=kr&l=korean"
    response = requests.get(url)
    data = response.json()
    if str(appid) in data and data[str(appid)]["success"]:
        return data[str(appid)]["data"]
    return None

async def send_steam_game_info(ctx, game_name):
    async with ctx.typing():
        appid = search_game_on_steam(game_name)
        if not appid:
            await ctx.send("❌ 해당 게임을 찾을 수 없습니다. 영문으로 입력해주세요!\nex) !스팀 정보 stardew valley")
            return

        details = get_game_details(appid)
        if not details:
            await ctx.send("❌ 게임 정보를 불러오지 못했습니다.")
            return

    name = details['name']
    price = details.get('price_overview', {}).get('final_formatted', '무료 또는 가격 정보 없음')
    categories = ', '.join([c['description'] for c in details.get('categories', [])])
    genres = ', '.join([g['description'] for g in details.get('genres', [])])
    desc = details.get('short_description', '설명이 없습니다.')
    store_url = f"https://store.steampowered.com/app/{appid}"
    image_url = details.get('header_image', '')

    embed = discord.Embed(
        title=f"🎮 {name}",
        url=store_url,
        description=(
            f"**🌊 가격**\n{price}\n\n"
            f"**🌊 장르**\n{genres or '정보 없음'}\n\n"
            f"**🌊 카테고리**\n{categories or '정보 없음'}\n\n"
            f"**🌊 게임 정보**\n{desc}"
        ),
        color=discord.Color.dark_blue()
    )
    embed.set_author(name="🐟TunaBot 게임 정보")
    embed.set_footer(text="🐳 Powered by Data Crawling | tuna.gg")
    embed.set_image(url=image_url)

    await ctx.send(embed=embed)
