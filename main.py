import os
import logging
import threading
import time
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
ping_thread_started = False

@app.route('/')
def home():
    global bot_thread, bot_started
    
    # Bot threadini tekshirish
    if bot_thread is None or not bot_thread.is_alive():
        logger.info("Bot threadi o'lik yoki yo'q, qaytadan ishga tushirish...")
        bot_thread = threading.Thread(target=run_bot)
        bot_thread.daemon = True
        bot_thread.start()
        bot_started = True
        logger.info("Bot threadi ishga tushirildi!")
        
    return "Bot ishlayapti! Server vaqti: " + time.strftime("%Y-%m-%d %H:%M:%S")

if __name__ == "__main__":
    # Bot threadni dastlab ishga tushirish
    logger.info("Dastlabki bot threadini ishga tushirish...")
    bot_thread = threading.Thread(target=run_bot)
    bot_thread.daemon = True
    bot_thread.start()
    bot_started = True
    
    # Flask serverini ishga tushirish
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=False)
