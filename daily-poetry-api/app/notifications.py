"""Web push notification delivery helpers."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date, datetime, timezone
from zoneinfo import ZoneInfo

from sqlalchemy import and_, select
from sqlalchemy.orm import Session

from app import models

try:  # pragma: no cover - import presence varies in local environments
    from pywebpush import WebPushException, webpush
except Exception:  # pragma: no cover - handled in caller
    WebPushException = Exception  # type: ignore[assignment]
    webpush = None


@dataclass(frozen=True)
class SendSummary:
    sent: int
    skipped: int
    failed: int
    deactivated: int


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def _due_now(preference: models.NotificationPreference, now_utc: datetime) -> bool:
    local_now = now_utc.astimezone(ZoneInfo(preference.time_zone))
    return local_now.hour == preference.local_hour


def _payload(today: date) -> str:
    return json.dumps(
        {
            "title": "daily-poetry",
            "body": f"Your poem for {today.isoformat()} is ready.",
            "url": "/",
        }
    )


def send_due_notifications(
    db: Session,
    *,
    vapid_public_key: str,
    vapid_private_key: str,
    vapid_subject: str,
    today: date | None = None,
    dry_run: bool = False,
) -> SendSummary:
    if webpush is None:
        raise RuntimeError("pywebpush is not installed")

    target_date = today or _now_utc().date()
    now_utc = _now_utc()

    stmt = (
        select(models.PushSubscription, models.NotificationPreference)
        .join(
            models.NotificationPreference,
            models.NotificationPreference.user_id == models.PushSubscription.user_id,
        )
        .where(
            and_(
                models.PushSubscription.active.is_(True),
                models.NotificationPreference.enabled.is_(True),
            )
        )
    )

    rows = db.execute(stmt).all()

    sent = 0
    skipped = 0
    failed = 0
    deactivated = 0

    for subscription, preference in rows:
        if subscription.last_notified_date == target_date:
            skipped += 1
            continue
        if not _due_now(preference, now_utc):
            skipped += 1
            continue

        if dry_run:
            sent += 1
            continue

        try:
            webpush(
                subscription_info={
                    "endpoint": subscription.endpoint,
                    "keys": {"p256dh": subscription.p256dh, "auth": subscription.auth},
                },
                data=_payload(target_date),
                vapid_private_key=vapid_private_key,
                vapid_claims={"sub": vapid_subject},
                ttl=3600,
            )
            subscription.last_notified_date = target_date
            subscription.updated_at = now_utc.replace(tzinfo=None)
            sent += 1
        except WebPushException as exc:
            status_code = getattr(getattr(exc, "response", None), "status_code", None)
            if status_code in {404, 410}:
                subscription.active = False
                subscription.updated_at = now_utc.replace(tzinfo=None)
                deactivated += 1
            else:
                failed += 1

    if not dry_run:
        db.commit()

    return SendSummary(sent=sent, skipped=skipped, failed=failed, deactivated=deactivated)
