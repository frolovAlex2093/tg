from aiogram import Bot
import os

class Notifier:
    def init(self, bot: Bot):
        self.bot = bot
        self.user_ids = [int(user_id) for user_id in os.getenv("NOTIFICATION_USER_IDS", "").split(",") if user_id]

    async def send_notification(self, student_name: str):
        message = f"⚠️ Напоминание: Завтра у {student_name} заканчиваются оплаченные занятия!"
        for user_id in self.user_ids:
            try:
                await self.bot.send_message(user_id, message)
            except Exception as e:
                print(f"Ошибка отправки уведомления пользователю {user_id}: {e}")