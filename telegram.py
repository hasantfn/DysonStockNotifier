import requests
import json
from dotenv import load_dotenv
import os
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from apscheduler.schedulers.background import BackgroundScheduler
import asyncio

load_dotenv()
bot_token = os.getenv("BOT_TOKEN")

# Global dictionary to store user URLs and chat IDs
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
                    return f"Product ID: {product_id}\nAvailable: {is_available}"
                except (json.JSONDecodeError, KeyError):
                    return "Error: Could not parse product availability information."
    else:
        return f"Error: Unable to fetch the page (Status code: {response.status_code})"

# Telegram bot fonksiyonları
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Welcome! Send me a product URL, and I'll start checking its availability every minute."
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    url = update.message.text
    chat_id = update.message.chat_id

    if url.startswith("http"):
        user_data[chat_id] = url
        await update.message.reply_text(
            f"The URL has been saved. I will now check its availability every minute:\n{url}"
        )
    else:
        await update.message.reply_text("Please send a valid URL.")

# Check availability for all users
async def scheduled_task(application: Application):
    for chat_id, url in user_data.items():
        availability = check_availability(url)
        await application.bot.send_message(chat_id=chat_id, text=f"Checked the product:\n{availability}")

def main():
    # Create the Application
    application = Application.builder().token(bot_token).build()
    
    # Command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Create an event loop reference
    loop = asyncio.get_event_loop()
    
    # Schedule periodic checks
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        lambda: asyncio.run_coroutine_threadsafe(scheduled_task(application), loop),
        'interval',
        minutes=1
    )
    scheduler.start()
    
    # Start the bot
    application.run_polling()

if __name__ == "__main__":
    main()