# -*- coding: utf-8 -*-
"""
Обработчик получения контакта пользователя
"""
from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from texts.messages import BASIC_TARIFF_MESSAGE, ASSISTANT_TARIFF_MESSAGE
from keyboards.inline import get_contact_manager_keyboard
from database.db import save_phone_number, log_action


router = Router()


class ContactForm(StatesGroup):
    """Состояния для сбора контакта"""
    waiting_for_contact = State()
    tariff_type = State()


async def request_contact(message: Message, state: FSMContext, action: str):
    """
    Запросить контакт пользователя
    """
    from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

    # Сохраняем действие (откуда пришел запрос) в состояние
    await state.update_data(action_type=action)
    await state.set_state(ContactForm.waiting_for_contact)

    # Создаем клавиатуру для запроса контакта (БЕЗ кнопки "Пропустить")
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📱 Поделиться контактом", request_contact=True)]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )

    await message.answer(
        "Чтобы менеджер мог с вами связаться, поделитесь своим контактом:",
        reply_markup=keyboard
    )


@router.message(ContactForm.waiting_for_contact, F.contact)
async def contact_received(message: Message, state: FSMContext):
    """
    Обработка полученного контакта
    """
    from texts.messages import TARIFFS_MESSAGE
    from keyboards.inline import get_tariffs_keyboard

    user_id = message.from_user.id
    phone_number = message.contact.phone_number

    # Сохраняем номер телефона в БД
    save_phone_number(user_id, phone_number)
    log_action(user_id, 'shared_contact', phone_number)

    # Очищаем состояние
    await state.clear()

    # Показываем благодарность и тарифы
    await message.answer(
        "Спасибо! Ваш контакт сохранен 📱",
        reply_markup=ReplyKeyboardRemove()
    )

    # Показываем тарифы
    log_action(user_id, 'view_tariffs')
    await message.answer(
        text=TARIFFS_MESSAGE,
        reply_markup=get_tariffs_keyboard()
    )


