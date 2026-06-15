import unittest


class _FakeCollection:
    def __init__(self):
        self.calls = []

    def get(self, **kwargs):
        self.calls.append(kwargs)
        where = kwargs.get("where")
        if where == {"professor_name": "Moshe Lach"}:
            return {
                "ids": ["01_rmp_moshe_lach_004"],
                "documents": ["PROFESSOR: Moshe Lach\nCOURSE: CISC3130 (Data Structures)\nREVIEW: Helpful."],
                "metadatas": [
                    {
                        "source_type": "rmp",
                        "source_file": "01_rmp_moshe_lach.txt",
                        "professor_name": "Moshe Lach",
                        "course_number": "CISC3130",
                    }
                ],
            }
        if where == {"course_number": "CISC3130"}:
            return {
                "ids": ["01_rmp_moshe_lach_005"],
                "documents": ["PROFESSOR: Moshe Lach\nCOURSE: CISC3130 (Data Structures)\nREVIEW: Study and you will do fine."],
                "metadatas": [
                    {
                        "source_type": "rmp",
                        "source_file": "01_rmp_moshe_lach.txt",
                        "professor_name": "Moshe Lach",
                        "course_number": "CISC3130",
                    }
                ],
            }
        return {"ids": [], "documents": [], "metadatas": []}


class RetrievalBehaviorTests(unittest.TestCase):
    def test_extract_keywords_prioritizes_professor_name_and_course_alias(self):
        from pipeline.retrieve import _extract_keywords

        keywords = _extract_keywords("What do students say about data structures with Moshe Lach?")

        self.assertEqual(keywords[:2], ["Moshe Lach", "CISC3130"])
        self.assertNotIn("data", keywords)
        self.assertNotIn("structures", keywords)

    def test_keyword_fetch_uses_professor_metadata_before_document_contains(self):
        from pipeline.retrieve import _keyword_fetch

        collection = _FakeCollection()

        chunks = _keyword_fetch(collection, ["Moshe Lach"], set(), limit=5)

        self.assertEqual(chunks[0]["chunk_id"], "01_rmp_moshe_lach_004")
        self.assertEqual(collection.calls[0]["where"], {"professor_name": "Moshe Lach"})

    def test_keyword_fetch_supports_course_alias_ids(self):
        from pipeline.retrieve import _keyword_fetch

        collection = _FakeCollection()

        chunks = _keyword_fetch(collection, ["CISC3130"], set(), limit=5)

        self.assertEqual(chunks[0]["chunk_id"], "01_rmp_moshe_lach_005")
        self.assertEqual(collection.calls[0]["where"], {"course_number": "CISC3130"})


if __name__ == "__main__":
    unittest.main()
