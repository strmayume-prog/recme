import os
import logging
from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Get bot token and webhook URL
BOT_TOKEN = os.environ.get('BOT_TOKEN', '7470899134:AAHAukDv6b1CKadBYv9rwEP5P3oECCgjymo')
PAYMENT_LINK_USD = "https://buy.stripe.com/eVqeV5as37G4bbD1YZgEg01"
PAYMENT_LINK_BR = "https://buy.stripe.com/3cI7sDdEf3pO1B3bzzgEg02"

# Create Flask app
app = Flask(__name__)

# Global variable to store the application
application = None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    
    keyboard = [
        [InlineKeyboardButton("USD 17.99", url=PAYMENT_LINK_USD)],
        [InlineKeyboardButton("BRL 0,50", url=PAYMENT_LINK_BR)]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    message_text = """Attention: Follow the instructions

After clicking on the link:
• Put your information to facilitate the process (your TL name)
• When you make the payment, a message will appear with a link to the group - a kind of room for better management
• We will do our best to serve you as quickly as possible
• We hope you have fun

REMEMBER TO PUT THE CORRECT INFORMATION"""
    
    await update.message.reply_text(message_text, reply_markup=reply_markup)

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Echo the user message."""
    await update.message.reply_text("Use /start to begin")

@app.route('/')
def home():
    return "🤖 Telegram Bot is running with Webhooks!"

@app.route('/webhook', methods=['POST'])
async def webhook():
    """Webhook endpoint for Telegram."""
    if application is None:
        return "Bot not initialized", 500
    
    try:
        json_data = await request.get_json()
        update = Update.de_json(json_data, application.bot)
        await application.process_update(update)
        return "OK"
    except Exception as e:
        logging.error(f"Error processing update: {e}")
        return "Error", 500

def setup_bot():
    """Setup the bot application."""
    global application
    
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    
    return application

@app.before_request
async def before_request():
    """Initialize bot before first request."""
    global application
    if application is None:
        application = setup_bot()

if __name__ == '__main__':
    # Setup bot
    application = setup_bot()
    
    # Get the Render URL (you'll need to set this as an environment variable)
    render_url = os.environ.get('RENDER_URL')
    
    if render_url:
        # Set webhook for production
        webhook_url = f"{render_url}/webhook"
        application.run_webhook(
            listen="0.0.0.0",
            port=int(os.environ.get("PORT", 10000)),
            webhook_url=webhook_url,
            secret_token='WEBHOOK_SECRET'  # Optional: add for security
        )
    else:
        # Fallback to polling for local development
        print("🤖 Starting bot with polling...")
        application.run_polling()
