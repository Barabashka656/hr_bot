from bot.handlers.hr.router import router as hr_router
from bot.handlers.start.router import router as start_router
from bot.handlers.error.router import router as error_router

from aiogram import Dispatcher


def setup_routers(dp: Dispatcher):
    dp.include_routers(
        start_router,
        hr_router,
        error_router
    )
