from bot.handlers.hr.services import UserService
from bot.loader import (
    dp, 
    bot
)
from bot.utils.router import setup_routers

import asyncio


async def main():
    setup_routers(dp)
    await bot.delete_webhook(drop_pending_updates=True)
    await UserService.set_table_count_default(12)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
