from bot.data.config import MAX_ASSISTANTS_PER_USER
from bot.handlers.hr.services import UserService

from aiogram import F, Router
from aiogram import types
from aiogram.filters import CommandStart

router = Router()


@router.message(CommandStart())
async def start(message: types.Message):
    reply_text = "Добро пожаловать в HappyAI ассистента!\n\n" \
                 "Здесь Вы можете самостоятельно создать своего ИИ HR /create_assistant\n\n" \
                 f"Вы можете создать до {MAX_ASSISTANTS_PER_USER} ассистентов, " \
                 f"чтобы протестировать разные Ваши гипотезы. После создания " \
                 f"Вы сможете попробовать пройти интервью с каждым из HR'ов"
    await message.answer(text=reply_text)
    await UserService.new_user(
        user_id=message.from_user.id,
        username=message.from_user.username
    )
