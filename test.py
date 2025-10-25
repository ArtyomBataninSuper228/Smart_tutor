import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

# Включаем логирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f"Получена команда /start от {update.effective_user.id}")
    await update.message.reply_text("🚀 Бот запущен и работает!")


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f"Получено сообщение: {update.message.text}")
    await update.message.reply_text(f"Вы сказали: {update.message.text}")


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Ошибка: {context.error}")
    if update and update.message:
        await update.message.reply_text("Произошла ошибка 😔")


def main():
    # ⚠️ ЗАМЕНИТЕ НА ВАШ ТОКЕН ⚠️
    BOT_TOKEN = "8215300847:AAHGW-KR6aJhm2uJgBtzdNJAYm093KwjVH0"

    try:
        print("🔄 Создаем Application...")
        application = Application.builder().token(BOT_TOKEN).build()

        print("✅ Добавляем обработчики...")
        application.add_handler(CommandHandler("start", start))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
        application.add_error_handler(error_handler)

        print("🚀 Запускаем бота...")
        print("Бот должен отвечать на команду /start")
        print("Откройте Telegram и напишите /start вашему боту")

        application.run_polling(
            drop_pending_updates=True,  # Игнорировать старые сообщения
            timeout=20,
            pool_timeout=20
        )

    except Exception as e:
        print(f"❌ Критическая ошибка при запуске: {e}")


if __name__ == "__main__":
    main()