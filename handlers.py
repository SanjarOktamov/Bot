import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext  # ContextTypes emas

from database import db
from messages import WELCOME_MESSAGE, HELP_MESSAGE, ALREADY_JOINED_MESSAGE, REFERRAL_LINK_MESSAGE, REWARD_MESSAGE, INVITES_PROGRESS_MESSAGE
from utils import create_referral_link, check_user_subscribed_to_channels, REQUIRED_CHANNELS

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Get the secret group link from environment variables
SECRET_GROUP_LINK = os.getenv("SECRET_GROUP_LINK", "https://t.me/+defaultSecretGroupLink")
REQUIRED_INVITES = 5

def start_handler(update: Update, context: CallbackContext):
    """Handle the /start command."""
    user_id = update.effective_user.id
    
    # Check if the user was referred by someone (command arguments contain referrer's ID)
    referrer_id = None
    if context.args and len(context.args) > 0:
        referrer_id = context.args[0]
        try:
            referrer_id = int(referrer_id)  # Convert to integer
        except ValueError:
            referrer_id = None
    
    # Add user to database (returns true if new)
    is_new_user = db.add_user(user_id, referrer_id)
    
    # If this user was already in the database, mark this as not a new registration
    if not is_new_user:
        logger.info(f"User {user_id} already exists in database")
    else:
        logger.info(f"New user {user_id} added to database with referrer {referrer_id}")
    
    # Foydalanuvchi kerakli kanallarga a'zo bo'lganligini tekshirish
    is_subscribed, not_subscribed_channels = check_user_subscribed_to_channels(update, context)
    
    # Generate a referral link for this user
    bot_username = context.bot.username
    referral_link = create_referral_link(bot_username, user_id)
    
    # Check how many users this user has invited
    invites_count = db.get_invites_count(user_id)
    
    # Create inline keyboard with referral link and channel subscription buttons
    keyboard = [
        [InlineKeyboardButton("Taklif Havolasini Ulashish", url=f"https://t.me/share/url?url={referral_link}")],
        [InlineKeyboardButton("Takliflarni Tekshirish", callback_data='check_invites')]
    ]
    
    # Add channel subscription buttons if user is not subscribed to all channels
    if not is_subscribed:
        for channel in REQUIRED_CHANNELS:
            if channel in not_subscribed_channels:
                channel_name = channel.replace('@', '')
                keyboard.append([InlineKeyboardButton(f"A'zo bo'lish: {channel}", url=f"https://t.me/{channel_name}")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Send the welcome message
    welcome_text = WELCOME_MESSAGE.format(
        required_invites=REQUIRED_INVITES
    )
    
    # Add message about subscription requirements if not subscribed
    if not is_subscribed:
        subscription_text = "\n⚠️ <b>Muhim:</b> Siz quyidagi kanallarga a'zo bo'lishingiz shart:\n"
        for channel in not_subscribed_channels:
            subscription_text += f"- {channel}\n"
        welcome_text += subscription_text
    
    update.message.reply_text(
        welcome_text,
        reply_markup=reply_markup,
        parse_mode="HTML"
    )

def help_handler(update: Update, context: CallbackContext):
    """Handle the /help command."""
    user_id = update.effective_user.id
    bot_username = context.bot.username
    referral_link = create_referral_link(bot_username, user_id)
    
    # Foydalanuvchi kerakli kanallarga a'zo bo'lganligini tekshirish
    is_subscribed, not_subscribed_channels = check_user_subscribed_to_channels(update, context)
    
    help_text = HELP_MESSAGE.format(
        referral_link=referral_link,
        required_invites=REQUIRED_INVITES
    )
    
    # Add message about subscription requirements if not subscribed
    if not is_subscribed:
        subscription_text = "\n⚠️ <b>Diqqat!</b> Siz quyidagi kanallarga a'zo bo'lishingiz kerak:\n"
        for channel in not_subscribed_channels:
            subscription_text += f"- {channel}\n"
        help_text += subscription_text
    
    # Create inline keyboard with referral link and channel subscription buttons
    keyboard = [
        [InlineKeyboardButton("Taklif Havolasini Ulashish", url=f"https://t.me/share/url?url={referral_link}")],
        [InlineKeyboardButton("Takliflarni Tekshirish", callback_data='check_invites')]
    ]
    
    # Add channel subscription buttons if user is not subscribed to all channels
    if not is_subscribed:
        for channel in REQUIRED_CHANNELS:
            if channel in not_subscribed_channels:
                channel_name = channel.replace('@', '')
                keyboard.append([InlineKeyboardButton(f"A'zo bo'lish: {channel}", url=f"https://t.me/{channel_name}")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    update.message.reply_text(
        help_text,
        reply_markup=reply_markup,
        parse_mode="HTML"
    )

def check_invites_handler(update: Update, context: CallbackContext):
    """Handle the /check command to check current invites."""
    user_id = update.effective_user.id
    
    # Foydalanuvchi kerakli kanallarga a'zo bo'lganligini tekshirish
    is_subscribed, not_subscribed_channels = check_user_subscribed_to_channels(update, context)
    
    invites_count = db.get_invites_count(user_id)
    
    # Generate a referral link for this user
    bot_username = context.bot.username
    referral_link = create_referral_link(bot_username, user_id)
    
    # Create inline keyboard with referral link and channel subscription buttons
    keyboard = [
        [InlineKeyboardButton("Taklif Havolasini Ulashish", url=f"https://t.me/share/url?url={referral_link}")],
    ]
    
    # Add channel subscription buttons if user is not subscribed to all channels
    if not is_subscribed:
        for channel in REQUIRED_CHANNELS:
            if channel in not_subscribed_channels:
                channel_name = channel.replace('@', '')
                keyboard.append([InlineKeyboardButton(f"A'zo bo'lish: {channel}", url=f"https://t.me/{channel_name}")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if invites_count >= REQUIRED_INVITES and is_subscribed:
        # User has enough invites and is subscribed to all required channels, send the secret group link
        update.message.reply_text(
            REWARD_MESSAGE.format(secret_group_link=SECRET_GROUP_LINK),
            reply_markup=reply_markup,
            parse_mode="HTML"
        )
    else:
        # Prepare progress message
        progress_text = INVITES_PROGRESS_MESSAGE.format(
            current_invites=invites_count,
            required_invites=REQUIRED_INVITES,
            remaining_invites=REQUIRED_INVITES - invites_count,
            referral_link=referral_link
        )
        
        # Add message about subscription requirements if not subscribed
        if not is_subscribed:
            subscription_text = "\n⚠️ <b>Diqqat!</b> Siz quyidagi kanallarga a'zo bo'lishingiz kerak:\n"
            for channel in not_subscribed_channels:
                subscription_text += f"- {channel}\n"
            progress_text += subscription_text
        
        update.message.reply_text(
            progress_text,
            reply_markup=reply_markup,
            parse_mode="HTML"
        )

def button_handler(update: Update, context: CallbackContext):
    """Handle inline keyboard button presses."""
    query = update.callback_query
    query.answer()
    
    user_id = query.from_user.id
    data = query.data
    
    if data == 'check_invites':
        # Get the number of people this user has invited
        invites_count = db.get_invites_count(user_id)
        
        # Foydalanuvchi kerakli kanallarga a'zo bo'lganligini tekshirish
        is_subscribed, not_subscribed_channels = check_user_subscribed_to_channels(update, context)
        
        # Generate a referral link for this user
        bot_username = context.bot.username
        referral_link = create_referral_link(bot_username, user_id)
        
        # Create inline keyboard with referral link and channel subscription buttons
        keyboard = [
            [InlineKeyboardButton("Taklif Havolasini Ulashish", url=f"https://t.me/share/url?url={referral_link}")],
        ]
        
        # Add channel subscription buttons if user is not subscribed to all channels
        if not is_subscribed:
            for channel in REQUIRED_CHANNELS:
                if channel in not_subscribed_channels:
                    channel_name = channel.replace('@', '')
                    keyboard.append([InlineKeyboardButton(f"A'zo bo'lish: {channel}", url=f"https://t.me/{channel_name}")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if invites_count >= REQUIRED_INVITES and is_subscribed:
            # User has enough invites and is subscribed to all required channels, send the secret group link
            query.edit_message_text(
                text=REWARD_MESSAGE.format(secret_group_link=SECRET_GROUP_LINK),
                reply_markup=reply_markup,
                parse_mode="HTML"
            )
        else:
            # Prepare progress message
            progress_text = INVITES_PROGRESS_MESSAGE.format(
                current_invites=invites_count,
                required_invites=REQUIRED_INVITES,
                remaining_invites=REQUIRED_INVITES - invites_count,
                referral_link=referral_link
            )
            
            # Add message about subscription requirements if not subscribed
            if not is_subscribed:
                subscription_text = "\n⚠️ <b>Diqqat!</b> Siz quyidagi kanallarga a'zo bo'lishingiz kerak:\n"
                for channel in not_subscribed_channels:
                    subscription_text += f"- {channel}\n"
                progress_text += subscription_text
            
            query.edit_message_text(
                text=progress_text,
                reply_markup=reply_markup,
                parse_mode="HTML"
    )
