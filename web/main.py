import os

import aiohttp_jinja2
import jinja2
from dotenv import load_dotenv, find_dotenv
from aiohttp import web

from bot.handlers.hr.dao import TableAssistantDAO
from bot.handlers.hr.schemas import TableAssistant
from bot.utils.database import async_session_maker

load_dotenv(find_dotenv())


env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.join('web', 'templates')),
    trim_blocks=True,
    lstrip_blocks=True,
    keep_trailing_newline=True
)


@aiohttp_jinja2.template('get_sys_prompts.html')
async def get_prompts(request):
    async with async_session_maker() as session:
        objects = await TableAssistantDAO.find_all(session=session)
    return {"objects": objects}


app = web.Application()

app.add_routes([
    web.get('/', get_prompts),
    # web.get('/add_ingredient', add_ingredient_get),
    # web.get('/add_meal', add_meal_get),
    # web.get('/add_plate', add_plate_get),
])

aiohttp_jinja2.setup(app, loader=env.loader, context_processors=[aiohttp_jinja2.request_processor])

if __name__ == '__main__':
    # web.run_app(app, host='0.0.0.0')
    web.run_app(app, host='localhost', port=80)
    
