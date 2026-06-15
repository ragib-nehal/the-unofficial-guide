import json
import tempfile
import unittest
from pathlib import Path


class PipelineBehaviorTests(unittest.TestCase):
    def test_load_documents_parses_text_sources_with_metadata(self):
        from pipeline.config import PipelinePaths
        from pipeline.load import load_documents

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            data_dir = root / "data"
            documents_dir = root / "documents"
            data_dir.mkdir()
            documents_dir.mkdir()
            (data_dir / "01_rmp_moshe_lach.txt").write_text(
                "https://www.ratemyprofessors.com/professor/2538695\n\n"
                "Moshe Lach\nComputer Science\nBrooklyn College\n",
                encoding="utf-8",
            )

            docs = load_documents(PipelinePaths(root=root, data_dir=data_dir, documents_dir=documents_dir))

        self.assertEqual(len(docs), 1)
        self.assertEqual(docs[0].url, "https://www.ratemyprofessors.com/professor/2538695")
        self.assertEqual(docs[0].source_id, 1)
        self.assertEqual(docs[0].source_type, "rmp")
        self.assertEqual(docs[0].metadata["professor_name"], "Moshe Lach")
        self.assertIn("Computer Science", docs[0].raw_text)

    def test_clean_rmp_keeps_review_context_and_removes_boilerplate(self):
        from pipeline.clean import clean_document
        from pipeline.load import Document

        raw = "\n".join(
            [
                "Logo",
                "Professors",
                "Help",
                "Moshe Lach",
                "Computer Science",
                "Brooklyn College",
                "53 Student Ratings",
                "All courses",
                "Quality",
                "5.0",
                "Difficulty",
                "2.0",
                "CISC3130",
                "Jan 26th, 2026",
                "For Credit: Yes",
                "Would Take Again: Yes",
                "Grade: A",
                "Textbook: N/A",
                "Really good professor. He bases his quizzes/test on the HW he assigns.",
                "Amazing lectures",
                "Lots of homework",
                "Thumbs up",
                "0",
                "Thumbs down",
                "0",
                "Load More Ratings",
                "Tech News & Deals from PCWorld & Macworld",
            ]
        )
        doc = Document(
            source_id=1,
            source_type="rmp",
            source_file="01_rmp_moshe_lach.txt",
            url="https://example.test",
            raw_text=raw,
            metadata={"professor_name": "Moshe Lach"},
        )

        cleaned = clean_document(doc)

        self.assertIn("PROFESSOR: Moshe Lach", cleaned.text)
        self.assertIn("COURSE: CISC3130 (Data Structures)", cleaned.text)
        self.assertIn("REVIEW: Really good professor", cleaned.text)
        self.assertIn("TAGS: Amazing lectures, Lots of homework", cleaned.text)
        self.assertNotIn("Logo", cleaned.text)
        self.assertNotIn("Thumbs up", cleaned.text)
        self.assertNotIn("PCWorld", cleaned.text)

    def test_clean_rmp_does_not_merge_reviewed_metadata_into_review(self):
        from pipeline.clean import clean_document
        from pipeline.load import Document

        raw = "\n".join(
            [
                "Moshe Lach",
                "53 Student Ratings",
                "All courses",
                "Quality",
                "5.0",
                "Difficulty",
                "5.0",
                "CISC3230",
                "May 24th, 2026",
                "For Credit: Yes",
                "Textbook: Yes",
                "First review body.",
                "Amazing lecturesCaring",
                "Thumbs up",
                "0",
                "Thumbs down",
                "0",
                "Reviewed: May 27th, 2026",
                "CISC1115",
                "Mar 26th, 2026",
                "Quality",
                "4.0",
                "Difficulty",
                "2.0",
                "CISC1115",
                "Mar 26th, 2026",
                "Second review body.",
                "Clear grading criteriaCaringRespected",
                "1",
                "0",
                "CISC3130",
                "Jan 27th, 2026",
                "Quality",
                "5.0",
                "Difficulty",
                "2.0",
                "CISC3130",
                "Jan 27th, 2026",
                "Third review body.",
            ]
        )
        doc = Document(
            source_id=1,
            source_type="rmp",
            source_file="01_rmp_moshe_lach.txt",
            url="https://example.test",
            raw_text=raw,
            metadata={"professor_name": "Moshe Lach"},
        )

        cleaned = clean_document(doc)

        self.assertIn("TAGS: Amazing lectures, Caring", cleaned.text)
        self.assertIn("TAGS: Clear grading criteria, Caring, Respected", cleaned.text)
        self.assertNotIn("Reviewed:", cleaned.text)
        self.assertNotIn("First review body. CISC1115", cleaned.text)
        self.assertNotIn("Second review body. CISC3130", cleaned.text)

    def test_chunk_rmp_uses_one_review_per_chunk_with_metadata(self):
        from pipeline.chunk import chunk_document
        from pipeline.clean import CleanedDocument

        cleaned = CleanedDocument(
            source_id=1,
            source_type="rmp",
            source_file="01_rmp_moshe_lach.txt",
            url="https://example.test",
            text=(
                "PROFESSOR: Moshe Lach | Computer Science | Brooklyn College\n"
                "---\n"
                "QUALITY: 5.0 | DIFFICULTY: 2.0 | COURSE: CISC3130 | DATE: Jan 26th, 2026\n"
                "REVIEW: Really good professor. He bases his quizzes/test on the HW he assigns.\n"
                "TAGS: Amazing lectures\n"
            ),
            metadata={"professor_name": "Moshe Lach"},
        )

        chunks = chunk_document(cleaned)

        self.assertEqual(len(chunks), 1)
        self.assertEqual(chunks[0].metadata["source_type"], "rmp")
        self.assertEqual(chunks[0].metadata["professor_name"], "Moshe Lach")
        self.assertEqual(chunks[0].metadata["course_number"], "CISC3130")
        self.assertIn("PROFESSOR: Moshe Lach", chunks[0].text)
        self.assertGreater(chunks[0].token_count, 10)

    def test_chunk_coursicle_does_not_emit_course_only_chunk(self):
        from pipeline.chunk import chunk_document
        from pipeline.clean import CleanedDocument

        cleaned = CleanedDocument(
            source_id=9,
            source_type="coursicle",
            source_file="09_coursicle_cisc_1115.txt",
            url="https://example.test",
            text=(
                "COURSE: CISC 1115\n\n"
                "TITLE: CISC 1115 - Introduction to Programming Using Java\n\n"
                "REVIEWS:\nStudents say this course requires practice.\n\n"
                "DESCRIPTION:\nAlgorithms, loops, methods, arrays, and Java programming."
            ),
            metadata={"course_number": "CISC 1115"},
        )

        chunks = chunk_document(cleaned)

        self.assertGreaterEqual(len(chunks), 1)
        self.assertNotEqual(chunks[0].text.strip(), "COURSE: CISC 1115")
        self.assertIn("TITLE: CISC 1115 - Introduction to Programming Using Java", chunks[0].text)
        self.assertIn("Students say this course requires practice.", chunks[0].text)

    def test_write_chunks_jsonl_serializes_expected_schema(self):
        from pipeline.chunk import Chunk, write_chunks_jsonl

        with tempfile.TemporaryDirectory() as tmp:
            output_path = Path(tmp) / "chunks.jsonl"
            write_chunks_jsonl(
                [
                    Chunk(
                        chunk_id="01_rmp_moshe_lach_001",
                        text="PROFESSOR: Moshe Lach\nREVIEW: Helpful.",
                        token_count=9,
                        metadata={"source_id": 1, "source_type": "rmp"},
                    )
                ],
                output_path,
            )
            rows = [json.loads(line) for line in output_path.read_text(encoding="utf-8").splitlines()]

        self.assertEqual(rows[0]["chunk_id"], "01_rmp_moshe_lach_001")
        self.assertEqual(rows[0]["metadata"]["source_type"], "rmp")
        self.assertEqual(rows[0]["token_count"], 9)


if __name__ == "__main__":
    unittest.main()
