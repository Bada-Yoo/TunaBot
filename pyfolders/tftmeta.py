import discord
import json
import os

async def send_tft_meta(ctx):
    try:
        path = os.path.join(os.path.dirname(__file__), "meta.json")
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        await ctx.send("❌ 메타 정보가 없습니다. 먼저 `update_tft_meta.py`를 실행하세요.")
        return

    meta_list = data.get("meta", [])
    updated_at = data.get("updated_at", "알 수 없음")

    embed = discord.Embed(title="롤체 현메타 추천 조합", color=0x5CD1E5)
    embed.set_author(name="🐟TunaBot 메타 정보")  # ← embed 생성 후 호출해야 함
    embed.description = "\n".join(f"{i+1}. {name}" for i, name in enumerate(meta_list))
    embed.set_footer(text=f"🐬 Updated At {updated_at} | tuna.gg")

    await ctx.send(embed=embed)
