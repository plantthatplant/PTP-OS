# Register Gaia to start at logon WITHOUT admin — by dropping a launcher in the user's Startup
# folder. Re-runnable. Remove by deleting the file it reports.
#   powershell -ExecutionPolicy Bypass -File run\install-startup.ps1
$ErrorActionPreference = "Stop"
$repo = if ($env:GAIA_REPO) { $env:GAIA_REPO } else { Split-Path -Parent $PSScriptRoot }
$start = Join-Path $repo "run\start-gaia.ps1"
$startup = [Environment]::GetFolderPath("Startup")
$dest = Join-Path $startup "GaiaGoLive.cmd"
$cmd = "@echo off`r`nstart `"`" /min powershell -NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -File `"$start`"`r`n"
Set-Content -Path $dest -Value $cmd -Encoding ASCII
Write-Host "Installed Gaia auto-start (no admin) at:" -ForegroundColor Green
Write-Host "  $dest"
Write-Host "Gaia launches at next sign-in -> http://127.0.0.1:8000/   (remove: delete that file)"
