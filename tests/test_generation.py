import unittest


class GenerationBehaviorTests(unittest.TestCase):
    def test_select_context_chunks_prioritizes_semantic_matches_and_caps_results(self):
        from pipeline.generate import select_context_chunks

        chunks = [
            {"chunk_id": "semantic-1", "match_type": "semantic"},
            {"chunk_id": "keyword-1", "match_type": "keyword"},
            {"chunk_id": "semantic-2", "match_type": "semantic"},
            {"chunk_id": "keyword-2", "match_type": "keyword"},
        ]

        selected = select_context_chunks(chunks, k=3)

        self.assertEqual([chunk["chunk_id"] for chunk in selected], ["semantic-1", "semantic-2", "keyword-1"])

    def test_build_sources_deduplicates_labels_in_retrieval_order(self):
        from pipeline.generate import build_sources

        chunks = [
            {
                "source_type": "rmp",
                "source_file": "01_rmp_moshe_lach.txt",
                "professor_name": "Moshe Lach",
            },
            {
                "source_type": "rmp",
                "source_file": "01_rmp_moshe_lach.txt",
                "professor_name": "Moshe Lach",
            },
            {
                "source_type": "coursicle",
                "source_file": "11_coursicle_cisc_3130.txt",
                "course_number": "CISC 3130",
            },
        ]

        sources = build_sources(chunks)

        self.assertEqual(
            sources,
            [
                "Moshe Lach reviews (01_rmp_moshe_lach.txt)",
                "CISC 3130 - Coursicle (11_coursicle_cisc_3130.txt)",
            ],
        )

    def test_format_context_includes_chunk_ids_types_and_text(self):
        from pipeline.generate import format_context

        context = format_context(
            [
                {
                    "chunk_id": "01_rmp_moshe_lach_004",
                    "source_type": "rmp",
                    "text": "REVIEW: Really good professor.",
                }
            ]
        )

        self.assertIn("[Document 1 | 01_rmp_moshe_lach_004 | rmp]", context)
        self.assertIn("REVIEW: Really good professor.", context)

    def test_select_context_chunks_prefers_requested_professor_and_course(self):
        from pipeline.generate import select_context_chunks

        chunks = [
            {
                "chunk_id": "moshe-3130",
                "match_type": "semantic",
                "professor_name": "Moshe Lach",
                "course_number": "CISC3130",
            },
            {
                "chunk_id": "mcneill-mentions-data-structures",
                "match_type": "semantic",
                "professor_name": "Matthew Mcneill",
                "course_number": "CISC3115",
            },
            {
                "chunk_id": "moshe-3115",
                "match_type": "semantic",
                "professor_name": "Moshe Lach",
                "course_number": "CISC3115",
            },
            {
                "chunk_id": "moshe-3130-keyword",
                "match_type": "keyword",
                "professor_name": "Moshe Lach",
                "course_number": "CISC3130",
            },
        ]

        selected = select_context_chunks(
            chunks,
            k=3,
            question="What do students say about data structures with Moshe Lach?",
        )

        self.assertEqual(
            [chunk["chunk_id"] for chunk in selected],
            ["moshe-3130", "moshe-3115", "moshe-3130-keyword"],
        )

    def test_format_retrieved_chunks_includes_source_match_type_and_text(self):
        from pipeline.generate import format_retrieved_chunks

        chunks = [
            {
                "source_type": "rmp",
                "source_file": "01_rmp_moshe_lach.txt",
                "professor_name": "Moshe Lach",
                "match_type": "semantic",
                "text": "REVIEW: Attend the lectures, study, and you will do fine.",
            }
        ]

        formatted = format_retrieved_chunks(chunks)

        self.assertIn("[1] Moshe Lach reviews (01_rmp_moshe_lach.txt) (semantic)", formatted)
        self.assertIn("REVIEW: Attend the lectures, study, and you will do fine.", formatted)


if __name__ == "__main__":
    unittest.main()
