# Main bot logic (example integration) with multimodal extraction. Adapt to your Telegram library.

from typing import Dict, Any, List
import re

from config import (
    BOT_USERNAME,
    DEVELOPER_HANDLE,
    SUPPORT_HANDLE,
)
import heart

# Start message + inline keyboard
START_MESSAGE = (
    "yo! 🌟 I'm Maya — your low-key Gen-Z assistant. Short replies, witty vibes. "
    "Hit a button for support or dev info."
)

START_INLINE_KEYBOARD = [
    [{"text": "Support", "url": f"https://t.me/{SUPPORT_HANDLE.lstrip('@')}"}],
    [{"text": "Developer", "url": f"https://t.me/{DEVELOPER_HANDLE.lstrip('@')}"}],
]

# Helper to extract attachments from the incoming message dict.
# Telegram APIs differ; adapt the extraction to your library. We expect a list of attachments:
# [{"url": "https://...", "mime": "audio/mpeg"}, ...]

def extract_attachments(message: Dict[str, Any]) -> List[Dict[str, Any]]:
    # If your framework provides file URLs via getFile, call that and pass the returned file URL here.
    if message.get("attachments"):
        return message.get("attachments")
    # For other libs, support 'photo', 'audio', 'video', 'document' keys with a 'file_url' field
    out = []
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

# Group mention detection: respond only when BOT_USERNAME is mentioned in groups

def should_respond(chat_type: str, text: str) -> bool:
    if chat_type in ("group", "supergroup"):
        if not text:
            return False
        lowered = text.lower()
        mention_pattern = re.escape(BOT_USERNAME.lower().lstrip("@"))
        if re.search(rf"@?{mention_pattern}\b", lowered):
            return True
        if "geninj" in lowered and ("detect" in lowered or BOT_USERNAME.lower().lstrip("@") in lowered):
            return True
        return False
    return True

# Handlers (pseudo-structures to be integrated with your bot framework)

def on_start(chat_id: int):
    return {
        "chat_id": chat_id,
        "text": START_MESSAGE,
        "reply_markup": {"inline_keyboard": START_INLINE_KEYBOARD},
    }


def on_message(message: Dict[str, Any]) -> Dict[str, Any]:
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
        return on_start(chat.get("id"))

    attachments = extract_attachments(message)
    reply_text = heart.handle_user_message(user_id, user_profile, clean_text, attachments=attachments)
    return {"chat_id": chat.get("id"), "text": reply_text}
