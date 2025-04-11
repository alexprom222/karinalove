# -*- coding: utf-8 -*- 
import logging
import os
from telegram import (  # эту тоже 
    Update,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    KeyboardButton,
)
from telegram.ext import ( # эту хуету не видит
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackContext,
)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
    level=logging.INFO
)
logger = logging.getLogger(__name__)

ROLE, TENANT_DATA, OWNER_DATA = range(3)


(
    METRAGE,
    DISTRICT,
    RATE,
    RENOVATION,
    ACTIVITY,
    METRO_DISTANCE,
    ADDITIONAL,
    CONFIRM_TENANT,
) = range(8)
(
    ADDRESS,
    METRO_OWNER,
    TYPE,
    METRAGE_OWNER,
    FLOOR,
    VENTILATION,
    CONDITIONING,
    WET_POINTS,
    CEILING,
    PARKING,
    DESCRIPTION,
    PHOTO,
    PRICE,
    COMMISSION,
    DEAL_TYPE,
    CONFIRM_OWNER,
) = range(16)

TOKEN = "8084850533:AAEpebkJgdrtB2WfFQ-wWsAGWg1s6nq8ce4"
CHANNEL_ID = "@proverka14"

def start(update: Update, context: CallbackContext) -> int:
    ("""Начало диалога, выбор роли.""")
    buttons = [
        ["1 Арендатор", 
        "2 Владелец недвижимости "]
    ]
    update.message.reply_text(
        "Добро пожаловать в dom Кто вы?",
        reply_markup=ReplyKeyboardMarkup(buttons, one_time_keyboard=True),
    )
    return ROLE
def role(update: Update, context: CallbackContext) -> int:
    """Обработка выбора роли."""
    user = update.message.from_user
    choice = update.message.text
    if choice.startswith("1"):
        update.message.reply_text(
            "Заполните заявку на аренду:",
            reply_markup=ReplyKeyboardRemove(),
        )
        update.message.reply_text("Введите желаемый метраж помещения (например, 50 м ):")
        return METRAGE
    elif choice.startswith("2"):
        update.message.reply_text(
            "Чтобы видеть новые заявки, подпишитесь на наш канал.\n"
            "После этого выберите «Добавить объект».",
            reply_markup=ReplyKeyboardRemove(),
        )
        return OWNER_DATA
    else:
        update.message.reply_text("Пожалуйста, выберите вариант из предложенных.")
        return ROLE
def metrage(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    context.user_data['metrage'] = update.message.text
    update.message.reply_text("Укажите район города или конкретное расположение:")
    return DISTRICT
def district(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    context.user_data["district"] = update.message.text
    update.message.reply_text("Какую ставку аренды вы готовы платить (в месяц)? Например, 100000:")
    return RATE
def rate(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    context.user_data["rate"] = update.message.text
    buttons = [["1 Чистовые отделочные работы", "2 Черновая отделка", "3 Без разницы"]]
    update.message.reply_text(
        "Выберите вариант ремонта:",
        reply_markup=ReplyKeyboardMarkup(buttons, one_time_keyboard=True),
    )
    return RENOVATION
def renovation(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    context.user_data["renovation"] = update.message.text
    update.message.reply_text("Укажите вашу сферу деятельности:")
    return ACTIVITY
def activity(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    context.user_data["activity"] = update.message.text
    update.message.reply_text(
        "Как далеко от метро должно быть помещение? Укажите время пешком или 'Не важно':"
    )
    return METRO_DISTANCE
def metro_distance(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    context.user_data["metro_distance"] = update.message.text
    update.message.reply_text("Укажите дополнительные пожелания (или пропустите):")
    return ADDITIONAL
def additional(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    context.user_data["additional"] = update.message.text
    summary = (
        f"Подтвердите вашу заявку:\n"
        f"Метраж: {context.user_data['metrage']}\n"
        f"Район: {context.user_data['district']}\n"
        f"Ставка: {context.user_data['rate']} руб.\n"
        f"Ремонт: {context.user_data['renovation']}\n"
        f"Вид деятельности: {context.user_data['activity']}\n"
        f"Метро: {context.user_data['metro_distance']}\n"
        f"Дополнительно: {context.user_data['additional']}"
    )
    buttons = [["Подтвердить", "Изменить"]]
    update.message.reply_text(
        summary,
        reply_markup=ReplyKeyboardMarkup(buttons, one_time_keyboard=True),
    )
    return CONFIRM_TENANT
def confirm_tenant(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    choice = update.message.text
    if choice == "Подтвердить":
        username = f"@{user.username}" if user.username else user.first_name
        post = (
            f"Новая заявка!\n"
            f"Ищет: {username}\n"
            f"Метраж: {context.user_data['metrage']}\n"
            f"Район: {context.user_data['district']}\n"
            f"Ставка: {context.user_data['rate']} руб.\n"
            f"Ремонт: {context.user_data['renovation']}\n"
            f"Вид деятельности: {context.user_data['activity']}\n"
            f"Метро: {context.user_data['metro_distance']}\n"
            f"Дополнительно: {context.user_data['additional']}"
        )
        context.bot.send_message(CHANNEL_ID, post)
        update.message.reply_text("Заявка опубликована!")
        return ConversationHandler.END
    else:
        update.message.reply_text("Редактирование пока не поддерживается. Начните заново.")
        return start(update, context)
def cancel(update: Update, context: CallbackContext) -> int:
    """Отмена диалога."""
    update.message.reply_text("Действие отменено.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END
def main() -> None:
    """Запуск бота."""
    updater = Updater(TOKEN)
    dispatcher = updater.dispatcher
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            ROLE: [MessageHandler(Filters.text & ~Filters.command, role)],
            METRAGE: [MessageHandler(Filters.text & ~Filters.command, metrage)],
            DISTRICT: [MessageHandler(Filters.text & ~Filters.command, district)],
            RATE: [MessageHandler(Filters.text & ~Filters.command, rate)],
            RENOVATION: [MessageHandler(Filters.text & ~Filters.command, renovation)],
            ACTIVITY: [MessageHandler(Filters.text & ~Filters.command, activity)],
            METRO_DISTANCE: [MessageHandler(Filters.text & ~Filters.command, metro_distance)],
            ADDITIONAL: [MessageHandler(Filters.text & ~Filters.command, additional)],
            CONFIRM_TENANT: [MessageHandler(Filters.text & ~Filters.command, confirm_tenant)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )
    dispatcher.add_handler(conv_handler)
    # dispatcher.add_handler(CommandHandler("history", history_command)) эту хуйню надо добавить чтоб видно было историю 
    updater.start_polling()
    updater.idle()
if __name__ == '__main__':
    main()