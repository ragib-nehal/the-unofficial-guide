import unittest


class EvalGenerationBehaviorTests(unittest.TestCase):
    def test_eval_queries_include_grounded_and_negative_cases(self):
        import eval_generation

        questions = [entry["question"] for entry in eval_generation.TEST_QUERIES]

        self.assertIn("What do students say about Moshe Lach for Data Structures?", questions)
        self.assertIn("What are the prerequisites for CISC 3130?", questions)
        self.assertIn("What is the recommended 4-year course schedule for a CS major?", questions)
        self.assertIn("What dining halls are best at Brooklyn College?", questions)


if __name__ == "__main__":
    unittest.main()
