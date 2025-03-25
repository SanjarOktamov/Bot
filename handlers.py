import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

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

async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /start command."""
    user = update.effective_user
    chat_id = update.effective_chat.id
    
    # Foydalanuvchi kerakli kanallarga a'zo bo'lganligini tekshirish
    is_subscribed, not_subscribed_channels = await check_user_subscribed_to_channels(update, context)
    
    # Check if this user was referred by someone
    referrer_id = None
    if context.args and len(context.args) > 0:
        try:
            referrer_id = int(context.args[0])
            logger.info(f"User {user.id} was referred by {referrer_id}")
        except ValueError:
            # Invalid referrer ID format
            logger.warning(f"Invalid referrer ID format: {context.args[0]}")
    
    # Add the user to our database
    is_new_user = db.add_user(user.id, referrer_id)
    
    # Generate a referral link for this user
    bot_username = context.bot.username
    referral_link = create_referral_link(bot_username, user.id)
    
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
    
    # Check if the user already has enough invites
    invites_count = db.get_invites_count(user.id)
    
    if invites_count >= REQUIRED_INVITES and is_subscribed:
        # User has enough invites and is subscribed to all channels, send the secret group link
        await update.message.reply_text(
            REWARD_MESSAGE.format(secret_group_link=SECRET_GROUP_LINK),
            parse_mode="HTML"
        )
    else:
        # Prepare welcome message
        welcome_text = WELCOME_MESSAGE.format(
            user_name=user.first_name,
            referral_link=referral_link,
            required_invites=REQUIRED_INVITES,
            current_invites=invites_count
        )
        
        # Add message about subscription requirements if not subscribed
        if not is_subscribed:
            subscription_text = "\n⚠️ <b>Diqqat!</b> Siz quyidagi kanallarga a'zo bo'lishingiz kerak:\n"
            for channel in not_subscribed_channels:
                subscription_text += f"- {channel}\n"
            welcome_text += subscription_text
        
        await update.message.reply_text(
            welcome_text,
            reply_markup=reply_markup,
            parse_mode="HTML"
        )
    
    # If this is a referred user, check if the referrer has enough invites now
    if referrer_id and is_new_user and is_subscribed:
        # Also check if the referrer is subscribed to required channels
        referrer_chat_member = await context.bot.get_chat_member(chat_id=REQUIRED_CHANNELS[0], user_id=referrer_id)
        referrer_status = referrer_chat_member.status
        
        if referrer_status in ["member", "administrator", "creator"]:
            referrer_invites = db.get_invites_count(referrer_id)
            if referrer_invites >= REQUIRED_INVITES:
                # Referrer has enough invites, send them the secret group link
                try:
                    await context.bot.send_message(
                        chat_id=referrer_id,
                        text=REWARD_MESSAGE.format(secret_group_link=SECRET_GROUP_LINK),
                        parse_mode="HTML"
                    )
                    logger.info(f"Sent secret group link to user {referrer_id}")
                except Exception as e:
                    logger.error(f"Failed to send message to referrer {referrer_id}: {e}")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle inline keyboard button presses."""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    
    if query.data == 'check_invites':
        # Foydalanuvchi kerakli kanallarga a'zo bo'lganligini tekshirish
        is_subscribed, not_subscribed_channels = await check_user_subscribed_to_channels(update, context)
        
        invites_count = db.get_invites_count(user_id)
        
        # Create a referral link for this user
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
            await query.edit_message_text(
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
            
            await query.edit_message_text(
                text=progress_text,
                reply_markup=reply_markup,
                parse_mode="HTML"
            )

async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /help command."""
    user_id = update.effective_user.id
    bot_username = context.bot.username
    referral_link = create_referral_link(bot_username, user_id)
    
    # Foydalanuvchi kerakli kanallarga a'zo bo'lganligini tekshirish
    is_subscribed, not_subscribed_channels = await check_user_subscribed_to_channels(update, context)
    
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
    
    await update.message.reply_text(
        help_text,
        reply_markup=reply_markup,
        parse_mode="HTML"
    )

async def check_invites_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /check command to check current invites."""
    user_id = update.effective_user.id
    
    # Foydalanuvchi kerakli kanallarga a'zo bo'lganligini tekshirish
    is_subscribed, not_subscribed_channels = await check_user_subscribed_to_channels(update, context)
    
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
        await update.message.reply_text(
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
        
        await update.message.reply_text(
            progress_text,
            reply_markup=reply_markup,
            parse_mode="HTML"
              )
