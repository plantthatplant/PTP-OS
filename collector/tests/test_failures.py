"""Failure & resilience tests — the Collector must fail safe.

Covers specs/gaia-collector.md §5: source failure leaves the previous latest.json untouched
(exit 3); an invalid snapshot is quarantined, never published (exit 2); a good run publishes
(exit 0) and archives the previous snapshot; sources raise SourceError cleanly.
"""
import contextlib
import io
import json
import os
import shutil
import tempfile
import unittest
from types import SimpleNamespace
from unittest import mock

from collector import _paths, collect
from collector.sources import make_source, FixtureSource, DropFolderSource, SourceError


class Sources(unittest.TestCase):
    def test_fixture_missing_file_raises(self):
        with self.assertRaises(SourceError):
            FixtureSource(path="does-not-exist.json").fetch()

    def test_fixture_bad_json_raises(self):
        d = tempfile.mkdtemp()
        try:
            bad = os.path.join(d, "x.json")
            with open(bad, "w", encoding="utf-8") as f:
                f.write("{not json")
            with self.assertRaises(SourceError):
                FixtureSource(path=bad).fetch()
        finally:
            shutil.rmtree(d, ignore_errors=True)

    def test_drop_folder_needs_path(self):
        with self.assertRaises(SourceError):
            DropFolderSource(path=None)

    def test_drop_folder_missing_dir_raises(self):
        with self.assertRaises(SourceError):
            DropFolderSource(path=r"C:\does\not\exist").fetch()

    def test_drop_folder_empty_dir_raises(self):
        d = tempfile.mkdtemp()
        try:
            with self.assertRaises(SourceError):
                DropFolderSource(path=d).fetch()
        finally:
            shutil.rmtree(d, ignore_errors=True)

    def test_drop_folder_picks_newest(self):
        d = tempfile.mkdtemp()
        try:
            old = os.path.join(d, "old.json")
            new = os.path.join(d, "new.json")
            with open(old, "w", encoding="utf-8") as f:
                json.dump({"tag": "old"}, f)
            with open(new, "w", encoding="utf-8") as f:
                json.dump({"tag": "new"}, f)
            # Make 'new' clearly newer regardless of write speed.
            os.utime(old, (1, 1))
            raw = DropFolderSource(path=d).fetch()
            self.assertEqual(raw["tag"], "new")
            self.assertEqual(raw["_source_file"], "new.json")
        finally:
            shutil.rmtree(d, ignore_errors=True)

    def test_make_source_selects_type(self):
        self.assertIsInstance(make_source("fixture"), FixtureSource)
        self.assertIsInstance(make_source("drop-folder", path="x"), DropFolderSource)


class CollectIntegration(unittest.TestCase):
    """Run the orchestrator with all outputs redirected to a temp dir."""

    def setUp(self):
        # Keep test output clean — the orchestrator prints a human summary.
        self._stdout = contextlib.redirect_stdout(io.StringIO())
        self._stdout.__enter__()
        self.tmp = tempfile.mkdtemp()
        self._orig = {k: getattr(_paths, k) for k in
                      ("DATA_DIR", "INBOX_DIR", "LATEST", "HISTORY_DIR", "QUARANTINE_DIR", "LOGS_DIR")}
        _paths.DATA_DIR = os.path.join(self.tmp, "data")
        _paths.INBOX_DIR = os.path.join(_paths.DATA_DIR, "inbox")
        _paths.LATEST = os.path.join(_paths.INBOX_DIR, "latest.json")
        _paths.HISTORY_DIR = os.path.join(_paths.INBOX_DIR, "history")
        _paths.QUARANTINE_DIR = os.path.join(_paths.INBOX_DIR, "quarantine")
        _paths.LOGS_DIR = os.path.join(_paths.DATA_DIR, "logs")

    def tearDown(self):
        for k, v in self._orig.items():
            setattr(_paths, k, v)
        shutil.rmtree(self.tmp, ignore_errors=True)
        self._stdout.__exit__(None, None, None)

    def test_good_run_publishes(self):
        code = collect.run(source_name="fixture")
        self.assertEqual(code, 0)
        self.assertTrue(os.path.exists(_paths.LATEST))
        with open(_paths.LATEST, encoding="utf-8") as f:
            snap = json.load(f)
        self.assertEqual(snap["greenhouse_id"], "gh-kalaberga")
        self.assertTrue(snap["observations"])

    def test_second_run_archives_previous(self):
        collect.run(source_name="fixture")
        collect.run(source_name="fixture")
        archived = os.listdir(_paths.HISTORY_DIR)
        self.assertEqual(len(archived), 1)

    def test_source_failure_leaves_latest_untouched(self):
        # Seed a known-good latest.json, then fail the source.
        os.makedirs(_paths.INBOX_DIR, exist_ok=True)
        sentinel = {"greenhouse_id": "previous-good"}
        with open(_paths.LATEST, "w", encoding="utf-8") as f:
            json.dump(sentinel, f)
        code = collect.run(source_name="drop-folder", path=r"C:\does\not\exist")
        self.assertEqual(code, 3)
        with open(_paths.LATEST, encoding="utf-8") as f:
            self.assertEqual(json.load(f), sentinel)  # untouched

    def test_invalid_snapshot_is_quarantined_not_published(self):
        os.makedirs(_paths.INBOX_DIR, exist_ok=True)
        sentinel = {"greenhouse_id": "previous-good"}
        with open(_paths.LATEST, "w", encoding="utf-8") as f:
            json.dump(sentinel, f)
        failing = SimpleNamespace(ok=False, errors=["forced failure"])
        with mock.patch.object(collect, "validate", return_value=failing):
            code = collect.run(source_name="fixture")
        self.assertEqual(code, 2)
        # latest.json untouched; a quarantine file was written instead.
        with open(_paths.LATEST, encoding="utf-8") as f:
            self.assertEqual(json.load(f), sentinel)
        self.assertTrue(os.listdir(_paths.QUARANTINE_DIR))


if __name__ == "__main__":
    unittest.main()
