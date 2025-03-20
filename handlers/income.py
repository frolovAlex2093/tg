import os
from datetime import datetime
from aiogram import Router, F, Dispatcher
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup

from services.google_sheets import GoogleSheetsService
from handlers.common import main_menu_keyboard  # Добавил импорт клавиатуры

router = Router()

income_keyboard =  [
    [KeyboardButton(text='1500'), KeyboardButton(text='5600'),KeyboardButton(text='10400')],
    [KeyboardButton(text='Свое значение'), KeyboardButton(text='Отмена')]
]
lesson_keyboard =  [
    [KeyboardButton(text='1'), KeyboardButton(text='4'), KeyboardButton(text='8')],
    [KeyboardButton(text='Свое значение'), KeyboardButton(text='Отмена')]
]

class IncomeStates(StatesGroup):
    date = State()
    name = State()
    income = State()
    lessons = State()

@router.message(F.text == 'Добавить доход')
async def start_income(message: Message, state: FSMContext):
    await message.answer("Введите дату в формате ДД.ММ.ГГГГ (или /today):", reply_markup=ReplyKeyboardRemove())
    await state.set_state(IncomeStates.date)

@router.message(IncomeStates.date, F.text == "Отмена")
@router.message(IncomeStates.name, F.text == "Отмена")
@router.message(IncomeStates.income, F.text == "Отмена")
@router.message(IncomeStates.lessons, F.text == "Отмена")
async def cancel_payment(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Операция отменена",
        reply_markup=ReplyKeyboardMarkup(
                keyboard=main_menu_keyboard,
                resize_keyboard=True
            )
    )

@router.message(Command('today'), IncomeStates.date)
async def today_date(message: Message, state: FSMContext):
    today = message.date.strftime('%d.%m.%Y')
    await state.update_data(date=today)
    await message.answer(f"Используем сегодняшнюю дату: {today}\nВведите название дохода:", reply_markup=ReplyKeyboardRemove())
    await state.set_state(IncomeStates.name)

@router.message(IncomeStates.date, F.text)
async def process_date(message: Message, state: FSMContext):
    try:
        datetime.strptime(message.text, '%d.%m.%Y')
        await state.update_data(date=message.text)
        await message.answer("Введите название дохода:")
        await state.set_state(IncomeStates.name)
    except ValueError:
        await message.answer("Неверный формат даты! Попробуйте снова:")

@router.message(IncomeStates.name, F.text)
async def process_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer(
        "Выберите доход:",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=income_keyboard,
            resize_keyboard=True,
            one_time_keyboard=True
        )
    )
    await state.set_state(IncomeStates.income)

@router.message(IncomeStates.income, F.text.in_(['10400', '5600', '1500']))
async def process_income(message: Message, state: FSMContext):
    await state.update_data(income=message.text)
    await message.answer(
        "Выберите количество уроков:",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=lesson_keyboard,
            resize_keyboard=True,
            one_time_keyboard=True
        )
    )
    await state.set_state(IncomeStates.lessons)

@router.message(IncomeStates.income, F.text == 'Свое значение')
async def custom_income(message: Message, state: FSMContext):
    await message.answer("Введите сумму дохода:")
    await state.set_state(IncomeStates.income)

@router.message(IncomeStates.income, F.text)
async def process_custom_income(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Введите число!")
        return
    
    await state.update_data(income=message.text)
    await message.answer(
        "Выберите количество уроков:",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=lesson_keyboard,
            resize_keyboard=True,
            one_time_keyboard=True
        )
    )
    await state.set_state(IncomeStates.lessons)

@router.message(IncomeStates.lessons, F.text.in_(['1', '4', '8']))
async def process_lessons(message: Message, state: FSMContext):
    await state.update_data(lessons=message.text)
    await save_data(message, state)

@router.message(IncomeStates.lessons, F.text == 'Свое значение')
async def custom_lessons(message: Message, state: FSMContext):
    await message.answer("Введите количество уроков:")
    await state.set_state(IncomeStates.lessons)
@router.message(IncomeStates.lessons, F.text)
async def process_custom_lessons(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Введите число!")
        return
    
    await state.update_data(lessons=message.text)
    await save_data(message, state)

async def save_data(message: Message, state: FSMContext):
    data = await state.get_data()
    sheet_service = GoogleSheetsService(
        credentials_file=os.getenv("GOOGLE_SHEETS_CREDS_PATH"),
        sheet_name=os.getenv("SHEET_NAME"),
        worksheet_name=os.getenv("WORKSHEET_NAME")
    )
    
    if await sheet_service.append_data([
        data['date'],
        data['name'],
        data['income'],
        data['lessons']
    ], 'A1'):
        await message.answer(
            "✅ Данные успешно сохранены!",
            reply_markup=ReplyKeyboardMarkup(
                keyboard=main_menu_keyboard,
                resize_keyboard=True
            )
        )
    else:
        await message.answer(
            "❌ Ошибка при сохранении данных",
            reply_markup=ReplyKeyboardMarkup(
                keyboard=main_menu_keyboard,
                resize_keyboard=True
            )
        )
    
    await state.clear()


def register_income_handlers(dp: Dispatcher):
    dp.include_router(router)