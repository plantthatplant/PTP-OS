"""Tests for the .env loader — where secrets belong (a git-ignored file the launcher reads)."""
import os
import tempfile
import unittest

from api.config import load_env_file


class LoadEnvFileTest(unittest.TestCase):
    def test_loads_values_without_overriding_real_env(self):
        fd, path = tempfile.mkstemp()
        os.close(fd)
        with open(path, "w", encoding="utf-8") as f:
            f.write("# a comment\n\nGAIA_TEST_A=fromfile\nGAIA_TEST_B = \"quoted value\"\nnot a kv line\n")
        os.environ["GAIA_TEST_A"] = "fromenv"      # already set → real env must win
        os.environ.pop("GAIA_TEST_B", None)
        try:
            load_env_file(path)
            self.assertEqual(os.environ["GAIA_TEST_A"], "fromenv")     # not overridden
            self.assertEqual(os.environ["GAIA_TEST_B"], "quoted value")  # loaded + de-quoted
        finally:
            for k in ("GAIA_TEST_A", "GAIA_TEST_B"):
                os.environ.pop(k, None)
            os.remove(path)

    def test_missing_file_is_silent(self):
        load_env_file("/nonexistent/path/.env")   # must not raise


if __name__ == "__main__":
    unittest.main()
