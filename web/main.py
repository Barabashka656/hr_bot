import asyncio

from bot.handlers.hr.dao import TableAssistantDAO
from bot.handlers.hr.schemas import TableAssistant
from bot.utils.database import async_session_maker
import os
from flask import Flask, render_template
from dotenv import load_dotenv, find_dotenv

# Load environment variables
load_dotenv(find_dotenv())

app = Flask(__name__)

# Assuming the TableAssistant model and TableAssistantDAO are similar to your aiohttp version
# You need to adapt these parts to work with Flask-SQLAlchemy


async def run_db():
    async with async_session_maker() as session:
        objects = await TableAssistantDAO.find_all(session=session)
    return objects


@app.route('/')
def get_prompts():
    # Adapt to synchronous call
    objects = asyncio.run(run_db())
    return render_template('get_sys_prompts.html', objects=objects)


if __name__ == '__main__':
    # Uncomment one of these depending on your deployment setup
    # app.run(host='0.0.0.0')
    port = os.getenv('PORT')
    app.run(host='0.0.0.0', port=port)
    pass
