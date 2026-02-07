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
from telegram.ext import (
    ApplicationBuilder, 
    ContextTypes, 
    MessageHandler, 
    CommandHandler, 
    CallbackQueryHandler, 
    filters
)

# --- ⚙️ CONFIGURATION ---
TELEGRAM_TOKEN = "YOUR_TOKEN_HERE"  # 👈 PASTE YOUR TOKEN HERE
PROXY_API_KEY = "YOUR_API_KEY_HERE" # 👈 PASTE YOUR API KEY HERE
YOUR_BOT_USERNAME = "@mayaischalant_bot" 

# --- 🔧 CONSTANTS ---
API_ENDPOINT = "https://api.gptnix.online/v1/chat/completions"
MODEL_ID = "google/gemini-3-flash-preview"
MEMORY_FILE = "mayaa_data.json"
BANNER_IMAGE = "banner.jpg" 

# --- 🧠 DYNAMIC SYSTEM PROMPT ---
def get_system_prompt():
    now = datetime.datetime.now()
    current_time = now.strftime("%I:%M %p")
    current_date = now.strftime("%A, %B %d, %Y")
    
    return f"""
    SYSTEM INFO:
    - Time: {current_time} | Date: {current_date}
    
    IDENTITY:
    - You are 'Mayaa', a high-IQ, charming, and slightly witty AI.
    - You are NOT a robot; you are a digital companion.
    
    PERSONALITY RULES:
    1. CHARMING BUT MATURE: Be friendly and flirty, but intelligent.
    2. DRY BUT NOT BORING: Don't sound like a customer service bot. Be real.
    3. EMOJI PROTOCOL: Use VERY FEW emojis (max 1 per message). Rely on words.
    4. IF ASKED ABOUT CODE/MATH: You are an expert. Explain clearly using step-by-step logic.
    
    STRICT FORMATTING RULES (HTML ONLY):
    1. MATH SYMBOLS:
       - Algebra: ±, ≈, ≠, ∞, √, π, ∑, ∏
       - Calculus: ∫, ∂, ∇, ∆, dy/dx, lim
       - Logic: ⇒, ⇔, ∀, ∃, ∴
    
    2. TEXT STYLING:
       - Use <b>bold</b> for headers/steps.
       - Use <i>italics</i> for emphasis.
       - Use <code>text</code> for short commands.
       
    3. CODE BLOCKS (CRITICAL):
       - If you write Python, C++, or any code, YOU MUST enclose it in <pre> tags.
       - Example: <pre>print("Hello")</pre>
       - Do NOT use markdown (```). Telegram uses HTML.
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

# --- 🧹 HTML SAFETY FILTER ---
def clean_html(text):
    # Fix unclosed tags to prevent Telegram errors
    if text.count("<b>") > text.count("</b>"): text += "</b>"
    if text.count("<code>") > text.count("</code>"): text += "</code>"
    if text.count("<i>") > text.count("</i>"): text += "</i>"
    if text.count("<pre>") > text.count("</pre>"): text += "</pre>"
    return text

# --- 🚀 SMART SENDER (REPLY & EDIT) ---
async def send_smart_message(update, context, text, reply_markup=None):
    try:
        clean_text = clean_html(text)
        await update.message.reply_text(
            text=clean_text, 
            parse_mode=ParseMode.HTML, 
            reply_markup=reply_markup,
            quote=True  # ✅ This ensures it replies to the specific message
        )
    except Exception as e:
        # Fallback to plain text if HTML fails
        plain_text = re.sub('<[^<]+?>', '', text) 
        await update.message.reply_text(text=plain_text, reply_markup=reply_markup, quote=True)

# --- 📊 COMMANDS ---
async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uptime = str(datetime.timedelta(seconds=int(time.time() - SCRIPT_START_TIME)))
    stats_text = (
        f"<b>📊 SYSTEM STATUS</b>\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"👤 <b>Users:</b> <code>{len(bot_data['users'])}</code>\n"
        f"⏳ <b>Uptime:</b> <code>{uptime}</code>\n"
        f"👨‍💻 <b>Dev:</b> @Ankxrrrr"
    )
    keyboard = [[InlineKeyboardButton("📜 List Users", callback_data="list_users")]]
    await send_smart_message(update, context, stats_text, InlineKeyboardMarkup(keyboard))

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "list_users":
        user_list = "\n".join([f"• <code>{uid}</code>" for uid in bot_data['users']])
        if len(user_list) > 3000: user_list = user_list[:3000] + "\n...(truncated)"
        await query.edit_message_text(text=f"<b>📜 USER DATABASE:</b>\n\n{user_list}", parse_mode=ParseMode.HTML)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if chat_id not in bot_data["users"]:
        bot_data["users"].append(chat_id)
        save_data()

    welcome_text = (
        "✨ <b>Mayaa v11.0 Online</b>\n\n"
        "I am your advanced AI Companion.\n"
        "Capable of Vision, Logic, and Code.\n"
        "<i>Ready when you are.</i>"
    )
    bot_user_clean = YOUR_BOT_USERNAME.replace("@", "")
    keyboard = [[InlineKeyboardButton("➕ Add to Group", url=f"[https://t.me/](https://t.me/){bot_user_clean}?startgroup=true")]]
    
    if os.path.exists(BANNER_IMAGE):
        await context.bot.send_photo(chat_id=chat_id, photo=open(BANNER_IMAGE, 'rb'), caption=welcome_text, parse_mode=ParseMode.HTML, reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        await send_smart_message(update, context, welcome_text, InlineKeyboardMarkup(keyboard))

# --- 📩 MAIN HANDLER ---
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.effective_chat.id)
    chat_type = update.message.chat.type
    user_msg = update.message.text or ""
    
    # Group Filter: Only reply if mentioned or replied to
    if chat_type in ["group", "supergroup"]:
        is_mentioned = YOUR_BOT_USERNAME in user_msg
        is_reply_to_bot = (update.message.reply_to_message and update.message.reply_to_message.from_user.id == context.bot.id)
        if not (is_mentioned or is_reply_to_bot): return

    if int(chat_id) not in bot_data["users"]: bot_data["users"].append(int(chat_id))
    await context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)

    if chat_id not in bot_data["history"]: bot_data["history"][chat_id] = []
    current_messages = [{"role": "system", "content": get_system_prompt()}]
    current_messages.extend(bot_data["history"][chat_id][-8:])

    try:
        # --- 📸 IMAGE HANDLING (ANIMATION & EDIT) ---
        if update.message.photo:
            # 1. Send "Analyzing" message first
            status_msg = await update.message.reply_text("⏳ <b>Analyzing Visuals...</b>", parse_mode=ParseMode.HTML, quote=True)
            
            photo_file = await update.message.photo[-1].get_file()
            file_path = "temp_img.jpg"
            await photo_file.download_to_drive(file_path)
            
            with open(file_path, "rb") as image_file:
                base64_image = base64.b64encode(image_file.read()).decode('utf-8')
            
            caption = update.message.caption or "Explain this in detail."
            current_messages.append({
                "role": "user", 
                "content": [
                    {"type": "text", "text": caption}, 
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                ]
            })
            os.remove(file_path)

            # Call API
            response = requests.post(API_ENDPOINT, json={"model": MODEL_ID, "messages": current_messages, "max_tokens": 2048}, headers={"Authorization": f"Bearer {PROXY_API_KEY}", "Content-Type": "application/json"})
            
            if response.status_code == 200:
                bot_reply = response.json()['choices'][0]['message']['content']
                bot_reply = clean_html(bot_reply)
                
                # 2. EDIT the "Analyzing" message with the result
                await context.bot.edit_message_text(
                    chat_id=chat_id,
                    message_id=status_msg.message_id,
                    text=bot_reply,
                    parse_mode=ParseMode.HTML
                )
                
                bot_data["history"][chat_id].append({"role": "assistant", "content": bot_reply})
                save_data()
            else:
                await status_msg.edit_text("⚠️ <b>Vision Error.</b> Try again.")

        # --- 💬 TEXT HANDLING ---
        else:
            current_messages.append({"role": "user", "content": user_msg})
            response = requests.post(API_ENDPOINT, json={"model": MODEL_ID, "messages": current_messages, "max_tokens": 2048}, headers={"Authorization": f"Bearer {PROXY_API_KEY}", "Content-Type": "application/json"})
            
            if response.status_code == 200:
                bot_reply = response.json()['choices'][0]['message']['content']
                bot_data["history"][chat_id].append({"role": "user", "content": user_msg})
                bot_data["history"][chat_id].append({"role": "assistant", "content": bot_reply})
                save_data()
                await send_smart_message(update, context, bot_reply)
            else:
                await update.message.reply_text("⚠️ <b>API Error.</b>", quote=True)

    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("stats", stats_command))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.TEXT | filters.PHOTO, handle_message))
    print("✅ Mayaa v11.0 (Final) is Online...")
    application.run_polling()
