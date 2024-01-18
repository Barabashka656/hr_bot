from bot.data.config import TELEGRAM_API_TOKEN, OPEN_AI_API_KEY

from aiogram import Bot
from aiogram import Dispatcher
from openai import AsyncOpenAI


bot = Bot(token=TELEGRAM_API_TOKEN)
dp = Dispatcher()

openai_client = AsyncOpenAI(
    api_key=OPEN_AI_API_KEY,
)
