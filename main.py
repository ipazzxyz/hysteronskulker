"""Это не модуль, если вы видите этот текст как подсказку, то вы делаете что-то не так"""

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
    await update.message.delete()
    await update.message.reply_text(
        """Привет! Я Робот долбоеб
Напишите название услуги или ведомства

Если захотите оценить ответ, поставьте лайк или дизлайк снизу \
от него — это поможет улучшить мою работу"""
    )


async def auth_entry(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # pylint: disable=unused-argument
    """entry-point для аутентификации"""
    reply_keyboard = ReplyKeyboardMarkup([["Отменить"]], one_time_keyboard=True)
    await update.message.reply_text(
        "Пожалуйста, введите вашу фамилию для аутентификации.",
        reply_markup=reply_keyboard,
    )
    return 0


async def auth_ask(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # pylint: disable=unused-argument
    """Состояние получения фамилии для аутентификации"""
    if False:  # TODO если пользователь в БД
        await update.message.reply_text("Пользователь найден в базе данных.")
        return ConversationHandler.END
    reply_keyboard = ReplyKeyboardMarkup([["Отменить"]], one_time_keyboard=True)
    await update.message.reply_text(
        "Пользователь не найден в базе данных.", reply_markup=reply_keyboard
    )
    return 0


async def auth_fallback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # pylint: disable=unused-argument
    """Состояние получения фамилии для аутентификации"""
    return ConversationHandler.END


async def unknown_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # pylint: disable=unused-argument
    """Обрабатывает неизвестную команду"""
    await update.message.delete()
    await update.message.reply_text("Извините, я не понимаю эту команду")


async def message_handle(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # pylint: disable=unused-argument
    """Обрабатывает текстовое сообщение"""
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


async def query_callback_handle(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    # pylint: disable=unused-argument
    """Обрабатывает оценку ответа модели"""
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        f"""{query.message.text}
Вы нажали {query.data}.
    """
    )


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
