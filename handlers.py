from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
import database as db
import keyboards as kb

# Определяем состояния для ConversationHandler
TYPE, CATEGORY, AMOUNT, COMMENT = range(4)
DELETE_SELECT, DELETE_CONFIRM = range(4, 6)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    db.add_user(user.id, user.username, user.first_name, user.last_name)
    welcome_text = f"Привет, {user.first_name}! Я бот для учета финансов."
    await update.message.reply_text(welcome_text, reply_markup=kb.get_main_keyboard())

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    
    if text == "Доход":
        # Сохраняем тип операции в контексте, чтобы не определять его позже.
        context.user_data['type'] = 'income'
        await update.message.reply_text("Выберите категорию дохода:", reply_markup=kb.get_category_keyboard('income'))
        return CATEGORY
        
    elif text == "Расход":
        context.user_data['type'] = 'expense'
        await update.message.reply_text("Выберите категорию расхода:", reply_markup=kb.get_category_keyboard('expense'))
        return CATEGORY
        
    elif text == "История":
        await show_history(update, context)
        
    elif text == "Отчет":
        await update.message.reply_text("Функция отчета в разработке")
    
    elif text == "Удалить операцию":
        await show_transactions_for_deletion(update, context)
        # Логика диалога удаления выглядит хорошо продуманной.
        return DELETE_SELECT

    else:
        await update.message.reply_text("Не понимаю команду. Используйте кнопки меню.")
        return ConversationHandler.END

async def show_transactions_for_deletion(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Функция для отображения доступных для удаления операций
    """
    user_id = update.effective_user.id
    transactions = db.get_transactions(user_id, limit=10)
    
    if not transactions:
        await update.message.reply_text("У вас пока нет операций для удаления.", reply_markup=kb.get_main_keyboard())
        return ConversationHandler.END
    
    # Сохраняем транзакции в контексте для последующего использования
    context.user_data['transactions_for_deletion'] = transactions
    
    text = "Выберите операцию для удаления:\n\n"
    for i, tr in enumerate(transactions, 1):
        emoji = "📈" if tr[2] == 'income' else "📉"
        text += f"{i}. {emoji} {tr[2]} ({tr[3]}): {tr[4]} руб."
        if tr[6]:  # Если есть комментарий
            text += f" - {tr[6]}"
        text += f" (ID: {tr[0]})\n"
    
    text += "\nВведите номер операции для удаления:"
    
    await update.message.reply_text(text, reply_markup=kb.get_back_keyboard())
    return DELETE_CONFIRM

async def handle_delete_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Функция для обработки подтверждения удаления 
    """
    text = update.message.text
    
    if text == "Назад":
        await update.message.reply_text("Отмена удаления.", reply_markup=kb.get_main_keyboard())
        return ConversationHandler.END
    
    try:
        selected_index = int(text) - 1
        transactions = context.user_data.get('transactions_for_deletion', [])
        
        if 0 <= selected_index < len(transactions):
            transaction_id = transactions[selected_index][0]
            context.user_data['transaction_to_delete'] = transaction_id
            
            # Показываем подтверждение удаления
            tr = transactions[selected_index]
            emoji = "📈" if tr[2] == 'income' else "📉"
            confirmation_text = f"Вы уверены, что хотите удалить операцию?\n\n"
            confirmation_text += f"{emoji} {tr[2]} ({tr[3]}): {tr[4]} руб."
            if tr[6]:
                confirmation_text += f" - {tr[6]}"
            
            confirmation_text += "\n\nПодтвердите удаление (да/нет):"
            
            await update.message.reply_text(confirmation_text, reply_markup=kb.get_back_keyboard())
            return DELETE_CONFIRM
        else:
            await update.message.reply_text("Неверный номер операции. Попробуйте снова:")
            return DELETE_SELECT
            
    except ValueError:
        await update.message.reply_text("Пожалуйста, введите номер операции:")
        return DELETE_SELECT

async def handle_delete_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Функция для удаления операции
    """
    text = update.message.text.lower()
    user_id = update.effective_user.id
    
    if text == "назад":
        await update.message.reply_text("Отмена удаления.", reply_markup=kb.get_main_keyboard())
        return ConversationHandler.END
    
    if text in ["да", "yes", "удалить"]:
        transaction_id = context.user_data.get('transaction_to_delete')
        
        if transaction_id and db.delete_transaction(transaction_id, user_id):
            await update.message.reply_text("Операция успешно удалена!", reply_markup=kb.get_main_keyboard())
        else:
            await update.message.reply_text("Не удалось удалить операцию.", reply_markup=kb.get_main_keyboard())
        
        # Очищаем временные данные
        context.user_data.pop('transaction_to_delete', None)
        context.user_data.pop('transactions_for_deletion', None)
        
        return ConversationHandler.END
        
    elif text in ["нет", "no", "отмена"]:
        await update.message.reply_text("Удаление отменено.", reply_markup=kb.get_main_keyboard())
        
        # Очищаем временные данные
        context.user_data.pop('transaction_to_delete', None)
        context.user_data.pop('transactions_for_deletion', None)
        
        return ConversationHandler.END
        
    else:
        await update.message.reply_text("Пожалуйста, ответьте 'да' или 'нет':")
        return DELETE_CONFIRM

async def handle_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Функция для обработки выбранной категории.
    """
    category = update.message.text
    
    if category == "Назад":
        await update.message.reply_text("Выберите действие:", reply_markup=kb.get_main_keyboard())
        # Не забываем чистить контекст при отмене.
        context.user_data.clear()
        return ConversationHandler.END
        
    context.user_data['category'] = category
    await update.message.reply_text("Введите сумму:")
    return AMOUNT

async def handle_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        amount = float(update.message.text.replace(',', '.')) # Добавим замену запятой на точку для удобства
        if amount <= 0:
             await update.message.reply_text("Сумма должна быть положительным числом.")
             return AMOUNT
        context.user_data['amount'] = amount
        await update.message.reply_text("Добавьте комментарий (или нажмите /skip):")
        return COMMENT
    except ValueError: # Улучшение: Ловим конкретную ошибку ValueError.
        await update.message.reply_text("Пожалуйста, введите корректное число.")
        return AMOUNT

async def _save_transaction(update: Update, context: ContextTypes.DEFAULT_TYPE, comment=""):
    """Вспомогательная функция для сохранения транзакции и отправки ответа."""
    user_data = context.user_data
    
    # Тип операции мы теперь берем напрямую из контекста.
    tr_type = user_data['type']
    
    db.add_transaction(
        update.effective_user.id,
        tr_type,
        user_data['category'],
        user_data['amount'],
        comment
    )
    
    # Формируем красивое сообщение для пользователя.
    type_text = "Доход" if tr_type == 'income' else "Расход"
    await update.message.reply_text(
        f"✅ Запись добавлена!\n<b>{type_text}</b>: {user_data['amount']:.2f} руб.\n<b>Категория</b>: {user_data['category']}",
        reply_markup=kb.get_main_keyboard(),
        parse_mode='HTML' # Используем HTML для форматирования.
    )
    
    # Очищаем данные после завершения операции.
    context.user_data.clear()
    return ConversationHandler.END

async def handle_comment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    comment = update.message.text
    return await _save_transaction(update, context, comment)

async def skip_comment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return await _save_transaction(update, context) # Вызываем без комментария

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Действие отменено.", reply_markup=kb.get_main_keyboard())
    context.user_data.clear()
    return ConversationHandler.END

async def show_history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    transactions = db.get_transactions(user_id)
    
    if not transactions:
        await update.message.reply_text("У вас пока нет операций.")
        return

    text = "Последние операции:\n\n"
    for tr in transactions:
        emoji = "📈" if tr[2] == 'income' else "📉"
        text += f"{emoji} {tr[2]} ({tr[3]}): {tr[4]} руб."
        if tr[6]:
            text += f" - {tr[6]}"
        text += "\n"
        
    await update.message.reply_text(text)