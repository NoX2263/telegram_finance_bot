from telegram import ReplyKeyboardMarkup, KeyboardButton

BTN_INCOME = "Доход"
BTN_EXPENSE = "Расход"
BTN_HISTORY = "История"
BTN_DELETE = "Удалить операцию"
BTN_REPORT = "Отчет"
BTN_BACK = "Назад"

def get_main_keyboard():
    """
    Функция для формирования кнопок основого меню
    """
    keyboard = [
        [KeyboardButton(BTN_INCOME), KeyboardButton(BTN_EXPENSE)],
        [KeyboardButton(BTN_HISTORY), KeyboardButton(BTN_DELETE)],
        [KeyboardButton(BTN_REPORT)]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)

# Список категорий расходов
expense_categories = ["Еда", "Транспорт", "Жилье", "Развлечения", "Другое"]
# Список категорий дохов
income_categories = ["Зарплата", "Подарок", "Инвестиции", "Другое"]

def get_category_keyboard(transaction_type):
    """
    Функция для формирования кнопок с категориями расходов/доходов.
    """
    categories = income_categories if transaction_type == 'income' else expense_categories
    keyboard = [[KeyboardButton(category)] for category in categories]
    keyboard.append([KeyboardButton(BTN_BACK)]) 
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True) 

def get_back_keyboard():
    """
    Функция для формирования меню с кнопкой "Назад".
    """
    return ReplyKeyboardMarkup([[KeyboardButton(BTN_BACK)]], resize_keyboard=True, one_time_keyboard=True)