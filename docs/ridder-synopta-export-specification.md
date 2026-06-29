# Synopta Scheduled Export — Integration Request

**To:** Ridder Growing Solutions / Synopta support
**From:** Plant That Plant — Kålaberga (site GUID `A8301A54-DA1D-427E-895C-E25BD788F235`)
**Re:** Enabling a scheduled data export from Synopta for a read-only analytics integration
**Date:** 2026-06-29

---

## 1. Purpose

We are connecting our greenhouse advisory system ("Gaia") to Synopta at Kålaberga so it can
**read** current climate, ventilation and alarm data and help our head grower. The integration is
strictly **read-only and observational** — it does not send setpoints, does not control equipment,
and does not connect to the control bus or the controller.

We have already built and tested the receiving side: a small local "Edge Collector" that runs on
the Windows PC beside Synopta, watches a folder, and imports any export file Synopta writes there.
**The only thing we need from Ridder is a scheduled export into that folder.** This document
specifies exactly what we need so it can be configured in one session.

## 2. What we are asking for

Please configure Synopta to **automatically write a periodic export file** containing the latest
readings per house (compartment) to a local folder on the Synopta PC. A standard Synopta
history/periodic export is sufficient — we do not need any custom development.

> **One sentence:** a scheduled CSV (or Excel) of the current per-house values, written to a folder
> on this PC every few minutes.

## 3. Delivery method

- **Where:** write the file to a folder on the greenhouse PC, e.g. `D:\SynoptaExport\incoming\`.
  (Our collector watches this folder; the exact path is configurable on our side — tell us what is
  easiest for Synopta and we will point the watcher at it.)
- **How:** Synopta's built-in scheduled/periodic export is ideal. A network share or FTP drop into
  the same folder also works. **No database access, API credentials, OPC, or control-bus access is
  required or requested.**
- **File naming:** any consistent name is fine. Either a new timestamped file per export
  (e.g. `kalaberga_YYYYMMDD_HHMM.csv`) **or** a fixed name that is overwritten each cycle
  (e.g. `kalaberga_latest.csv`) — our collector handles both safely and never double-imports.
- **Atomicity:** if possible, write to a temporary name and rename into place when complete (e.g.
  `*.tmp` → `*.csv`). Our collector already guards against half-written files, but an atomic rename
  makes it instantaneous.

## 4. Preferred format

**First choice: CSV.** Excel (`.xlsx`), TSV, and JSON are also fully supported — whichever Synopta
produces most naturally. One row per house, a header row of column names.

- **Delimiter:** semicolon `;` preferred (so decimal commas are unambiguous); comma or tab are fine.
- **Decimal separator:** either `24.2` or `24,2` is accepted.
- **Character encoding:** **UTF-8** preferred. Windows-1252/Latin-1 is also handled. (We just need
  to know which, if it is not UTF-8.)
- **Header row:** required, with column names (any of the aliases in §6 are recognised).

## 5. Required update interval

- **Preferred: every 5 minutes.**
- **Acceptable range:** 1–15 minutes. (More frequent is welcome; our collector polls every 30 s by
  default and imports each new file immediately.)
- A consistent cadence matters more than a precise one — it lets us detect a stalled feed.

## 6. Required fields

Per house/compartment, each export should carry the following. **Column order does not matter** and
**extra columns are ignored** — we map by column name. Any of the listed header names are recognised
(English / Swedish / Dutch); if Synopta uses a different name, just tell us and we add it in one line.

| Meaning | Unit | Accepted header names (examples) | Required? |
| --- | --- | --- | --- |
| House / compartment id | — | `house`, `Hus`, `compartment`, `afdeling`, `zone` | **Yes** |
| Reading timestamp | ISO-8601 | `timestamp`, `Tidpunkt`, `tijd`, `datetime` | **Strongly preferred** |
| Air temperature | °C | `air_temp`, `Lufttemperatur`, `luchttemperatuur`, `temperature` | **Yes** |
| Relative humidity | %RH | `rel_humidity`, `Luftfuktighet`, `luchtvochtigheid`, `RH` | **Yes** |
| Ventilation / window position | % | `vent_position`, `Ventilation`, `raamstand`, `window` | Preferred |
| Outside temperature | °C | `outside_temp`, `Utetemperatur`, `buitentemperatuur` | Optional |
| Alarm active | 0/1 | `alarm`, `Larm`, `storing`, `fault` | Optional |
| Alarm text | text | `alarm_text`, `Larmtext`, `storingstekst` | Optional |

Other signals Synopta can include (CO₂, PAR/light, pipe/heating temperature, screen position, soil
moisture, EC/pH, etc.) are **welcome** — send what is available and we will map them. Anything not
sent is honestly recorded as "not observed"; we never guess a missing value.

Houses at Kålaberga are identified as **1, 2, 3** (House 1 propagation, House 2 growing-on, House 3
finishing). Please use those compartment numbers if possible.

## 7. Timestamps (important)

- Please include a **reading timestamp** column.
- **Strongly preferred:** ISO-8601 **with a UTC offset or `Z`**, e.g. `2026-06-29T05:48:00+02:00`
  or `2026-06-29T03:48:00Z`. An explicit offset removes all daylight-saving ambiguity.
- If only local wall-clock time is available (e.g. `2026-06-29 05:48:00`), that is acceptable — tell
  us the site timezone (Europe/Stockholm) and we interpret it, but an offset is safer across the
  March/October DST changes.
- If no timestamp can be included, we fall back to the export file's own write-time.

## 8. Units

Report in standard horticultural units: temperature in **°C**, humidity in **%RH**, positions in
**%**, CO₂ in **ppm**, light in **µmol·m⁻²·s⁻¹ (PAR)**. If a column is in different units, just note
it and we convert on our side. Please keep units consistent between exports.

## 9. A minimal example we can already import

`kalaberga_latest.csv` (UTF-8, `;`-delimited):

```
Tidpunkt;Hus;Lufttemperatur;Luftfuktighet;Ventilation;Utetemperatur;Larm;Larmtext
2026-06-29T05:48:00+02:00;1;24.2;92;0;11.0;0;
2026-06-29T05:48:00+02:00;2;16.0;66;20;11.0;1;Sensorfel: temperatur utanför intervall
2026-06-29T05:48:00+02:00;3;21.0;64;30;11.0;0;
```

This exact shape imports cleanly today. Anything close to it will too.

## 10. Success criteria

The integration is complete when **all** of the following hold:

1. Synopta writes an export file to the agreed folder on the agreed schedule (target: every 5 min).
2. Each export contains at least: house id, air temperature, relative humidity — with a timestamp.
3. The file is complete when our collector reads it (atomic rename, or simply finished writing).
4. The cadence is consistent, so a missing export is detectable.
5. No control-system, database, or API access is involved — file export only.

Once these hold, our side requires **no further development** — the collector imports automatically.

## 11. What we explicitly do NOT need

- ❌ No write access, setpoints, or control of any kind.
- ❌ No connection to the control bus (RabbitMQ/AMQP), the CX/process controller, or the GUI.
- ❌ No SynDesk protocol access, no OPC, no database credentials.
- ❌ No cloud API (unless Ridder would prefer that route — we can discuss, but the scheduled export
  is simplest and safest for everyone).

## 12. Contact

Plant That Plant — hello@plantthatplant.com. Please reply with: the export folder path you will use,
the format and encoding, the cadence, and the column names Synopta will emit, so we can confirm the
mapping before go-live.

Thank you — this single export is the last step before Gaia can quietly help at Kålaberga every
morning.
