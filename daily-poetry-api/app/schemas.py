"""Pydantic response schemas."""

from __future__ import annotations

from pydantic import BaseModel


class PoemPayload(BaseModel):
    id: str
    title: str
    text: str
    linecount: int


class AuthorPayload(BaseModel):
    id: str
    name: str
    bio_short: str
    image_url: str | None


class DailyResponse(BaseModel):
    date: str
    poem: PoemPayload
    author: AuthorPayload


class FavouriteItem(BaseModel):
    poem_id: str
    title: str
    author: str
    date_featured: str | None
    poem_text: str | None


class FavouritesResponse(BaseModel):
    favourites: list[FavouriteItem]


class CreateFavouriteRequest(BaseModel):
    poem_id: str


class AnonymousAuthResponse(BaseModel):
    user_id: str
    token: str
