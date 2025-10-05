# database.py

import sqlite3
import datetime

def create_connection():
    """
    Функция создания соединения с БД.
    """    
    conn = sqlite3.connect('finance_bot.db', check_same_thread=False)
    return conn

def init_db():
    """
    Функция создания необходимых таблиц БД.
    """    
    with create_connection() as conn:
        cursor = conn.cursor()
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            user_id INTEGER UNIQUE,
            username TEXT,
            first_name TEXT,
            last_name TEXT,
            registered_at TEXT
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            type TEXT,
            category TEXT,
            amount REAL,
            date TEXT,
            comment TEXT
        )
        ''')

def add_user(user_id, username, first_name, last_name):
    """
    Функция для добавления нового пользователя в БД.
    """
    registered_at = datetime.datetime.now().isoformat()

    try:
        with create_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
            INSERT INTO users (user_id, username, first_name, last_name, registered_at)
            VALUES (?, ?, ?, ?, ?)
            ''', (user_id, username, first_name, last_name, registered_at))
    except sqlite3.IntegrityError:
        print(f"Пользователь {user_id} уже существует.")
    except Exception as e:
        print(f"Произошла непредвиденная ошибка при добавлении пользователя: {e}")

def add_transaction(user_id, transaction_type, category, amount, comment=""):
    """
    Функция для добавления новой операции.
    """
    date = datetime.datetime.now().isoformat()
    with create_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
        INSERT INTO transactions (user_id, type, category, amount, date, comment)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, transaction_type, category, amount, date, comment))

def get_transactions(user_id, limit=10):
    """
    Функция для получения последних операций пользователя.
    """
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('''
    SELECT * FROM transactions
    WHERE user_id = ?
    ORDER BY date DESC
    LIMIT ?
    ''', (user_id, limit))
    transactions = cursor.fetchall()
    conn.close()
    return transactions

def get_transaction_by_id(transaction_id, user_id):
    """
    Функция для получения информации об операции пользователя по id.
    """
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('''
    SELECT * FROM transactions
    WHERE id = ? AND user_id = ?
    ''', (transaction_id, user_id))
    transaction = cursor.fetchone()
    conn.close()
    return transaction

def delete_transaction(transaction_id, user_id):
    """
    Функция для удаления операции пользователя по id.
    """
    with create_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
        DELETE FROM transactions
        WHERE id = ? AND user_id = ?
        ''', (transaction_id, user_id))
        deleted = cursor.rowcount > 0
    return deleted