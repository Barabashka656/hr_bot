from aiogram.fsm.storage.redis import RedisStorage

from bot.data.config import REDIS_HOST, REDIS_PORT, TELEGRAM_API_TOKEN, OPEN_AI_API_KEY, REDIS_URL

from aiogram import Bot
from aiogram import Dispatcher
from openai import AsyncOpenAI

bot = Bot(token=TELEGRAM_API_TOKEN)
storage = RedisStorage.from_url(REDIS_URL)
dp = Dispatcher(storage=storage)


openai_client = AsyncOpenAI(
    api_key=OPEN_AI_API_KEY,
)
