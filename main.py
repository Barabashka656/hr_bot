from bot.handlers.hr.services import RedisService, UserService
from bot.loader import (
    dp, 
    bot
)
from bot.utils.commands import set_commands
from bot.utils.router import setup_routers

import asyncio

async def main():
    setup_routers(dp)
    await set_commands(bot)
    asyncio.create_task(RedisService.process_queue())
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
