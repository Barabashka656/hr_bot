from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.handlers.hr.schemas import Assistant


class HRCallback(CallbackData, prefix='hr'):
    create: bool
    assistant_id: str | None

create_hr_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="Создать HR", 
                callback_data=HRCallback(create=True, assistant_id=None).pack()
            )
        ]
    ],
    resize_keyboard=True,
    selective=True
)

def assistants_kb(assistants: list[Assistant]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for idx, assistant in enumerate(assistants):
        builder.button(
            text=f"№ {idx+1}", 
            callback_data=HRCallback(create=False, assistant_id=assistant.assistant_id).pack()
        )
    builder.adjust(3)
    return builder.as_markup(resize_keyboard=True, selective=True)
