"""Tests for the .env loader — where secrets belong (a git-ignored file the launcher reads)."""
import os
import tempfile
import unittest

from api.config import Config, load_env_file


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

    def test_blank_value_does_not_claim_the_var(self):
        # The .env template ships `OPENAI_API_KEY=` blank; it must NOT set the var to "".
        fd, path = tempfile.mkstemp()
        os.close(fd)
        with open(path, "w", encoding="utf-8") as f:
            f.write("GAIA_TEST_C=\nGAIA_TEST_C=real\n")   # blank first, real second
        os.environ.pop("GAIA_TEST_C", None)
        try:
            load_env_file(path)
            self.assertEqual(os.environ["GAIA_TEST_C"], "real")   # blank skipped, real applied
        finally:
            os.environ.pop("GAIA_TEST_C", None)
            os.remove(path)

    def test_missing_file_is_silent(self):
        load_env_file("/nonexistent/path/.env")   # must not raise


class PortResolutionTest(unittest.TestCase):
    """GAIA_PORT wins; else a host-injected $PORT (Render/Railway); else 8000."""
    def setUp(self):
        self._saved = {k: os.environ.pop(k, None) for k in ("GAIA_PORT", "PORT")}

    def tearDown(self):
        for k, v in self._saved.items():
            os.environ.pop(k, None)
            if v is not None:
                os.environ[k] = v

    def test_default(self):
        self.assertEqual(Config.from_env().port, 8000)

    def test_host_injected_port(self):
        os.environ["PORT"] = "5055"
        self.assertEqual(Config.from_env().port, 5055)

    def test_gaia_port_wins(self):
        os.environ["PORT"] = "5055"
        os.environ["GAIA_PORT"] = "9090"
        self.assertEqual(Config.from_env().port, 9090)


if __name__ == "__main__":
    unittest.main()
