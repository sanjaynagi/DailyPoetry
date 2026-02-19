"""Core query logic for Daily Poetry API."""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from fastapi import HTTPException
from sqlalchemy import Select, String, cast, func, select
from sqlalchemy.orm import Session

from app import models


def utc_today_iso() -> str:
    return datetime.now(timezone.utc).date().isoformat()


def get_or_create_user_by_token(db: Session, token: str) -> models.User:
    user = db.execute(select(models.User).where(models.User.auth_token == token)).scalar_one_or_none()
    if user is not None:
        return user

    user = models.User(id=str(uuid4()), auth_token=token, created_at=datetime.now(timezone.utc).replace(tzinfo=None))
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def fetch_daily_payload(db: Session) -> dict:
    today = datetime.now(timezone.utc).date()

    stmt: Select[tuple[models.DailySelection, models.Poem, models.Author]] = (
        select(models.DailySelection, models.Poem, models.Author)
        .join(models.Poem, models.Poem.id == models.DailySelection.poem_id)
        .join(models.Author, models.Author.id == models.Poem.author_id)
        .where(cast(models.DailySelection.date, String) == today.isoformat())
    )

    row = db.execute(stmt).one_or_none()
    if row is None:
        raise HTTPException(status_code=404, detail=f"No daily selection configured for {today.isoformat()}")

    daily, poem, author = row
    return {
        "date": daily.date.isoformat() if hasattr(daily.date, "isoformat") else str(daily.date),
        "poem": {
            "id": poem.id,
            "title": poem.title,
            "text": poem.text,
            "linecount": poem.linecount,
        },
        "author": {
            "id": author.id,
            "name": author.name,
            "bio_short": author.bio_short or "",
            "image_url": author.image_url,
        },
    }


def fetch_user_favourites(db: Session, user: models.User) -> list[dict]:
    date_subquery = (
        select(models.DailySelection.poem_id, func.max(models.DailySelection.date).label("date_featured"))
        .group_by(models.DailySelection.poem_id)
        .subquery()
    )

    stmt = (
        select(models.Poem, models.Author, date_subquery.c.date_featured)
        .join(models.Favourite, models.Favourite.poem_id == models.Poem.id)
        .join(models.Author, models.Author.id == models.Poem.author_id)
        .join(date_subquery, date_subquery.c.poem_id == models.Poem.id, isouter=True)
        .where(models.Favourite.user_id == user.id)
        .order_by(models.Favourite.created_at.desc())
    )

    rows = db.execute(stmt).all()
    favourites: list[dict] = []
    for poem, author, date_featured in rows:
        favourites.append(
            {
                "poem_id": poem.id,
                "title": poem.title,
                "author": author.name,
                "date_featured": (
                    date_featured.isoformat()
                    if date_featured is not None and hasattr(date_featured, "isoformat")
                    else (str(date_featured) if date_featured is not None else None)
                ),
            }
        )
    return favourites


def create_favourite(db: Session, user: models.User, poem_id: str) -> None:
    poem = db.execute(select(models.Poem).where(models.Poem.id == poem_id)).scalar_one_or_none()
    if poem is None:
        raise HTTPException(status_code=404, detail="Poem not found")

    existing = db.execute(
        select(models.Favourite).where(models.Favourite.user_id == user.id, models.Favourite.poem_id == poem_id)
    ).scalar_one_or_none()
    if existing is not None:
        return

    favourite = models.Favourite(
        id=str(uuid4()),
        user_id=user.id,
        poem_id=poem_id,
        created_at=datetime.now(timezone.utc).replace(tzinfo=None),
    )
    db.add(favourite)
    db.commit()
