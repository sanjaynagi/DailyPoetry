import unittest

from daily_poetry_ingest.dedupe import dedupe_poems
from daily_poetry_ingest.normalize import NormalizedPoem


class DedupeTests(unittest.TestCase):
    def test_dedupe_selects_deterministic_winner(self) -> None:
        poem_a = NormalizedPoem(
            title="Z title",
            author="B Author",
            text="same text",
            linecount=1,
            content_hash="hash1",
        )
        poem_b = NormalizedPoem(
            title="A title",
            author="A Author",
            text="same text",
            linecount=1,
            content_hash="hash1",
        )

        canonical, duplicates = dedupe_poems([poem_a, poem_b])

        self.assertEqual(len(canonical), 1)
        self.assertEqual(canonical[0]["author"], "A Author")
        self.assertEqual(len(duplicates), 1)
        self.assertEqual(duplicates[0]["author"], "B Author")

    def test_dedupe_keeps_unique_hashes(self) -> None:
        poem_a = NormalizedPoem("T1", "A1", "text1", 1, "hash1")
        poem_b = NormalizedPoem("T2", "A2", "text2", 1, "hash2")

        canonical, duplicates = dedupe_poems([poem_a, poem_b])

        self.assertEqual(len(canonical), 2)
        self.assertEqual(len(duplicates), 0)


if __name__ == "__main__":
    unittest.main()
