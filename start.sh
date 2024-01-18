#!/bin/bash
alembic upgrade head
poetry install
poetry run python main.py
