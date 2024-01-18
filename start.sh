#!/bin/bash
alembic upgrade head
pip install -r requirements.txt
python main.py
