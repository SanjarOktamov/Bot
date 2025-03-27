import os
import logging
import threading
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

# Bot thread o'zgaruvchisi
bot_thread = None
bot_started = False

@app.route('/')
def home():
    global bot_thread, bot_started
    
    # Agar bot hali ishga tushirilmagan bo'lsa
    if not bot_started:
        try:
            # Botni alohida threadda ishga tushirish
            logger.info("Bot threadini ishga tushirish...")
            bot_thread = threading.Thread(target=run_bot)
            bot_thread.daemon = True
            bot_thread.start()
            bot_started = True
            logger.info("Bot threadi ishga tushirildi!")
        except Exception as e:
            logger.error(f"Bot threadini ishga tushirishda xatolik: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return f"Xatolik: {str(e)}"
    
    return "Bot ishlayapti!"

if __name__ == "__main__":
    # Bot threadni dastlab ishga tushirish
    logger.info("Dastlabki bot threadini ishga tushirish...")
    bot_thread = threading.Thread(target=run_bot)
    bot_thread.daemon = True
    bot_thread.start()
    bot_started = True
    
    # Flask serverini ishga tushirish
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
