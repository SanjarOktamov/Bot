import os
import logging
import asyncio
from dotenv import load_dotenv
from telegram import Bot
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters

from handlers import start_handler, button_handler, help_handler, check_invites_handler
from utils import handle_deep_linking

# Load environment variables from .env file
load_dotenv()

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG  # Changed to DEBUG for more verbose logging
)
logger = logging.getLogger(__name__)

def run_bot():
    """Start the bot."""
    # Get the token from environment variables
    logger.debug("Trying to load environment variables")
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    logger.debug(f"Token found: {bool(token)}")
    
    if not token:
        logger.error("No token provided. Set the TELEGRAM_BOT_TOKEN environment variable.")
        return

    # Get the secret group link from environment variables
    secret_group_link = os.getenv("SECRET_GROUP_LINK", "https://t.me/+defaultSecretGroupLink")
    
    try:
        # Create the Application and pass it the bot's token
        logger.info("Application yaratilmoqda...")
        application = Application.builder().token(token).build()

        # Add handlers
        application.add_handler(CommandHandler("start", start_handler))
        application.add_handler(CommandHandler("help", help_handler))
        application.add_handler(CommandHandler("check", check_invites_handler))
        application.add_handler(CallbackQueryHandler(button_handler))
        
        # Handle deep linking for referrals
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_deep_linking))

        # Log all errors
        application.add_error_handler(error_handler)

        # Webhook o'chirish
        logger.info("Webhook o'chirilmoqda...")
        application.bot.delete_webhook(drop_pending_updates=True)
        logger.info("Webhook muvaffaqiyatli o'chirildi!")
        
        # Start the Bot
        logger.info("Bot polling boshlanyapti...")
        application.run_polling(
            poll_interval=1.0,
            drop_pending_updates=True,
            allowed_updates=["message", "callback_query"]
        )
        
    except Exception as e:
        logger.error(f"Bot ishga tushirishda xatolik: {e}")
        import traceback
        logger.error(traceback.format_exc())

def error_handler(update, context):
    """Log errors caused by updates."""
    logger.warning(f'Update "{update}" caused error "{context.error}"')

if __name__ == "__main__":
    run_bot()
