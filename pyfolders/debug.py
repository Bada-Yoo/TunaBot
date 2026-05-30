# pyfolders/debug.py
import os
import discord
from typing import Union, Optional, Callable
from dotenv import load_dotenv

# -------- 환경 변수 로드 --------
load_dotenv()
ADMIN_ID = os.getenv("DISCORD_ADMIN_ID")
if ADMIN_ID:
    ADMIN_ID = int(ADMIN_ID)


# -------- 내부 유틸 --------
def _emoji_to_str(emoji) -> str:
    try:
        if hasattr(emoji, "id") and emoji.id:
            return f"{getattr(emoji, 'name', '?')}:{emoji.id}"
        return str(emoji)
    except Exception:
        return str(emoji)


def _shorten(text: str, limit: int) -> str:
    text = " ".join((text or "").split())
    return (text[:limit] + "…") if len(text) > limit else text


def _preview_message_content(msg: discord.Message, limit: int = 50) -> str:
    cmd = None

    try:
        metadata = getattr(msg, "interaction_metadata", None)

        if metadata:
            cmd = (
                getattr(metadata, "name", None)
                or getattr(metadata, "command_name", None)
            )
    except Exception:
        pass

    if msg.content:
        base = msg.content

    elif msg.embeds:
        e = msg.embeds[0]

        base = e.title or e.description

        if not base and e.fields:
            f0 = e.fields[0]
            base = (
                f"{(f0.name or '').strip()}: "
                f"{(f0.value or '').strip()}"
            ).strip(": ").strip()

        if not base and e.footer and e.footer.text:
            base = e.footer.text

        base = f"[EMBED] {base or ''}".strip()

    elif msg.attachments:
        names = ", ".join(a.filename for a in msg.attachments[:3])
        more = "" if len(msg.attachments) <= 3 else f" 외 {len(msg.attachments)-3}개"
        base = f"[첨부 {len(msg.attachments)}개] {names}{more}"

    elif msg.stickers:
        names = ", ".join(s.name for s in msg.stickers[:3])
        more = "" if len(msg.stickers) <= 3 else f" 외 {len(msg.stickers)-3}개"
        base = f"[스티커] {names}{more}"

    else:
        base = "— (첨부/임베드 메시지) —"

    if cmd:
        base = f"/{cmd} · {base}"

    return _shorten(base, limit)


# -------- 공개 함수: 캐시 있는 on_reaction_add 전용 --------
async def log_reaction_simple(
    reaction: discord.Reaction,
    user: Union[discord.User, discord.Member],
    client: Optional[discord.Client] = None,
):
    try:
        msg = reaction.message

        guild = getattr(msg, "guild", None)
        guild_name = guild.name if guild else "DM"

        emoji_str = _emoji_to_str(reaction.emoji)
        preview = _preview_message_content(msg)

        log_text = f"[서버] {guild_name} | {user}\n{preview} | {emoji_str}"
        print(log_text)

        if client and ADMIN_ID:
            try:
                admin = await client.fetch_user(ADMIN_ID)
                await admin.send(log_text)

            except discord.Forbidden:
                pass

            except Exception as e:
                print(f"⚠️ 관리자 DM 전송 중 오류: {e}")

    except Exception as e:
        print(f"[REACTION][ERROR] {e}")


# -------- 공개 함수: 캐시 불문 on_raw_reaction_add 처리 --------
async def handle_raw_reaction_add(
    client: discord.Client,
    payload: discord.RawReactionActionEvent,
    refresh_cb: Optional[Callable] = None,
    ignore_self: bool = True,
):
    try:
        if ignore_self and client.user and payload.user_id == client.user.id:
            return

        user = await client.fetch_user(payload.user_id)

        try:
            channel = await client.fetch_channel(payload.channel_id)
            message = await channel.fetch_message(payload.message_id)

            guild = getattr(channel, "guild", None)
            guild_name = guild.name if guild else "DM"

            emoji_str = _emoji_to_str(payload.emoji)
            preview = _preview_message_content(message)

            log_text = f"[서버] {guild_name} | {user}\n{preview} | {emoji_str}"
            print(log_text)

            if callable(refresh_cb):

                class _ReactionLike:
                    __slots__ = ("message", "emoji")

                    def __init__(self, message, emoji):
                        self.message = message
                        self.emoji = emoji

                reaction_like = _ReactionLike(
                    message,
                    payload.emoji
                )

                await refresh_cb(
                    reaction_like,
                    user,
                    client
                )

        except (discord.Forbidden, discord.NotFound):
            return

    except Exception as e:
        print(f"[RAW_REACTION][ERROR] {e}")