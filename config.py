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

# Путь к базе данных
DATABASE_PATH = "database/bot_database.db"

# Настройки
DEBUG = os.getenv("DEBUG", "False") == "True"
