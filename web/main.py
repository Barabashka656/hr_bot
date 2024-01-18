import os

import aiohttp_jinja2
import jinja2
from dotenv import load_dotenv, find_dotenv
from aiohttp import web


load_dotenv(find_dotenv())


env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.join('web', 'templates')),
    trim_blocks=True,
    lstrip_blocks=True,
    keep_trailing_newline=True
)
app = web.Application()

app.router.add_static('/static/', path='root/web/static', name='static')

app.add_routes([
    # web.get('/profile/{user_id}', profile_view),
    # web.get('/add_ingredient', add_ingredient_get),
    # web.get('/add_meal', add_meal_get),
    # web.get('/add_plate', add_plate_get),
])

aiohttp_jinja2.setup(app, loader=env.loader, context_processors=[aiohttp_jinja2.request_processor])

if __name__ == '__main__':
    # web.run_app(app, host='0.0.0.0')
    # web.run_app(app, host='127.0.0.1', port=80)
    pass
