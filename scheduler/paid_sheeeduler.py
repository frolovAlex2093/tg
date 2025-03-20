import asyncio
import os
from datetime import datetime, timedelta
from aiogram import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from services.google_sheets import GoogleSheetsService
from notification.notifier import Notifier

class LessonScheduler:
    def init(self, bot: Bot):
        self.bot = bot
        self.scheduler = AsyncIOScheduler()
        self.sheet_service = GoogleSheetsService(
            credentials_file=os.getenv("GOOGLE_SHEETS_CREDS_PATH"),
            sheet_name=os.getenv("SHEET_NAME"),
            worksheet_name=os.getenv("WORKSHEET_NAME")
        )
        self.notifier = Notifier(bot)
        self.start_range = "L6"  # Диапазон начала проверки

    async def check_lessons(self):
        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%d.%m.%Y")
        records = self.sheet_service.get_lesson_dates(self.start_range)

        for row in records:
            try:
                student_name, lessons_paid, last_date = row
                if last_date == tomorrow:
                    await self.notifier.send_notification(student_name)
            except ValueError:
                continue  # Пропускаем строки с некорректными данными

    def start(self):
        # self.scheduler.add_job(self.check_lessons, "cron", hour=9, minute=0)
        self.scheduler.add_job(self.check_lessons, "interval", minute=1)
        self.scheduler.start()