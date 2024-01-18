from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

from bot.handlers.callback_datas import MenuCallback


balance_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="Реферальная ссылка", 
                callback_data=MenuCallback(handler='balance', level='1').pack()
            )
        ]
    ],
    resize_keyboard=True,
    selective=True
)

