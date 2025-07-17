import discord

async def send_anonymous_channel(interaction: discord.Interaction, message: str):
    await interaction.response.defer(ephemeral=True)

    embed = discord.Embed(
        title="익명 메세지",
        description=message,
        color=discord.Color.blurple()
    )
    embed.set_footer(text="🦈 TunaBot Secret Message | tuna.gg")

    await interaction.channel.send(embed=embed)
    await interaction.followup.send("✅ 익명 메시지를 보냈어요.")


async def send_anonymous_dm(
    interaction: discord.Interaction,
    message: str,
    target: discord.User = None,
    username: str = None
):
    await interaction.response.defer(ephemeral=True)

    # 1️⃣ 서버 내 유저 선택
    if target:
        await _try_send_dm(interaction, target, message)
        return

    # 2️⃣ 유저 ID 기반 전송
    if username:
        try:
            user_id = int(username)
            user = await interaction.client.fetch_user(user_id)
            await _try_send_dm(interaction, user, message)
            return
        except:
            await interaction.followup.send("❌ 해당 ID로 유저를 찾을 수 없어요.")
            return

    await interaction.followup.send("❗ 대상 유저를 선택하거나 ID를 입력해주세요.")


async def _try_send_dm(interaction: discord.Interaction, user: discord.User, message: str):
    embed = discord.Embed(
        title="익명 DM 도착!",
        description=message,
        color=discord.Color.blurple()
    )
    embed.set_footer(text="🦈 TunaBot Secret Message | tuna.gg")

    try:
        await user.send(embed=embed)
        await interaction.followup.send("✅ 익명 DM을 보냈어요.")
    except:
        await interaction.followup.send("❌ 해당 유저에게 DM을 보낼 수 없어요.")
