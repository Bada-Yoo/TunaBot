import discord
from TunaDB import player_dao

async def send_tuna_point(ctx):
    player_id = ctx.author.id
    point = player_dao.get_player_point(player_id)

    if point is None:
        await ctx.send(f"{ctx.author.mention} 등록되지 않은 사용자입니다. 먼저 `!참치 등록`을 해주세요.")
        return

    embed = discord.Embed(
        title="나의 포인트",
        description=f"{ctx.author.mention} 님의 현재 포인트는 **{point}** 입니다!",
        color=discord.Color.blurple()
    )
    embed.set_author(name="🐟 TunaBot 포인트 조회")
    embed.set_footer(text="🎣 TunaBot MyPage System | tuna.gg")

    await ctx.send(embed=embed)
