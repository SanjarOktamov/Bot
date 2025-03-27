import os
import logging
from dotenv import load_dotenv
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters

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

# Global Updater
updater = None

def run_bot():
    """Start the bot."""
    global updater
    
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
        # Create the Updater and pass it the bot's token
        logger.info("Updater yaratilmoqda...")
        updater = Updater(token)
        
        # Get the dispatcher to register handlers
        dispatcher = updater.dispatcher

        # Add handlers
        dispatcher.add_handler(CommandHandler("start", start_handler))
        dispatcher.add_handler(CommandHandler("help", help_handler))
        dispatcher.add_handler(CommandHandler("check", check_invites_handler))
        dispatcher.add_handler(CallbackQueryHandler(button_handler))
        
        # Handle deep linking for referrals
        dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_deep_linking))

        # Log all errors
        dispatcher.add_error_handler(error_handler)
        
        # Webhook o'chirish
        logger.info("Webhook o'chirilmoqda...")
        updater.bot.delete_webhook(drop_pending_updates=True)
        logger.info("Webhook muvaffaqiyatli o'chirildi!")
        
        # Start the Bot
        logger.info("Bot polling boshlanyapti...")
        updater.start_polling(drop_pending_updates=True)
        logger.info("Bot polling muvaffaqiyatli boshlandi")
        
    except Exception as e:
        logger.error(f"Bot ishga tushirishda xatolik: {e}")
        import traceback
        logger.error(traceback.format_exc())

def error_handler(update, context):
    """Log errors caused by updates."""
    logger.warning(f'Update "{update}" caused error "{context.error}"')

def is_bot_running():
    """Check if the bot is running."""
    global updater
    return updater is not None and updater.running

if __name__ == "__main__":
    run_bot()
