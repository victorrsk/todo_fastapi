#!/bin/bash

uv run alembic upgrade head

uv run uvicorn --host 0.0.0.0 --port 8000 todo_fastapi.main.app:app