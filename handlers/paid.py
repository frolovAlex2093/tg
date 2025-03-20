import os
from datetime import datetime
from aiogram import Router, F, Dispatcher
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
from utils.students_keyboard import get_students_keyboard

from services.google_sheets import GoogleSheetsService
from handlers.common import main_menu_keyboard  # Добавил импорт клавиатуры

router = Router()

lesson_keyboard =  [
    [KeyboardButton(text='1'), KeyboardButton(text='4'), KeyboardButton(text='8')],
    [KeyboardButton(text='Свое значение'), KeyboardButton(text="Отмена")]
]

class PaymentStates(StatesGroup):
    date = State()
    student = State()
    lessons = State()

@router.message(F.text == 'Добавить оплаченные занятия')
async def start_payment(message: Message, state: FSMContext):
    keyboard = await get_students_keyboard()
    if not keyboard:
        await message.answer("Нет доступных учеников")
        return
        
    await message.answer(
        "Выберите ученика:",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=keyboard,
            resize_keyboard=True,
            one_time_keyboard=True
        )
    )
    await state.set_state(PaymentStates.student)

@router.message(PaymentStates.student, F.text == "Отмена")
@router.message(PaymentStates.lessons, F.text == "Отмена")
@router.message(PaymentStates.date, F.text == "Отмена")
async def cancel_payment(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Операция отменена",
        reply_markup=ReplyKeyboardMarkup(
                keyboard=main_menu_keyboard,
                resize_keyboard=True
            )
    )

@router.message(PaymentStates.student, F.text)
async def process_student(message: Message, state: FSMContext):
    await state.update_data(student=message.text)
    
    await message.answer(
        "Выберите количество оплаченных занятий:",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=lesson_keyboard,
            resize_keyboard=True,
            one_time_keyboard=True
        )
    )
    await state.set_state(PaymentStates.lessons)

@router.message(PaymentStates.lessons, F.text.in_(['1', '4', '8']))
async def process_lessons(message: Message, state: FSMContext):
    await state.update_data(lessons=message.text)
    await message.answer(
        "Введите дату оплаты (ДД.ММ.ГГГГ) или используйте /today:",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(PaymentStates.date)

@router.message(PaymentStates.lessons, F.text == "Свое значение")
async def custom_lessons(message: Message, state: FSMContext):
    await message.answer("Вве��ите количество оплаченных занятий:", reply_markup=ReplyKeyboardRemove())
    await state.set_state(PaymentStates.lessons)

@router.message(PaymentStates.lessons, F.text)
async def process_custom_lessons(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Введите целое число!")
        return
        
    await state.update_data(lessons=message.text)
    await message.answer(
        "Введите дату оплаты (ДД.ММ.ГГГГ) или используйте /today:",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(PaymentStates.date)

@router.message(Command("today"), PaymentStates.date)
async def payment_today(message: Message, state: FSMContext):
    today = datetime.now().strftime("%d.%m.%Y")
    await state.update_data(date=today)
    await save_payment_data(message, state)

@router.message(PaymentStates.date, F.text)
async def process_date(message: Message, state: FSMContext):
    try:
        datetime.strptime(message.text, "%d.%m.%Y")
        await state.update_data(date=message.text)
        await save_payment_data(message, state)
    except ValueError:
        await message.answer("Неверный формат даты! Используйте ДД.ММ.ГГГГ")

async def save_payment_data(message: Message, state: FSMContext):
    data = await state.get_data()
    sheet_service = GoogleSheetsService(
        credentials_file=os.getenv("GOOGLE_SHEETS_CREDS_PATH"),
        sheet_name=os.getenv("SHEET_NAME"),
        worksheet_name=os.getenv("WORKSHEET_NAME")
    )

    row_data = [
        data['student'],
        data['lessons'],
        data['date']
    ]

    if await sheet_service.append_data(row_data, 'L5'):
        await message.answer(
            "✅ Данные об оплате успешно сохранены!",
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


def register_paid_handlers(dp: Dispatcher):
    dp.include_router(router)