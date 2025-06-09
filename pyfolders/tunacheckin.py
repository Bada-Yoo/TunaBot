import discord
from TunaDB import player_dao

async def send_tuna_checkin(interaction: discord.Interaction):
    player_id = interaction.user.id

    if not player_dao.is_registered(player_id):
        await interaction.response.send_message(
            f"{interaction.user.mention} 등록되지 않은 사용자입니다. 먼저 `/참치 등록`을 해주세요.",
            ephemeral=False
        )
        return

    if player_dao.has_checked_today(player_id):
        embed = discord.Embed(
            title="이미 출석하셨습니다!",
            description="출석은 하루에 한 번만 가능합니다.",
            color=discord.Color.red()
        )
    else:
        bonus = player_dao.update_attendance(player_id) 
        embed = discord.Embed(
            title="출석 완료!",
            description=f"{bonus}포인트가 지급되었습니다! 내일 또 만나요",
            color=discord.Color.blurple()
        )

    embed.set_author(name="🐟 TunaBot 출석체크")
    embed.set_footer(text="🎣 TunaBot Point System | tuna.gg")

    await interaction.response.send_message(embed=embed, ephemeral=False)
