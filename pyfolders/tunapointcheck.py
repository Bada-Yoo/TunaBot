import discord
from TunaDB import player_dao

async def send_tuna_point(interaction: discord.Interaction):
    player_id = interaction.user.id

    point = player_dao.get_player_point(player_id)
    if point is None:
        await interaction.response.send_message(f"{interaction.user.mention} 등록되지 않은 사용자입니다. 먼저 `!참치 등록`을 해주세요.")
        return

    embed = discord.Embed(
        title="나의 포인트",
        description=f"{interaction.user.mention} 님의 현재 포인트는 **{point}** 입니다!",
        color=discord.Color.blurple()
    )
    embed.set_author(name="🐟 TunaBot 포인트 조회")
    embed.set_footer(text="🎣 TunaBot MyPage System | tuna.gg")

    await interaction.response.send_message(embed=embed)
