#!/bin/bash
alembic upgrade head
pip install -r requirements.txt
#uvicorn asgi:asgi_app web.main:app
python -m web.main &
python main.py
