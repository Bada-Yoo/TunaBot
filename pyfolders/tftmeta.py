import discord
import json
import os


class MetaView(discord.ui.View):

    def __init__(self, metas, details, updated_at, image_dir):
        super().__init__(timeout=120)
        self.metas = metas
        self.details = details
        self.updated_at = updated_at
        self.image_dir = image_dir
        self.page = 0

    def make_embed(self):

        meta = self.metas[self.page]

        embed = discord.Embed(
            title="롤체 현메타 추천 조합",
            description=meta["name"],
            color=0x5CD1E5
        )

        embed.set_author(name="🐟TunaBot 메타 정보")
        embed.set_footer(text=f"🐬 Updated At {self.updated_at} | tuna.gg")
        embed.set_image(url="attachment://meta.png")

        return embed

    def get_file(self):

        path = os.path.join(
            self.image_dir,
            f"meta_card_{self.page+1}.png"
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

        detail = self.details[self.page] if self.page < len(self.details) else None

        if not detail:
            await interaction.response.send_message(
                "상세 정보를 찾을 수 없습니다.",
                ephemeral=True
            )
            return

        embed = discord.Embed(
            title=f"{self.metas[self.page]['name']} 상세정보",
            description=detail.get("overview", "정보 없음"),
            color=0x5CD1E5
        )

        embed.set_author(name="🐟TunaBot 현메타 정보")
        embed.set_footer(text=f"🐬 Updated At {self.updated_at} | tuna.gg")

        await interaction.response.send_message(embed=embed)


async def send_tft_meta_with_filter(
        interaction,
        metas,
        updated_at,
        details,
        image_dir
):

    view = MetaView(metas, details, updated_at, image_dir)

    file = view.get_file()
    embed = view.make_embed()

    await interaction.response.send_message(
        embed=embed,
        file=file,
        view=view
    )
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
    details = detail_data.get("meta_detail", [])

    # 앞 두 개 제거
    metas = metas[2:]
    details = details[2:]

    updated_at = meta_data.get("updated_at", "알 수 없음")

    if query is None or query.strip().lower() == "전체":

        name_list = [
            f"{i+1}. {'🔥 ' if m.get('hot') else ''}{m['name']}"
            for i, m in enumerate(metas)
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

    if keyword.isdigit():

        index = int(keyword) - 1

        if 0 <= index < len(metas):

            await send_tft_meta_with_filter(
                interaction,
                metas,
                updated_at,
                details,
                image_dir
            )
            return

    matched = [
        m for m in metas
        if any(keyword in u["name"] for u in m.get("units", []))
    ]

    if not matched:

        embed = discord.Embed(
            title="❌ 메타를 찾을 수 없습니다",
            description="유닛 이름 또는 번호를 확인해주세요.",
            color=discord.Color.red()
        )

        await interaction.response.send_message(embed=embed)
        return

    await send_tft_meta_with_filter(
        interaction,
        matched,
        updated_at,
        details,
        image_dir
    )
        