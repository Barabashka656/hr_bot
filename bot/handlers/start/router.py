
from bot.handlers.hr.services import UserService
from bot.handlers.start.keyboards import tables_kb


from aiogram import F, Router
from aiogram import types
from aiogram.filters import CommandStart


router = Router()

@router.message(CommandStart())
async def start(message: types.Message):
    # await UserService.new_user(message.from_user.id)
    reply_text = "Добро пожаловать в бота HappyAI\n" +\
                 "выберите свой стол"
    table_count = await UserService.table_count()
    await message.answer(text=reply_text, reply_markup=tables_kb(table_count))
