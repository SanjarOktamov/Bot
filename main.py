import os
import logging
import threading
from telegram import Bot
from flask import Flask
from bot import run_bot

# Flask app yaratish
app = Flask(__name__)

# Logging sozlamalari
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

@app.route('/')
def home():
    return "Bot ishlayapti!"

def start_bot():
    logger.info("Bot threadini ishga tushirmoqda...")
    try:
        # Webhook o'chirilganiga ishonch hosil qilish
        token = os.environ.get("TELEGRAM_BOT_TOKEN")
        if not token:
            logger.error("TELEGRAM_BOT_TOKEN topilmadi!")
            return
            
        bot = Bot(token=token)
        bot.delete_webhook(drop_pending_updates=True)
        logger.info("Webhook o'chirildi va kutilayotgan yangilanishlar o'chirildi!")
        
        # Botni ishga tushirish
        logger.info("Bot ishga tushmoqda...")
        run_bot()
    except Exception as e:
        logger.error(f"Botda xatolik: {e}")
        import traceback
        logger.error(traceback.format_exc())

# Bot thread'ini ishga tushirish
bot_thread = None

@app.before_first_request
def start_bot_thread():
    global bot_thread
    if bot_thread is None or not bot_thread.is_alive():
        logger.info("Bot threadini yaratish...")
        bot_thread = threading.Thread(target=start_bot)
        bot_thread.daemon = True
        bot_thread.start()
        logger.info("Bot threadi ishga tushirildi!")

# Dastur bevosita ishga tushirilganda ham bot ishga tushsin
if __name__ == "__main__":
    # Botni ishga tushirish
    bot_thread = threading.Thread(target=start_bot)
    bot_thread.daemon = True
    bot_thread.start()
    
    # Flask serverini ishga tushirish
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
