import discord
import json
import os

# !롤체 현메타 명령어 구현 (embed + 페이지네이션 + 상세보기)
async def send_tft_meta(ctx):
    base_dir = os.path.dirname(__file__)
    meta_path = os.path.join(base_dir, "tft_meta.json")
    detail_path = os.path.join(base_dir, "tft_metadetail.json")
    image_dir = os.path.join(base_dir, "tft_meta_images")

    with open(meta_path, encoding="utf-8") as f:
        meta_data = json.load(f)
    with open(detail_path, encoding="utf-8") as f:
        detail_data = json.load(f)

    metas = meta_data.get("meta", [])
    updated_at = meta_data.get("updated_at", "알 수 없음")
    total_pages = len(metas)
    current_page = 0

    def make_embed(page):
        meta = metas[page]
        title = f"{page+1}. {'🔥 ' if meta.get('hot') else ''}{meta['name'].replace(chr(10), ' ')}"
        embed = discord.Embed(title="롤체 현메타 추천 조합", description=title, color=0x5CD1E5)
        embed.set_author(name="🐟TunaBot 메타 정보")
        embed.set_footer(text=f"🐬 Updated At {updated_at} | tuna.gg")
        embed.set_image(url="attachment://meta.png")
        return embed

    def get_file(page):
        filename = os.path.join(image_dir, f"meta_card_{metas[page]['index']}.png")
        return discord.File(filename, filename="meta.png")

    file = get_file(current_page)
    embed = make_embed(current_page)
    message = await ctx.send(embed=embed, file=file)

    if total_pages > 1:
        await message.add_reaction("⬅️")
        await message.add_reaction("➡️")
    await message.add_reaction("✅")

    def check(reaction, user):
        return (
            user == ctx.author and
            str(reaction.emoji) in ["⬅️", "➡️", "✅"] and
            reaction.message.id == message.id
        )

    while True:
        try:
            reaction, user = await ctx.bot.wait_for("reaction_add", timeout=60.0, check=check)

            if str(reaction.emoji) == "➡️" and current_page < total_pages - 1:
                current_page += 1
            elif str(reaction.emoji) == "⬅️" and current_page > 0:
                current_page -= 1
            elif str(reaction.emoji) == "✅":
                meta = metas[current_page]
                detail = next((d for d in detail_data.get("meta", []) if d["name"] == meta["name"]), None)

                if not detail:
                    await ctx.send("상세 정보를 찾을 수 없습니다.")
                    continue

                difficulty = detail.get("difficulty", "알 수 없음")

                item_section = ""
                for group in detail.get("recommended_items", []):
                    target = group.get("target", "")
                    item_info = "\n".join(group.get("info", []))
                    item_section += f"**{target}**\n{item_info}\n\n"

                leveling_info = "\n".join(detail.get("leveling", []))

                detail_embed = discord.Embed(
                    title=f"{meta['name']} 상세정보",
                    description=(
                        f"**🌊 덱 난이도**\n{difficulty}\n\n"
                        f"**🌊 추천 템**\n{item_section or '정보 없음'}\n"
                        f"**🌊 스테이지별 레벨업 추천**\n{leveling_info or '정보 없음'}"
                    ),
                    color=discord.Color.dark_blue()
                )
                detail_embed.set_author(name="🐟TunaBot 현메타 정보")
                detail_embed.set_footer(text=f"🐬 Updated At {updated_at} | tuna.gg")
                await ctx.send(embed=detail_embed)
                continue  # 페이지 이동은 아님

            else:
                continue  # 아무 동작 없음

            await message.clear_reactions()
            file = get_file(current_page)
            embed = make_embed(current_page)
            await message.edit(embed=embed, attachments=[file])

            if current_page > 0:
                await message.add_reaction("⬅️")
            if current_page < total_pages - 1:
                await message.add_reaction("➡️")
            await message.add_reaction("✅")

        except Exception:
            break
