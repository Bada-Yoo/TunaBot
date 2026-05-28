import discord
import json
import os

TRIM_OFFSET = 2


class MetaView(discord.ui.View):

    def __init__(self, metas, details, updated_at, image_dir):
        super().__init__(timeout=120)
        self.metas = metas
        self.details = details
        self.updated_at = updated_at
        self.image_dir = image_dir
        self.page = 0

    def make_embed(self):

        meta = self.metas[self.page]["data"]

        embed = discord.Embed(
            title=meta["name"],
            url=meta.get("url"),
            color=0x5CD1E5
        )

        embed.set_author(name="🐟TunaBot 메타 정보")
        embed.set_footer(text=f"🐬 Updated At {self.updated_at} | tuna.gg")
        embed.set_image(url="attachment://meta.png")

        return embed

    def get_file(self):

        meta_index = self.metas[self.page]["index"]

        path = os.path.join(
            self.image_dir,
            f"meta_card_{meta_index+1}.png"
        )

        return discord.File(path, filename="meta.png")

    @discord.ui.button(label="⬅ 이전", style=discord.ButtonStyle.gray)
    async def prev(self, interaction: discord.Interaction, button: discord.ui.Button):

        if self.page > 0:
            self.page -= 1

        file = self.get_file()
        embed = self.make_embed()

        await interaction.response.edit_message(
            embed=embed,
            attachments=[file],
            view=self
        )

    @discord.ui.button(label="다음 ➡", style=discord.ButtonStyle.gray)
    async def next(self, interaction: discord.Interaction, button: discord.ui.Button):

        if self.page < len(self.metas) - 1:
            self.page += 1

        file = self.get_file()
        embed = self.make_embed()

        await interaction.response.edit_message(
            embed=embed,
            attachments=[file],
            view=self
        )

    @discord.ui.button(label="상세보기", style=discord.ButtonStyle.green)
    async def detail(self, interaction: discord.Interaction, button: discord.ui.Button):

        meta = self.metas[self.page]
        detail = meta.get("detail") or self.details[meta["index"]]

        embed = discord.Embed(
            title=f"{meta['data']['name']} 상세정보",
            url=detail.get("url"),
            description=detail.get("overview", "정보 없음"),
            color=0x5CD1E5
        )

        embed.set_author(name="🐟TunaBot 현메타 정보")
        embed.set_footer(text=f"🐬 Updated At {self.updated_at} | tuna.gg")

        await interaction.response.send_message(embed=embed)


class SingleMetaView(discord.ui.View):

    def __init__(self, meta, detail, updated_at):
        super().__init__(timeout=120)
        self.meta = meta
        self.detail = detail
        self.updated_at = updated_at

    @discord.ui.button(label="상세보기", style=discord.ButtonStyle.green)
    async def detail_btn(self, interaction: discord.Interaction, button: discord.ui.Button):

        embed = discord.Embed(
            title=f"{self.meta['name']} 상세정보",
            url=self.detail.get("url"),
            description=self.detail.get("overview", "정보 없음"),
            color=0x5CD1E5
        )

        embed.set_author(name="🐟TunaBot 현메타 정보")
        embed.set_footer(text=f"🐬 Updated At {self.updated_at} | tuna.gg")

        await interaction.response.send_message(embed=embed)


async def send_tft_meta(interaction: discord.Interaction, query=None):

    base_dir = os.path.dirname(__file__)

    meta_path = os.path.join(base_dir, "tft_meta.json")
    detail_path = os.path.join(base_dir, "tft_metadetail.json")
    image_dir = os.path.join(base_dir, "tft_meta_images")

    with open(meta_path, encoding="utf-8") as f:
        meta_data = json.load(f)

    with open(detail_path, encoding="utf-8") as f:
        detail_data = json.load(f)

    metas = meta_data.get("meta", [])[TRIM_OFFSET:]
    details = detail_data.get("meta_detail", [])

    updated_at = meta_data.get("updated_at", "알 수 없음")

    metas_with_index = [
        {"index": i, "data": m, "detail": details[i]}
        for i, m in enumerate(metas)
    ]

    if query is None or query.strip().lower() == "전체":

        name_list = [
            f"{i+1}. {'🔥 ' if m['data'].get('hot') else ''}{m['data']['name']}"
            for i, m in enumerate(metas_with_index)
        ]

        embed = discord.Embed(
            title="롤체 메타 조합 목록",
            description="\n".join(name_list),
            color=0x5CD1E5
        )

        embed.set_author(name="🐟TunaBot 메타 정보")
        embed.set_footer(text=f"🐳 Updated At {updated_at} | tuna.gg")

        await interaction.response.send_message(embed=embed)
        return

    keyword = query.strip()

    # 숫자 검색
    if keyword.isdigit():

        display_index = int(keyword) - 1

        if display_index >= len(metas_with_index):

            await interaction.response.send_message("❌ 해당 메타가 없습니다.")
            return

        meta_entry = metas_with_index[display_index]

        meta = meta_entry["data"]
        meta_index = meta_entry["index"]
        detail = meta_entry["detail"]

        image_path = os.path.join(
            image_dir,
            f"meta_card_{meta_index+1}.png"
        )

        file = discord.File(image_path, filename="meta.png")

        embed = discord.Embed(
            title=meta["name"],
            url=meta.get("url"),
            color=0x5CD1E5
        )

        embed.set_image(url="attachment://meta.png")
        embed.set_author(name="🐟TunaBot 메타 정보")
        embed.set_footer(text=f"🐬 Updated At {updated_at} | tuna.gg")

        view = SingleMetaView(meta, detail, updated_at)

        await interaction.response.send_message(
            embed=embed,
            file=file,
            view=view
        )

        return

    # 챔피언 검색
    metas_filtered = [
        m for m in metas_with_index
        if any(keyword in u["name"] for u in m["data"].get("units", []))
    ]

    if not metas_filtered:

        await interaction.response.send_message("❌ 메타를 찾을 수 없습니다.")
        return

    view = MetaView(metas_filtered, details, updated_at, image_dir)

    file = view.get_file()
    embed = view.make_embed()

    await interaction.response.send_message(
        embed=embed,
        file=file,
        view=view
    )