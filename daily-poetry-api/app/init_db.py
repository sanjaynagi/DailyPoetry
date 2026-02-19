"""Utility to run schema migrations manually."""

from __future__ import annotations

from app.database import engine
from app.migrate import run_sql_migrations


def main() -> None:
    run_sql_migrations(engine)
    print("Migrations applied")


if __name__ == "__main__":
    main()
