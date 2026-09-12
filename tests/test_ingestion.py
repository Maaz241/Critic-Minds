"""
test_ingestion.py
Unit tests for Critic Minds document ingestion and metadata extraction.
"""
import unittest
from app.ingestion.unified import extract_and_chunk, ExtractionError
from app.ingestion.txt import extract_txt


class TestIngestion(unittest.TestCase):

    def test_txt_ingestion(self):
        sample_txt = "Photosynthesis is the process by which green plants make food.\nIt requires light and CO2."
        doc = extract_and_chunk(sample_txt.encode("utf-8"), "biology_notes.txt")
        self.assertEqual(doc.file_type, "txt")
        self.assertEqual(doc.filename, "biology_notes.txt")
        self.assertGreater(len(doc.chunks), 0)
        chunk = doc.chunks[0]
        self.assertTrue("Photosynthesis" in chunk.text)
        self.assertEqual(chunk.section, "General")
        self.assertTrue("biology_notes.txt" in chunk.citation)

    def test_empty_file_error(self):
        with self.assertRaises(ExtractionError):
            extract_and_chunk(b"", "empty.txt")

    def test_unsupported_format_error(self):
        with self.assertRaises(ExtractionError):
            extract_and_chunk(b"fake data", "file.xyz")


if __name__ == "__main__":
    unittest.main()
