# -*- coding: utf-8 -*-
"""
Inline-клавиатуры (кнопки) для бота
"""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from texts.messages import MANAGER_USERNAME


def get_main_menu_keyboard():
    """
    Главное меню (после /start)
    3 кнопки:
    - Условия доступа
    - Об авторах канала
    - Задать вопрос
    """
    builder = InlineKeyboardBuilder()
    builder.button(text="💛 Условия доступа", callback_data="tariffs")
    builder.button(text="👥 Об авторах канала", callback_data="about_authors")
    builder.button(text="❓ Задать вопрос", callback_data="ask_question")
    builder.adjust(1)  # 1 кнопка в ряд
    return builder.as_markup()


def get_tariffs_keyboard():
    """
    Кнопки выбора тарифа:
    - Выбрать тариф «БАЗОВЫЙ»
    - Выбрать тариф «АССИСТЕНТ ДЛЯ АССИСТЕНТА»
    - Назад в меню
    """
    builder = InlineKeyboardBuilder()
    builder.button(text="💼 Выбрать тариф «БАЗОВЫЙ»", callback_data="select_basic")
    builder.button(text="⭐ Выбрать тариф «АССИСТЕНТ ДЛЯ АССИСТЕНТА»", callback_data="select_assistant")
    builder.button(text="🏠 Назад в меню", callback_data="main_menu")
    builder.adjust(1)  # 1 кнопка в ряд
    return builder.as_markup()


def get_contact_manager_keyboard():
    """
    Кнопки после выбора тарифа:
    - Написать менеджеру (ссылка на @sp_assistant)
    - Назад к тарифам
    """
    builder = InlineKeyboardBuilder()
    builder.button(
        text="✉️ Написать менеджеру",
        url=f"https://t.me/{MANAGER_USERNAME}"
    )
    builder.button(text="⬅️ Назад к тарифам", callback_data="tariffs")
    builder.button(text="🏠 В меню", callback_data="main_menu")
    builder.adjust(1)  # 1 кнопка в ряд
    return builder.as_markup()


def get_about_authors_keyboard():
    """
    Кнопки на странице "Об авторах":
    - Условия доступа
    - Задать вопрос
    - В меню
    """
    builder = InlineKeyboardBuilder()
    builder.button(text="💛 Условия доступа", callback_data="tariffs")
    builder.button(text="❓ Задать вопрос", callback_data="ask_question")
    builder.button(text="🏠 В меню", callback_data="main_menu")
    builder.adjust(1)  # 1 кнопка в ряд
    return builder.as_markup()


def get_ask_question_keyboard():
    """
    Кнопка для страницы "Задать вопрос":
    - Написать менеджеру
    - В меню
    """
    builder = InlineKeyboardBuilder()
    builder.button(
        text="✉️ Написать менеджеру",
        url=f"https://t.me/{MANAGER_USERNAME}"
    )
    builder.button(text="🏠 В меню", callback_data="main_menu")
    builder.adjust(1)  # 1 кнопка в ряд
    return builder.as_markup()


def get_contact_request_keyboard():
    """
    Клавиатура для запроса контакта (номера телефона)
    """
    from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
    
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    contact_button = KeyboardButton(
        text="📱 Поделиться контактом",
        request_contact=True
    )
    skip_button = KeyboardButton(text="⏭ Пропустить")
    
    keyboard.add(contact_button)
    keyboard.add(skip_button)
    
    return keyboard

