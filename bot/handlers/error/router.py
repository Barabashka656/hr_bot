from aiogram import F, Router
from aiogram.filters import ExceptionTypeFilter
from aiogram.types import ErrorEvent, Message

from bot.handlers.error.exceptions import UserExistException
from bot.loader import dp

router = Router()

@dp.error(ExceptionTypeFilter(UserExistException), F.update.callback_query.as_("message"))
async def handle_my_custom_exception(event: ErrorEvent, message: Message):
    await message.answer(event.exception.message)


@dp.error(ExceptionTypeFilter(Exception), F.update.message.as_("message"))
async def handle_my_custom_exception(event: ErrorEvent, message: Message):
    reply_text='произошла ошибка'
    print(event.exception)
    await message.answer(text=reply_text)

@dp.error()
async def error_handler(event: ErrorEvent):
    print(event)
    pass
