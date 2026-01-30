# -*- coding: utf-8 -*-
"""
Главный файл для запуска Telegram-бота
@Assist_SupportBot - Скорая помощь для ассистента
"""
import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from config import BOT_TOKEN
from database.db import init_db
from handlers import start, callbacks, contact, admin


# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def main():
    """
    Запуск бота
    """
    # Проверка токена
    if not BOT_TOKEN or BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        logger.error("❌ ОШИБКА: Токен бота не указан!")
        logger.error("Получите токен у @BotFather и добавьте в файл .env")
        return

    logger.info("🚀 Бот запускается...")

    # Инициализация базы данных
    init_db()

    # Инициализация бота и диспетчера
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher()

    # Подключение роутеров (обработчиков)
    dp.include_router(admin.router)
    dp.include_router(start.router)
    dp.include_router(contact.router)
    dp.include_router(callbacks.router)

    logger.info("✅ Бот успешно запущен и готов к работе!")

    # Запуск бота
    await dp.start_polling(bot, skip_updates=True)


if __name__ == '__main__':
    asyncio.run(main())
