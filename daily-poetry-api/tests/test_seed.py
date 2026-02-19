from __future__ import annotations

import json
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


def test_seed_from_artifacts_includes_author_image(tmp_path: Path) -> None:
    artifacts = tmp_path / "artifacts"
    artifacts.mkdir(parents=True)

    authors = [
        {
            "name": "Percy Bysshe Shelley",
            "image_url": "https://upload.wikimedia.org/example.jpg",
            "image_source": "wikipedia",
        }
    ]
    poems = [
        {
            "title": "Ozymandias",
            "author": "Percy Bysshe Shelley",
            "text": "I met a traveller from an antique land",
            "linecount": 1,
            "content_hash": "abc123",
        }
    ]

    (artifacts / "authors.jsonl").write_text("\n".join(json.dumps(row) for row in authors) + "\n", encoding="utf-8")
    (artifacts / "poems.jsonl").write_text("\n".join(json.dumps(row) for row in poems) + "\n", encoding="utf-8")

    from app.migrate import run_sql_migrations
    from app.models import Author, DailySelection, Favourite, Poem, User
    from app.seed_from_artifacts import seed_from_artifacts

    db_path = tmp_path / "seed.db"
    test_engine = create_engine(f"sqlite:///{db_path}", future=True, connect_args={"check_same_thread": False})
    TestSession = sessionmaker(autocommit=False, autoflush=False, bind=test_engine, future=True)
    run_sql_migrations(test_engine)

    with TestSession() as session:
        session.query(Favourite).delete()
        session.query(DailySelection).delete()
        session.query(Poem).delete()
        session.query(Author).delete()
        session.query(User).delete()
        session.commit()

    summary = seed_from_artifacts(artifacts, schedule_days=2, db_engine=test_engine, session_factory=TestSession)

    assert summary["authors"] >= 1
    assert summary["poems"] >= 1
    assert summary["scheduled_days"] == 2

    with TestSession() as session:
        author = session.query(Author).filter(Author.name == "Percy Bysshe Shelley").one()
        assert author.image_url == "https://upload.wikimedia.org/example.jpg"
