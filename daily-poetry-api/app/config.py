"""Configuration for Daily Poetry API."""

from __future__ import annotations

import os


def get_database_url() -> str:
    return os.getenv("DAILY_POETRY_DATABASE_URL", "sqlite:///./daily_poetry.db")


def get_cors_origins() -> list[str]:
    raw = os.getenv("DAILY_POETRY_CORS_ORIGINS", "*")
    origins = [item.strip() for item in raw.split(",") if item.strip()]
    return origins or ["*"]
