# -*- coding: utf-8 -*-
"""
Обработчики нажатий на кнопки (callback queries)
"""
from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from texts.messages import (
    get_welcome_message,
    get_tariffs_text_and_entities,
    BASIC_TARIFF_MESSAGE,
    ASSISTANT_TARIFF_MESSAGE,
    ABOUT_AUTHORS_MESSAGE,
    ASK_QUESTION_MESSAGE
)
from keyboards.inline import (
    get_main_menu_keyboard,
    get_tariffs_keyboard,
    get_contact_manager_keyboard,
    get_about_authors_keyboard,
    get_ask_question_keyboard
)
from database.db import log_action, log_tariff_selection


router = Router()


@router.callback_query(F.data == "main_menu")
async def callback_main_menu(callback: CallbackQuery):
    """
    Возврат в главное меню
    """
    user = callback.from_user
    welcome_text = get_welcome_message(user.first_name)

    await callback.message.edit_text(
        text=welcome_text,
        reply_markup=get_main_menu_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == "tariffs")
async def callback_tariffs(callback: CallbackQuery, state: FSMContext):
    """
    Запрос контакта перед показом тарифов
    """
    from database.db import get_user_phone
    from handlers.contact import request_contact

    user_id = callback.from_user.id

    # Проверяем, есть ли уже контакт в БД
    phone = get_user_phone(user_id)

    if phone:
        # Контакт уже есть, показываем тарифы (через entities — раскрывающиеся цитаты)
        log_action(user_id, 'view_tariffs')
        text, entities = get_tariffs_text_and_entities()
        await callback.message.edit_text(
            text=text,
            entities=entities,
            parse_mode=None,
            reply_markup=get_tariffs_keyboard()
        )
        await callback.answer()
    else:
        # Контакта нет, запрашиваем
        await callback.message.delete()
        await callback.answer()
        await request_contact(callback.message, state, 'view_tariffs')


@router.callback_query(F.data == "select_basic")
async def callback_select_basic(callback: CallbackQuery):
    """
    Выбран тариф БАЗОВЫЙ
    """
    from keyboards.inline import get_contact_manager_keyboard

    user_id = callback.from_user.id
    log_action(user_id, 'select_basic')
    log_tariff_selection(user_id, 'basic')

    await callback.answer("✅ Отличный выбор!")

    # Показываем информацию о тарифе и контакт менеджера
    await callback.message.edit_text(
        text=BASIC_TARIFF_MESSAGE,
        reply_markup=get_contact_manager_keyboard()
    )


@router.callback_query(F.data == "select_assistant")
async def callback_select_assistant(callback: CallbackQuery):
    """
    Выбран тариф АССИСТЕНТ ДЛЯ АССИСТЕНТА
    """
    from keyboards.inline import get_contact_manager_keyboard

    user_id = callback.from_user.id
    log_action(user_id, 'select_assistant')
    log_tariff_selection(user_id, 'assistant')

    await callback.answer("⭐ Превосходный выбор!")

    # Показываем информацию о тарифе и контакт менеджера
    await callback.message.edit_text(
        text=ASSISTANT_TARIFF_MESSAGE,
        reply_markup=get_contact_manager_keyboard()
    )


@router.callback_query(F.data == "about_authors")
async def callback_about_authors(callback: CallbackQuery):
    """
    Показать информацию об авторах
    """
    user_id = callback.from_user.id
    log_action(user_id, 'view_about')

    await callback.message.edit_text(
        text=ABOUT_AUTHORS_MESSAGE,
        reply_markup=get_about_authors_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == "ask_question")
async def callback_ask_question(callback: CallbackQuery):
    """
    Задать вопрос - показать контакт менеджера
    """
    user_id = callback.from_user.id
    log_action(user_id, 'ask_question')

    await callback.message.edit_text(
        text=ASK_QUESTION_MESSAGE,
        reply_markup=get_ask_question_keyboard()
    )
    await callback.answer()
