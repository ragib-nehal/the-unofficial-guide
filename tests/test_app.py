import importlib
import sys
import types
import unittest


class _FakeBlocks:
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def launch(self):
        return None


class _FakeButton:
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def click(self, *args, **kwargs):
        return None


class _FakeTextbox:
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def submit(self, *args, **kwargs):
        return None


class AppBehaviorTests(unittest.TestCase):
    def setUp(self):
        sys.modules.pop("app", None)
        sys.modules["gradio"] = types.SimpleNamespace(
            Blocks=_FakeBlocks,
            Markdown=lambda *args, **kwargs: None,
            Textbox=_FakeTextbox,
            Button=_FakeButton,
        )

    def tearDown(self):
        sys.modules.pop("app", None)
        sys.modules.pop("gradio", None)

    def test_handle_query_prompts_for_blank_input(self):
        app = importlib.import_module("app")

        self.assertEqual(
            app.handle_query("  "),
            ("Enter a question about Brooklyn College CS courses or professors.", "", ""),
        )

    def test_handle_query_returns_answer_and_sources(self):
        app = importlib.import_module("app")
        app.ask = lambda question: {
            "answer": "Grounded answer.",
            "sources": ["Source A", "Source B"],
            "chunks": "Retrieved chunk text",
        }

        self.assertEqual(
            app.handle_query("What do students say?"),
            ("Grounded answer.", "- Source A\n- Source B", "Retrieved chunk text"),
        )


if __name__ == "__main__":
    unittest.main()
