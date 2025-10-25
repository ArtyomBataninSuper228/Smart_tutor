import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters, CallbackContext


def decorator(func):
    application.add_handler(CommandHandler("start", start))


# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /start"""
    user = update.effective_user
    logger.info(f"User {user.id} started the bot")
    print(f"🚨 ВЫЗВАН /start от {user.first_name} (ID: {user.id})")

    await update.message.reply_text(
        f"✅ Бот работает! Привет, {user.first_name}!\n"
        "Используй /help для списка команд"
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /help"""
    await update.message.reply_text(
        "📚 Доступные команды:\n"
        "/start - Запустить бота\n"
        "/help - Помощь\n"
        "/test - Тестовая команда"
    )


async def test_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Тестовая команда"""
    await update.message.reply_text("🔧 Тестовая команда работает!")


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик текстовых сообщений"""
    print(f"📩 Получено сообщение: '{update.message.text}'")
    await update.message.reply_text(f"Эхо: {update.message.text}")


def main():
    # 🔐 ЗАМЕНИТЕ НА ВАШ РЕАЛЬНЫЙ ТОКЕН
    BOT_TOKEN = "8215300847:AAHGW-KR6aJhm2uJgBtzdNJAYm093KwjVH0"

    print("🤖 Запуск бота...")
    print("📱 Напишите /start вашему боту в Telegram")

    try:
        # Создаем Application
        application = Application.builder().token(BOT_TOKEN).build()

        # Добавляем обработчики
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CommandHandler("test", test_command))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

        # ✅ ПРАВИЛЬНЫЕ ПАРАМЕТРЫ для run_polling:
        application.run_polling(
            drop_pending_updates=True,  # Очистить старые сообщения
            allowed_updates=Update.ALL_TYPES
        )

    except Exception as e:
        logger.error(f"Ошибка: {e}")
        print(f"💥 Ошибка: {e}")


if __name__ == "__main__":
    main()