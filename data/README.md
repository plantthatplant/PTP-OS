# data/

**Runtime output — generated, not source.** The Gaia Collector writes here; Gaia reads from
here. The contents are git-ignored (see [`.gitignore`](../.gitignore)); only this README is
tracked, so the directory's purpose is documented even when it is otherwise empty.

| Path | What it holds |
| --- | --- |
| `inbox/latest.json` | The current Canonical Greenhouse Snapshot Gaia consumes. |
| `inbox/history/` | Previous snapshots, archived on each publish (immutable records of a moment). |
| `inbox/quarantine/` | Snapshots that failed validation — written here, **never** published. |
| `logs/collector-YYYYMMDD.jsonl` | One structured JSON line per collection run. |

Regenerate at any time with `python collector/collect.py`. Nothing here needs to be committed;
deleting it is safe and it will be recreated on the next run. See
[`docs/gaia-collector.md`](../docs/gaia-collector.md).
