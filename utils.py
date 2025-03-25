import logging
from telegram import Update
from telegram.ext import ContextTypes

from database import db

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Kerakli kanallar ro'yxati
REQUIRED_CHANNELS = ['@kimyo_ess', '@kimyo_ess_video_yechimlari']

def create_referral_link(bot_username, user_id):
    """
    Create a referral link for the given user.
    
    Args:
        bot_username: Username of the bot
        user_id: Telegram user ID
        
    Returns:
        Referral link
    """
    return f"https://t.me/{bot_username}?start={user_id}"

async def check_user_subscribed_to_channels(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Foydalanuvchi barcha kerakli kanallarga a'zo bo'lganligini tekshiradi.
    
    Args:
        update: Telegram update
        context: CallbackContext
        
    Returns:
        tuple: (bool, list) - a'zo bo'lmagan kanallar ro'yxati
    """
    user_id = update.effective_user.id
    not_subscribed = []
    
    for channel in REQUIRED_CHANNELS:
        channel_id = channel  # kanal usernameni o'z ichiga oladi
        try:
            chat_member = await context.bot.get_chat_member(chat_id=channel_id, user_id=user_id)
            status = chat_member.status
            # python-telegram-bot kutubxonasida status oddiy string sifatida qaytariladi
            if status not in ["member", "administrator", "creator"]:
                not_subscribed.append(channel)
                logger.info(f"User {user_id} is not subscribed to {channel}")
        except Exception as e:
            logger.error(f"Error checking membership for {channel}: {e}")
            not_subscribed.append(channel)
    
    is_subscribed = len(not_subscribed) == 0
    return (is_subscribed, not_subscribed)

async def handle_deep_linking(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle messages that are not commands, mainly for debugging and helping users.
    """
    user_id = update.effective_user.id
    message_text = update.message.text
    
    # Check if the message might be a deep link
    if message_text.startswith('https://t.me/'):
        # If someone sends the bot's link, explain how to use it properly
        await update.message.reply_text(
            "Bu havolani do'stlaringizga yuboring, ularga havola orqali botga kirishlarini so'rang. "
            "Bu sizning taklifingiz hisoblanadi."
        )
    else:
        # For any other message, show a helpful message
        bot_username = context.bot.username
        referral_link = create_referral_link(bot_username, user_id)
        
        invites_count = db.get_invites_count(user_id)
        remaining = max(0, 5 - invites_count)
        
        await update.message.reply_text(
            f"Siz {invites_count} ta odamni taklif qildingiz. Maxfiy guruhga kirish uchun yana {remaining} ta odam taklif qiling.\n\n"
            f"Taklif havolangiz:\n<code>{referral_link}</code>\n\n"
            f"Taklif statistikangizni ko'rish uchun /check buyrug'ini yuboring.",
            parse_mode="HTML"
        )
