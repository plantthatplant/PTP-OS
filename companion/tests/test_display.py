"""Display + independence tests — primitives are device-independent; the Brain knows no device."""
import os
import unittest

from companion import _paths  # noqa: F401
from companion.messages import CompanionMessage, Primitive, Urgency, HEADLINE_MAX
from companion.display import CompanionDisplay
from companion.devices.even_g2 import EvenG2Display


class _Capture(CompanionDisplay):
    name = "capture"
    def __init__(self):
        self.msgs = []
    def render(self, message):
        self.msgs.append(message)


class Primitives(unittest.TestCase):
    def test_all_eight_primitives_route_through_render(self):
        d = _Capture()
        d.show_message("m"); d.show_priority("p"); d.show_status("s"); d.show_navigation("n")
        d.show_confirmation("c"); d.show_warning("w"); d.show_summary("sm")
        d.show_question(CompanionMessage(Primitive.QUESTION, "q?", options=["yes", "no"]))
        kinds = {m.primitive for m in d.msgs}
        self.assertEqual(kinds, set(Primitive))   # every primitive exercised


class EvenG2(unittest.TestCase):
    def test_one_line_truncation(self):
        g2 = EvenG2Display(echo=False)
        long = "x" * 200
        g2.render(CompanionMessage(Primitive.MESSAGE, long))
        self.assertTrue(all(len(line) <= g2.LINE_WIDTH for line in g2.sent))

    def test_question_answer_via_injected_source(self):
        g2 = EvenG2Display(answer_source=lambda m: "no", echo=False)
        ans = g2.show_question(CompanionMessage(Primitive.QUESTION, "House 1: canopy wet?",
                                               options=["yes", "no", "not sure"], needs_response=True))
        self.assertEqual(ans, "no")

    def test_messages_fit_one_screen_after_format(self):
        g2 = EvenG2Display(echo=False)
        g2.render(CompanionMessage(Primitive.WARNING, "House 1: Rising disease risk (humid, wet canopy)"))
        self.assertTrue(all(len(line) <= g2.LINE_WIDTH for line in g2.sent))


class Independence(unittest.TestCase):
    def test_brain_does_not_import_the_companion(self):
        # The Brain must never depend on the Companion or any device.
        brain_dir = os.path.join(_paths.APP_DIR, "greenhouse_brain")
        offenders = []
        for root, _, files in os.walk(brain_dir):
            for fn in files:
                if fn.endswith(".py"):
                    src = open(os.path.join(root, fn), encoding="utf-8").read()
                    if "import companion" in src or "from companion" in src:
                        offenders.append(fn)
        self.assertEqual(offenders, [], f"Brain imports the Companion in: {offenders}")


if __name__ == "__main__":
    unittest.main()
