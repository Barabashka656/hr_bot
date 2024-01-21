from bot.data.config import MAX_ASSISTANTS_PER_USER
from bot.handlers.hr.services import UserService

from aiogram import F, Router
from aiogram import types
from aiogram.filters import CommandStart


router = Router()

@router.message(CommandStart())
async def start(message: types.Message):
    reply_text = "Добро пожаловать в HappyAISuperCrazyMegaAIEnabledAssistantGPTBeast!\n" \
                "создайте ассистента /create_assistant\n" \
                f"нельзя создать больше {MAX_ASSISTANTS_PER_USER} ассистентов"
    await message.answer(text=reply_text)
    await UserService.new_user(
        user_id=message.from_user.id,
        username=message.from_user.username
    )
