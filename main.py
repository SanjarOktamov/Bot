import os
import telegram
from bot import run_bot

# Webhook o'chirilganiga ishonch hosil qilish
try:
    bot = telegram.Bot(token=os.environ.get("TELEGRAM_BOT_TOKEN"))
    bot.delete_webhook(drop_pending_updates=True)
    print("Webhook o'chirildi va kutilayotgan yangilanishlar o'chirildi!")
except Exception as e:
    print(f"Webhook o'chirishda xatolik: {e}")

if __name__ == "__main__":
    # Botni ishga tushirish
    print("Bot ishga tushmoqda...")
    run_bot()
