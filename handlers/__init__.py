from .common import register_common_handlers
from .income import register_income_handlers
from .expenses import register_expense_handlers
from .paid import register_paid_handlers
from .student import register_student_handlers

__all__ = ['register_common_handlers', 'register_income_handlers', 'register_expense_handlers', 'register_paid_handlers', 'register_student_handlers']