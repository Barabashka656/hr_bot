#!/bin/bash
alembic upgrade head
pip install -r requirements.txt
python -m web.main &
python main.py

