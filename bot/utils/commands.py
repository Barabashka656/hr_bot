from bot.data.config import MAX_ASSISTANTS_PER_USER

from aiogram import Bot
from aiogram.types import BotCommand



async def set_commands(bot: Bot):
    await bot.set_my_commands(
        [
            BotCommand(command='/start', description='старт бота'),
            BotCommand(
                command='/create_assistant', 
                description=f'создать hr менеджера, максимум: {MAX_ASSISTANTS_PER_USER}'
            ),
            BotCommand(command='/start_interview', description='начать интервью с hr менеджером'),
            BotCommand(
                command='/choose_assistant', 
                description='выбрать с каким hr менеджером вы будете вести диалог'
            )
        ]
    )