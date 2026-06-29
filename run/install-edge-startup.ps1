# Register the Gaia Edge Collector to start at logon WITHOUT admin — by dropping a launcher in the
# user's Startup folder, next to the Gaia one (GaiaGoLive.cmd). Re-runnable. Remove by deleting the
# file it reports.
#   powershell -ExecutionPolicy Bypass -File run\install-edge-startup.ps1
$ErrorActionPreference = "Stop"
$repo = if ($env:GAIA_REPO) { $env:GAIA_REPO } else { Split-Path -Parent $PSScriptRoot }
$start = Join-Path $repo "run\start-edge.ps1"
$startup = [Environment]::GetFolderPath("Startup")
$dest = Join-Path $startup "GaiaEdgeCollector.cmd"
$cmd = "@echo off`r`nstart `"`" /min powershell -NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -File `"$start`"`r`n"
Set-Content -Path $dest -Value $cmd -Encoding ASCII
Write-Host "Installed Edge Collector auto-start (no admin) at:" -ForegroundColor Green
Write-Host "  $dest"
Write-Host "It launches at next sign-in and watches the Synopta export folder. (Remove: delete that file.)"
