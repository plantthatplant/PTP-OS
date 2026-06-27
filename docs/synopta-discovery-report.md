# Synopta Discovery Report — Sprint 3

**Date:** 2026-06-27 · **Method:** read-only investigation of this Windows machine
(`Syn5Server1`, user `Synopta`). **No writes, no commands, no controller probing, no GUI
automation.** **Outcome:** **no safe, supported, read-only live interface exists on this
machine** → per the sprint rules, **we stop before implementing a `LiveSynoptaProvider`** and
list the single remaining action needed. (See §7.)

Every finding below is tagged **[FACT]** (directly observed) or **[ASSUMPTION]** (inferred,
not verified from here), with a confidence level.

---

## 1. Architecture (as discovered)

```
   ┌────────────────────────────────────────────────────────────────────┐
   │  GREENHOUSE LAN  (172.27.0.0/24)                                     │
   │                                                                      │
   │   ┌───────────────────────────┐         ┌────────────────────────┐  │
   │   │  HortiMaX CX controller    │  proprietary   │  THIS PC          │  │
   │   │  (process computer)        │◀──────────────▶│  172.27.0.101      │  │
   │   │  172.27.0.250              │  TCP, dynamic   │                    │  │
   │   │  CP-MOD KD1825 I/O modules │  high ports     │  SynDesk.exe       │  │
   │   │  (AI16 analog / DO16 dig.) │  (cpprest)      │  (PID 17804)       │  │
   │   └───────────────────────────┘                 │  GUI client        │  │
   │            ▲                                     └────────────────────┘  │
   │            │ sensors / actuators                          │             │
   │       air temp, RH, CO₂, light, pipe temp,                │ (no local   │
   │       vents, screens, heating, irrigation, alarms         │  server/API)│
   └──────────────────────────────────────────────────────────┼─────────────┘
                                                               │
                          ┌────────────────────────────────────┘
                          │  office LAN / internet (192.168.1.0/24)
                          ▼
              Ridder cloud portal (HTTPS, via CX Assistant / PortalDLL)
              — used to download proprietary .site CONFIG files only
```

- **[FACT, high]** The greenhouse controller is a **HortiMaX CX** at `172.27.0.250`. This PC is
  `172.27.0.101` on the same LAN; it also has an office/internet NIC (`192.168.1.195`).
- **[FACT, high]** This PC runs **`SynDesk.exe`** (Ridder/Hortimax *Synopta Desktop* client),
  PID 17804, from `…\AppData\Roaming\hortimax\synopta\sdclients\Synopta\Bin\SynDesk\`, with
  **six live TCP connections to `172.27.0.250`** (server ports 64500–64515) — the live link.
- **[FACT, high]** It is a **thin client**: the Synopta *server* and historical database are
  **not on this machine** (drives D: and E: are empty; no server folders, services, or DB here).

---

## 2. Inventory of what is on this machine

### 2.1 Installations [FACT]
| What | Path | Role |
| --- | --- | --- |
| Synopta SynDesk client | `…\AppData\Roaming\hortimax\synopta\sdclients\Synopta\` | Live GUI client to the controller |
| HortiMaX CX Assistant | `C:\Program Files (x86)\HortiMaX CX Assistant\` (`CX500Config.exe`) | Commissioning/config tool; downloads `.site` config via Ridder portal |
| CX Assistant user data | `…\Documents\HortiMaX\HortiMaX CX Assistant\` | `.site` config downloads + `Sites\Kålaberga trädgård.site` |

### 2.2 Configuration files [FACT]
- `…\sdclients\Synopta\SynInfo.dat` — references server paths (`HDM_DATA`, `SYSTEM_DATA`,
  `Export`), `127.0.0.1`, an **AMQP string `admin:admin@localhost:5672`**, and `HortiMaX CX`.
  These describe the **server's** layout; they are not active on this client.
- `guiinfo.dat` (site GUID `A8301A54-…`, `172.27.0.250`), `LocalParams.dat`, registry
  `HKCU\Software\HortiMaX\Synopta\SynDesk\…` — **UI/workspace state only**, no climate data.
- `…\Documents\HortiMaX\…\Cache\44308\Definition\` — the controller program in **proprietary
  binary** (`SynDef.dat`, `CX.dat`, `XPIO.dat`, `hmx5.bin`, …). Defines points/units but is
  not a readable export.

### 2.3 Databases [FACT]
- `sqlite3.dll` ships with SynDesk, but **no SQLite/SQL database with climate data exists on
  this machine** — the only local stores are a UI icon/string cache and workspace settings.
- **No SQL Server / MySQL / Postgres** service, instance, or data file present.

### 2.4 Export folders [FACT]
- **None for climate data.** The only "exports" are proprietary `.site` **config** downloads
  (binary, ~63 KB, magic `64 00 00 00…`, manual) and an `IOExport.xsl` (transforms an I/O
  *configuration* list to XML — config, not measurements).

### 2.5 Scheduled tasks [FACT]
- **No Synopta/Hortimax/export/backup tasks.** Only stock Windows maintenance tasks exist.

### 2.6 Windows services [FACT]
- **No** Synopta, Hortimax, Ridder, RabbitMQ, Erlang, SQL, OPC, or Modbus service.

### 2.7 Network connections [FACT]
- Live: `172.27.0.101 → 172.27.0.250:6450x` ×6 (SynDesk ↔ controller, proprietary).
- Listening locally: only Windows RPC/SMB (`135/139/445`), `5040`, `5357`, **`5939` =
  TeamViewer**, `7680` (Delivery Optimization), dynamic RPC. **No application API listener.**

### 2.8 Local APIs / HTTP endpoints [FACT]
- **None hosted on this machine.** SynDesk is a *client*; it exposes no local server. Nothing
  serves climate data over HTTP/localhost.

### 2.9 OPC / Modbus [FACT / ASSUMPTION]
- **[FACT]** No OPC or Modbus client/server software, service, DLL, or listening port on this PC
  (no `502`, no OPC DA/UA runtime).
- **[ASSUMPTION, low]** The HortiMaX CX controller *might* expose Modbus/OPC on the LAN, but
  this is unverified and **out of bounds** — using it would mean touching the controller.

### 2.10 SQL databases [FACT]
- None present or reachable from this machine (see 2.3).

### 2.11 RabbitMQ usage [FACT]
- An AMQP URL (`admin:admin@localhost:5672`) is referenced in `SynInfo.dat`, but **nothing
  listens on 5672**, and **RabbitMQ/Erlang are not installed**. No usable broker here. (Using a
  production message bus with default `admin:admin` would also violate the safety rules.)

### 2.12 Log files [FACT]
- `…\sdclients\Synopta\Log\` holds the client's own diagnostic logs: `scom_*` (communication),
  `srta_*` (real-time analog), `srtd_*` (real-time digital), `sdef_*` (definitions), `shd_*`.
  These are **client logs**, not a climate data feed; recent ones (2026-06-26) confirm the
  client is actively talking to the controller.

---

## 3. Data flow — how climate values move

```
 sensor / actuator  ──▶  HortiMaX CX controller  ──▶  Synopta server + history DB  ──▶  SynDesk client (this PC)  ──▶  GUI
 (AI16 / DO16 I/O)       (172.27.0.250)               (off-machine)                     (proprietary cpprest link)      (screen)
```

The Brain would need to tap this **between the server and the client**, as a Canonical
Snapshot — but the only access on this PC is the proprietary client link and the on-screen GUI,
neither of which is a supported, safe, read-only data interface.

Per-measurement detail (origin is **[FACT]** from the CX I/O datasheets; storage/interval/
units/timestamp are **[ASSUMPTION]** because the exact values live in the proprietary protocol
and binary definitions, which the rules forbid decoding):

| Measurement | Origin | Storage | Update interval | Units | Timestamp source | Confidence to read here |
| --- | --- | --- | --- | --- | --- | --- |
| Air temperature | CX analog input (AI16) | controller + server history | ~controller scan (sec–min) | °C | controller clock | **None** (no safe local read) |
| Humidity | CX analog input | server history | ~scan | %RH | controller | None |
| CO₂ | CX analog input | server history | ~scan | ppm | controller | None |
| Light | CX analog input | server history | ~scan | W/m² or µmol·m⁻²·s⁻¹ | controller | None |
| Pipe temperature | CX analog input | server history | ~scan | °C | controller | None |
| Vent position | CX digital/analog output (DO16) | server history | on change / scan | % open | controller | None |
| Screen position | CX output | server history | on change / scan | % drawn | controller | None |
| Heating | CX output | server history | on change / scan | on/off or % | controller | None |
| Irrigation | CX output | server history | on event | on/off, events | controller | None |
| Alarms | CX logic | server | on event | category + text | controller | None |

"Confidence to read here = None" means: there is **no supported way to obtain this value on
this machine** without a forbidden technique. The values themselves are real and high-quality
at the controller; we simply have no sanctioned tap.

---

## 4. Existing export functionality (task 3)

| Capability | Present on this machine? | Notes |
| --- | --- | --- |
| CSV export | **No** [FACT] | No CSV produced anywhere; no recent `.csv` in the profile |
| JSON export | **No** [FACT] | — |
| XML export | **Config only** [FACT] | `IOExport.xsl` exports the I/O *configuration*, not live data |
| Scheduled exports | **No** [FACT] | No scheduled task does any export |
| Shared folders | **No** [FACT] | No export share configured/observed |
| REST API | **Proprietary, internal** [FACT/ASSUMPTION] | SynDesk uses `cpprest` to the controller; not a documented/public API |
| Database access | **No** [FACT] | No local DB; server DB not reachable from here |
| Ridder portal | **Config only** [FACT] | CX Assistant downloads `.site` config via HTTPS; not live climate |

**Official routes that *may* exist but are NOT available from this client machine
[ASSUMPTION, medium]:** Synopta's server-side **history/data export** (GUI or scheduled, on the
*server*), and/or a **Ridder cloud API**. Both require server access and/or Ridder
involvement — neither can be confirmed or used from this thin client.

---

## 5. Discovered interfaces — summary with confidence

| Interface | Status | Safe & supported for read-only live data? | Confidence |
| --- | --- | --- | --- |
| SynDesk ↔ controller proprietary link (cpprest, :6450x) | Live | **No** — undocumented; using it = reverse engineering | high it exists |
| Controller Modbus/OPC | Unverified | **No** — would touch the controller; out of bounds | low it exists |
| AMQP/RabbitMQ `:5672` | Referenced, not running locally | **No** — not present; default creds; production bus | high it's unusable here |
| Local DB / SQL | Absent | **No** | high |
| Local HTTP/REST API on this PC | Absent | **No** | high |
| `.site` config download (Ridder portal) | Working, manual | **No** — configuration, not live climate | high |
| Synopta server history export | Unverified, off-machine | **Potentially yes** — the recommended route | medium |
| Ridder cloud API | Unverified | **Potentially yes** — needs Ridder confirmation | low–medium |

---

## 6. Recommended integration method

**Do not tap the proprietary client link, the controller, or the GUI.** The architecture we
built (the `SynoptaSource` seam + `DropFolderSource`) is already the right shape; it just needs a
*sanctioned source of data*. In order of preference:

1. **Synopta server-side scheduled export** → a folder this PC can read. Ask Ridder / the
   Synopta server admin to enable Synopta's built-in history/data export (CSV) on a schedule to
   a shared/local folder. The existing `DropFolderSource` then consumes it unchanged — **zero
   new reverse engineering, fully supported, read-only.** *Recommended.*
2. **Official Ridder/Hortimax API or cloud feed** — if one exists and read-only credentials can
   be provisioned. Then add a single `ApiSource`/`LiveSynoptaProvider` module behind the seam.

Both are additive: one new source module + a field-mapping check. Nothing above the seam
changes (see [`docs/gaia-collector.md`](gaia-collector.md)).

---

## 7. Decision: STOP — no safe live interface exists yet

Per the sprint rules ("prefer official interfaces", "never reverse engineer", "never scrape the
GUI", "never compromise safety"), **a `LiveSynoptaProvider` cannot be implemented now**, because
every live-data path available *on this machine* is disqualified:

- the **SynDesk ↔ controller protocol** is proprietary and undocumented → tapping it is reverse
  engineering (**forbidden**);
- the **SynDesk GUI** shows the values → reading it is screen scraping / OCR (**forbidden**);
- the **controller's** possible Modbus/OPC/AMQP → connecting to it touches the live control
  system (**forbidden**, and unverified, with default credentials);
- there is **no local database, export, API, or scheduled export** to read (**confirmed
  absent**).

There is nothing safe left to build against. Inventing a workaround would violate the rules and
the project's "trust before automation" principle.

### The single smallest remaining action

**Obtain one sanctioned, read-only source of greenhouse data — via the Synopta *server*, not
this client.** Concretely, one of:

- **(Preferred)** Ask Ridder / the Synopta server administrator to **enable a scheduled history
  export (CSV) to a folder readable from this PC** (e.g. a shared network folder). *Then* the
  existing `DropFolderSource` ingests it immediately, and a thin `LiveSynoptaProvider` is added
  only if the format needs it.
- **(Alternative)** Confirm with **Ridder** whether a **supported read-only API/cloud feed**
  exists and obtain its URL + read-only credentials.

Until one of those is in hand, the Brain continues to run on the Collector's fixture/snapshot
inputs, and **no live integration is built** — by design.

---

## 8. Facts vs assumptions (at a glance)

**Facts (observed on this machine):** HortiMaX CX controller at `172.27.0.250`; SynDesk client
live-connected to it (PID 17804, proprietary link); thin client (server/DB off-machine); no
local DB/export/API/scheduled-export; no RabbitMQ/OPC/Modbus/SQL service; `.site` files are
proprietary binary config; CX Assistant is a config/commissioning tool.

**Assumptions (not verified from here):** exact protocol semantics; per-measurement update
intervals and stored units; existence of a server-side Synopta history export or a Ridder API.
These are explicitly *not* resolved by guessing or by decoding proprietary formats.
