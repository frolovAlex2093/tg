from aiogram.types import KeyboardButton
from services.google_sheets import GoogleSheetsService
import os

async def get_students_keyboard():
    """Возвращает клавиатуру с учениками"""
    sheet_service = GoogleSheetsService(
        credentials_file=os.getenv("GOOGLE_SHEETS_CREDS_PATH"),
        sheet_name=os.getenv("SHEET_NAME"),
        worksheet_name="Лист2"
    )
    
    students = await sheet_service.get_student_names()
    
    if not students:
        return None
        
    # Создаем кнопки по одной в ряду
    keyboard = [[KeyboardButton(text=student)] for student in students]
    
    # Добавляем кнопку отмены в последний ряд
    keyboard.append([KeyboardButton(text="Отмена")])
    
    return keyboard