import os
import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Get bot token
BOT_TOKEN = os.environ.get('BOT_TOKEN', '7470899134:AAHAukDv6b1CKadBYv9rwEP5P3oECCgjymo')
PAYMENT_LINK = "https://buy.stripe.com/eVqeV5as37G4bbD1YZgEg01"

def start(update, context):
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
    
    update.message.reply_text(message_text, reply_markup=reply_markup)

def main():
    """Start the bot."""
    updater = Updater(BOT_TOKEN, use_context=True)
    
    # Get the dispatcher to register handlers
    dp = updater.dispatcher
    
    # Add command handler
    dp.add_handler(CommandHandler("start", start))
    
    # Start the Bot
    print("Bot is starting...")
    updater.start_polling()
    
    # Run the bot until you press Ctrl-C
    updater.idle()

if __name__ == '__main__':
    main()
