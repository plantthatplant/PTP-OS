# collector/tests/

The Collector's automated tests. Dependency-free — standard-library `unittest` only, in
keeping with the repo's "no install, no dependencies" ethos.

```
python -m unittest discover -s collector/tests          # from the repo root
```

| File | Covers |
| --- | --- |
| `test_units.py` | Shared number/airflow primitives (`greenhouse_brain.units`). |
| `test_translate.py` | Translation: number/unit cleaning, vent text, provenance-based confidence, honest absence, coverage gaps, time fields. |
| `test_validate.py` | Required fields, observation wellformedness, importer round-trip. |
| `test_changes.py` | First run, no-change, value/appeared/disappeared, alarm raised/cleared, coverage shifts. |
| `test_failures.py` | Source errors, source-failure safety, quarantine-not-publish, archiving. |
| `test_snapshot_compat.py` | The Collector's output runs through Gaia's **unchanged** pipeline. |

The integration tests redirect all output under a temporary directory, so they never touch the
real `data/` folder.
