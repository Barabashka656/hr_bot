#!/bin/bash
# Install Poetry
curl -sSL https://install.python-poetry.org | python3.10

# Add Poetry to PATH
export PATH="$HOME/.local/bin:$PATH"

poetry install
poetry run alembic upgrade head
poetry run python main.py
