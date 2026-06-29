# Launch the Gaia Edge Collector in production — the daemon that watches the Synopta export
# folder and keeps data/inbox/latest.json current. Machine-specific by nature (it pins the Python
# interpreter and repo path); the collector itself has no hardcoded paths/keys — every value below
# is an env var with a sensible default, overridable here or in the environment.
$ErrorActionPreference = "Stop"

# --- machine settings (edit these two for a new computer) ---
$Python = if ($env:GAIA_PYTHON) { $env:GAIA_PYTHON } else { "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe" }
$Repo   = if ($env:GAIA_REPO)   { $env:GAIA_REPO }   else { "C:\Users\Synopta\Desktop\PTP-OS-filer" }

# --- Edge Collector configuration (all optional; these defaults suit this PC) ---
# The export folder Ridder writes into. D: is the large empty data drive on this box — a clean,
# dedicated landing area separate from the repo. Point Ridder's scheduled export here.
if (-not $env:SYNOPTA_IMPORT_PATH)  { $env:SYNOPTA_IMPORT_PATH  = "D:\SynoptaExport\incoming" }
if (-not $env:SYNOPTA_ARCHIVE_PATH) { $env:SYNOPTA_ARCHIVE_PATH = "D:\SynoptaExport\archive" }
if (-not $env:SYNOPTA_FAILED_PATH)  { $env:SYNOPTA_FAILED_PATH  = "D:\SynoptaExport\failed" }
if (-not $env:IMPORT_INTERVAL)      { $env:IMPORT_INTERVAL      = "30" }       # poll seconds
if (-not $env:MAX_FILE_SIZE)        { $env:MAX_FILE_SIZE        = "16777216" } # 16 MB
if (-not $env:SUPPORTED_FORMATS)    { $env:SUPPORTED_FORMATS    = "csv,tsv,xlsx,json" }
if (-not $env:SYNOPTA_FRESHNESS_SLA_S) { $env:SYNOPTA_FRESHNESS_SLA_S = "900" } # 15 min before "stale"
# Publishes to the same snapshot the API reads (GAIA_DATA_DIR / GAIA_SNAPSHOT, shared defaults).
$env:PYTHONUTF8 = "1"

Set-Location $Repo
# Supervised loop: if it ever exits, restart after a short pause so it "runs all day" and survives
# a crash without waiting for the next logon. (Stop it by ending the window/process.)
while ($true) {
  & $Python -m collector.edge.run
  Start-Sleep -Seconds 5
}
