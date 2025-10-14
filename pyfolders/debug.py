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
    """유니코드/커스텀 이모지 문자열 통일"""
    try:
        if hasattr(emoji, "id") and emoji.id:
            return f"{getattr(emoji, 'name', '?')}:{emoji.id}"
        return str(emoji)
    except Exception:
        return str(emoji)

def _shorten(text: str, limit: int) -> str:
    text = " ".join((text or "").split())  # 줄바꿈/여러 공백 정리
    return (text[:limit] + "…") if len(text) > limit else text

def _preview_message_content(msg: discord.Message, limit: int = 50) -> str:
    """
    메시지 미리보기:
    1) 일반 텍스트
    2) 임베드(제목 > 설명 > 첫 필드명/값)
    3) 첨부 파일
    4) 스티커
    5) (선택) 슬래시 명령어 이름 프리픽스
    """
    cmd = None
    try:
        inter = getattr(msg, "interaction", None)
        if inter:
            cmd = getattr(inter, "name", None) or getattr(inter, "command_name", None)
    except Exception:
        cmd = None

    if msg.content:
        base = msg.content
    elif msg.embeds:
        e = msg.embeds[0]
        base = e.title or e.description
        if not base and e.fields:
            f0 = e.fields[0]
            base = f"{(f0.name or '').strip()}: {(f0.value or '').strip()}".strip(": ").strip()
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
    """on_reaction_add에서 두 줄 로그 출력 + 관리자 DM"""
    try:
        msg = reaction.message
        guild = getattr(msg, "guild", None)
        guild_name = guild.name if guild else "DM"
        emoji_str = _emoji_to_str(reaction.emoji)
        preview = _preview_message_content(msg)

        log_text = f"[서버] {guild_name} | {user}\n{preview} | {emoji_str}"
        print(log_text)

        # 관리자 DM 발송
        if client and ADMIN_ID:
            try:
                admin = await client.fetch_user(ADMIN_ID)
                await admin.send(log_text)
            except discord.Forbidden:
                print("⚠️ 관리자 DM 전송 실패 (차단 또는 DM 비허용)")
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
    """
    on_raw_reaction_add 이벤트에서:
      1) 두 줄 로그 출력 (메시지 fetch)
      2) 관리자 DM 전송
      3) (선택) refresh_cb(reaction_like, user, client) 호출
    """
    try:
        if ignore_self and client.user and payload.user_id == client.user.id:
            return

        # 채널/메시지/유저 fetch
        channel = await client.fetch_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        user = await client.fetch_user(payload.user_id)
        guild = getattr(channel, "guild", None)

        guild_name = guild.name if guild else "DM"
        author_name = getattr(message.author, "name", "Unknown")
        emoji_str = _emoji_to_str(payload.emoji)
        preview = _preview_message_content(message)

        log_text = f"[서버] {guild_name} | {user}\n{preview} | {emoji_str}"
        print(log_text)

        # 관리자 DM 발송
        if ADMIN_ID:
            try:
                admin = await client.fetch_user(ADMIN_ID)
                await admin.send(log_text)
            except discord.Forbidden:
                print("⚠️ 관리자 DM 전송 실패 (차단 또는 DM 비허용)")
            except Exception as e:
                print(f"⚠️ 관리자 DM 전송 중 오류: {e}")

        # 선택 콜백 (예: 발로란트 새로고침)
        if callable(refresh_cb):
            class _ReactionLike:
                __slots__ = ("message", "emoji")
                def __init__(self, message, emoji):
                    self.message = message
                    self.emoji = emoji
            reaction_like = _ReactionLike(message, payload.emoji)
            await refresh_cb(reaction_like, user, client)

    except discord.Forbidden:
        print("[RAW_REACTION][ERROR] 권한 부족 (메시지 기록/채널 접근)")
    except discord.NotFound:
        print("[RAW_REACTION][ERROR] 대상 메시지/채널/유저를 찾을 수 없음")
    except Exception as e:
        print(f"[RAW_REACTION][ERROR] {e}")
