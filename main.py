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

@app.route('/')
def home():
    global bot_thread, bot_started
    
    # Bot ishga tushganini tekshirish
    if bot_started:
        bot_status = "Bot ishlayapti!" if bot_thread and bot_thread.is_alive() else "Bot to'xtab qolgan!"
    else:
        bot_status = "Bot hali ishga tushmagan!"
        
    return f"Bot statusi: {bot_status} Server vaqti: {time.strftime('%Y-%m-%d %H:%M:%S')}"

# Bot threadini ishga tushirish
def start_bot():
    global bot_thread, bot_started
    
    if not bot_started:
        logger.info("Bot threadini ishga tushirish...")
        bot_thread = threading.Thread(target=run_bot)
        bot_thread.daemon = True
        bot_thread.start()
        bot_started = True
        logger.info("Bot threadi ishga tushirildi!")

if __name__ == "__main__":
    # Bot threadni dastlab ishga tushirish
    start_bot()
    
    # Flask serverini ishga tushirish
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=False)
