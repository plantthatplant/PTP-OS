@echo off
rem Manual launcher — double-click or call to start Gaia. Runs the PowerShell launcher next to it.
start "" /min powershell -NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -File "%~dp0start-gaia.ps1"
