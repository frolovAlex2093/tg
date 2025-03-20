import gspread
from oauth2client.service_account import ServiceAccountCredentials


class GoogleSheetsService:
    def __init__(self, credentials_file: str, sheet_name: str, worksheet_name: str):
        scope = ['https://spreadsheets.google.com/feeds',
                 'https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_name(credentials_file, scope)
        self.client = gspread.authorize(creds)
        self.sheet = self.client.open(sheet_name).worksheet(worksheet_name)

    async def append_data(self, data: list, range) -> bool:
        try:
            self.sheet.append_row(data, table_range=range)
            return True
        except Exception as e:
            print(f"Google Sheets error: {e}")
            return False
    
    async def get_student_names(self) -> list[str]:
        """Получает список учеников из колонки A листа"""
        try:
            values = self.sheet.col_values(1)  # Получаем всю колонку A
            
            if not values:
                return []
                
            # Фильтруем пустые строки и заголовки
            students = [
                row.strip() 
                for row in values 
                if row.strip() and not row.startswith("Текущие ученики:")
            ]
            
            return students
            
        except Exception as e:
            print(f"Error getting students: {str(e)}")
            return []

        async def get_lesson_dates(self, start_range: str) -> list:
            """
            Получает данные о датах последних оплаченных занятий, начиная с указанной ячейки.
            
            :param start_range: Имя ячейки (например, "A2"), с которой начинать просмотр.
            :return: Список списков с данными (ФИО, кол-во занятий, дата).
            """
            try:
                data = self.sheet.get(start_range + ":N")  # Берем столбцы A, B, C начиная с указанной строки
                return data
            except Exception as e:
                print(f"Ошибка при получении данных из Google Sheets: {e}")
                return []