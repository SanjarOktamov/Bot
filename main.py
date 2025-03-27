import os
import logging
import threading
import time
from flask import Flask, jsonify
from bot import run_bot, is_bot_running

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
    return """
    <html>
    <head>
        <title>Telegram Referral Bot</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }
            h1 { color: #4CAF50; }
            .container { max-width: 800px; margin: 0 auto; }
            .status { padding: 15px; border-radius: 5px; margin-bottom: 20px; }
            .success { background-color: #dff0d8; color: #3c763d; }
            .error { background-color: #f2dede; color: #a94442; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Telegram Referral Bot</h1>
            <div class="status success">
                <h3>Server statusi:</h3>
                <p>Ishlayapti! Vaqt: {time}</p>
            </div>
            <div class="status {bot_status_class}">
                <h3>Bot statusi:</h3>
                <p>{bot_status}</p>
                <p>Bot threadini tekshirish: {thread_status}</p>
            </div>
            <p>Bu sahifa faqat server ishlayotganini tekshirish uchun. Botdan foydalanish uchun Telegram'ga o'ting.</p>
        </div>
    </body>
    </html>
    """.format(
        time=time.strftime('%Y-%m-%d %H:%M:%S'),
        bot_status="Ishlayapti!" if is_bot_running() else "Ishlamayapti!",
        bot_status_class="success" if is_bot_running() else "error",
        thread_status="Faol" if bot_thread and bot_thread.is_alive() else "Faol emas"
    )

@app.route('/status')
def status():
    return jsonify({
        'server': 'running',
        'time': time.strftime('%Y-%m-%d %H:%M:%S'),
        'bot_thread_alive': bot_thread is not None and bot_thread.is_alive(),
        'bot_running': is_bot_running()
    })

# Bot threadini ishga tushirish
def start_bot():
    global bot_thread, bot_started
    
    if not bot_started:
        try:
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

if __name__ == "__main__":
    # Bot threadni dastlab ishga tushirish
    start_bot()
    
    # Flask serverini ishga tushirish
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=False)
