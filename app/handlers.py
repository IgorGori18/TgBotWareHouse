import asyncio
import logging

from aiogram import F, Router
from aiogram import Bot, Dispatcher
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, CallbackQuery
from aiogram.filters import CommandStart, Command, or_f
from aiogram.types import Message

import app.keyboards as kb
from app.keyboards import main_keyboard
from app.table_handler import cash_rest

router = Router()



@router.message(or_f(CommandStart(), F.text == 'Вернуться в главное меню'))
async def cmd_start(message: Message):
    await message.answer('Вы в главном меню.', reply_markup = kb.main_keyboard)



@router.message(F.text == 'Остатки')
async def remains(message: Message):
    await message.answer('Выберите остаток...', reply_markup = kb.remains_keyboard)


@router.message(F.text.in_(['Отгрузки', 'Поступления']))
async def transaction (message: Message):
    await message.answer('.....', reply_markup = kb.transaction_keyboard)

@router.callback_query(F.text == 'Общий остаток')
async def rest(callback: CallbackQuery):
    print("Кнопка нажата!")  # Для отладки
    total_rest = cash_rest()
    print("Общий остаток:", total_rest)  # Для отладки
    await callback.message.answer(f"Общий остаток: {total_rest}")  # Отправляем результат пользователю









