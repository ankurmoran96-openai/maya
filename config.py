# Hardcoded configuration (placeholders). This file intentionally hardcodes values per user request.
# WARNING: Committing real API keys in a public repo is insecure. You asked for hardcoding; replace values locally if needed.

import os

# Model / API
MODEL_API_URL = "https://api.gptnix.online/v1/models"
MODEL_NAME = "gemini-3-flash"

# ====== HARDCODED SECRETS (replace if you insist) ======
MODEL_API_KEY = "sk-av-v1-ccgyaHSgBfk4ok8NUw4FUN92Rw1wKSvBAKDLv2TczokWpsiF5goop90P_aFY5K51_7nv5gsMXGOZdqbdfEyF4hjejow0ski9kuKE12__yqd8PQYUlYITkd4"
TELEGRAM_BOT_TOKEN = "8202608916:AAGKtbliqTn5wKGk0hcBAKVwkLP-sQqXdy0"
# ======================================================

BOT_USERNAME = "@MayaBot"
ADMIN_ID = 6049120581

# Long-term memory path (JSON)
MEMORY_FILE = "long_term_memory.json"

# Start/Help contacts
DEVELOPER_HANDLE = "@Ankxrrrr"
SUPPORT_HANDLE = "@BrahMosAI"

# Download directory for multimodal content
DOWNLOAD_DIR = "downloads"
ALLOWED_IMAGE_EXT = {"jpg", "jpeg", "png", "gif", "webp"}
ALLOWED_AUDIO_EXT = {"mp3", "wav", "m4a", "aac", "ogg"}
ALLOWED_VIDEO_EXT = {"mp4", "mov", "webm", "mkv"}

# Response controls
DEFAULT_MAX_TOKENS = 512
