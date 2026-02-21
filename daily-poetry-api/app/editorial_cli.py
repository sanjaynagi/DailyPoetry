"""Interactive editorial moderation CLI for poem approval workflow."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from typing import Literal

from sqlalchemy import Select, func, or_, select, update
from sqlalchemy.orm import Session

from app.database import SessionLocal, engine
from app.migrate import run_sql_migrations
from app.models import Author, Poem

EditorialStatus = Literal["pending", "approved", "rejected"]
VALID_STATUSES: tuple[EditorialStatus, ...] = ("pending", "approved", "rejected")


@dataclass
class PoemRow:
    poem_id: str
    title: str
    author_name: str
    editorial_status: str
    linecount: int


def _base_select(status: str = "all", search: str | None = None) -> Select[tuple[Poem, Author]]:
    stmt: Select[tuple[Poem, Author]] = select(Poem, Author).join(Author, Author.id == Poem.author_id)
    if status != "all":
        stmt = stmt.where(Poem.editorial_status == status)

    if search:
        pattern = f"%{search.lower()}%"
        stmt = stmt.where(or_(func.lower(Poem.title).like(pattern), func.lower(Author.name).like(pattern)))
    return stmt


def list_poems(
    db: Session,
    *,
    status: str = "pending",
    search: str | None = None,
    limit: int = 20,
    offset: int = 0,
) -> tuple[list[PoemRow], int]:
    stmt = _base_select(status=status, search=search)
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = db.execute(count_stmt).scalar_one()

    rows = (
        db.execute(stmt.order_by(Author.name.asc(), Poem.title.asc()).limit(limit).offset(offset)).all()
        if total
        else []
    )
    poems = [
        PoemRow(
            poem_id=poem.id,
            title=poem.title,
            author_name=author.name,
            editorial_status=poem.editorial_status,
            linecount=poem.linecount,
        )
        for poem, author in rows
    ]
    return poems, total


def fetch_random_poem(db: Session, *, status: str = "pending", search: str | None = None) -> PoemRow | None:
    stmt = _base_select(status=status, search=search).order_by(func.random()).limit(1)
    row = db.execute(stmt).one_or_none()
    if row is None:
        return None
    poem, author = row
    return PoemRow(
        poem_id=poem.id,
        title=poem.title,
        author_name=author.name,
        editorial_status=poem.editorial_status,
        linecount=poem.linecount,
    )


def set_editorial_status(db: Session, poem_id: str, status: EditorialStatus) -> bool:
    poem = db.execute(select(Poem).where(Poem.id == poem_id)).scalar_one_or_none()
    if poem is None:
        return False
    poem.editorial_status = status
    db.commit()
    return True


def auto_reject_long_poems(db: Session, *, max_lines: int = 50, status: str = "pending") -> int:
    stmt = update(Poem).where(Poem.linecount > max_lines)
    if status != "all":
        stmt = stmt.where(Poem.editorial_status == status)

    result = db.execute(stmt.values(editorial_status="rejected"))
    db.commit()
    return int(result.rowcount or 0)


def fetch_poem_text(db: Session, poem_id: str) -> tuple[str, str, str] | None:
    row = db.execute(select(Poem, Author).join(Author, Author.id == Poem.author_id).where(Poem.id == poem_id)).one_or_none()
    if row is None:
        return None
    poem, author = row
    return poem.title, author.name, poem.text


def print_rows(rows: list[PoemRow], *, offset: int, total: int, page_size: int) -> None:
    if not rows:
        print("No poems found for current filter.")
        return

    start = offset + 1
    end = min(offset + len(rows), total)
    print(f"Showing {start}-{end} of {total} poems")
    print("-" * 88)
    for i, row in enumerate(rows, start=1):
        print(f"{i:>2}. [{row.editorial_status:<8}] {row.title} — {row.author_name} ({row.linecount} lines)")
        print(f"    id: {row.poem_id}")
    print("-" * 88)
    if total > page_size:
        print("Commands: n(next), p(prev), a <n|id>, r <n|id>, v <n|id>, s <status|all>, f <text>, c, q")
    else:
        print("Commands: a <n|id>, r <n|id>, v <n|id>, s <status|all>, f <text>, c, q")


def run_interactive(db: Session, *, status: str = "pending") -> None:
    current_status = status
    while True:
        poem = fetch_random_poem(db, status=current_status)
        if poem is None:
            print(f"No poems available for status={current_status}.")
            print("Tip: use `python -m app.editorial_cli list --status all --limit 10` to inspect current state.")
            break

        poem_data = fetch_poem_text(db, poem.poem_id)
        if poem_data is None:
            continue

        title, author, text = poem_data
        print()
        print(f"[{poem.editorial_status}] {title} — {author} ({poem.linecount} lines)")
        print(f"id: {poem.poem_id}")
        print("-" * 88)
        print(text)
        print("-" * 88)
        raw = input("Approve [a], Reject [r], Skip [s], Quit [q]: ").strip().lower()

        if raw in {"q", "quit", "exit"}:
            print("Exiting editorial moderation.")
            break
        if raw in {"a", "approve"}:
            set_editorial_status(db, poem.poem_id, "approved")
            print(f"Approved: {poem.poem_id}")
            continue
        if raw in {"r", "reject"}:
            set_editorial_status(db, poem.poem_id, "rejected")
            print(f"Rejected: {poem.poem_id}")
            continue
        if raw in {"s", "skip", ""}:
            print("Skipped.")
            continue

        print("Unknown input. Use a/r/s/q.")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Editorial moderation CLI for daily-poetry")
    subparsers = parser.add_subparsers(dest="command", required=True)

    list_parser = subparsers.add_parser("list", help="List poems by editorial status")
    list_parser.add_argument("--status", choices=[*VALID_STATUSES, "all"], default="pending")
    list_parser.add_argument("--search", type=str, default=None)
    list_parser.add_argument("--limit", type=int, default=30)
    list_parser.add_argument("--offset", type=int, default=0)

    approve_parser = subparsers.add_parser("approve", help="Approve a poem")
    approve_parser.add_argument("--poem-id", required=True)

    reject_parser = subparsers.add_parser("reject", help="Reject a poem")
    reject_parser.add_argument("--poem-id", required=True)

    stats_parser = subparsers.add_parser("stats", help="Show counts by editorial status")
    stats_parser.add_argument("--search", type=str, default=None)

    auto_reject_parser = subparsers.add_parser(
        "auto-reject-long",
        help="Reject poems with linecount greater than threshold",
    )
    auto_reject_parser.add_argument("--max-lines", type=int, default=50)
    auto_reject_parser.add_argument("--status", choices=[*VALID_STATUSES, "all"], default="pending")

    interactive_parser = subparsers.add_parser("interactive", help="Launch interactive moderation UI")
    interactive_parser.add_argument("--status", choices=VALID_STATUSES, default="pending")

    return parser


def main() -> None:
    run_sql_migrations(engine)
    args = build_parser().parse_args()

    with SessionLocal() as db:
        if args.command == "list":
            rows, total = list_poems(
                db,
                status=args.status,
                search=args.search,
                limit=max(1, args.limit),
                offset=max(0, args.offset),
            )
            print_rows(rows, offset=max(0, args.offset), total=total, page_size=max(1, args.limit))
            return

        if args.command == "approve":
            if set_editorial_status(db, args.poem_id, "approved"):
                print(f"Approved: {args.poem_id}")
                return
            raise SystemExit(f"Poem not found: {args.poem_id}")

        if args.command == "reject":
            if set_editorial_status(db, args.poem_id, "rejected"):
                print(f"Rejected: {args.poem_id}")
                return
            raise SystemExit(f"Poem not found: {args.poem_id}")

        if args.command == "stats":
            for status in VALID_STATUSES:
                rows, total = list_poems(db, status=status, search=args.search, limit=1, offset=0)
                _ = rows
                print(f"{status}: {total}")
            return

        if args.command == "auto-reject-long":
            max_lines = max(0, args.max_lines)
            updated = auto_reject_long_poems(db, max_lines=max_lines, status=args.status)
            print(f"Rejected {updated} poem(s) with linecount > {max_lines} (scope: {args.status})")
            return

        if args.command == "interactive":
            run_interactive(db, status=args.status)
            return

    raise SystemExit("Unknown command")


if __name__ == "__main__":
    main()
