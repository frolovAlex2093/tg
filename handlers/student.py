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


class AddStudentStates(StatesGroup):
    name = State()
    confirmation = State()

@router.message(F.text == 'Добавить ученика')
async def start_adding_student(message: Message, state: FSMContext):
    await message.answer(
        "Введите ФИО ученика:",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(AddStudentStates.name)

@router.message(AddStudentStates.name, F.text)
async def process_student_name(message: Message, state: FSMContext):
    # Сохраняем имя и просим подтверждение
    await state.update_data(name=message.text.strip())
    
    confirm_keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Подтвердить"), KeyboardButton(text="Отменить")]
        ],
        resize_keyboard=True
    )
    
    await message.answer(
        f"Добавить ученика: {message.text}?\n"
        "Проверьте правильность написания!",
        reply_markup=confirm_keyboard
    )
    await state.set_state(AddStudentStates.confirmation)

@router.message(AddStudentStates.confirmation, F.text == "Подтвердить")
async def confirm_adding(message: Message, state: FSMContext):
    data = await state.get_data()
    student_name = data['name']
    
    sheet_service = GoogleSheetsService(
        credentials_file=os.getenv("GOOGLE_SHEETS_CREDS_PATH"),
        sheet_name=os.getenv("SHEET_NAME"),
        worksheet_name="Лист2"
    )
    
    # Проверяем существование ученика
    existing_students = await sheet_service.get_student_names()
    if student_name in existing_students:
        await message.answer(
            "⚠️ Этот ученик уже существует в списке!",
            reply_markup=ReplyKeyboardMarkup(
                keyboard=main_menu_keyboard,
                resize_keyboard=True
            )
        )
        await state.clear()
        return
    
    # Добавляем в конец списка
    if await sheet_service.append_data([student_name], 'A1'):
        await message.answer(
            "✅ Ученик успешно добавлен!",
            reply_markup=ReplyKeyboardMarkup(
                keyboard=main_menu_keyboard,
                resize_keyboard=True
            )
        )
    else:
        await message.answer(
            "❌ Ошибка при добавлении ученика",
            reply_markup=ReplyKeyboardMarkup(
                keyboard=main_menu_keyboard,
                resize_keyboard=True
            )
        )
    
    await state.clear()

@router.message(AddStudentStates.confirmation, F.text == "Отменить")
async def cancel_adding(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Добавление ученика отменено",
        reply_markup=ReplyKeyboardMarkup(
                keyboard=main_menu_keyboard,
                resize_keyboard=True
            )
    )

def register_student_handlers(dp: Dispatcher):
    dp.include_router(router)