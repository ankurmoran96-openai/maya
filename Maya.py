
# Main bot logic (integration helpers) with typing-action detector and multimodal extraction.
# This file provides typed handler signatures you can adapt to a real Telegram library.
#
# Key behavior:
# - Group chats: only respond if @mayaischalant_bot is mentioned or geninj trigger present.
# - Shows typing action during thinking and stops when message is sent.
# - Accepts optional callbacks for sending actions or messages so you can plug into python-telegram-bot / aiogram / telebot.

from typing import Dict, Any, List, Optional, Callable
import re

from config import (
    BOT_USERNAME,
    DEVELOPER_HANDLE,
    SUPPORT_HANDLE,
)
import heart

# Start message + inline keyboard
START_MESSAGE: str = (
    "yo! 🌟 I'm Maya — your low-key Gen-Z assistant. Short replies, witty vibes. "
    "Hit a button for support or dev info."
)

START_INLINE_KEYBOARD = [
    [{"text": "Support", "url": f"https://t.me/{SUPPORT_HANDLE.lstrip('@')}"}],
    [{"text": "Developer", "url": f"https://t.me/{DEVELOPER_HANDLE.lstrip('@')}"}],
]

# Attachment extractor (expects a dict structure from your Telegram lib)
def extract_attachments(message: Dict[str, Any]) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    if message.get("attachments"):
        return message.get("attachments")
    if "photo" in message:
        for p in message["photo"]:
            if isinstance(p, dict) and p.get("file_url"):
                out.append({"url": p["file_url"], "mime": "image/*"})
    if "audio" in message and isinstance(message["audio"], dict):
        if message["audio"].get("file_url"):
            out.append({"url": message["audio"]["file_url"], "mime": message["audio"].get("mime_type", "audio/*")})
    if "voice" in message and isinstance(message["voice"], dict):
        if message["voice"].get("file_url"):
            out.append({"url": message["voice"]["file_url"], "mime": "audio/ogg"})
    if "video" in message and isinstance(message["video"], dict):
        if message["video"].get("file_url"):
            out.append({"url": message["video"]["file_url"], "mime": "video/*"})
    if "document" in message and isinstance(message["document"], dict):
        if message["document"].get("file_url"):
            out.append({"url": message["document"]["file_url"], "mime": message["document"].get("mime_type", "application/octet-stream")})
    return out

# Group mention detection: in group/supergroup only respond when mentioned or geninj trigger present
def should_respond(chat_type: str, text: str) -> bool:
    if chat_type in ("group", "supergroup"):
        if not text:
            return False
        lowered = text.lower()
        mention_pattern = re.escape(BOT_USERNAME.lower().lstrip("@"))
        if re.search(rf"@?{mention_pattern}\b", lowered):
            return True
        # geninj detector: allow if message includes 'geninj' and either 'detect' or bot name
        if "geninj" in lowered and ("detect" in lowered or BOT_USERNAME.lower().lstrip("@") in lowered):
            return True
        return False
    return True

# on_start payload helper
def on_start(chat_id: int) -> Dict[str, Any]:
    return {
        "chat_id": chat_id,
        "text": START_MESSAGE,
        "reply_markup": {"inline_keyboard": START_INLINE_KEYBOARD},
    }

# Main message handler with optional integration callbacks:
# - send_action(chat_id: int, action: str) -> None  (e.g., send 'typing')
# - send_message(payload: Dict[str, Any]) -> None  (e.g., bot.send_message(**payload))
def on_message(
    message: Dict[str, Any],
    send_action: Optional[Callable[[int, str], None]] = None,
    send_message: Optional[Callable[[Dict[str, Any]], None]] = None,
    thinking_seconds: float = 0.25,
) -> Dict[str, Any]:
    """
    message: expected shape:
      {
        "chat": {"id": int, "type": "private"|"group"|"supergroup"},
        "from": {"id": int, "first_name": str, "username": str},
        "text": "message text",
        ... attachments ...
      }
    send_action: optional callback that sends a chat action (typing). signature send_action(chat_id, action)
    send_message: optional callback that actually sends the reply payload (dict with chat_id, text, ...).
    """
    chat = message.get("chat", {})
    chat_type = chat.get("type", "private")
    text = message.get("text", "") or ""
    user = message.get("from", {})
    user_id = str(user.get("id", "unknown"))
    user_profile = {"first_name": user.get("first_name"), "username": user.get("username")}

    if not should_respond(chat_type, text):
        return {}

    # Clean mention and commands
    clean_text = re.sub(rf"@?{re.escape(BOT_USERNAME.lstrip('@'))}\b[:,]?\s*", "", text, flags=re.IGNORECASE)
    if clean_text.strip().lower().startswith("/start"):
        payload = on_start(chat.get("id"))
        if send_message:
            send_message(payload)
            return payload
        return payload

    attachments = extract_attachments(message)

    chat_id = chat.get("id")

    # If a send_action callback is provided, indicate typing during thinking_step
    if send_action and isinstance(chat_id, int):
        try:
            # start typing
            send_action(chat_id, "typing")
        except Exception:
            pass

    # Call core handler (this includes the inner think_before_sense which sleeps briefly)
    reply_text = heart.handle_user_message(
        user_id=user_id,
        user_profile=user_profile,
        incoming_text=clean_text,
        attachments=attachments,
        thinking_seconds=thinking_seconds,
    )

    # After thinking finished, sending the reply stops the typing indicator in Telegram clients.
    payload = {"chat_id": chat_id, "text": reply_text or "¯\\_(ツ)_/¯"}

    if send_message:
        try:
            send_message(payload)
        except Exception:
            pass

    return payload
