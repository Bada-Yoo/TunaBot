import discord

# ✅ 채널에 익명 메시지 보내기
async def send_anonymous_channel(interaction: discord.Interaction, message: str):
    await interaction.response.defer(ephemeral=True)

    embed = discord.Embed(
        title="익명 메세지",
        description=message,
        color=discord.Color.blurple()
    )
    embed.set_footer(text="🪸 TunaBot Secret Message | tuna.gg")

    await interaction.channel.send(embed=embed)
    await interaction.followup.send("✅ 익명 메시지를 보냈어요.")


# ✅ 익명 DM 보내기 - 오직 서버 내 유저 선택만 사용
async def send_anonymous_dm(
    interaction: discord.Interaction,
    message: str,
    target: discord.User  # 필수 인자로 변경
):
    await interaction.response.defer(ephemeral=True)

    if target:
        await _try_send_dm(interaction, target, message)
    else:
        await interaction.followup.send("❗ 대상 유저를 반드시 선택해주세요.")


# ✅ DM 전송 시도 (내부 함수)
async def _try_send_dm(interaction: discord.Interaction, user: discord.User, message: str):
    embed = discord.Embed(
        title="익명 DM 도착!",
        description=message,
        color=discord.Color.blurple()
    )
    embed.set_footer(text="🪸 TunaBot Secret Message | tuna.gg")

    try:
        await user.send(embed=embed)
        await interaction.followup.send("✅ 익명 DM을 보냈어요.")
    except:
        await interaction.followup.send("❌ 해당 유저에게 DM을 보낼 수 없어요.")
