# -*- coding: utf-8 -*-
"""
Работа с базой данных SQLite
Сохранение информации о пользователях и их действиях для статистики
"""
import sqlite3
import os
from datetime import datetime
from config import DATABASE_PATH


def init_db():
    """
    Инициализация базы данных
    Создание таблиц если их нет
    """
    # Создаем папку для БД если её нет
    os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)

    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    # Таблица пользователей
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            last_name TEXT,
            phone_number TEXT,
            first_interaction TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_interaction TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Таблица действий пользователей (для статистики)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_actions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            action_type TEXT,
            action_data TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
    ''')

    # Таблица выбранных тарифов
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tariff_selections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            tariff_type TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
    ''')

    conn.commit()
    conn.close()
    print("База данных инициализирована")


def add_or_update_user(user_id, username=None, first_name=None, last_name=None):
    """
    Добавить или обновить информацию о пользователе
    """
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO users (user_id, username, first_name, last_name)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(user_id) DO UPDATE SET
            username=excluded.username,
            first_name=excluded.first_name,
            last_name=excluded.last_name,
            last_interaction=CURRENT_TIMESTAMP
    ''', (user_id, username, first_name, last_name))

    conn.commit()
    conn.close()


def log_action(user_id, action_type, action_data=None):
    """
    Записать действие пользователя для статистики

    action_type примеры:
    - 'start' - запустил бота
    - 'view_tariffs' - посмотрел тарифы
    - 'view_about' - посмотрел об авторах
    - 'ask_question' - нажал "Задать вопрос"
    - 'select_basic' - выбрал базовый тариф
    - 'select_assistant' - выбрал тариф "Ассистент для ассистента"
    """
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO user_actions (user_id, action_type, action_data)
        VALUES (?, ?, ?)
    ''', (user_id, action_type, action_data))

    conn.commit()
    conn.close()


def log_tariff_selection(user_id, tariff_type):
    """
    Записать выбор тарифа пользователем

    tariff_type: 'basic' или 'assistant'
    """
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO tariff_selections (user_id, tariff_type)
        VALUES (?, ?)
    ''', (user_id, tariff_type))

    conn.commit()
    conn.close()


def get_user_count():
    """
    Получить общее количество пользователей
    """
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute('SELECT COUNT(*) FROM users')
    count = cursor.fetchone()[0]

    conn.close()
    return count


def get_tariff_stats():
    """
    Получить статистику по выбранным тарифам
    """
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute('''
        SELECT tariff_type, COUNT(*) as count
        FROM tariff_selections
        GROUP BY tariff_type
    ''')

    stats = cursor.fetchall()
    conn.close()

    return {row[0]: row[1] for row in stats}


def get_stats_summary():
    """
    Получить общую статистику
    """
    user_count = get_user_count()
    tariff_stats = get_tariff_stats()

    return {
        'total_users': user_count,
        'basic_tariff': tariff_stats.get('basic', 0),
        'assistant_tariff': tariff_stats.get('assistant', 0)
    }


def save_phone_number(user_id, phone_number):
    """
    Сохранить номер телефона пользователя
    """
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE users
        SET phone_number = ?
        WHERE user_id = ?
    """, (phone_number, user_id))

    conn.commit()
    conn.close()


def get_user_phone(user_id):
    """
    Получить номер телефона пользователя
    """
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT phone_number
        FROM users
        WHERE user_id = ?
    """, (user_id,))

    result = cursor.fetchone()
    conn.close()

    return result[0] if result and result[0] else None


def get_users_with_contacts(limit=None):
    """
    Получить пользователей с контактами
    """
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    query = """
        SELECT
            u.user_id,
            u.username,
            u.first_name,
            u.last_name,
            u.phone_number,
            u.first_interaction,
            COALESCE(
                (SELECT tariff_type FROM tariff_selections
                 WHERE user_id = u.user_id
                 ORDER BY timestamp DESC LIMIT 1),
                NULL
            ) as tariff
        FROM users u
        WHERE u.phone_number IS NOT NULL
        ORDER BY u.first_interaction DESC
    """

    if limit:
        query += f" LIMIT {limit}"

    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()

    return results


def get_all_user_ids():
    """
    Получить все user_id для рассылки
    """
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT user_id FROM users")
    results = cursor.fetchall()
    conn.close()

    return [row[0] for row in results]


def get_contacts_count():
    """
    Количество пользователей, оставивших контакты
    """
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT COUNT(*) FROM users
        WHERE phone_number IS NOT NULL
    """)

    result = cursor.fetchone()
    conn.close()

    return result[0] if result else 0


def get_recent_users_count(days=1):
    """
    Количество новых пользователей за последние N дней
    """
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT COUNT(*) FROM users
        WHERE first_interaction >= datetime('now', '-{} days')
    """.format(days))

    result = cursor.fetchone()
    conn.close()

    return result[0] if result else 0

