# -*- coding: utf-8 -*-
"""
Конфигурация бота
"""
import os
from dotenv import load_dotenv

# Загрузка переменных окружения из файла .env
load_dotenv()

# Токен бота (получить у @BotFather)
BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")

# ID администраторов (для уведомлений и статистики)
# Чтобы узнать свой ID, используйте команду /myid в боте
# Можно указать несколько ID через запятую: 123456789,987654321
admin_ids_str = os.getenv("ADMIN_ID", "")
if admin_ids_str:
    ADMIN_IDS = [int(id.strip()) for id in admin_ids_str.split(",") if id.strip()]
else:
    ADMIN_IDS = []

# База данных - SQLite (локально) или PostgreSQL (Bothost)
# Если есть DATABASE_URL или POSTGRES_* переменные - используем PostgreSQL
# Иначе - SQLite
DATABASE_URL = os.getenv("DATABASE_URL")  # Формат: postgresql://user:pass@host:port/dbname
POSTGRES_HOST = os.getenv("POSTGRES_HOST")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
POSTGRES_DB = os.getenv("POSTGRES_DB", os.getenv("POSTGRES_DATABASE"))
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")

# Определяем тип БД
USE_POSTGRES = bool(DATABASE_URL or (POSTGRES_HOST and POSTGRES_DB and POSTGRES_USER))

# Путь к SQLite базе (если PostgreSQL не настроен)
# На Bothost используем /data для постоянного хранения (не удаляется при Rebuild)
# Локально - database/bot_database.db
DATABASE_PATH = os.getenv("DATABASE_PATH", "/data/bot_database.db" if os.path.exists("/data") else "database/bot_database.db")

# Настройки
DEBUG = os.getenv("DEBUG", "False") == "True"
