import discord
import uuid
import time
import asyncio

# 메모리 기반 토큰 저장소: token -> (보낸사람 ID, 받은사람 ID, 생성시각)
reply_tokens = {}

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


# ✅ 익명 DM 보내기 (서버 내 유저 대상만)
async def send_anonymous_dm(interaction: discord.Interaction, message: str, target: discord.User):
    await interaction.response.defer(ephemeral=True)

    try:
        embed = discord.Embed(
            title="익명 DM 도착!",
            description=message,
            color=discord.Color.blurple()
        )
        embed.set_footer(text="🪸 TunaBot Secret Message | tuna.gg")

        token = str(uuid.uuid4())
        reply_tokens[token] = (interaction.user.id, target.id, time.time())

        # 수신자에게 전송
        await target.send(
            embed=embed,
            view=discord.ui.View().add_item(
                discord.ui.Button(label=f"/익명답장 message=... token={token}", style=discord.ButtonStyle.secondary, disabled=True)
            )
        )
        await interaction.followup.send("✅ 익명 DM을 보냈어요.")

        # 1시간 후 토큰 만료
        asyncio.create_task(_expire_token_later(token, 3600))

    except:
        await interaction.followup.send("❌ 해당 유저에게 DM을 보낼 수 없어요.")


# ✅ 익명 답장 처리
async def handle_anonymous_reply(interaction: discord.Interaction, message: str, token: str):
    await interaction.response.defer(ephemeral=True)

    entry = reply_tokens.get(token)
    if not entry:
        await interaction.followup.send("❌ 유효하지 않거나 만료된 토큰입니다.")
        return

    sender_id, receiver_id, _ = entry
    if interaction.user.id != receiver_id:
        await interaction.followup.send("⚠️ 이 토큰은 당신이 사용할 수 없습니다.")
        return

    try:
        sender = await interaction.client.fetch_user(sender_id)
        embed = discord.Embed(
            title="익명 답장이 도착했어요!",
            description=message,
            color=discord.Color.blurple()
        )
        embed.set_footer(text=f"🪸 보낸 사람: {interaction.user.display_name} | tuna.gg")
        await sender.send(embed=embed)

        await interaction.followup.send("✅ 답장을 보냈어요.")
        del reply_tokens[token]
    except:
        await interaction.followup.send("❌ 상대방에게 답장을 보낼 수 없어요.")


# ✅ 토큰 자동 만료 처리
async def _expire_token_later(token: str, delay: int):
    await asyncio.sleep(delay)
    reply_tokens.pop(token, None)
