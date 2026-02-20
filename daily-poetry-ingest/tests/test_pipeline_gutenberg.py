import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from daily_poetry_ingest.pipeline import run_gutenberg_ingestion


_POEM_TEXT = """*** START OF THE PROJECT GUTENBERG EBOOK 10 ***
A Song
by Sample Poet

I sing the dawn in amber fire,
I keep the dusk in quiet thread,
I lift the rain through cedar wire,
I name the stars above my head;

I leave a line for fields to keep,
I leave a line for seas to find,
I plant the hush where children sleep,
I set the day inside the mind.
*** END OF THE PROJECT GUTENBERG EBOOK 10 ***"""


class GutenbergPipelineTests(unittest.TestCase):
    @patch("daily_poetry_ingest.pipeline.enrich_authors")
    def test_run_gutenberg_ingestion_writes_standard_artifacts(self, mock_enrich_authors) -> None:
        mock_enrich_authors.return_value = (
            [{"name": "Sample Poet", "image_url": None, "image_source": None}],
            [],
        )

        with TemporaryDirectory() as tmp_dir:
            base = Path(tmp_dir)
            catalog = base / "catalog.csv"
            texts = base / "texts"
            output = base / "out"
            texts.mkdir(parents=True)

            catalog.write_text(
                "Text#,Type,Title,Language,Authors,Subjects,Bookshelves,LoCC\n"
                "10,Text,A Song,en,Sample Poet,Poetry,Poetry,PS\n",
                encoding="utf-8",
            )
            (texts / "10.txt").write_text(_POEM_TEXT, encoding="utf-8")

            report = run_gutenberg_ingestion(
                output_dir=output,
                catalog_csv=catalog,
                texts_dir=texts,
                language="en",
                rate_limit_rps=0,
            )

            poems_path = output / "poems.jsonl"
            authors_path = output / "authors.jsonl"
            duplicates_path = output / "duplicates.jsonl"
            report_path = output / "report.json"

            self.assertTrue(poems_path.exists())
            self.assertTrue(authors_path.exists())
            self.assertTrue(duplicates_path.exists())
            self.assertTrue(report_path.exists())

            poems_lines = poems_path.read_text(encoding="utf-8").strip().splitlines()
            self.assertEqual(len(poems_lines), 1)
            poem = json.loads(poems_lines[0])
            self.assertEqual(poem["title"], "A Song")
            self.assertEqual(poem["author"], "Sample Poet")
            self.assertEqual(poem["source"], "gutenberg:10")

            self.assertEqual(report["source"], "gutenberg")
            self.assertEqual(report["canonical_poems"], 1)
            self.assertEqual(report["normalized_poems"], 1)


if __name__ == "__main__":
    unittest.main()
