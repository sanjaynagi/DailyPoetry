import unittest

from daily_poetry_ingest.normalize import canonical_text, normalize_record


class NormalizeTests(unittest.TestCase):
    def test_canonical_text_preserves_stanza_breaks_and_trims_eof_blanks(self) -> None:
        lines = ["  first  ", "", "second", "", ""]
        self.assertEqual(canonical_text(lines), "  first\n\nsecond")

    def test_normalize_record_counts_lines_from_canonical_text(self) -> None:
        record = {"title": "T", "author": "A", "lines": ["l1", "", "l3", ""]}
        result = normalize_record(record)
        self.assertEqual(result.linecount, 3)
        self.assertEqual(result.text, "l1\n\nl3")

    def test_normalize_record_returns_error_for_missing_fields(self) -> None:
        result = normalize_record({"author": "A", "lines": ["x"]})
        self.assertEqual(result.reason, "missing_title")


if __name__ == "__main__":
    unittest.main()
