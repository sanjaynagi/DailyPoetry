from __future__ import annotations

from datetime import date, datetime, timezone
from uuid import uuid4

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.migrate import run_sql_migrations
from app.models import NotificationPreference, PushSubscription, User
from app.notifications import send_due_notifications


def test_send_due_notifications_marks_sent(tmp_path, monkeypatch) -> None:
    db_path = tmp_path / "notifications.db"
    engine = create_engine(f"sqlite:///{db_path}")
    run_sql_migrations(engine)
    session_factory = sessionmaker(bind=engine)

    user_id = str(uuid4())
    now = datetime(2026, 2, 20, 9, 0, 0, tzinfo=timezone.utc)
    target_date = date(2026, 2, 20)

    with session_factory() as session:
        session.add(
            User(
                id=user_id,
                auth_token="token-1",
                created_at=now,
            )
        )
        session.add(
            NotificationPreference(
                user_id=user_id,
                enabled=True,
                time_zone="UTC",
                local_hour=9,
                updated_at=now,
            )
        )
        session.add(
            PushSubscription(
                id=str(uuid4()),
                user_id=user_id,
                endpoint="https://example.test/sub",
                p256dh="abc",
                auth="xyz",
                active=True,
                created_at=now,
                updated_at=now,
            )
        )
        session.commit()

        calls: list[dict] = []

        monkeypatch.setattr("app.notifications._now_utc", lambda: now)
        monkeypatch.setattr("app.notifications.webpush", lambda **kwargs: calls.append(kwargs))

        summary = send_due_notifications(
            session,
            vapid_public_key="public",
            vapid_private_key="private",
            vapid_subject="mailto:test@example.com",
            today=target_date,
            dry_run=False,
        )
        assert summary.sent == 1
        assert summary.failed == 0
        assert len(calls) == 1

        stored = session.query(PushSubscription).filter(PushSubscription.user_id == user_id).one()
        assert stored.last_notified_date == target_date
