"""Это не модуль, если вы видите этот текст как подсказку, то вы делаете что-то не так"""

# TODO переписать систему логирования
# TODO переписать сообщения, которые видит пользователь
# TODO переписать докстринги
from os import getenv
import logging
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    CallbackQueryHandler,
    ContextTypes,
    ConversationHandler,
)
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # pylint: disable=unused-argument
    """Обрабатывает команду /start"""
    user_id = update.effective_user.id
    logger.debug("User %s started the bot with /start", user_id)
    await update.message.delete()
    logger.debug("Удален вызов /start")
    await update.message.reply_text(
        """Привет! Я Робот долбоеб
Напишите название услуги или ведомства

Если захотите оценить ответ, поставьте лайк или дизлайк снизу \
от него — это поможет улучшить мою работу"""
    )
    logger.debug("Sent greeting to user %s", user_id)


async def auth_entry(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # pylint: disable=unused-argument
    """entry-point для аутентификации"""
    logger.debug("User %s started authentication", update.effective_user.id)
    reply_keyboard = ReplyKeyboardMarkup([["Отменить"]], one_time_keyboard=True)
    await update.message.reply_text(
        "Пожалуйста, введите вашу фамилию для аутентификации.",
        reply_markup=reply_keyboard,
    )
    logger.debug("Asked user %s for last name", update.effective_user.id)
    return 0


async def auth_ask(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # pylint: disable=unused-argument
    """Состояние получения фамилии для аутентификации"""
    logger.debug(
        "User %s is providing last name for authentication", update.effective_user.id
    )
    if False:  # TODO если пользователь в БД
        await update.message.reply_text("Пользователь найден в базе данных.")
        logger.debug("User %s found in the database", update.effective_user.id)
        return ConversationHandler.END
    reply_keyboard = ReplyKeyboardMarkup([["Отменить"]], one_time_keyboard=True)
    await update.message.reply_text(
        "Пользователь не найден в базе данных.", reply_markup=reply_keyboard
    )
    logger.debug("User %s not found in the database", update.effective_user.id)

    return 0


async def auth_fallback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # pylint: disable=unused-argument
    """Состояние получения фамилии для аутентификации"""
    logger.debug("User %s cancelled authentication", update.effective_user.id)

    return ConversationHandler.END


async def unknown_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # pylint: disable=unused-argument
    """Обрабатывает неизвестную команду"""
    await update.message.delete()
    logger.debug(
        "Deleted unknown command message from user %s", update.effective_user.id
    )
    await update.message.reply_text("Извините, я не понимаю эту команду")
    logger.debug("User %s sent an unknown command", update.effective_user.id)


async def message_handle(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # pylint: disable=unused-argument
    """Обрабатывает текстовое сообщение"""
    logger.debug("%s sent a message %s", update.effective_user.id, update.message.text)
    reply_markup = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("👍", callback_data="понравилось"),
                InlineKeyboardButton("👎", callback_data="не понравилось"),
            ]
        ]
    )
    await update.message.reply_text(
        "Sunt quis ut occaecat ullamco enim exercitation eiusmod aute culpa veniam ea fugiat ex.",
        reply_markup=reply_markup,
    )
    logger.debug(
        "Отправлен ответ на сообщение пользователю %s", update.effective_user.id
    )


async def query_callback_handle(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    # pylint: disable=unused-argument
    """Обрабатывает оценку ответа модели"""
    query = update.callback_query
    await query.answer()
    logger.debug("User %s pressed %s button", update.effective_user.id, query.data)
    await query.edit_message_text(
        f"""{query.message.text}
Вы нажали {query.data}.
    """
    )
    logger.debug("Edited message text for user %s", update.effective_user.id)


def main():
    """Основная функция"""
    app = ApplicationBuilder().token(getenv("TOKEN")).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(
        ConversationHandler(
            entry_points=[CommandHandler("auth", auth_entry)],
            states={
                0: [
                    MessageHandler(
                        ~filters.COMMAND & ~filters.Regex("Отменить"), auth_ask
                    )
                ]
            },
            fallbacks=[MessageHandler(filters.Regex("Отменить"), auth_fallback)],
        )
    )
    app.add_handler(MessageHandler(filters.COMMAND, unknown_command))
    app.add_handler(MessageHandler(~filters.COMMAND, message_handle))
    app.add_handler(CallbackQueryHandler(query_callback_handle))
    app.run_polling()


if __name__ == "__main__":
    main()
