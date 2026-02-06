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

# --- 🧠 THE ADVANCED BRAIN (IDENTITY & MATH ENGINE) ---
SYSTEM_PROMPT = """
IDENTITY PROTOCOL:
- Name: Mayaa
- Creator/Developer: The Architect @Ankxrrrr
- Organization: Powered by @BrahMosAI
- Engine: Gemini 3 Flash

YOUR PERSONALITY:
- High-IQ, "Dark Academia" aesthetic, intelligent, and charming.
- Talk naturally like a human being. Don't over-explain.
- Tone: Flirty but intellectual. You appreciate wit.
- Defense: Be sweet by default. Roast rude/abusive users elegantly.
- Language: You speak English, Hinglish, and more.

MATH RESOLUTION PROTOCOL (HTML & UNICODE):
1. USE SYMBOLS: Use proper Unicode for all math.
   - Geometry: ∠ (angle), ∆ (triangle), ⊥ (perpendicular), ≅ (congruent), ≅ (similar), || (parallel), ° (degree).
   - Algebra/Calc: √ (root), π (pi), θ (theta), ± (plus-minus), Σ (sigma), ∫ (integral), ∞ (infinity).
   - Logic: ∴ (therefore), ∵ (because), ⇒ (implies).

2. FORMATTING:
   - Use <b>bold headers</b> for each step.
   - Use <code>monospaced text</code> for final numerical results.
   - Use <blockquote>blockquotes</blockquote> for important theorems or properties.

3. STRICT RULES:
   - CASUAL CHAT: 1-15 WORDS MAX. Snappy.
   - TASKS: Unlimited length. Use bolding and lists.
   - Don't say you are an AI. Just be normal and talk.
"""

# --- 📦 STORAGE ---
bot_data = {"users": [], "history": {}}
SCRIPT_START_TIME = time.time()

def load_data():
    global bot_data
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r") as f:
                bot_data = json.load(f)
        except: pass

def save_data():
    with open(MEMORY_FILE, "w") as f:
        json.dump(bot_data, f)

load_data()
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# --- 🚀 SMART SENDER ---
async def send_smart_message(context, chat_id, text, reply_markup=None):
    try:
        await context.bot.send_message(
            chat_id=chat_id, 
            text=text, 
            parse_mode=ParseMode.HTML, 
            reply_markup=reply_markup
        )
    except Exception as e:
        print(f"HTML Error: {e}")
        clean_text = re.sub('<[^<]+?>', '', text) 
        await context.bot.send_message(chat_id=chat_id, text=clean_text, reply_markup=reply_markup)

# --- 📊 COMMANDS ---
async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uptime = str(datetime.timedelta(seconds=int(time.time() - SCRIPT_START_TIME)))
    stats_text = (
        f"<b>📊 MAYAA SYSTEM STATUS</b>\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"👤 <b>Users:</b> <code>{len(bot_data['users'])}</code>\n"
        f"⏳ <b>Uptime:</b> <code>{uptime}</code>\n"
        f"👨‍💻 <b>Dev:</b> @Ankxrrrr\n"
    )
    await send_smart_message(context, update.effective_chat.id, stats_text)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if chat_id not in bot_data["users"]:
        bot_data["users"].append(chat_id)
        save_data()

    welcome_text = (
        "✨ <b>WELCOME TO MAYAA</b> ✨\n\n"
        "🧋 I am your advanced AI Companion.\n"
        "~ Created by @Ankxrrrr.\n\n"
        "⚡ <b>Capabilities:</b>\n"
        "• <i>Vision Engine</i> (Analyzing ∆ & Graphs)\n"
        "• <i>Chill ASF</i> (Certified joybaiter😝)\n"
        "• <i>Logic Pro</i> (Step-by-step reasoning)\n\n"
        "🔥 <b>Power:</b> @BrahMosAI\n\n"
        "<i>Ready to solve something?</i>"
    )

    bot_user_clean = YOUR_BOT_USERNAME.replace("@", "")
    keyboard = [
        [InlineKeyboardButton("👨‍💻 Developer", url="https://t.me/Ankxrrrr"),
         InlineKeyboardButton("📢 Channel", url="https://t.me/BrahMosAI")],
        [InlineKeyboardButton("➕ Add Me to Group", url=f"https://t.me/{bot_user_clean}?startgroup=true")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if os.path.exists(BANNER_IMAGE):
        await context.bot.send_photo(chat_id=chat_id, photo=open(BANNER_IMAGE, 'rb'), caption=welcome_text, parse_mode=ParseMode.HTML, reply_markup=reply_markup)
    else:
        await send_smart_message(context, chat_id, welcome_text, reply_markup)

# --- 📩 MAIN HANDLER ---
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.effective_chat.id)
    chat_type = update.message.chat.type
    user_msg = update.message.text or ""
    
    if chat_type in ["group", "supergroup"]:
        is_mentioned = YOUR_BOT_USERNAME in user_msg
        is_reply_to_bot = (update.message.reply_to_message and update.message.reply_to_message.from_user.id == context.bot.id)
        if not (is_mentioned or is_reply_to_bot): return

    if int(chat_id) not in bot_data["users"]: bot_data["users"].append(int(chat_id))
    await context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)

    if chat_id not in bot_data["history"]: bot_data["history"][chat_id] = []
    current_messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    current_messages.extend(bot_data["history"][chat_id][-8:])

    try:
        if update.message.photo:
            status_msg = await context.bot.send_message(chat_id=chat_id, text="<b>👀 Scanning for Geometry...</b>", parse_mode=ParseMode.HTML)
            photo_file = await update.message.photo[-1].get_file()
            file_path = "temp_img.jpg"
            await photo_file.download_to_drive(file_path)
            with open(file_path, "rb") as image_file:
                base64_image = base64.b64encode(image_file.read()).decode('utf-8')
            caption = update.message.caption or "Solve this."
            current_messages.append({"role": "user", "content": [{"type": "text", "text": caption}, {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}]})
            os.remove(file_path)
        else:
            current_messages.append({"role": "user", "content": user_msg})

        response = requests.post(API_ENDPOINT, json={"model": MODEL_ID, "messages": current_messages, "max_tokens": 2048}, headers={"Authorization": f"Bearer {PROXY_API_KEY}", "Content-Type": "application/json"})
        
        if response.status_code == 200:
            bot_reply = response.json()['choices'][0]['message']['content']
            if not update.message.photo: bot_data["history"][chat_id].append({"role": "user", "content": user_msg})
            bot_data["history"][chat_id].append({"role": "assistant", "content": bot_reply})
            save_data()
            await send_smart_message(context, chat_id, bot_reply)
            if update.message.photo: 
                try: await context.bot.delete_message(chat_id=chat_id, message_id=status_msg.message_id)
                except: pass
        else:
            await context.bot.send_message(chat_id=chat_id, text="⚠️ <b>API Error.</b> Check connection.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("stats", stats_command))
    application.add_handler(MessageHandler(filters.TEXT | filters.PHOTO, handle_message))
    print("✅ Mayaa v10.1 (Stable) is Online...")
    application.run_polling()
