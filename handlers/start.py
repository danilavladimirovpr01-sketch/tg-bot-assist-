# -*- coding: utf-8 -*-
"""
Обработчик команды /start
"""
from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from texts.messages import get_welcome_message
from keyboards.inline import get_main_menu_keyboard
from database.db import add_or_update_user, log_action


router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message):
    """
    Обработка команды /start
    Приветствие с именем пользователя + главное меню
    """
    user = message.from_user

    # Сохраняем пользователя в БД
    add_or_update_user(
        user_id=user.id,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name
    )

    # Логируем действие
    log_action(user.id, 'start')

    # Получаем приветственное сообщение с именем
    welcome_text = get_welcome_message(user.first_name)

    # Отправляем сообщение с главным меню
    await message.answer(
        text=welcome_text,
        reply_markup=get_main_menu_keyboard()
    )
