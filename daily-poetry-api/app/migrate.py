"""Simple SQL migration runner for backend MVP."""

from __future__ import annotations

from pathlib import Path

from sqlalchemy import text
from sqlalchemy.engine import Engine


def run_sql_migrations(engine: Engine) -> None:
    migration_file = Path(__file__).resolve().parent.parent / "migrations" / "001_init.sql"
    sql_text = migration_file.read_text(encoding="utf-8")

    with engine.begin() as connection:
        for statement in [chunk.strip() for chunk in sql_text.split(";")]:
            if statement:
                connection.execute(text(statement))
