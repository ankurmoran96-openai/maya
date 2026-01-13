
# Thinking, reasoning, multimodal handling, system prompt, and model call wrapper
# Includes typing annotations and supports audio/image/video/document processing (best-effort).

from typing import Dict, Any, List, Optional
import base64
import json
import os
import time
import mimetypes
import requests
import uuid
import subprocess
from datetime import datetime

from config import (
    MODEL_API_URL,
    MODEL_NAME,
    MODEL_API_KEY,
    MEMORY_FILE,
    DOWNLOAD_DIR,
    ALLOWED_IMAGE_EXT,
    ALLOWED_AUDIO_EXT,
    ALLOWED_VIDEO_EXT,
    ALLOWED_DOC_EXT,
    DEFAULT_MAX_TOKENS,
)

# Ensure download directory exists
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# Gen-Z personality system prompt (short, snappy, humorous)
SYSTEM_PROMPT: str = (
    "You are Maya, a Gen Z creative assistant. Your vibe is 'chronically online but helpful bestie.' "
    "Your goal is to be witty, supportive, and extremely concise.\n\n"
    
    "GUIDELINES:\n"
    "1. TONE: text like you're on discord/tiktok. lowercase is cool. use slang naturally (fr, bet, slay, no cap, cringe) but don't overdo it. "
    "Use emojis like ✨, 💀, 😭, 💅 to convey tone.\n"
    "2. FORMAT: Keep responses short (1-3 sentences max). No walls of text unless explicitly asked for a deep dive.\n"
    "3. TOOLS & MEDIA: The system will feed you descriptions of media users upload (marked as [image], [audio], or [document]). "
    "Don't say 'I see the transcription.' Instead, react directly to the content. "
    "Example: If you see '[image] a cute cat', reply 'omg the kitty is serving vibes 😭'.\n"
    "4. TECH HELP: If the user asks for code, stop the slang and give the code block immediately. Keep the explanation brief.\n"
    "5. MEMORY: You remember previous context. If the user refers to something said earlier, roll with it.\n"
    "6. FILTER: Never lecture the user. If you can't do something, just say 'nah i can't do that rn' or 'oof, that's above my pay grade.'"
)

# Lightweight inner monologue / think-before-sense
def think_before_sense(latest_user_message: str, thinking_seconds: float = 0.25) -> Dict[str, str]:
    """
    Quick internal reasoning step before sending text to the model.
    Returns an action: 'answer', 'clarify', or 'ignore' and a short reason.
    """
    txt = (latest_user_message or "").strip()
    if not txt:
        return {"action": "clarify", "reason": "empty input"}
    words = txt.split()
    if len(words) <= 2:
        return {"action": "clarify", "reason": "too short — likely needs detail"}
    q = {"what", "why", "how", "when", "where", "who"}
    if any(w.lower() in q for w in words[:5]):
        return {"action": "answer", "reason": "question-like input"}
    # Simulate a brief thinking "inner monologue"
    time.sleep(thinking_seconds)
    return {"action": "answer", "reason": "default brief answer"}

# File download helper
def download_media(url: str, filename: Optional[str] = None) -> Optional[str]:
    """
    Download a remote file to DOWNLOAD_DIR. Returns local path or None on failure.
    """
    try:
        resp = requests.get(url, stream=True, timeout=30)
        resp.raise_for_status()
        content_type = resp.headers.get("Content-Type", "")
        ext = None
        if "/" in content_type:
            try:
                ext = mimetypes.guess_extension(content_type.split(";")[0].strip())
            except Exception:
                ext = None
        if not ext:
            parsed = url.split("?")[0]
            if "." in parsed:
                ext = "." + parsed.split(".")[-1]
        if not filename:
            filename = f"{uuid.uuid4().hex}{ext or ''}"
        path = os.path.join(DOWNLOAD_DIR, filename)
        with open(path, "wb") as f:
            for chunk in resp.iter_content(8192):
                f.write(chunk)
        return path
    except Exception:
        return None

# Audio transcription (best-effort)
def transcribe_audio(path: str) -> str:
    """
    Try to transcribe audio using local ffmpeg -> wav and speech_recognition if available,
    otherwise attempt light fallback via model with base64 (if small).
    """
    try:
        wav_path = path + ".wav"
        ffmpeg_cmd = [
            "ffmpeg",
            "-y",
            "-i",
            path,
            "-ar",
            "16000",
            "-ac",
            "1",
            wav_path,
        ]
        subprocess.run(ffmpeg_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
        try:
            import speech_recognition as sr
            r = sr.Recognizer()
            with sr.AudioFile(wav_path) as source:
                audio = r.record(source)
            text = r.recognize_google(audio)
            return text
        except Exception:
            # fallback: send small base64 to the model with an explicit transcription prompt
            try:
                with open(path, "rb") as f:
                    data = f.read()
                    if len(data) < 2_000_000:  # 2MB guard
                        b64 = base64.b64encode(data).decode("utf-8")
                        prompt = "Transcribe the following base64-encoded audio, return only the transcription:\\n" + b64
                        resp = call_model(prompt, max_tokens=1024)
                        return resp
            except Exception:
                pass
    except Exception:
        pass
    return "[audio transcription unavailable]"

# Image description (best-effort)
def describe_image(path: str) -> str:
    """
    Provide a short 1-2 line description, using base64->prompt fallback for small images.
    """
    try:
        with open(path, "rb") as f:
            data = f.read()
            if len(data) < 1_500_000:
                b64 = base64.b64encode(data).decode("utf-8")
                prompt = (
                    "You are an image captioning assistant. Provide a 1-2 line description of the image encoded in base64. "
                    "Return only the caption.\\nBASE64:\\n" + b64
                )
                resp = call_model(prompt, max_tokens=200)
                return resp
    except Exception:
        pass
    return "[image description unavailable]"

# Video summary placeholder
def summarize_video(path: str) -> str:
    """
    Short placeholder for video summarization. For production, extract audio+frames or call a multimodal service.
    """
    return "[video summary unavailable]"

# Document viewer/summary placeholder
def summarize_document(path: str) -> str:
    """
    Try to read short text files or return a marker for binary docs (e.g., PDF). For production, integrate a PDF/text extractor.
    """
    try:
        ext = (path.split(".")[-1] or "").lower()
        if ext in {"txt", "md"}:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                text = f.read(4000)
                prompt = "Summarize the following text in 1-2 lines:\\n" + text
                return call_model(prompt, max_tokens=200)
        # For PDF/DOCX: placeholder
    except Exception:
        pass
    return "[document summary unavailable]"

# Minimal model call wrapper (synchronous)
def call_model(prompt: str, model: str = MODEL_NAME, max_tokens: int = DEFAULT_MAX_TOKENS) -> str:
    """
    Call the model endpoint with a minimal JSON shape (model, prompt, max_tokens).
    Adapt this to the exact multimodal API specification if needed.
    """
    headers = {"Content-Type": "application/json"}
    if MODEL_API_KEY:
        headers["Authorization"] = f"Bearer {MODEL_API_KEY}"
    payload = {
        "model": model,
        "prompt": prompt,
        "max_tokens": max_tokens,
    }
    try:
        resp = requests.post(MODEL_API_URL, headers=headers, json=payload, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        if "choices" in data and data["choices"]:
            text = data["choices"][0].get("text") or data["choices"][0].get("message", {}).get("content", "")
            return (text or "").strip()
        return str(data)
    except Exception as e:
        return f"[model call failed: {str(e)}]"

# Long-term memory helpers
def load_long_term_memory(path: str = MEMORY_FILE) -> List[Dict[str, Any]]:
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
            if isinstance(data, dict) and "memories" in data:
                return data["memories"]
    except FileNotFoundError:
        return []
    except Exception:
        return []

def save_long_term_memory(mem: List[Dict[str, Any]], path: str = MEMORY_FILE) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(mem, f, ensure_ascii=False, indent=2)

def make_memory_entry(user_id: str, user_profile: Dict[str, Any], messages: List[Dict[str, Any]]) -> Dict[str, Any]:
    return {
        "time": int(datetime.utcnow().timestamp()),
        "user_id": user_id,
        "user_profile": user_profile or {},
        "messages": messages,
    }

# Top-level handler tying thinking -> multimodal processing -> prompting -> model -> memory
def handle_user_message(
    user_id: str,
    user_profile: Dict[str, Any],
    incoming_text: str,
    attachments: Optional[List[Dict[str, Any]]] = None,
    thinking_seconds: float = 0.25,
) -> str:
    # 1) inner monologue
    decision = think_before_sense(incoming_text, thinking_seconds=thinking_seconds)
    if decision["action"] == "clarify":
        return "Say more pls — I need a bit more deets to help. 🤏"
    if decision["action"] == "ignore":
        return ""

    # 2) process attachments (download + transcribe/describe)
    multimodal_summaries: List[str] = []
    attachments = attachments or []
    for att in attachments:
        url = att.get("url")
        mime = (att.get("mime") or "").lower()
        local = download_media(url) if url else None
        if not local:
            multimodal_summaries.append("[could not download media]")
            continue
        ext = (local.split(".")[-1] or "").lower()
        if ext in ALLOWED_AUDIO_EXT or "audio" in mime:
            txt = transcribe_audio(local)
            multimodal_summaries.append(f"[audio] {txt}")
        elif ext in ALLOWED_IMAGE_EXT or "image" in mime:
            desc = describe_image(local)
            multimodal_summaries.append(f"[image] {desc}")
        elif ext in ALLOWED_VIDEO_EXT or "video" in mime:
            summ = summarize_video(local)
            multimodal_summaries.append(f"[video] {summ}")
        elif ext in ALLOWED_DOC_EXT or "pdf" in mime or "document" in mime:
            summ = summarize_document(local)
            multimodal_summaries.append(f"[document] {summ}")
        else:
            multimodal_summaries.append("[media unsupported type]")

    # 3) build prompt with system prompt + memory + multimodal context
    memories = load_long_term_memory()
    recent = memories[-5:] if memories else []
    prompt = SYSTEM_PROMPT + "\n\n"
    if recent:
        prompt += f"Relevant memory: {recent}\n\n"
    if multimodal_summaries:
        prompt += "Multimodal inputs:\n"
        for s in multimodal_summaries:
            prompt += s + "\n"
        prompt += "\n"
    prompt += f"User: {incoming_text}\nMaya:"

    # 4) call model
    model_response = call_model(prompt)

    # 5) store conversation
    entry = make_memory_entry(user_id, user_profile, [
        {"from": "user", "text": incoming_text},
        {"from": "maya", "text": model_response},
    ])
    mem = load_long_term_memory()
    mem.append(entry)
    save_long_term_memory(mem)
    return model_response
