




from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


class TableCallback(CallbackData, prefix='table'):
    number: int

class HRCallback(CallbackData, prefix='hr'):
    create: bool

create_hr_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="Создать HR", 
                callback_data=HRCallback(create=True).pack()
            )
        ]
    ],
    resize_keyboard=True,
    selective=True
)