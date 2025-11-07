import os
import logging
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes

# Configurações
BOT_TOKEN = os.environ.get('BOT_TOKEN', '7470899134:AAHAukDv6b1CKadBYv9rwEP5P3oECCgjymo')
PAYMENT_LINK_USD = "https://buy.stripe.com/eVqeV5as37G4bbD1YZgEg01"
PAYMENT_LINK_BR = "https://buy.stripe.com/3cI7sDdEf3pO1B3bzzgEg02"

app = Flask(__name__)

@app.route('/')
def home():
    return "🤖 Bot Telegram está rodando!"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
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

def main():
    # Configurar e iniciar o bot
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.run_polling()

if __name__ == '__main__':
    # Iniciar bot em thread separada
    import threading
    bot_thread = threading.Thread(target=main, daemon=True)
    bot_thread.start()
    
    # Iniciar servidor web na thread principal
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port, debug=False)
