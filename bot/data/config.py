import os
from dotenv import find_dotenv, load_dotenv


load_dotenv(find_dotenv())

TELEGRAM_API_TOKEN = os.getenv('TELEGRAM_API_TOKEN')
OPEN_AI_API_KEY = os.getenv('OPEN_AI_API_KEY')

DB_USER = os.getenv('DB_USER')
DB_PASS = os.getenv('DB_PASS')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_NAME = os.getenv('DB_NAME')

DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

