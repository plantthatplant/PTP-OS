# Launch Gaia in production. This launcher is machine-specific by nature (it pins the Python
# interpreter and the repo path); the Gaia app itself has no hardcoded paths/keys — everything
# below is an env var with a sensible default, overridable here or in the environment.
$ErrorActionPreference = "Stop"

# --- machine settings (edit these two for a new computer) ---
$Python = if ($env:GAIA_PYTHON) { $env:GAIA_PYTHON } else { "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe" }
$Repo   = if ($env:GAIA_REPO)   { $env:GAIA_REPO }   else { "C:\Users\Synopta\Desktop\PTP-OS-filer" }

# --- Gaia configuration (all optional; defaults are safe for a local single-user PC) ---
if (-not $env:GAIA_API_KEY)             { $env:GAIA_API_KEY = "kalaberga-local-key" }   # change for production
if (-not $env:GAIA_PORT)                { $env:GAIA_PORT = "8000" }
if (-not $env:GAIA_HOST)                { $env:GAIA_HOST = "127.0.0.1" }
if (-not $env:GAIA_SOURCE)              { $env:GAIA_SOURCE = "fixture" }   # set 'drop-folder' + GAIA_DROP_PATH for real Synopta exports
if (-not $env:GAIA_COLLECT_INTERVAL_MIN){ $env:GAIA_COLLECT_INTERVAL_MIN = "60" }
$env:PYTHONUTF8 = "1"

Set-Location $Repo
# Supervised loop: if Gaia ever exits, restart it after a short pause, so it "runs all day"
# and survives a crash without waiting for the next logon. (Stop it by ending the window/process.)
while ($true) {
  & $Python -m api.run
  Start-Sleep -Seconds 5
}
