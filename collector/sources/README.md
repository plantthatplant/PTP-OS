# collector/sources/

The **only** place Synopta's vendor reality enters the Collector. Every source implements one
interface — `SynoptaSource.fetch() -> dict` — returning a raw, vendor-shaped reading (or
raising `SourceError`). Everything downstream (translate, validate, diff, write) is identical
no matter which source produced the data, so the live-source decision changes **one module**
and nothing above it.

This mirrors the Brain's own transport seam
([`app/greenhouse_brain/providers/transport.py`](../../app/greenhouse_brain/providers/transport.py)).

| File | Source | Status |
| --- | --- | --- |
| `base.py` | `SynoptaSource` interface + `SourceError` | — |
| `fixture_source.py` | `FixtureSource` — bundled captured reading (offline) | shipped |
| `drop_folder_source.py` | `DropFolderSource` — newest export file in a folder (read-only) | shipped |
| `sample_synopta_export.json` | A captured raw export (vendor-shaped, deliberately messy) | fixture |
| `__init__.py` | `make_source(name, path)` — composition-time selection | — |

To add the live source, see *"How to connect a new Synopta source"* in
[`docs/gaia-collector.md`](../../docs/gaia-collector.md#7-how-to-connect-a-new-synopta-source-the-single-module-path).
Contain all vendor specifics (endpoints, auth, formats) here; never leak them upward.
