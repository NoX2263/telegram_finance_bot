import os
from dotenv import load_dotenv # pip install python-dotenv

load_dotenv() # Загружает переменные из .env файла

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("Токен бота не найден в переменных окружения BOT_TOKEN")