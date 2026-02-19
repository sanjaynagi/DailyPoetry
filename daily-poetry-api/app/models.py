"""SQLAlchemy models for Daily Poetry backend MVP."""

from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Author(Base):
    __tablename__ = "authors"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    name: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    bio_short: Mapped[str | None] = mapped_column(Text, nullable=True)
    image_url: Mapped[str | None] = mapped_column(Text, nullable=True)


class Poem(Base):
    __tablename__ = "poems"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    linecount: Mapped[int] = mapped_column(Integer, nullable=False)
    author_id: Mapped[str] = mapped_column(String(36), ForeignKey("authors.id"), nullable=False)


class DailySelection(Base):
    __tablename__ = "daily_selection"

    date: Mapped[date] = mapped_column(Date, primary_key=True)
    poem_id: Mapped[str] = mapped_column(String(36), ForeignKey("poems.id"), nullable=False)


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    auth_token: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)


class Favourite(Base):
    __tablename__ = "favourites"
    __table_args__ = (UniqueConstraint("user_id", "poem_id", name="uq_favourites_user_poem"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
    poem_id: Mapped[str] = mapped_column(String(36), ForeignKey("poems.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
