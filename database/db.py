# -*- coding: utf-8 -*-
"""
Работа с базой данных (SQLite или PostgreSQL)
Сохранение информации о пользователях и их действиях для статистики
"""
import os
import logging
from datetime import datetime
from pathlib import Path
from config import (
    USE_POSTGRES, DATABASE_URL, POSTGRES_HOST, POSTGRES_PORT,
    POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD, DATABASE_NAME
)

logger = logging.getLogger(__name__)

# Импорты в зависимости от типа БД
if USE_POSTGRES:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    from urllib.parse import urlparse
else:
    import sqlite3


def get_connection():
    """
    Получить подключение к БД (SQLite или PostgreSQL)
    """
    if USE_POSTGRES:
        # PostgreSQL подключение
        if DATABASE_URL:
            # Парсим DATABASE_URL (формат: postgresql://user:pass@host:port/dbname)
            result = urlparse(DATABASE_URL)
            return psycopg2.connect(
                database=result.path[1:],
                user=result.username,
                password=result.password,
                host=result.hostname,
                port=result.port
            )
        else:
            # Используем отдельные переменные
            return psycopg2.connect(
                host=POSTGRES_HOST,
                port=POSTGRES_PORT,
                database=POSTGRES_DB,
                user=POSTGRES_USER,
                password=POSTGRES_PASSWORD
            )
    else:
        # SQLite подключение (согласно документации Bothost)
        # Путь к папке data
        DATA_DIR = Path("/data")
        DATA_DIR.mkdir(parents=True, exist_ok=True)

        # Путь к базе данных
        DB_PATH = DATA_DIR / DATABASE_NAME

        # Подключаемся к базе
        conn = sqlite3.connect(str(DB_PATH))
        return conn


def init_db():
    """
    Инициализация базы данных
    Создание таблиц если их нет
    """
    # Проверяем существование базы данных (для SQLite)
    if not USE_POSTGRES:
        DATA_DIR = Path("/data")
        DB_PATH = DATA_DIR / DATABASE_NAME

        if DB_PATH.exists():
            logger.info(f"✅ База данных уже существует: {DB_PATH}")
        else:
            logger.info(f"🔨 Создаём новую базу данных: {DB_PATH}")

    conn = get_connection()
    cursor = conn.cursor()

    if USE_POSTGRES:
        # PostgreSQL синтаксис
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id BIGINT PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                phone_number TEXT,
                first_interaction TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_interaction TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_actions (
                id SERIAL PRIMARY KEY,
                user_id BIGINT,
                action_type TEXT,
                action_data TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tariff_selections (
                id SERIAL PRIMARY KEY,
                user_id BIGINT,
                tariff_type TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        ''')
    else:
        # SQLite синтаксис
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

    db_type = "PostgreSQL" if USE_POSTGRES else "SQLite"
    logger.info(f"✅ База данных инициализирована ({db_type})")


def add_or_update_user(user_id, username=None, first_name=None, last_name=None):
    """
    Добавить или обновить информацию о пользователе
    """
    conn = get_connection()
    cursor = conn.cursor()

    if USE_POSTGRES:
        # PostgreSQL: используем %s вместо ?
        cursor.execute('''
            INSERT INTO users (user_id, username, first_name, last_name)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT(user_id) DO UPDATE SET
                username=EXCLUDED.username,
                first_name=EXCLUDED.first_name,
                last_name=EXCLUDED.last_name,
                last_interaction=CURRENT_TIMESTAMP
        ''', (user_id, username, first_name, last_name))
    else:
        # SQLite: используем ?
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
    """
    conn = get_connection()
    cursor = conn.cursor()

    placeholder = '%s' if USE_POSTGRES else '?'
    cursor.execute(f'''
        INSERT INTO user_actions (user_id, action_type, action_data)
        VALUES ({placeholder}, {placeholder}, {placeholder})
    ''', (user_id, action_type, action_data))

    conn.commit()
    conn.close()


def log_tariff_selection(user_id, tariff_type):
    """
    Записать выбор тарифа пользователем
    """
    conn = get_connection()
    cursor = conn.cursor()

    placeholder = '%s' if USE_POSTGRES else '?'
    cursor.execute(f'''
        INSERT INTO tariff_selections (user_id, tariff_type)
        VALUES ({placeholder}, {placeholder})
    ''', (user_id, tariff_type))

    conn.commit()
    conn.close()


def get_user_count():
    """
    Получить общее количество пользователей
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT COUNT(*) FROM users')
    count = cursor.fetchone()[0]

    conn.close()
    return count


def get_tariff_stats():
    """
    Получить статистику по выбранным тарифам
    """
    conn = get_connection()
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
    conn = get_connection()
    cursor = conn.cursor()

    placeholder = '%s' if USE_POSTGRES else '?'
    cursor.execute(f"""
        UPDATE users
        SET phone_number = {placeholder}
        WHERE user_id = {placeholder}
    """, (phone_number, user_id))

    conn.commit()
    conn.close()


def get_user_phone(user_id):
    """
    Получить номер телефона пользователя
    """
    conn = get_connection()
    cursor = conn.cursor()

    placeholder = '%s' if USE_POSTGRES else '?'
    cursor.execute(f"""
        SELECT phone_number
        FROM users
        WHERE user_id = {placeholder}
    """, (user_id,))

    result = cursor.fetchone()
    conn.close()

    return result[0] if result and result[0] else None


def get_users_with_contacts(limit=None):
    """
    Получить пользователей с контактами
    """
    conn = get_connection()
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
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT user_id FROM users")
    results = cursor.fetchall()
    conn.close()

    return [row[0] for row in results]


def get_contacts_count():
    """
    Количество пользователей, оставивших контакты
    """
    conn = get_connection()
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
    conn = get_connection()
    cursor = conn.cursor()

    if USE_POSTGRES:
        # PostgreSQL синтаксис для дат
        cursor.execute("""
            SELECT COUNT(*) FROM users
            WHERE first_interaction >= NOW() - INTERVAL '%s days'
        """, (days,))
    else:
        # SQLite синтаксис для дат
        cursor.execute("""
            SELECT COUNT(*) FROM users
            WHERE first_interaction >= datetime('now', '-{} days')
        """.format(days))

    result = cursor.fetchone()
    conn.close()

    return result[0] if result else 0
