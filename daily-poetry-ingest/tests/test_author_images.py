import unittest
from unittest.mock import patch

from daily_poetry_ingest.author_images import AuthorImageRecord, enrich_authors


class AuthorImageTests(unittest.TestCase):
    def test_enrich_authors_handles_missing_images_with_null(self) -> None:
        with patch(
            "daily_poetry_ingest.author_images.resolve_author_image",
            return_value=AuthorImageRecord(name="No Image", image_url=None, image_source=None),
        ):
            records, errors = enrich_authors(
                ["No Image"],
                timeout_seconds=1,
                retries=0,
                backoff_seconds=0,
                rate_limit_rps=0,
            )

        self.assertEqual(errors, [])
        self.assertEqual(records[0]["name"], "No Image")
        self.assertIsNone(records[0]["image_url"])

    def test_enrich_authors_sorts_and_keeps_source(self) -> None:
        mapping = {
            "B": AuthorImageRecord(name="B", image_url="https://img/b.jpg", image_source="wikipedia"),
            "A": AuthorImageRecord(name="A", image_url="https://img/a.jpg", image_source="wikipedia"),
        }

        def fake_resolver(author: str, *_args):
            return mapping[author]

        with patch("daily_poetry_ingest.author_images.resolve_author_image", side_effect=fake_resolver):
            records, errors = enrich_authors(
                ["B", "A"],
                timeout_seconds=1,
                retries=0,
                backoff_seconds=0,
                rate_limit_rps=0,
            )

        self.assertEqual(errors, [])
        self.assertEqual([record["name"] for record in records], ["A", "B"])
        self.assertEqual(records[0]["image_source"], "wikipedia")


if __name__ == "__main__":
    unittest.main()
