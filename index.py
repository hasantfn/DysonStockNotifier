import requests
import json
from dotenv import load_dotenv
import os
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from apscheduler.schedulers.background import BackgroundScheduler
import asyncio
from datetime import datetime

load_dotenv()
bot_token = os.getenv("BOT_TOKEN")

user_data = {}

# Ürün kontrol fonksiyonu
def check_availability(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        script_tags = soup.find_all("script")
        for script in script_tags:
            if "Magento_Catalog/js/product/view/provider" in script.text:
                json_start = script.text.find('{')
                json_end = script.text.rfind('}') + 1
                json_data = script.text[json_start:json_end]
                
                try:
                    data = json.loads(json_data)
                    product_id = next(iter(data["*"]["Magento_Catalog/js/product/view/provider"]["data"]["items"].keys()))
                    is_available = data["*"]["Magento_Catalog/js/product/view/provider"]["data"]["items"][product_id]["is_available"]
                    return is_available
                except (json.JSONDecodeError, KeyError):
                    return None
    else:
        return None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Welcome! Please send me a product URL, and I'll start tracking its availability for you."
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    url = update.message.text
    chat_id = update.message.chat_id

    if chat_id in user_data and user_data[chat_id]["url"] == url:
        await update.message.reply_text("This product is already being tracked.")
        return

    if url.startswith("http"):
        is_available = check_availability(url)
        if is_available is None:
            await update.message.reply_text("Error: Could not fetch or parse product availability information.")
        elif is_available:
            await update.message.reply_text("The product is already available. No need to track this URL.")
        else:
            user_data[chat_id] = {"url": url, "status": "unavailable"}
            await update.message.reply_text(
                f"The product is currently unavailable. I will notify you when it becomes available:\n"
            )
    else:
        await update.message.reply_text("Please send a valid URL.")

async def scheduled_task(application: Application):
    print(f"[{datetime.now()}] Checking product availability for all tracked URLs...")
    for chat_id, data in list(user_data.items()):
        url = data["url"]
        current_status = data["status"]
        is_available = check_availability(url)

        if is_available is None:
            continue 

        if is_available and current_status == "unavailable":
            await application.bot.send_message(chat_id=chat_id, text=f"🔥🎉 GREAT NEWS! 🎉🔥\n\nThe product you've been tracking is NOW AVAILABLE! 🛒💥\n\nCheck it out before it's gone:\n{url}")
            user_data.pop(chat_id) 
        elif not is_available and current_status == "unavailable":
            continue

def main():
    application = Application.builder().token(bot_token).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    loop = asyncio.get_event_loop()
    
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        lambda: asyncio.run_coroutine_threadsafe(scheduled_task(application), loop),
        'interval',
        minutes=1
    )
    scheduler.start()
    
    print("Bot is running and will check product availability every 1 minute...")
    
    application.run_polling()

if __name__ == "__main__":
    main()
