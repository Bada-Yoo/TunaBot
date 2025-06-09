import discord
from TunaDB import player_dao

# 등록
async def send_tuna_register(interaction: discord.Interaction):
    player_id = interaction.user.id
    player_name = str(interaction.user)

    if player_dao.is_registered(player_id):
        await interaction.response.send_message(f"{interaction.user.mention} 이미 등록되어 있습니다.",ephemeral=False)
        return

    player_dao.register_new_player(player_id, player_name)

    embed = discord.Embed(
        title="환영합니다, 신규 플레이어!",
        description=f"{interaction.user.mention} 님께 100 포인트가 지급되었습니다!",
        color=discord.Color.blurple()
    )
    embed.set_author(name="🐟 TunaBot 등록 완료")
    embed.set_footer(text="🎣 TunaBot MyPage System | tuna.gg")

    await interaction.response.send_message(embed=embed, ephemeral=False)


# 삭제 
async def send_tuna_unregister(interaction: discord.Interaction):
    player_id = interaction.user.id

    if not player_dao.is_registered(player_id):
        await interaction.response.send_message(f"{interaction.user.mention} 등록된 계정이 없습니다.", ephemeral=False)
        return

    player_dao.delete_player(player_id)

    embed = discord.Embed(
        title="계정 삭제 완료",
        description=f"{interaction.user.mention}님의 참치 계정이 정상적으로 삭제되었습니다.",
        color=discord.Color.red()
    )
    embed.set_author(name="🐟 TunaBot 계정 삭제")
    embed.set_footer(text="🎣 TunaBot MyPage System | tuna.gg")

    await interaction.response.send_message(embed=embed, ephemeral=False)
