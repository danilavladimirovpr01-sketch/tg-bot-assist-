# -*- coding: utf-8 -*-
"""
Админ-панель бота
Команды для администратора: статистика, экспорт, рассылки
"""
import asyncio
import csv
import io
from datetime import datetime
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, BufferedInputFile
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from config import ADMIN_IDS
from database.db import (
    get_user_count,
    get_tariff_stats,
    get_users_with_contacts,
    get_all_user_ids,
    get_contacts_count,
    get_recent_users_count
)


router = Router()


class BroadcastState(StatesGroup):
    """Состояния для рассылки"""
    waiting_for_message = State()
    waiting_for_confirmation = State()


def is_admin(user_id: int) -> bool:
    """
    Проверка прав администратора
    """
    if not ADMIN_IDS:
        return False
    return user_id in ADMIN_IDS


@router.message(Command("myid"))
async def cmd_myid(message: Message):
    """
    Показать свой Telegram ID
    Доступно всем пользователям
    """
    user_id = message.from_user.id
    await message.answer(
        f"<b>Ваш Telegram ID:</b> <code>{user_id}</code>\n\n"
        f"Этот ID можно использовать для настройки прав администратора."
    )


@router.message(Command("admin", "stats"))
async def cmd_admin(message: Message):
    """
    Показать общую статистику бота
    Доступно только админу
    """
    if not is_admin(message.from_user.id):
        await message.answer("У вас нет прав для использования этой команды.")
        return

    # Собираем статистику
    total_users = get_user_count()
    contacts_count = get_contacts_count()
    tariff_stats = get_tariff_stats()

    today = get_recent_users_count(1)
    week = get_recent_users_count(7)
    month = get_recent_users_count(30)

    contacts_percent = round(contacts_count / total_users * 100) if total_users > 0 else 0

    stats_text = f"""
📊 <b>Статистика бота</b>

👥 <b>Всего пользователей:</b> {total_users}
📱 <b>Оставили контакты:</b> {contacts_count} ({contacts_percent}%)

📦 <b>Выбрали тарифы:</b>
  💼 Базовый: {tariff_stats.get('basic', 0)}
  ⭐ Ассистент: {tariff_stats.get('assistant', 0)}
  ❌ Не выбрали: {total_users - tariff_stats.get('basic', 0) - tariff_stats.get('assistant', 0)}

📈 <b>Активность:</b>
  Сегодня: {today}
  За неделю: {week}
  За месяц: {month}

<i>Обновлено: {datetime.now().strftime('%d.%m.%Y %H:%M')}</i>
"""

    await message.answer(stats_text)


@router.message(Command("users"))
async def cmd_users(message: Message):
    """
    Список пользователей с контактами
    Доступно только админу
    """
    if not is_admin(message.from_user.id):
        await message.answer("У вас нет прав для использования этой команды.")
        return

    users = get_users_with_contacts(limit=10)
    total_contacts = get_contacts_count()

    if not users:
        await message.answer("Пока нет пользователей с контактами.")
        return

    users_text = "👥 <b>Пользователи с контактами</b> (первые 10):\n\n"

    for idx, user in enumerate(users, 1):
        user_id, username, first_name, last_name, phone, registered, tariff = user

        name = first_name or "Без имени"
        if last_name:
            name += f" {last_name}"

        username_str = f"@{username}" if username else ""
        tariff_emoji = "💼" if tariff == "basic" else "⭐" if tariff == "assistant" else "❓"
        tariff_name = "Базовый" if tariff == "basic" else "Ассистент" if tariff == "assistant" else "Не выбран"

        reg_date = datetime.fromisoformat(registered).strftime('%d.%m.%Y')

        users_text += f"""
{idx}. <b>{name}</b> {username_str}
   📱 <code>{phone}</code>
   🎯 Тариф: {tariff_emoji} {tariff_name}
   📅 Зарегистрирован: {reg_date}
"""

    users_text += f"\n<i>Показано 10 из {total_contacts}</i>\n"
    users_text += "<i>Используйте /export для полной выгрузки</i>"

    await message.answer(users_text)


@router.message(Command("export"))
async def cmd_export(message: Message):
    """
    Экспорт всех контактов в CSV
    Доступно только админу
    """
    if not is_admin(message.from_user.id):
        await message.answer("У вас нет прав для использования этой команды.")
        return

    await message.answer("📤 Экспорт базы контактов...")

    users = get_users_with_contacts()

    if not users:
        await message.answer("Нет пользователей с контактами для экспорта.")
        return

    # Создаем CSV в памяти
    output = io.StringIO()
    writer = csv.writer(output, delimiter=';')  # Точка с запятой для Excel (русская версия)

    # Заголовки на русском
    writer.writerow([
        'ID',
        'Username',
        'Имя',
        'Фамилия',
        'Телефон',
        'Тариф',
        'Дата регистрации'
    ])

    # Данные
    for user in users:
        user_id, username, first_name, last_name, phone, registered, tariff = user

        # Преобразуем тариф в читаемый вид
        tariff_name = {
            'basic': 'Базовый',
            'assistant': 'Ассистент для ассистента',
            None: 'Не выбран'
        }.get(tariff, 'Не выбран')

        # Преобразуем дату в читаемый формат
        try:
            reg_date = datetime.fromisoformat(registered).strftime('%d.%m.%Y %H:%M')
        except:
            reg_date = registered

        writer.writerow([
            user_id,
            f"@{username}" if username else '',
            first_name or '',
            last_name or '',
            phone,
            tariff_name,
            reg_date
        ])

    # Конвертируем в байты
    csv_bytes = output.getvalue().encode('utf-8-sig')  # BOM для Excel
    output.close()

    # Создаем файл для отправки
    filename = f"contacts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    file = BufferedInputFile(csv_bytes, filename=filename)

    await message.answer_document(
        document=file,
        caption=f"✅ Экспортировано {len(users)} контактов"
    )


@router.message(Command("broadcast"))
async def cmd_broadcast(message: Message, state: FSMContext):
    """
    Начать рассылку сообщений
    Доступно только админу
    """
    if not is_admin(message.from_user.id):
        await message.answer("У вас нет прав для использования этой команды.")
        return

    total_users = get_user_count()

    await state.set_state(BroadcastState.waiting_for_message)

    await message.answer(
        f"📢 <b>Рассылка сообщений</b>\n\n"
        f"Отправьте текст сообщения, который хотите разослать всем пользователям ({total_users} чел.).\n\n"
        f"Для отмены используйте /cancel"
    )


@router.message(Command("cancel"))
async def cmd_cancel(message: Message, state: FSMContext):
    """
    Отмена текущего действия
    """
    current_state = await state.get_state()
    if current_state is None:
        await message.answer("Нечего отменять.")
        return

    await state.clear()
    await message.answer("Действие отменено.")


@router.message(BroadcastState.waiting_for_message)
async def broadcast_message_received(message: Message, state: FSMContext):
    """
    Получен текст для рассылки, запрашиваем подтверждение
    """
    if not is_admin(message.from_user.id):
        return

    broadcast_text = message.text
    total_users = get_user_count()

    # Сохраняем текст в состояние
    await state.update_data(broadcast_text=broadcast_text)
    await state.set_state(BroadcastState.waiting_for_confirmation)

    await message.answer(
        f"Вы собираетесь отправить это сообщение <b>{total_users}</b> пользователям:\n\n"
        f"─────────────\n"
        f"{broadcast_text}\n"
        f"─────────────\n\n"
        f"Подтверждаете? Напишите <b>да</b> или <b>нет</b>"
    )


@router.message(BroadcastState.waiting_for_confirmation)
async def broadcast_confirmation(message: Message, state: FSMContext):
    """
    Подтверждение рассылки
    """
    if not is_admin(message.from_user.id):
        return

    confirmation = message.text.lower().strip()

    if confirmation not in ['да', 'yes', 'y', 'д']:
        await state.clear()
        await message.answer("Рассылка отменена.")
        return

    # Получаем текст из состояния
    data = await state.get_data()
    broadcast_text = data.get('broadcast_text')

    await state.clear()

    # Получаем всех пользователей
    user_ids = get_all_user_ids()
    total = len(user_ids)

    await message.answer(f"📨 Рассылка началась... (0/{total})")

    success = 0
    failed = 0
    start_time = datetime.now()

    # Отправляем сообщения
    for idx, user_id in enumerate(user_ids, 1):
        try:
            await message.bot.send_message(user_id, broadcast_text)
            success += 1
        except Exception:
            failed += 1

        # Показываем прогресс каждые 25 сообщений
        if idx % 25 == 0 or idx == total:
            try:
                await message.answer(f"✅ {idx}/{total}")
            except Exception:
                pass

        # Задержка, чтобы не попасть под ограничения Telegram
        await asyncio.sleep(0.05)  # 50ms между сообщениями

    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()

    # Итоговая статистика
    await message.answer(
        f"📊 <b>Рассылка завершена!</b>\n\n"
        f"✅ Успешно: {success}\n"
        f"❌ Ошибок: {failed} (заблокировали бота)\n"
        f"⏱ Время: {int(duration)} сек"
    )
