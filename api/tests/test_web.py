"""Smoke test for the built-in Control Center page — guards the Sprint-14 fixes against
regression. (The interactive flow itself is verified in the browser; this asserts the rendered
HTML carries the fixed, no-silent-failure answer/note handlers.)"""
import unittest

from api.web import home_page


class ControlCenterTest(unittest.TestCase):
    def setUp(self):
        self.html = home_page("test-key")

    def test_key_is_injected(self):
        self.assertIn("test-key", self.html)
        self.assertNotIn("__KEY__", self.html)

    def test_answer_flow_has_persistent_feedback_and_guards(self):
        # the dedicated feedback element (so the question's auto-refresh can't wipe the confirmation)
        self.assertIn('id="qmsg"', self.html)
        self.assertIn("Answered ✓", self.html)
        # no silent failures: explicit feedback for no-question and empty-input
        self.assertIn("No question to answer", self.html)
        self.assertIn("Type your answer first", self.html)
        # the request path and error handling are present
        self.assertIn("/questions/", self.html)
        self.assertIn("Send failed", self.html)

    def test_note_flow_has_feedback_and_guard(self):
        self.assertIn("/voice-notes", self.html)
        self.assertIn("Noted ✓", self.html)
        self.assertIn("Type an observation first", self.html)


if __name__ == "__main__":
    unittest.main()
