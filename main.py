import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Get bot token
BOT_TOKEN = os.environ.get('BOT_TOKEN', '7470899134:AAHAukDv6b1CKadBYv9rwEP5P3oECCgjymo')
PAYMENT_LINK = "https://buy.stripe.com/eVqeV5as37G4bbD1YZgEg01"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    
    keyboard = [[InlineKeyboardButton("USD 17.99", url=PAYMENT_LINK)]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    message_text = """Attention: Follow the instructions

After clicking on the link:
• Put your information to facilitate the process (your TL name)
• When you make the payment, a message will appear with a link to the group - a kind of room for better management
• We will do our best to serve you as quickly as possible
• We hope you have fun

REMEMBER TO PUT THE CORRECT INFORMATION"""
    
    await update.message.reply_text(message_text, reply_markup=reply_markup)

def main() -> None:
    """Start the bot."""
    # Create the Application
    application = Application.builder().token(BOT_TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    
    print("Bot is starting...")
    
    # Start the Bot
    application.run_polling()

if __name__ == '__main__':
    main()
