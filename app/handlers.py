
from app.table_handler import get_db_connection

from aiogram import F, Router
from aiogram.types import CallbackQuery
from aiogram.filters import CommandStart, or_f
from aiogram.types import Message

import app.keyboards as kb

from app.table_handler import rest_of_controllers
from app.table_handler import cash_rest, rest_of_good
from app.table_handler import shipments, delivery
from app.table_handler import employees_work

from app.table_handler import get_product_name, insert_transaction

from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

router = Router()

class ProductRest(StatesGroup):
    article = State()
    controller = State()

class MovementForm(StatesGroup):
    article = State()
    move_type = State()
    amount = State()
    comment = State()

class TransactionStates(StatesGroup):
    waiting_for_article = State()
    waiting_for_receipt = State()
    waiting_for_shipment = State()
    waiting_for_comment = State()
    waiting_for_surname = State()



@router.message(or_f(CommandStart(), F.text == "Вернуться в главное меню"))
async def cmd_start(message: Message):
    await message.answer("Вы в главном меню.", reply_markup = kb.main_keyboard)

@router.message(F.text == "Отчеты")
async def reports(message: Message):
    await message.answer("Выберите", reply_markup = kb.second_keyboard)

@router.message(F.text == "Назад")
async def back(message: Message):
    await message.answer("Выберите", reply_markup = kb.second_keyboard)


@router.message(F.text == "Остатки")
async def remains(message: Message):
    await message.answer("Выберите остаток...", reply_markup = kb.remains_keyboard)


@router.message(F.text == "Поступления")
async def delivery_menu(message: Message):
    await message.answer('Поступления', reply_markup = kb.delivery_keyboard)

@router.message(F.text == "Отгрузки")
async def shipments_menu(message: Message):
    await message.answer("Отгрузки", reply_markup = kb.shipment_keyboard)

@router.message(F.text == "Отчеты сотрудников")
async def employees_transaction(message: Message):
    ans = employees_work()
    await message.answer(ans)


@router.message(F.text == "Общий остаток")
async def money_rest(message: Message):
    total_rest = cash_rest()
    await message.answer(f"Общий остаток: {total_rest} руб")

@router.message(F.text == "Остаток контроллеров")
async def controller_rest(message: Message):
    total_rest = rest_of_controllers()
    await message.answer(total_rest)


@router.message(F.text == "Отгрузки за 7 дней")
async def seven_days_shipment(message: Message, state: FSMContext):
    ans = shipments(0)
    await message.answer(ans)


@router.message(F.text == "Отгрузки за месяц")
async def thirty_days_shipment(message: Message, state: FSMContext):
    ans = shipments(1)
    await message.answer(ans)



@router.message(F.text == "Поступления за 7 дней")
async def seven_days_delivery(message: Message, state: FSMContext):
    ans = delivery(0)
    await message.answer(ans)


@router.message(F.text == "Поступления за месяц")
async def thirty_days_delivery(message: Message, state: FSMContext):
    ans = delivery(1)
    await message.answer(ans)


@router.message(F.text == "Остаток определенного товара")
async def article_rest(message: Message, state: FSMContext):
    await state.set_state(ProductRest.article)
    await message.answer("Напишите артикул товара: ")
@router.message(ProductRest.article)
async def article_name(message: Message, state: FSMContext):
    ans = rest_of_good(message.text)
    await message.answer(ans)
    await state.clear()



# ВВОД В ТАБЛИЦУ
# Обработчик кнопки «Ввод поступления/отгрузки»
@router.message(F.text=="Ввод поступления/отгрузки")
async def start_transaction(message: Message, state: FSMContext):
    await message.answer("Введите артикул товара:")
    await state.set_state(TransactionStates.waiting_for_article)


@router.message(TransactionStates.waiting_for_article)
async def process_article(message: Message, state: FSMContext):
    article = message.text.strip()
    connection = get_db_connection()
    product_name = get_product_name(connection, article)
    connection.close()
    if product_name == "Unknown":
        await message.answer("Артикул не найден. Пожалуйста, введите существующий артикул:")
        return
    await state.update_data(article=article)
    await message.answer("Введите количество поступления (если нет, введите 0):")
    await state.set_state(TransactionStates.waiting_for_receipt)

# Обработка ввода количества поступления
@router.message(TransactionStates.waiting_for_receipt)
async def process_receipt(message: Message, state: FSMContext):
    try:
        receipt = int(message.text.strip())
    except ValueError:
        await message.answer("Пожалуйста, введите число для поступления.")
        return
    await state.update_data(receipt=receipt)
    await message.answer("Введите количество отгрузки (если нет, введите 0):")
    await state.set_state(TransactionStates.waiting_for_shipment)

# Обработка ввода количества отгрузки
@router.message(TransactionStates.waiting_for_shipment)
async def process_shipment(message: Message, state: FSMContext):
    try:
        shipment = int(message.text.strip())
    except ValueError:
        await message.answer("Пожалуйста, введите число для отгрузки.")
        return
    await state.update_data(shipment=shipment)
    await message.answer("Введите комментарий: ")
    await state.set_state(TransactionStates.waiting_for_comment)


@router.message(TransactionStates.waiting_for_comment)
async def process_comment(message: Message, state: FSMContext):
    comment = message.text.strip()
    await state.update_data(comment=comment)
    await message.answer("Выберите вашу фамилию:", reply_markup=kb.surname_keyboard)
    await state.set_state(TransactionStates.waiting_for_surname)

@router.callback_query(TransactionStates.waiting_for_surname)
async def process_surname(callback: CallbackQuery, state: FSMContext):
    # Получаем фамилию напрямую из callback_data
    chosen_surname = callback.data
    await state.update_data(surname=chosen_surname)

    data_state = await state.get_data()
    article = data_state.get("article")
    receipt = data_state.get("receipt", 0)
    shipment = data_state.get("shipment", 0)
    comment = data_state.get("comment", "")

    connection = get_db_connection()
    product_name = get_product_name(connection, article)
    insert_transaction(connection, article, product_name, receipt, shipment, comment, chosen_surname)
    connection.close()

    await callback.message.answer("Транзакция успешно добавлена!")
    await state.clear()
    await callback.answer()






