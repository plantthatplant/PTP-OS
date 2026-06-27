# Register Gaia to start automatically at logon (Windows Task Scheduler). Re-runnable.
# Run once:  powershell -ExecutionPolicy Bypass -File run\install-autostart.ps1
# Remove:    schtasks /delete /tn GaiaGoLive /f
$ErrorActionPreference = "Stop"
$task = "GaiaGoLive"
$repo = if ($env:GAIA_REPO) { $env:GAIA_REPO } else { Split-Path -Parent $PSScriptRoot }
$start = Join-Path $repo "run\start-gaia.ps1"

# Task Scheduler may require an elevated shell. If you get "Access denied", either run this in an
# Administrator PowerShell, or use the no-admin alternative: run\install-startup.ps1
$action = "powershell -NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -File `"$start`""
try { schtasks /delete /tn $task /f *> $null } catch {}
schtasks /create /tn $task /sc onlogon /rl LIMITED /tr $action /f
Write-Host "Registered '$task' to launch Gaia at logon." -ForegroundColor Green
Write-Host "Gaia will be at http://127.0.0.1:8000/ after the next sign-in (or run start-gaia.ps1 now)."
