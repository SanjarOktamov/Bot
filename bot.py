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
    
    # Create the Application and pass it the bot's token
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

    # Start the Bot (asyncio ishga tushiriladi)
    import asyncio
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(application.run_polling())
