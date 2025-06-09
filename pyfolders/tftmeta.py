import discord
import json
import os
import asyncio

def get_invalid_query_embed():
    embed = discord.Embed(
        title="메타 검색 예시 안내",
        description=(
            "**아래와 같이 입력해보세요!**\n\n"
            " `/메타 전체` → 전체 메타 조합 목록 보기\n"
            " `/메타 3` → 3번 메타 카드 보기 + 상세정보\n"
            " `/메타 모르가나` → 모르가나 포함된 메타 보기\n\n"
            " 숫자 또는 유닛명을 정확히 입력했는지 확인해주세요."
        ),
        color=discord.Color.red()
    )
    embed.set_author(name="🐟TunaBot 메타 검색 도움말")
    embed.set_footer(text=f"🐳 TunaBot TFT Info | tuna.gg")
    return embed

async def send_tft_meta(interaction: discord.Interaction, query=None):
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

    if query is None or query.strip().lower() == "전체":
        name_list = [f"{i+1}. {'🔥 ' if m.get('hot') else ''}{m['name']}" for i, m in enumerate(metas)]
        description = "\n".join(name_list)
        embed = discord.Embed(
            title="롤체 메타 조합 목록",
            description=description,
            color=discord.Color(0x5CD1E5)
        )
        embed.set_author(name="🐟TunaBot 메타 정보")
        embed.set_footer(text=f"🐳 Updated At {updated_at} | tuna.gg")
        await interaction.response.send_message(embed=embed)
        return

    if query.isdigit():
        index = int(query) - 1
        if 0 <= index < len(metas):
            meta = metas[index]
            detail = next((d for d in detail_data["meta"] if d["name"] == meta["name"]), None)
            file_path = os.path.join(image_dir, f"meta_card_{meta['index']}.png")

            if not os.path.exists(file_path):
                await interaction.response.send_message("이미지 파일을 찾을 수 없습니다.")
                return

            file = discord.File(file_path, filename="meta.png")
            embed1 = discord.Embed(title=meta['name'], color=0x5CD1E5)
            embed1.set_image(url="attachment://meta.png")
            embed1.set_author(name="🐟TunaBot 현메타 정보")  
            embed1.set_footer(text=f"🐬 Updated At {updated_at} | tuna.gg") 

            await interaction.response.defer()
            message = await interaction.followup.send(file=file, embed=embed1, wait=True)
            await message.add_reaction("✅")

            def check(reaction, user):
                return user == interaction.user and str(reaction.emoji) == "✅" and reaction.message.id == message.id

            try:
                reaction, user = await interaction.client.wait_for("reaction_add", timeout=60.0, check=check)
                if not detail:
                    await interaction.followup.send("상세 정보를 찾을 수 없습니다.")
                    return

                item_text = ""
                for group in detail.get("recommended_items", []):
                    item_text += f"**{group['target']}**\n" + "\n".join(group["info"]) + "\n\n"
                level_text = "\n".join(detail.get("leveling", []))

                embed2 = discord.Embed(
                    title=f"{meta['name']} 상세정보",
                    description=(
                        f"**🌊 덱 난이도**\n{detail.get('difficulty', '알 수 없음')}\n\n"
                        f"**🌊 추천 템**\n{item_text or '정보 없음'}\n"
                        f"**🌊 스테이지별 레벨업 추천**\n{level_text or '정보 없음'}"
                    ),
                    color=discord.Color(0x5CD1E5)
                )
                embed2.set_author(name="🐟TunaBot 현메타 정보")
                embed2.set_footer(text=f"🐬 Updated At {updated_at} | tuna.gg")
                await interaction.followup.send(embed=embed2)
            except asyncio.TimeoutError:
                pass
        else:
            await interaction.response.send_message(
                content="❌ 해당 번호의 메타는 존재하지 않아요.",
                embed=get_invalid_query_embed()
            )
        return

    keyword = query.strip()
    matched = [
        m for m in metas
        if any(keyword in u["name"] for u in m.get("units", []))
    ]
    if not matched:
        await interaction.response.send_message(
            content="❌ 메타를 찾을 수 없어요.",
            embed=get_invalid_query_embed()
        )
        return

    await send_tft_meta_with_filter(interaction, matched, updated_at, detail_data, image_dir)

# 🔁 필터된 메타 페이지네이션
async def send_tft_meta_with_filter(interaction, metas, updated_at, detail_data, image_dir):
    current_page = 0
    total_pages = len(metas)

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
    await interaction.response.defer()
    
    message = await interaction.followup.send(embed=embed, file=file, wait=True)

    if total_pages > 1:
        await message.add_reaction("⬅️")
        await message.add_reaction("➡️")
    await message.add_reaction("✅")

    def check(reaction, user):
        return user == interaction.user and str(reaction.emoji) in ["⬅️", "➡️", "✅"] and reaction.message.id == message.id

    while True:
        try:
            reaction, user = await interaction.client.wait_for("reaction_add", timeout=60.0, check=check)

            if str(reaction.emoji) == "➡️" and current_page < total_pages - 1:
                current_page += 1
            elif str(reaction.emoji) == "⬅️" and current_page > 0:
                current_page -= 1
            elif str(reaction.emoji) == "✅":
                meta = metas[current_page]
                detail = next((d for d in detail_data.get("meta", []) if d["name"] == meta["name"]), None)
                if not detail:
                    await interaction.followup.send("상세 정보를 찾을 수 없습니다.")
                    continue

                item_section = ""
                for group in detail.get("recommended_items", []):
                    target = group.get("target", "")
                    item_info = "\n".join(group.get("info", []))
                    item_section += f"**{target}**\n{item_info}\n\n"

                leveling_info = "\n".join(detail.get("leveling", []))

                detail_embed = discord.Embed(
                    title=f"{meta['name']} 상세정보",
                    description=(
                        f"**🌊 덱 난이도**\n{detail.get('difficulty', '알 수 없음')}\n\n"
                        f"**🌊 추천 템**\n{item_section or '정보 없음'}\n"
                        f"**🌊 스테이지별 레벨업 추천**\n{leveling_info or '정보 없음'}"
                    ),
                    color=discord.Color(0x5CD1E5)
                )
                detail_embed.set_author(name="🐟TunaBot 현메타 정보")
                detail_embed.set_footer(text=f"🐬 Updated At {updated_at} | tuna.gg")
                await interaction.followup.send(embed=detail_embed)
                continue

            await message.clear_reactions()
            file = get_file(current_page)
            embed = make_embed(current_page)
            await message.edit(embed=embed, attachments=[file])
            if current_page > 0:
                await message.add_reaction("⬅️")
            if current_page < total_pages - 1:
                await message.add_reaction("➡️")
            await message.add_reaction("✅")

        except asyncio.TimeoutError:
            break
