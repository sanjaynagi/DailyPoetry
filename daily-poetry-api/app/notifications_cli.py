"""CLI for daily-poetry web push notifications."""

from __future__ import annotations

import argparse
from datetime import date

from app.config import get_vapid_private_key, get_vapid_public_key, get_vapid_subject
from app.database import SessionLocal, engine
from app.migrate import run_sql_migrations
from app.notifications import send_due_notifications


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Send daily-poetry web push notifications")
    parser.add_argument("--date", type=str, default=None, help="Target UTC date in YYYY-MM-DD (optional)")
    parser.add_argument("--dry-run", action="store_true", help="Compute recipients without sending notifications")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    vapid_public_key = get_vapid_public_key()
    vapid_private_key = get_vapid_private_key()
    vapid_subject = get_vapid_subject()

    if not vapid_public_key or not vapid_private_key:
        raise SystemExit("Missing VAPID keys: DAILY_POETRY_VAPID_PUBLIC_KEY and DAILY_POETRY_VAPID_PRIVATE_KEY")

    target_date = date.fromisoformat(args.date) if args.date else None

    run_sql_migrations(engine)
    with SessionLocal() as db:
        summary = send_due_notifications(
            db,
            vapid_public_key=vapid_public_key,
            vapid_private_key=vapid_private_key,
            vapid_subject=vapid_subject,
            today=target_date,
            dry_run=args.dry_run,
        )

    print(
        "notifications summary:",
        f"sent={summary.sent}",
        f"skipped={summary.skipped}",
        f"failed={summary.failed}",
        f"deactivated={summary.deactivated}",
    )


if __name__ == "__main__":
    main()
