



from aiogram.utils.keyboard import InlineKeyboardBuilder
from bot.handlers.hr.keyboards import TableCallback


def tables_kb(tables_count: int):
    builder = InlineKeyboardBuilder()
    for number in range(1, tables_count+1):
        builder.button(text=str(number), callback_data=TableCallback(number=number).pack())
    builder.adjust(4)
    return builder.as_markup(resize_keyboard=True, selective=True)
