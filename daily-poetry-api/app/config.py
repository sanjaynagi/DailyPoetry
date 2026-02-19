"""Configuration for Daily Poetry API."""

from __future__ import annotations

import os


def get_database_url() -> str:
    return os.getenv("DAILY_POETRY_DATABASE_URL", "sqlite:///./daily_poetry.db")
