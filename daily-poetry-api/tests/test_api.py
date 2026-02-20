from __future__ import annotations

import os
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4


def _configure_database_path() -> Path:
    db_path = Path(__file__).resolve().parent / "test_api.db"
    if db_path.exists():
        db_path.unlink()
    os.environ["DAILY_POETRY_DATABASE_URL"] = f"sqlite:///{db_path}"
    return db_path


def test_api_endpoints() -> None:
    db_path = _configure_database_path()

    from fastapi.testclient import TestClient

    from app.database import SessionLocal, engine
    from app.main import app
    from app.migrate import run_sql_migrations
    from app.models import Author, DailySelection, Poem

    run_sql_migrations(engine)

    today = datetime.now(timezone.utc).date()

    with SessionLocal() as session:
        author = Author(id=str(uuid4()), name="Percy Bysshe Shelley", bio_short="Romantic poet", image_url=None)
        poem = Poem(
            id=str(uuid4()),
            title="Ozymandias",
            text="I met a traveller from an antique land",
            linecount=1,
            author_id=author.id,
        )
        daily = DailySelection(date=today, poem_id=poem.id)
        session.add_all([author, poem, daily])
        session.commit()
        poem_id = poem.id

    with TestClient(app) as client:
        auth_response = client.post("/v1/auth/anonymous")
        assert auth_response.status_code == 200
        auth_payload = auth_response.json()
        assert "token" in auth_payload
        token_headers = {"Authorization": f"Bearer {auth_payload['token']}"}

        daily_response = client.get("/v1/daily")
        assert daily_response.status_code == 200
        daily_payload = daily_response.json()
        assert daily_payload["date"] == today.isoformat()
        assert daily_payload["poem"]["id"] == poem_id
        assert daily_payload["author"]["name"] == "Percy Bysshe Shelley"

        unauthorized = client.get("/v1/me/favourites")
        assert unauthorized.status_code == 401

        favourites_empty = client.get("/v1/me/favourites", headers=token_headers)
        assert favourites_empty.status_code == 200
        assert favourites_empty.json() == {"favourites": []}

        create_response = client.post("/v1/me/favourites", headers=token_headers, json={"poem_id": poem_id})
        assert create_response.status_code == 201

        favourites_after = client.get("/v1/me/favourites", headers=token_headers)
        assert favourites_after.status_code == 200
        payload = favourites_after.json()
        assert len(payload["favourites"]) == 1
        assert payload["favourites"][0]["poem_id"] == poem_id
        assert payload["favourites"][0]["poem_text"] == "I met a traveller from an antique land"

        delete_response = client.delete(f"/v1/me/favourites/{poem_id}", headers=token_headers)
        assert delete_response.status_code == 204

        favourites_after_delete = client.get("/v1/me/favourites", headers=token_headers)
        assert favourites_after_delete.status_code == 200
        assert favourites_after_delete.json() == {"favourites": []}

    if db_path.exists():
        db_path.unlink()
