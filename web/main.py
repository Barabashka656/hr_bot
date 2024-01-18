import asyncio
from bot.handlers.hr.dao import TableAssistantDAO
from bot.utils.database import async_session_maker
import os
from flask import Flask, render_template
from dotenv import load_dotenv, find_dotenv

# Load environment variables
load_dotenv(find_dotenv())

app = Flask(__name__)


async def fetch_table_assistants():
    async with async_session_maker() as session:
        return await TableAssistantDAO.find_all(session=session)


def run_async(coroutine):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    return loop.run_until_complete(coroutine)


@app.route('/')
def get_prompts():
    objects = run_async(fetch_table_assistants())
    return render_template('get_sys_prompts.html', objects=objects)


if __name__ == '__main__':
    port = os.getenv('PORT', 5000)  # Default to 5000 if PORT is not set
    app.run(host='0.0.0.0', port=port)
