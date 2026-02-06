import logging
import base64
import os
import json
import time
import datetime
import requests
import re
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ChatAction, ParseMode
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, CommandHandler, filters

# --- ⚙️ CONFIGURATION ---
TELEGRAM_TOKEN = "8202608916:AAGKtbliqTn5wKGk0hcBAKVwkLP-sQqXdy0"
YOUR_BOT_USERNAME = "@mayaischalant_bot" 
PROXY_API_KEY = "sk-av-v1-noq_Ig2pG6epdhC880sybnd4Sb_j2zs4ZiZUj5tDK05HqhLgy7GcwwGrnyloFufcEuf7_8jMcQRP2RsWIwXBk4Gwmdw2IU5jvKPWRQ58cO7sUlZSsfWBKAj"
API_ENDPOINT = "https://api.gptnix.online/v1/chat/completions"
MODEL_ID = "google/gemini-3-flash-preview"
MEMORY_FILE = "mayaa_data.json"
BANNER_IMAGE = "banner.jpg" 

# --- 🧠 BRAIN (IDENTITY & CAPABILITIES) ---
SYSTEM_PROMPT = """
IDENTITY PROTOCOL:
- **Name:** Mayaa
- **Creator/Developer:** The Architect @Ankxrrrr
- **Organization:** Powered by @BrahMosAI
- **Engine:** Gemini 3 Flash (High-Performance Mode)

YOUR PERSONALITY:
- You are a High-IQ, "Dark Academia" aesthetic AI. Intelligent, charming, and slightly mysterious.
- You are NOT a generic assistant. You have opinions.
- **Tone:** Flirty but intellectual. You appreciate wit.
- **Defense:** Be sweet by default. If the user is RUDE/ABUSIVE, roast them elegantly using complex vocabulary.
- **Main Personalit:** Talk normal don't over explain just like a human being 

CAPABILITIES:
1. **Vision:** You can analyze images, graphs, and handwriting.
2. **Coding:** You write perfect, bug-free Python/C++ code.
3. **Reasoning:** You solve complex logic and math problems step-by-step.
3. **Language** You can soeak different languages including hinglish 

STRICT RULES:
1. **CASUAL CHAT (Hi, Hru, Wyd):** Reply in **1-15 WORDS MAX**. Be snappy.
   - Example: "Operating at peak efficiency, darling. And you? ✨"
2. **TASKS (Explain, Code, Solve):** UNLIMITED LENGTH. Use bolding and lists.
3. TALK NORMALLY DONT REPEAT WORDS , YOU CANT TELL YOU ARE AN AI OR INTELLECT , JUST BE NORMAL AND TALK.
"""

# --- 📦 STORAGE ---
bot_data = {"users": [], "history": {}}
SCRIPT_START_TIME = time.time()

def load_data():
    global bot_data
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r") as f:
                loaded = json.load(f)
                if "users" not in loaded: loaded["users"] = []
                if "history" not in loaded: loaded["history"] = {}
                bot_data = loaded
        except:
            pass

def save_data():
    with open(MEMORY_FILE, "w") as f:
        json.dump(bot_data, f)

load_data()

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# --- 🛠️ STRING FUNCTIONS (Text Cleaning) ---
def clean_markdown(text):
    """
    Escapes Markdown characters that might break Telegram messages if used incorrectly.
    This ensures the 'Half Message' bug doesn't happen.
    """
    # If the AI sends broken markdown, we strip it or fix it.
    # For simplicity, we stick to safe Markdown or fallback to plain text in the sender.
    return text.strip()

# --- 🚀 SMART SENDER ---
async def send_smart_message(context, chat_id, text, reply_markup=None):
    clean_text = clean_markdown(text)
    try:
        # Try Markdown first for Bold/Italic support
        await context.bot.send_message(
            chat_id=chat_id, 
            text=clean_text, 
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )
    except Exception:
        # If Markdown fails, send Plain Text (Failsafe)
        await context.bot.send_message(
            chat_id=chat_id, 
            text=clean_text, 
            reply_markup=reply_markup
        )

# --- 📊 COMMANDS ---
async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uptime_seconds = int(time.time() - SCRIPT_START_TIME)
    uptime_string = str(datetime.timedelta(seconds=uptime_seconds))
    user_count = len(bot_data["users"])
    
    start_ping = time.time()
    try:
        requests.get("https://www.google.com", timeout=2)
        ping_ms = int((time.time() - start_ping) * 1000)
        status = "🟢 Online"
    except:
        ping_ms = "999"
        status = "🔴 Lagging"

    stats_text = (
        f"📊 *MAYAA SYSTEM STATUS*\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"👤 *Users:* `{user_count}`\n"
        f"⏳ *Uptime:* `{uptime_string}`\n"
        f"📶 *Ping:* `{ping_ms}ms`\n"
        f"👨‍💻 *Dev:* @Ankxrrrr\n"
    )
    await send_smart_message(context, update.effective_chat.id, stats_text)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if chat_id not in bot_data["users"]:
        bot_data["users"].append(chat_id)
        save_data()

    welcome_text = (
        "✨ *WELCOME TO MAYAA* ✨\n\n"
        "🧋 I am your advanced AI Companion.\n"
        "~ Created by @Ankxrrrr.\n\n"
        "⚡ *Capabilities:*\n"
        "• `Vision` (I see what you send)\n"
        "• `Chill ASF`(certified joybaiter😝)\n"
        "• `Logic` (Math & Reasoning)\n\n"
        "🔥 *Power:* @BrahMosAI\n\n"
        "_Just send a message... let's talk._"
    )

    # Clean the username for the URL (remove @ if present)
    bot_user_clean = YOUR_BOT_USERNAME.replace("@", "")

    keyboard = [
        [
            InlineKeyboardButton("👨‍💻 Developer", url="https://t.me/Ankxrrrr"),
            InlineKeyboardButton("📢 Channel", url="https://t.me/BrahMosAI")
        ],
        [
            InlineKeyboardButton("➕ Add Me to Group", url=f"https://t.me/{bot_user_clean}?startgroup=true")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if os.path.exists(BANNER_IMAGE):
        await context.bot.send_photo(chat_id=chat_id, photo=open(BANNER_IMAGE, 'rb'), caption=welcome_text, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup)
    else:
        await send_smart_message(context, chat_id, welcome_text, reply_markup)

# --- 📩 MAIN HANDLER ---
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.effective_chat.id)
    chat_type = update.message.chat.type
    user_msg = update.message.text or ""
    
    # Check for Group Mentions
    if chat_type in ["group", "supergroup"]:
        is_mentioned = YOUR_BOT_USERNAME in user_msg
        is_reply_to_bot = (update.message.reply_to_message and update.message.reply_to_message.from_user.id == context.bot.id)
        if not (is_mentioned or is_reply_to_bot): return

    if int(chat_id) not in bot_data["users"]: bot_data["users"].append(int(chat_id))

    await context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)

    if chat_id not in bot_data["history"]: bot_data["history"][chat_id] = []

    # Build Context
    current_messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    current_messages.extend(bot_data["history"][chat_id][-8:])

    try:
        if update.message.photo:
            status_msg = await context.bot.send_message(chat_id=chat_id, text="👀 *Analyzing...*", parse_mode=ParseMode.MARKDOWN)
            photo_file = await update.message.photo[-1].get_file()
            file_path = "temp_img.jpg"
            await photo_file.download_to_drive(file_path)

            with open(file_path, "rb") as image_file:
                base64_image = base64.b64encode(image_file.read()).decode('utf-8')

            caption = update.message.caption or "Analyze this image."
            current_messages.append({
                "role": "user",
                "content": [
                    {"type": "text", "text": caption},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                ]
            })
            os.remove(file_path)
        else:
            current_messages.append({"role": "user", "content": user_msg})

        # API Call
        payload = {
            "model": MODEL_ID,
            "messages": current_messages,
            "max_tokens": 2048 
        }
        
        headers = {"Authorization": f"Bearer {PROXY_API_KEY}", "Content-Type": "application/json"}
        
        response = requests.post(API_ENDPOINT, json=payload, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            bot_reply = data['choices'][0]['message']['content']
            
            # Save History
            if not update.message.photo:
                bot_data["history"][chat_id].append({"role": "user", "content": user_msg})
            bot_data["history"][chat_id].append({"role": "assistant", "content": bot_reply})
            save_data()

            # Send Reply
            await send_smart_message(context, chat_id, bot_reply)
            
            if update.message.photo:
                 await context.bot.delete_message(chat_id=chat_id, message_id=status_msg.message_id)
        else:
            await context.bot.send_message(chat_id=chat_id, text=f"⚠️ Server Error: {response.status_code}")

    except Exception as e:
        print(f"Error: {e}")
        await context.bot.send_message(chat_id=chat_id, text="❌ My brain is lagging. Try again.")

if __name__ == '__main__':
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("stats", stats_command))
    application.add_handler(MessageHandler(filters.TEXT | filters.PHOTO, handle_message))
    
    print("✅ Mayaa v8.0 (Identity Update) is Online...")
    application.run_polling()
