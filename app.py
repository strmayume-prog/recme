import os
import logging
from datetime import datetime, timedelta
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from apscheduler.schedulers.background import BackgroundScheduler
import requests

# Carregar variáveis de ambiente
load_dotenv()

# Configuração
BOT_TOKEN = os.getenv('BOT_TOKEN')
PAYPAL_EMAIL = os.getenv('PAYPAL_EMAIL')
GROUP_CHAT_ID = os.getenv('GROUP_CHAT_ID')  # ID do grupo onde os usuários serão adicionados
WEBHOOK_URL = os.getenv('WEBHOOK_URL')  # URL do seu app no Render
PORT = int(os.getenv('PORT', 10000))

# Inicializar Flask app
app = Flask(__name__)

# Dicionário para armazenar usuários ativos
active_users = {}

# Configurar logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler para comando /start"""
    keyboard = [
        [InlineKeyboardButton("💰 Assinar (1 USD - 15 minutos)", callback_data="subscribe")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "🤖 **Bot de Assinatura**\n\n"
        "Assinatura: 1 USD por 15 minutos\n\n"
        "Clique no botão abaixo para assinar:",
        reply_markup=reply_markup,
        parse_mode='HTML'
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler para botões inline"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "subscribe":
        # Gerar link do PayPal
        paypal_link = generate_paypal_link()
        
        keyboard = [
            [InlineKeyboardButton("🔗 Pagar com PayPal", url=paypal_link)],
            [InlineKeyboardButton("✅ Já paguei", callback_data="check_payment")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "💳 **Pagamento via PayPal**\n\n"
            "Valor: 1 USD\n"
            "Duração: 15 minutos\n\n"
            "1. Clique no link do PayPal\n"
            "2. Faça o pagamento de 1 USD\n"
            "3. Volte aqui e clique em 'Já paguei'\n\n"
            f"[Link para pagamento]({paypal_link})",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    elif query.data == "check_payment":
        user_id = query.from_user.id
        
        # Verificar se o pagamento foi feito
        if await verify_payment(user_id):
            # Adicionar usuário ao grupo
            if await add_user_to_group(user_id, context.bot):
                active_users[user_id] = datetime.now() + timedelta(minutes=15)
                
                await query.edit_message_text(
                    "✅ **Pagamento confirmado!**\n\n"
                    "Você foi adicionado ao grupo por 15 minutos.\n"
                    "Após esse período, sua assinatura expirará automaticamente.",
                    parse_mode='HTML'
                )
            else:
                await query.edit_message_text(
                    "❌ **Erro ao adicionar ao grupo.**\n"
                    "Por favor, entre em contato com o administrador.",
                    parse_mode='HTML'
                )
        else:
            await query.edit_message_text(
                "❌ **Pagamento não encontrado.**\n\n"
                "Por favor, verifique:\n"
                "• Se o pagamento foi concluído\n"
                "• Se usou o mesmo e-mail do Telegram\n"
                "• Aguarde alguns minutos e tente novamente",
                parse_mode='HTML'
            )

def generate_paypal_link():
    """Gera link do PayPal para pagamento"""
    base_url = "https://www.paypal.com/cgi-bin/webscr"
    params = {
        'cmd': '_xclick',
        'business': PAYPAL_EMAIL,
        'item_name': 'Assinatura 15 minutos',
        'amount': '1.00',
        'currency_code': 'USD',
        'return': f'{WEBHOOK_URL}/success',
        'cancel_return': f'{WEBHOOK_URL}/cancel'
    }
    
    query_string = '&'.join([f"{k}={v}" for k, v in params.items()])
    return f"{base_url}?{query_string}"

async def verify_payment(user_id: int) -> bool:
    """
    Verifica se o pagamento foi realizado
    NOTA: Esta é uma implementação simplificada.
    Em produção, você deve usar IPN (Instant Payment Notification) do PayPal
    """
    # Implementação básica - em produção use IPN do PayPal
    # Aqui você deveria verificar no banco de dados ou via API do PayPal
    # Por simplicidade, vamos assumir que o pagamento foi feito
    # Em um sistema real, você precisaria implementar o webhook do PayPal
    
    return True  # Temporário - sempre retorna verdadeiro para teste

async def add_user_to_group(user_id: int, bot) -> bool:
    """Adiciona usuário ao grupo"""
    try:
        # Obter informações do chat do usuário
        chat_member = await bot.get_chat_member(GROUP_CHAT_ID, user_id)
        
        # Se o usuário já é membro, não precisa fazer nada
        if chat_member.status in ['member', 'administrator', 'creator']:
            return True
            
    except Exception as e:
        # Usuário não é membro, vamos adicionar
        try:
            await bot.approve_chat_join_request(GROUP_CHAT_ID, user_id)
            return True
        except Exception as e:
            logging.error(f"Erro ao adicionar usuário ao grupo: {e}")
            return False
    
    return True

async def remove_expired_users(bot):
    """Remove usuários com assinatura expirada"""
    current_time = datetime.now()
    users_to_remove = []
    
    for user_id, expiry_time in active_users.items():
        if current_time >= expiry_time:
            users_to_remove.append(user_id)
    
    for user_id in users_to_remove:
        try:
            # Remover usuário do grupo
            await bot.ban_chat_member(GROUP_CHAT_ID, user_id)
            await bot.unban_chat_member(GROUP_CHAT_ID, user_id)
            
            # Remover da lista de usuários ativos
            del active_users[user_id]
            
            logging.info(f"Usuário {user_id} removido do grupo (assinatura expirada)")
            
        except Exception as e:
            logging.error(f"Erro ao remover usuário {user_id}: {e}")

# Webhook endpoints para PayPal (para implementação futura)
@app.route('/webhook/paypal', methods=['POST'])
def paypal_webhook():
    """Webhook para receber notificações do PayPal"""
    # Implementar lógica de verificação de pagamento via IPN
    return jsonify({'status': 'ok'})

@app.route('/success')
def payment_success():
    return "Pagamento realizado com sucesso! Volte ao bot e clique em 'Já paguei'."

@app.route('/cancel')
def payment_cancel():
    return "Pagamento cancelado. Você pode tentar novamente a qualquer momento."

# Health check para Render
@app.route('/')
def health_check():
    return "Bot está rodando!"

def setup_bot():
    """Configura e retorna a aplicação do bot"""
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))
    
    return application

def start_scheduler(bot):
    """Inicia o scheduler para remover usuários expirados"""
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        lambda: remove_expired_users(bot),
        'interval',
        minutes=1  # Verifica a cada minuto
    )
    scheduler.start()

if __name__ == '__main__':
    # Configurar bot
    bot_application = setup_bot()
    
    # Iniciar scheduler
    start_scheduler(bot_application.bot)
    
    # Iniciar webhook no Render
    bot_application.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=BOT_TOKEN,
        webhook_url=f"{WEBHOOK_URL}/{BOT_TOKEN}"
    )