import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler

# States for ConversationHandler
SELECT_SLOT, ENTER_NAME = range(2)

# Dictionary of available slots and registered users
SLOTS = {
    "10:00": [],
    "12:00": [],
    "14:00": []
}

# Track user registrations {username: slot}
REGISTERED_USERS = {}

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = update.effective_user.username
    if username in REGISTERED_USERS:
        await update.message.reply_text(
            f"Вы уже зарегистрированы на слот {REGISTERED_USERS[username]}")
        return ConversationHandler.END

    available_slots = [slot for slot, users in SLOTS.items() if len(users) < 8]
    if not available_slots:
        await update.message.reply_text("Все слоты заполнены.")
        return ConversationHandler.END

    keyboard = [[slot] for slot in available_slots]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
    await update.message.reply_text(
        "Выберите доступный временной слот:", reply_markup=reply_markup)
    return SELECT_SLOT

async def select_slot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    slot = update.message.text
    if slot not in SLOTS or len(SLOTS[slot]) >= 8:
        await update.message.reply_text("Выбранный слот недоступен. Попробуйте снова.")
        return ConversationHandler.END
    context.user_data['slot'] = slot
    await update.message.reply_text("Введите ваше имя:")
    return ENTER_NAME

async def enter_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = update.message.text
    slot = context.user_data['slot']
    username = update.effective_user.username
    SLOTS[slot].append({'username': username, 'name': name})
    REGISTERED_USERS[username] = slot
    await update.message.reply_text(
        f"{name}, вы зарегистрированы на слот {slot}.")
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Регистрация отменена.')
    return ConversationHandler.END


def main():
    # Replace 'TOKEN' with your bot token
    application = ApplicationBuilder().token('YOUR_TELEGRAM_BOT_TOKEN').build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            SELECT_SLOT: [MessageHandler(filters.TEXT & ~filters.COMMAND, select_slot)],
            ENTER_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, enter_name)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    application.add_handler(conv_handler)

    application.run_polling()

if __name__ == '__main__':
    main()
