import os
import logging
from telegram import Bot
from flask import Flask
from bot import run_bot
import threading

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
    try:
        # Webhook o'chirilganiga ishonch hosil qilish
        token = os.environ.get("TELEGRAM_BOT_TOKEN")
        if not token:
            logger.error("TELEGRAM_BOT_TOKEN topilmadi!")
            return
            
        bot = Bot(token=token)
        bot.delete_webhook(drop_pending_updates=True)
        logger.info("Webhook o'chirildi!")
        
        # Botni ishga tushirish
        run_bot()
    except Exception as e:
        logger.error(f"Botda xatolik: {e}")

if __name__ == "__main__":
    # Botni alohida thread'da ishga tushirish
    bot_thread = threading.Thread(target=start_bot)
    bot_thread.daemon = True
    bot_thread.start()
    
    # Flask serverini ishga tushirish
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
