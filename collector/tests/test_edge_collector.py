"""Edge Collector integration tests — the watcher must be safe, idempotent, and unkillable.

Covers Sprint-14 Phases 2/4/5/6/8: new-file detection, partial-write protection, content-hash
dedup, archive/quarantine, bounded retries, reboot/power-loss recovery, the never-overwrite-newer
guard, never publishing an invalid snapshot, Collector Health, and a raised Knowledge Gap on
failure. Output is redirected so the suite stays quiet.
"""
import json
import os
import shutil
import tempfile
import unittest
from unittest import mock

from collector import _paths
from collector.edge import gaps  # noqa: F401  (ensures package import path)
from collector.edge.config import EdgeConfig
from collector.edge.health import read_health
from collector.edge.watcher import Watcher


def _csv(ts, rows):
    """rows: list of (house, air_temp, rh, vent, out, alarm, alarmtext)."""
    out = ["timestamp;house;air_temp;rel_humidity;vent_position;outside_temp;alarm;alarm_text"]
    for r in rows:
        out.append(";".join(str(x) for x in (ts,) + r))
    return "\n".join(out) + "\n"

_THREE = [("1", "24,2", "92", "0", "11,0", "0", ""),
          ("2", "16,0", "66", "20", "11,0", "1", "Sensor fault"),
          ("3", "21,0", "64", "30", "11,0", "0", "")]


class EdgeHarness(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        # Redirect the collector's published outputs into the temp tree.
        self._orig = {k: getattr(_paths, k) for k in
                      ("DATA_DIR", "INBOX_DIR", "LATEST", "HISTORY_DIR", "QUARANTINE_DIR", "LOGS_DIR")}
        _paths.DATA_DIR = os.path.join(self.tmp, "data")
        _paths.INBOX_DIR = os.path.join(_paths.DATA_DIR, "inbox")
        _paths.LATEST = os.path.join(_paths.INBOX_DIR, "latest.json")
        _paths.HISTORY_DIR = os.path.join(_paths.INBOX_DIR, "history")
        _paths.QUARANTINE_DIR = os.path.join(_paths.INBOX_DIR, "quarantine")
        _paths.LOGS_DIR = os.path.join(_paths.DATA_DIR, "logs")
        os.makedirs(_paths.INBOX_DIR, exist_ok=True)
        os.makedirs(_paths.LOGS_DIR, exist_ok=True)
        self.imp = os.path.join(self.tmp, "drop")
        self.arch = os.path.join(self.tmp, "archive")
        self.faildir = os.path.join(self.tmp, "failed")

    def tearDown(self):
        for k, v in self._orig.items():
            setattr(_paths, k, v)
        shutil.rmtree(self.tmp, ignore_errors=True)

    def cfg(self, **over) -> EdgeConfig:
        base = dict(
            import_path=self.imp, archive_path=self.arch, failed_path=self.faildir,
            poll_interval_s=1, max_file_bytes=16 * 1024 * 1024,
            supported_formats=(".csv", ".tsv", ".xlsx", ".json"),
            checkpoint_path=os.path.join(self.tmp, "ckpt.json"),
            health_path=os.path.join(self.tmp, "health.json"),
            stability_seconds=0, max_retries=2, allow_older=False,
            freshness_sla_s=10 ** 9,        # huge: fixed-date fixtures are never "stale" by clock
            facility_path=os.path.join(_paths.REPO_ROOT, "collector", "facility.json"),
            default_tz="UTC", column_map=None,
        )
        base.update(over)
        return EdgeConfig(**base)

    def watcher(self, **over) -> Watcher:
        return Watcher(self.cfg(**over), event=lambda m: None)

    def drop(self, name, content, mtime=None):
        p = os.path.join(self.imp, name)
        os.makedirs(self.imp, exist_ok=True)
        with open(p, "w", encoding="utf-8", newline="") as f:
            f.write(content)
        if mtime is not None:
            os.utime(p, (mtime, mtime))
        return p

    def latest(self):
        with open(_paths.LATEST, encoding="utf-8") as f:
            return json.load(f)


class HappyPath(EdgeHarness):
    def test_imports_and_archives(self):
        w = self.watcher()
        self.drop("e1.csv", _csv("2026-06-29T05:48:00Z", _THREE))
        self.assertEqual(w.scan_once(), 1)
        snap = self.latest()
        self.assertEqual(snap["greenhouse_id"], "gh-kalaberga")
        self.assertTrue(any(o["kind"] == "air-temperature" for o in snap["observations"]))
        self.assertEqual(len(os.listdir(self.arch)), 1)      # processed file archived
        self.assertEqual(len(os.listdir(self.imp)), 0)       # import folder left clean

    def test_health_is_populated(self):
        w = self.watcher()
        self.drop("e1.csv", _csv("2026-06-29T05:48:00Z", _THREE))
        w.scan_once()
        h = read_health(w.cfg.health_path)
        self.assertEqual(h["status"], "ok")
        self.assertEqual(h["last_file_processed"], "e1.csv")
        self.assertIsNotNone(h["last_successful_import"])
        self.assertIsNotNone(h["last_import_duration_ms"])
        self.assertEqual(h["imports_total"], 1)
        self.assertEqual(h["failed_imports"], 0)
        self.assertIn("current_freshness_seconds", h)

    def test_stale_when_reading_older_than_sla(self):
        # A short freshness SLA + an old fixture reading → reported "stale" (not "ok").
        w = self.watcher(freshness_sla_s=1)
        self.drop("e1.csv", _csv("2026-06-29T05:48:00Z", _THREE))
        w.scan_once()
        self.assertEqual(read_health(w.cfg.health_path)["status"], "stale")


class Dedup(EdgeHarness):
    def test_identical_content_imported_once(self):
        w = self.watcher()
        content = _csv("2026-06-29T05:48:00Z", _THREE)
        self.drop("e1.csv", content)
        self.assertEqual(w.scan_once(), 1)
        # Same bytes dropped again under a different name → recognised as a duplicate.
        self.drop("e1-copy.csv", content)
        self.assertEqual(w.scan_once(), 0)
        h = read_health(w.cfg.health_path)
        self.assertEqual(h["skipped_duplicates"], 1)
        self.assertEqual(h["imports_total"], 1)

    def test_changed_content_same_name_reimports(self):
        w = self.watcher()
        self.drop("export.csv", _csv("2026-06-29T05:48:00Z", _THREE))
        w.scan_once()
        newer = _csv("2026-06-29T06:48:00Z",
                     [("1", "25,0", "90", "0", "11,0", "0", "")] + _THREE[1:])
        self.drop("export.csv", newer)            # same filename, new content
        self.assertEqual(w.scan_once(), 1)
        self.assertEqual(read_health(w.cfg.health_path)["imports_total"], 2)


class PartialWrites(EdgeHarness):
    def test_recent_file_not_imported_until_quiet(self):
        import time
        w = self.watcher(stability_seconds=3)
        self.drop("e1.csv", _csv("2026-06-29T05:48:00Z", _THREE), mtime=time.time())
        self.assertEqual(w.scan_once(), 0)            # still settling — looks like a partial write
        # Make it quiet (mtime well in the past) → now safe to import.
        os.utime(os.path.join(self.imp, "e1.csv"), (time.time() - 60, time.time() - 60))
        self.assertEqual(w.scan_once(), 1)

    def test_growing_file_resets_stability(self):
        import time
        w = self.watcher(stability_seconds=3)
        p = self.drop("e1.csv", _csv("2026-06-29T05:48:00Z", _THREE), mtime=time.time())
        w.scan_once()                                 # register
        with open(p, "a", encoding="utf-8") as f:     # still being written
            f.write("2026-06-29T05:48:00Z;9;20,0;50;0;11,0;0;\n")
        os.utime(p, (time.time(), time.time()))
        self.assertEqual(w.scan_once(), 0)            # changed → not stable → not imported
        self.assertEqual(len(os.listdir(self.imp)), 1)


class MultipleAndFreshness(EdgeHarness):
    def test_multiple_simultaneous_lands_on_newest(self):
        w = self.watcher()
        base = 1_700_000_000
        self.drop("a_05.csv", _csv("2026-06-29T05:00:00Z", _THREE), mtime=base + 1)
        self.drop("b_07.csv", _csv("2026-06-29T07:00:00Z",
                  [("1", "26,0", "88", "0", "11,0", "0", "")] + _THREE[1:]), mtime=base + 3)
        self.drop("c_06.csv", _csv("2026-06-29T06:00:00Z", _THREE), mtime=base + 2)
        published = w.scan_once()
        self.assertGreaterEqual(published, 1)
        # latest.json must hold the freshest reading (07:00), regardless of arrival order.
        self.assertEqual(max(o["captured_at"] for o in self.latest()["observations"]
                             if o.get("captured_at")), "2026-06-29T07:00:00+00:00")
        self.assertEqual(len(os.listdir(self.imp)), 0)

    def test_older_reading_does_not_overwrite_newer(self):
        w = self.watcher()
        self.drop("new.csv", _csv("2026-06-29T07:00:00Z", _THREE))
        w.scan_once()
        before = self.latest()
        self.drop("late_old.csv", _csv("2026-06-29T05:00:00Z", _THREE))
        w.scan_once()                                 # older reading arrives late
        self.assertEqual(self.latest(), before)        # newer reality preserved
        self.assertEqual(read_health(w.cfg.health_path)["stale_skipped"], 1)
        self.assertEqual(len(os.listdir(self.arch)), 2)  # both files filed away, none lost


class Failures(EdgeHarness):
    def test_corrupt_file_quarantined_and_gap_raised(self):
        # Seed a known-good snapshot first; a corrupt import must not disturb it.
        w = self.watcher()
        self.drop("good.csv", _csv("2026-06-29T05:48:00Z", _THREE))
        w.scan_once()
        good = self.latest()
        self.drop("broken.csv", "this is not a real export at all\n")
        self.assertEqual(w.scan_once(), 0)
        self.assertEqual(self.latest(), good)          # latest.json untouched
        self.assertEqual(len(os.listdir(self.faildir)), 1)  # moved to FAILED
        h = read_health(w.cfg.health_path)
        self.assertEqual(h["failed_imports"], 1)
        self.assertEqual(h["status"], "degraded")
        gaps_log = os.path.join(_paths.LOGS_DIR, "knowledge-gaps.jsonl")
        self.assertTrue(os.path.exists(gaps_log))
        with open(gaps_log, encoding="utf-8") as f:
            self.assertIn("knowledge-gap", f.read())

    def test_oversized_file_rejected(self):
        w = self.watcher(max_file_bytes=50)
        self.drop("big.csv", _csv("2026-06-29T05:48:00Z", _THREE))  # > 50 bytes
        self.assertEqual(w.scan_once(), 0)
        self.assertEqual(len(os.listdir(self.faildir)), 1)
        self.assertFalse(os.path.exists(_paths.LATEST))

    def test_invalid_snapshot_never_published(self):
        w = self.watcher()
        self.drop("seed.csv", _csv("2026-06-29T05:48:00Z", _THREE))
        w.scan_once()
        good = self.latest()
        from collector.edge import pipeline
        failing = mock.Mock(ok=False, errors=["forced invalid"],
                            coverage={"coverage_pct": 0}, reality_confidence={})
        self.drop("next.csv", _csv("2026-06-29T06:48:00Z", _THREE))
        with mock.patch.object(pipeline, "validate", return_value=failing):
            self.assertEqual(w.scan_once(), 0)
        self.assertEqual(self.latest(), good)          # unchanged — invalid never published
        self.assertEqual(len(os.listdir(self.faildir)), 1)

    def test_transient_failure_retries_then_fails(self):
        w = self.watcher(max_retries=1)
        self.drop("flaky.csv", _csv("2026-06-29T05:48:00Z", _THREE))
        from collector.edge import watcher as wmod
        with mock.patch.object(wmod, "parse_export", side_effect=OSError("disk hiccup")):
            self.assertEqual(w.scan_once(), 0)         # attempt 1 → retry, file stays
            self.assertEqual(len(os.listdir(self.imp)), 1)
            self.assertEqual(w.scan_once(), 0)         # attempt 2 → retries exhausted → FAILED
        self.assertEqual(len(os.listdir(self.faildir)), 1)
        self.assertEqual(len(os.listdir(self.imp)), 0)

    def test_one_bad_file_does_not_stop_the_good_one(self):
        w = self.watcher()
        self.drop("broken.csv", "garbage\n", mtime=1_700_000_000)
        self.drop("good.csv", _csv("2026-06-29T05:48:00Z", _THREE), mtime=1_700_000_500)
        published = w.scan_once()
        self.assertEqual(published, 1)                 # good one still published
        self.assertTrue(os.path.exists(_paths.LATEST))
        self.assertEqual(len(os.listdir(self.faildir)), 1)


class RebootRecovery(EdgeHarness):
    def test_checkpoint_survives_restart_no_double_import(self):
        content = _csv("2026-06-29T05:48:00Z", _THREE)
        w1 = self.watcher()
        self.drop("e1.csv", content)
        self.assertEqual(w1.scan_once(), 1)
        # Simulate a restart: a brand-new watcher with the SAME checkpoint/health files.
        w2 = self.watcher()
        self.assertEqual(read_health(w2.cfg.health_path)["imports_total"], 1)  # counters resumed
        self.drop("e1-again.csv", content)             # same content reappears post-reboot
        self.assertEqual(w2.scan_once(), 0)            # recognised as already imported
        self.assertEqual(read_health(w2.cfg.health_path)["skipped_duplicates"], 1)

    def test_leftover_processed_file_is_reconciled_not_republished(self):
        # Simulate a crash AFTER checkpointing but BEFORE the archive move: the file is still in
        # the import folder, but its hash is already known. It must be filed away, not re-imported.
        content = _csv("2026-06-29T05:48:00Z", _THREE)
        w = self.watcher()
        self.drop("e1.csv", content)
        w.scan_once()
        published_snapshot = self.latest()
        # Put an identical file back into import as if the move never happened.
        self.drop("e1.csv", content)
        with mock.patch.object(Watcher, "_process_file", wraps=w._process_file):
            result = w.scan_once()
        self.assertEqual(result, 0)
        self.assertEqual(self.latest(), published_snapshot)
        self.assertEqual(len(os.listdir(self.imp)), 0)  # reconciled out of the import folder


if __name__ == "__main__":
    unittest.main()
