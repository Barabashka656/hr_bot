from aiohttp_asgi import ASGIResource
from web.main import app

asgi_app = ASGIResource(app)
