from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
    CallbackQueryHandler,
)
from dotenv import load_dotenv
from os import getenv
import logging

load_dotenv()
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    logger.info(f"""User {user_id} started the bot with /start""")
    await update.message.delete()
    logger.info(f"""Deleted the /start command message""")
    await update.message.reply_text(
        f"""Привет! Я Робот долбоеб
Напишите название услуги или ведомства

Если захотите оценить ответ, поставьте лайк или дизлайк снизу от него — это поможет улучшить мою работу"""
    )
    logger.info(f"""Sent greeting to user {user_id}""")


async def unknown_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.delete()
    logger.info(
        f"""Deleted unknown command message from user {update.effective_user.id}"""
    )
    await update.message.reply_text("Извините, я не понимаю эту команду.")
    logger.info(f"""User {update.effective_user.id} sent an unknown command""")


async def message_handle(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.info(f"""{update.effective_user.id} sent a message {update.message.text}""")
    await update.message.reply_text(
        "Received your message!",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("👍", callback_data="понравилось"),
                    InlineKeyboardButton("👎", callback_data="не понравилось"),
                ]
            ]
        ),
    )
    logger.info(
        f"""Sent reply with like/dislike buttons to user {update.effective_user.id}"""
    )


async def query_callback_handle(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    query = update.callback_query
    await query.answer()
    logger.info(f"""User {update.effective_user.id} pressed {query.data} button""")
    await query.edit_message_text(
        f"""{query.message.text}

Вы нажали {query.data}.
    """
    )
    logger.info(f"""Edited message text for user {update.effective_user.id}""")


def main():
    app = ApplicationBuilder().token(getenv("TOKEN")).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.COMMAND, unknown_command))
    app.add_handler(MessageHandler(~filters.COMMAND, message_handle))
    app.add_handler(CallbackQueryHandler(query_callback_handle))
    app.run_polling()


if __name__ == "__main__":
    main()
