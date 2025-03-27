import os
import logging
import time
from telegram import Bot
from bot import run_bot

# Logging sozlamalari
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def main():
    # Webhook o'chirilganiga ishonch hosil qilish
    try:
        token = os.environ.get("TELEGRAM_BOT_TOKEN")
        bot = Bot(token=token)
        bot.delete_webhook(drop_pending_updates=True)
        logger.info("Webhook o'chirildi va kutilayotgan yangilanishlar o'chirildi!")
    except Exception as e:
        logger.error(f"Webhook o'chirishda xatolik: {e}")
    
    # Botni ishga tushirish
    logger.info("Bot ishga tushmoqda...")
    
    # Xatoliklar bilan ishlash
    retry_count = 0
    max_retries = 5
    
    while retry_count < max_retries:
        try:
            run_bot()
            break  # Agar xatolik bo'lmasa, tsikldan chiqing
        except Exception as e:
            retry_count += 1
            logger.error(f"Botda xatolik yuz berdi: {e}")
            logger.info(f"Qayta urinish {retry_count}/{max_retries}...")
            time.sleep(10)  # 10 soniya kutish
    
    logger.info("Bot muvaffaqiyatli ishga tushdi!")

if __name__ == "__main__":
    main()
