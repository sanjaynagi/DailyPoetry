import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from daily_poetry_ingest.gutenberg import extract_strict_poem_lines, ingest_gutenberg_candidates, load_catalog_candidates


_VALID_POEM_TEXT = """*** START OF THE PROJECT GUTENBERG EBOOK 9999 ***
O Captain! My Captain!
by Walt Whitman

O Captain! my Captain! our fearful trip is done,
The ship has weather'd every rack, the prize we sought is won,
The port is near, the bells I hear, the people all exulting,
While follow eyes the steady keel, the vessel grim and daring;

But O heart! heart! heart!
O the bleeding drops of red,
Where on the deck my Captain lies,
Fallen cold and dead.
*** END OF THE PROJECT GUTENBERG EBOOK 9999 ***"""


class GutenbergTests(unittest.TestCase):
    def test_load_catalog_candidates_filters_strictly(self) -> None:
        with TemporaryDirectory() as tmp_dir:
            csv_path = Path(tmp_dir) / "pg_catalog.csv"
            csv_path.write_text(
                "Text#,Type,Title,Language,Authors,Subjects,Bookshelves,LoCC\n"
                "10,Text,O Captain! My Captain!,en,Walt Whitman,Poetry,Poetry,PS\n"
                "11,Text,Collected Poems,en,Walt Whitman,Poetry,Poetry,PS\n"
                "12,Text,Novel,en,Jane Doe,Fiction,Fiction,PR\n"
                "13,Text,No Author,en,,Poetry,Poetry,PS\n",
                encoding="utf-8",
            )

            candidates, errors = load_catalog_candidates(csv_path, language="en")

        self.assertEqual([candidate.ebook_id for candidate in candidates], [10])
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0]["kind"], "metadata_error")

    def test_extract_strict_poem_lines_rejects_prose(self) -> None:
        prose = """*** START OF THE PROJECT GUTENBERG EBOOK 1 ***
Chapter 1
This is a very long prose paragraph that keeps going on and on with sentence structure
that is not shaped like poetry and should therefore fail strict extraction checks.

Another very long paragraph continues the prose shape.
*** END OF THE PROJECT GUTENBERG EBOOK 1 ***"""
        self.assertIsNone(extract_strict_poem_lines(prose, "Chapter 1", "Prose Author"))

    def test_ingest_gutenberg_candidates_normalizes_strict_poems(self) -> None:
        with TemporaryDirectory() as tmp_dir:
            texts_dir = Path(tmp_dir) / "texts"
            texts_dir.mkdir(parents=True)
            (texts_dir / "10.txt").write_text(_VALID_POEM_TEXT, encoding="utf-8")

            candidates, _ = load_catalog_candidates(
                _write_catalog(
                    Path(tmp_dir) / "catalog.csv",
                    rows=[
                        "10,Text,O Captain! My Captain!,en,Walt Whitman,Poetry,Poetry,PS",
                    ],
                ),
                language="en",
            )
            poems, errors = ingest_gutenberg_candidates(candidates, texts_dir=texts_dir)

        self.assertEqual(errors, [])
        self.assertEqual(len(poems), 1)
        self.assertEqual(poems[0].title, "O Captain! My Captain!")
        self.assertEqual(poems[0].author, "Walt Whitman")
        self.assertTrue(poems[0].source.startswith("gutenberg:"))


def _write_catalog(path: Path, *, rows: list[str]) -> Path:
    path.write_text(
        "Text#,Type,Title,Language,Authors,Subjects,Bookshelves,LoCC\n" + "\n".join(rows) + "\n",
        encoding="utf-8",
    )
    return path


if __name__ == "__main__":
    unittest.main()
