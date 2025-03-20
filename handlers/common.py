from aiogram import Router, F, Dispatcher
from aiogram.types import Message, ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from services.google_sheets import GoogleSheetsService


router = Router()
main_menu_keyboard =  [
    [KeyboardButton(text='Добавить доход'), KeyboardButton(text='Добавить расход')],
    [KeyboardButton(text='Добавить оплаченные занятия')],
    [KeyboardButton(text='Добавить ученика')]
]

@router.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        "Добро пожаловать! Выберите действие:",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=main_menu_keyboard,
            resize_keyboard=True,
            input_field_placeholder="Выберите действие"
        )
    )

@router.message(F.text == "Главное меню")
async def main_menu(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Главное меню:",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=main_menu_keyboard,
            resize_keyboard=True
        )
    )

def register_common_handlers(dp: Dispatcher):
    dp.include_router(router)