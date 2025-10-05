from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler
import config
import database as db
import handlers as hnd
import logging # Модуль для логирования

# Настраиваем логирование, чтобы видеть ошибки
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

async def error_handler(update, context):
    """
    Функция для логирования ошибок обновления
    """
    logger.error(msg="Произошло исключение при обработке обновления", exc_info=context.error)

def main():
    db.init_db()

    application = Application.builder().token(config.BOT_TOKEN).build()
    
    # Улучшение: Добавляем обработчик ошибок.
    application.add_error_handler(error_handler)

    add_conv_handler = ConversationHandler(
        entry_points=[            
            MessageHandler(filters.Regex("^(Доход|Расход)$"), hnd.handle_message),
        ],
        states={
            hnd.CATEGORY: [MessageHandler(filters.TEXT & ~filters.COMMAND, hnd.handle_category)],
            hnd.AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, hnd.handle_amount)],
            hnd.COMMENT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, hnd.handle_comment),
                CommandHandler("skip", hnd.skip_comment)
            ],
        },
        fallbacks=[CommandHandler("cancel", hnd.cancel)],
    )

    delete_conv_handler = ConversationHandler(
        entry_points=[
            MessageHandler(filters.Regex("^(Удалить операцию)$"), hnd.handle_message),
        ],
        states={
            hnd.DELETE_SELECT: [MessageHandler(filters.TEXT & ~filters.COMMAND, hnd.handle_delete_selection)],
            hnd.DELETE_CONFIRM: [MessageHandler(filters.TEXT & ~filters.COMMAND, hnd.handle_delete_confirmation)],
        },
        fallbacks=[CommandHandler("cancel", hnd.cancel)],
    )

    application.add_handler(CommandHandler("start", hnd.start))
    application.add_handler(add_conv_handler)
    application.add_handler(delete_conv_handler)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, hnd.handle_message))

    print("Бот запущен...")
    application.run_polling()

if __name__ == "__main__":
    main()
