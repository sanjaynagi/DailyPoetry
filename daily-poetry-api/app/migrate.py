"""Simple SQL migration runner for backend MVP."""

from __future__ import annotations

import re
from pathlib import Path

from sqlalchemy import text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import OperationalError


def run_sql_migrations(engine: Engine) -> None:
    migrations_dir = Path(__file__).resolve().parent.parent / "migrations"
    migration_files = sorted(migrations_dir.glob("*.sql"))

    with engine.begin() as connection:
        dialect_name = connection.dialect.name
        for migration_file in migration_files:
            sql_text = migration_file.read_text(encoding="utf-8")
            for statement in [chunk.strip() for chunk in sql_text.split(";")]:
                if statement:
                    sql_statement = statement
                    if dialect_name == "sqlite":
                        sql_statement = re.sub(
                            r"ADD\s+COLUMN\s+IF\s+NOT\s+EXISTS",
                            "ADD COLUMN",
                            sql_statement,
                            flags=re.IGNORECASE,
                        )

                    try:
                        connection.execute(text(sql_statement))
                    except OperationalError as exc:
                        message = str(exc).lower()
                        if (
                            dialect_name == "sqlite"
                            and "idx_poems_editorial_status" in sql_statement
                            and "no such column: editorial_status" in message
                        ):
                            connection.execute(
                                text("ALTER TABLE poems ADD COLUMN editorial_status TEXT NOT NULL DEFAULT 'pending'")
                            )
                            connection.execute(text(sql_statement))
                            continue
                        if "duplicate column name" in message or "already exists" in message:
                            continue
                        raise
