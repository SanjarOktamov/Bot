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
    global bot_thread, bot_started, ping_thread_started
    
    # Ping threadini birinchi marta ishga tushirish
    if not ping_thread_started:
        setup_ping()
        ping_thread_started = True
    
    # Bot threadini tekshirish
    if bot_thread is None or not bot_thread.is_alive():
        logger.info("Bot threadi o'lik yoki yo'q, qaytadan ishga tushirish...")
        start_bot_thread()
        
    return "Bot ishlayapti! Server vaqti: " + time.strftime("%Y-%m-%d %H:%M:%S")

def start_bot_thread():
    global bot_thread, bot_started
    try:
        # Eski threadni o'chirish
        if bot_thread is not None:
            logger.info("Eski bot threadi mavjud, yangi threadni boshlash...")
            
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

# Har 5 daqiqada botni tekshirish
def setup_ping():
    def ping_app():
        while True:
            try:
                # Thread active ekanligini tekshirish
                global bot_thread
                if bot_thread is None or not bot_thread.is_alive():
                    logger.info("Bot threadi o'lik, qaytadan ishga tushirish...")
                    start_bot_thread()
                
                # 5 daqiqa kutish
                time.sleep(300)
            except Exception as e:
                logger.error(f"Ping threadida xatolik: {e}")
                time.sleep(60)  # Xatolik yuz berganda 1 daqiqa kutish
                
    ping_thread = threading.Thread(target=ping_app)
    ping_thread.daemon = True
    ping_thread.start()
    logger.info("Ping thread boshlandi!")

if __name__ == "__main__":
    # Bot threadni dastlab ishga tushirish
    logger.info("Dastlabki bot threadini ishga tushirish...")
    start_bot_thread()
    
    # Ping threadni ham ishga tushirish
    setup_ping()
    
    # Flask serverini ishga tushirish
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=False)
