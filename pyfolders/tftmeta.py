import discord
import json
import os

# !롤체 현메타 명령어 구현 (embed + 페이지네이션)
async def send_tft_meta(ctx):
    base_dir = os.path.dirname(__file__)
    meta_path = os.path.join(base_dir, "meta.json")
    image_dir = os.path.join(base_dir, "meta_images")

    with open(meta_path, encoding="utf-8") as f:
        data = json.load(f)

    metas = data.get("meta", [])
    updated_at = data.get("updated_at", "알 수 없음")
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

    if total_pages <= 1:
        return

    if current_page < total_pages - 1:
        await message.add_reaction("➡️")

    def check(reaction, user):
        return (
            user == ctx.author and
            str(reaction.emoji) in ["⬅️", "➡️"] and
            reaction.message.id == message.id
        )

    while True:
        try:
            reaction, user = await ctx.bot.wait_for("reaction_add", timeout=60.0, check=check)

            if str(reaction.emoji) == "➡️" and current_page < total_pages - 1:
                current_page += 1
            elif str(reaction.emoji) == "⬅️" and current_page > 0:
                current_page -= 1
            else:
                continue

            await message.clear_reactions()
            file = get_file(current_page)
            embed = make_embed(current_page)
            await message.edit(embed=embed, attachments=[file])

            if current_page > 0:
                await message.add_reaction("⬅️")
            if current_page < total_pages - 1:
                await message.add_reaction("➡️")

        except Exception:
            break
