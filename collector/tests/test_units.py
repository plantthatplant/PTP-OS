"""Tests for the shared number/airflow primitives (greenhouse_brain.units).

These are the cleaning primitives the Collector and the Brain's providers now share, so they
are tested once, here.
"""
import unittest

from greenhouse_brain.units import to_number, airflow_from_vent


class ToNumber(unittest.TestCase):
    def test_plain_numbers(self):
        self.assertEqual(to_number(24.2), 24.2)
        self.assertEqual(to_number(92), 92.0)
        self.assertEqual(to_number(0), 0.0)

    def test_european_comma_and_unit_suffix(self):
        self.assertEqual(to_number("24,2 °C"), 24.2)
        self.assertEqual(to_number("11,0"), 11.0)

    def test_percent_string(self):
        self.assertEqual(to_number("20%"), 20.0)
        self.assertEqual(to_number("92%"), 92.0)

    def test_negative(self):
        self.assertEqual(to_number("-3.5"), -3.5)

    def test_non_numbers_become_none_never_zero(self):
        # The core honesty rule: no value is not 0.
        for v in (None, "", "closed", "open", "n/a", True, False, "abc"):
            self.assertIsNone(to_number(v), f"{v!r} should be None, not a fabricated number")


class AirflowFromVent(unittest.TestCase):
    def test_words(self):
        self.assertEqual(airflow_from_vent("closed"), "low")
        self.assertEqual(airflow_from_vent("open"), "good")

    def test_numbers_and_percent(self):
        self.assertEqual(airflow_from_vent(0), "low")
        self.assertEqual(airflow_from_vent("0%"), "low")
        self.assertEqual(airflow_from_vent(20), "normal")
        self.assertEqual(airflow_from_vent("40%"), "normal")
        self.assertEqual(airflow_from_vent(60), "good")

    def test_unknown_is_neutral_not_invented(self):
        self.assertEqual(airflow_from_vent(None), "normal")
        self.assertEqual(airflow_from_vent("???"), "normal")


if __name__ == "__main__":
    unittest.main()
