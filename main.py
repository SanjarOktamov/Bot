import os
import logging
from telegram import Bot
from bot import run_bot
from flask import Flask, request

# Flask app yaratish
app = Flask(__name__)

# Logging sozlamalari
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Bot webhook yo'lini yaratish
@app.route("/")
def hello():
    return "Bot ishlayapti!"

# Bot dasturini ishga tushirish uchun funksiya
def start_bot():
    try:
        # Webhook o'chirilganiga ishonch hosil qilish
        token = os.environ.get("TELEGRAM_BOT_TOKEN")
        bot = Bot(token=token)
        bot.delete_webhook(drop_pending_updates=True)
        logger.info("Webhook o'chirildi va kutilayotgan yangilanishlar o'chirildi!")
        
        # Botni ishga tushirish
        run_bot()
    except Exception as e:
        logger.error(f"Botni ishga tushirishda xatolik: {e}")

# Bot dasturini alohida thread'da ishga tushirish
if __name__ == "__main__":
    import threading
    bot_thread = threading.Thread(target=start_bot)
    bot_thread.daemon = True
    bot_thread.start()
    
    # Flask serverini ishga tushirish
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
