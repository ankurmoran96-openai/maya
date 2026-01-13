
# Hardcoded configuration (per request: secrets are written directly here).
# WARNING: this is insecure for public repos. You asked for hardcoding; this file reflects that.

# Model / API
MODEL_API_URL = "https://api.gptnix.online/v1/models"
MODEL_NAME = "google/gemini-3-flash-preview"  # updated model name

# ====== HARDCODED SECRETS (as requested) ======
MODEL_API_KEY = "sk-av-v1-ccgyaHSgBfk4ok8NUw4FUN92Rw1wKSvBAKDLv2TczokWpsiF5goop90P_aFY5K51_7nv5gsMXGOZdqbdfEyF4hjejow0ski9kuKE12__yqd8PQYUlYITkd4"
TELEGRAM_BOT_TOKEN = "8202608916:AAGKtbliqTn5wKGk0hcBAKVwkLP-sQqXdy0"
# =====================================================

BOT_USERNAME = "@mayaischalant_bot"  # updated bot username
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
ALLOWED_DOC_EXT = {"pdf", "docx", "txt", "pptx"}

# Response controls
DEFAULT_MAX_TOKENS = 512
