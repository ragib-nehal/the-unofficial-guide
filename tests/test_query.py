import unittest


class QueryBehaviorTests(unittest.TestCase):
    def test_ask_returns_answer_and_programmatic_sources(self):
        import query

        retrieved_chunks = [
            {"chunk_id": "semantic-1", "match_type": "semantic", "source_file": "source_a.txt"},
            {"chunk_id": "keyword-1", "match_type": "keyword", "source_file": "source_b.txt"},
        ]
        selected_chunks = [retrieved_chunks[0]]
        calls = {}

        def fake_retrieve(question, k=5, hybrid=True):
            calls["retrieve"] = (question, k, hybrid)
            return retrieved_chunks

        def fake_select_context_chunks(chunks, k=5, question=""):
            calls["select"] = (chunks, k, question)
            return selected_chunks

        def fake_generate_answer(question, chunks):
            calls["generate"] = (question, chunks)
            return "Grounded answer."

        def fake_build_sources(chunks):
            calls["sources"] = chunks
            return ["Programmatic source"]

        def fake_format_retrieved_chunks(chunks):
            calls["chunks"] = chunks
            return "Retrieved chunk text"

        query.retrieve = fake_retrieve
        query.select_context_chunks = fake_select_context_chunks
        query.generate_answer = fake_generate_answer
        query.build_sources = fake_build_sources
        query.format_retrieved_chunks = fake_format_retrieved_chunks

        result = query.ask("What do students say?", k=3)

        self.assertEqual(
            result,
            {
                "answer": "Grounded answer.",
                "sources": ["Programmatic source"],
                "chunks": "Retrieved chunk text",
            },
        )
        self.assertEqual(calls["retrieve"], ("What do students say?", 3, True))
        self.assertEqual(calls["select"], (retrieved_chunks, 3, "What do students say?"))
        self.assertEqual(calls["generate"], ("What do students say?", retrieved_chunks))
        self.assertEqual(calls["sources"], selected_chunks)
        self.assertEqual(calls["chunks"], selected_chunks)


if __name__ == "__main__":
    unittest.main()
