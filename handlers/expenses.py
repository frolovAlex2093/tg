import os
from datetime import datetime
from aiogram import Router, F, Dispatcher
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup

from services.google_sheets import GoogleSheetsService
from handlers.common import main_menu_keyboard  # Добавил импорт клавиатуры

class ExpenseStates(StatesGroup):
    date = State()
    name = State()
    cost = State()

expenses_router = Router()

expenses_keyboard = [
    [KeyboardButton(text='Комиссия'), KeyboardButton(text='Клаудкассир')],
    [KeyboardButton(text='ФНС')],
    [KeyboardButton(text='Оповещения Т-банк'), KeyboardButton(text='Обслуживание Т-банк')],
    [KeyboardButton(text='Свое значение')],
    [KeyboardButton(text='Отмена')]
]

cost_keyboard = [
    [KeyboardButton(text='41,6'), KeyboardButton(text='2900'), KeyboardButton(text='199'), KeyboardButton(text='490')],
    [KeyboardButton(text='Свое значение'), KeyboardButton(text='Отмена')]
]

@expenses_router.message(F.text == 'Добавить расход')
async def start_expense(message: Message, state: FSMContext):
    await message.answer("Введите дату в формате ДД.ММ.ГГГГ (или /today):", reply_markup=ReplyKeyboardRemove())
    await state.set_state(ExpenseStates.date)


    
@expenses_router.message(ExpenseStates.date, F.text == "Отмена")
@expenses_router.message(ExpenseStates.name, F.text == "Отмена")
@expenses_router.message(ExpenseStates.cost, F.text == "Отмена")
async def cancel_payment(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Операция отменена",
        reply_markup=ReplyKeyboardMarkup(
                keyboard=main_menu_keyboard,
                resize_keyboard=True
            )
    )

@expenses_router.message(Command('today'), ExpenseStates.date)
async def today_date_expense(message: Message, state: FSMContext):
    today = message.date.strftime('%d.%m.%Y')
    await state.update_data(date=today)
    await message.answer(
        f"Используем сегодняшнюю дату: {today}\nВыберите название расхода:",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=expenses_keyboard,
            resize_keyboard=True,
            one_time_keyboard=True
        )
    )
    await state.set_state(ExpenseStates.name)

@expenses_router.message(ExpenseStates.date, F.text)
async def process_date_expense(message: Message, state: FSMContext):
    try:
        datetime.strptime(message.text, '%d.%m.%Y')
        await state.update_data(date=message.text)
        await message.answer(
            "Выберите название расхода:",
            reply_markup=ReplyKeyboardMarkup(
                keyboard=expenses_keyboard,
                resize_keyboard=True,
                one_time_keyboard=True
            )
        )
        await state.set_state(ExpenseStates.name)
    except ValueError:
        await message.answer("Неверный формат даты! Попробуйте снова:")

# Обработка выбора названия из кнопок
@expenses_router.message(ExpenseStates.name, F.text.in_(['Комиссия', 'Клаудкассир', 'ФНС', 'Оповещения Т-банк', 'Обслуживание Т-банк']))
async def process_name_expense(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer(
        "Выберите сумму расхода:",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=cost_keyboard,
            resize_keyboard=True,
            one_time_keyboard=True
        )
    )
    await state.set_state(ExpenseStates.cost)

# Обработка "��вое значение" для названия
@expenses_router.message(ExpenseStates.name, F.text == 'Свое значение')
async def custom_name_expense(message: Message, state: FSMContext):
    await message.answer("Введите название расхода:", reply_markup=ReplyKeyboardRemove())
    await state.set_state(ExpenseStates.name)

# Обработка ручного ввода названия
@expenses_router.message(ExpenseStates.name, F.text)
async def process_custom_name_expense(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer(
        "Выберите сумму расхода:",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=cost_keyboard,
            resize_keyboard=True,
            one_time_keyboard=True
        )
    )
    await state.set_state(ExpenseStates.cost)

# Обработка выбора суммы из кнопок
@expenses_router.message(ExpenseStates.cost, F.text.in_(['41,6', '2900', '199', '490']))
async def process_cost(message: Message, state: FSMContext):
    await state.update_data(cost=message.text.replace(',', '.'))  # Конвертируем запятую в точку
    await save_expense_data(message, state)

# Обработка "Свое значение" для суммы
@expenses_router.message(ExpenseStates.cost, F.text == 'Свое значение')
async def custom_cost(message: Message, state: FSMContext):
    await message.answer("Введите сумму расхода:", reply_markup=ReplyKeyboardRemove())
    await state.set_state(ExpenseStates.cost)

# Обработка ручного ввода суммы
@expenses_router.message(ExpenseStates.cost, F.text)
async def process_custom_cost(message: Message, state: FSMContext):
    try:
        cost = message.text.replace(',', '.')
        # Проверяем что введено число
        float(cost)
        await state.update_data(cost=cost)
        await save_expense_data(message, state)
    except ValueError:
        await message.answer("Введите корректное число! Например: 100,50 или 200.75")

async def save_expense_data(message: Message, state: FSMContext):
    data = await state.get_data()
    sheet_service = GoogleSheetsService(
        credentials_file=os.getenv("GOOGLE_SHEETS_CREDS_PATH"),
        sheet_name=os.getenv("SHEET_NAME"),
        worksheet_name=os.getenv("WORKSHEET_NAME")
    )
    
    if await sheet_service.append_data([
        data['date'],
        data['name'],
        data['cost']
    ], 'F1'):
        await message.answer(
            "✅ Расход успешно сохранен!",
            reply_markup=ReplyKeyboardMarkup(
                keyboard=main_menu_keyboard,
                resize_keyboard=True
            )
        )
    else:
        await message.answer(
            "❌ Ошибка при сохранении расхода",
            reply_markup=ReplyKeyboardMarkup(
                keyboard=main_menu_keyboard,
                resize_keyboard=True
            )
        )
    
    await state.clear()


def register_expense_handlers(dp: Dispatcher):
    dp.include_router(expenses_router)