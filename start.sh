#!/bin/bash
alembic upgrade head
pip install -r requirements.txt
#uvicorn asgi:asgi_app web.main:app
python -m web.main &
#uvicorn web.main:app --host 0.0.0.0 --port $PORT &
python main.py

