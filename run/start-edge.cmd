@echo off
rem Manual launcher — double-click or call to start the Gaia Edge Collector. Runs the PowerShell
rem launcher next to it (which supervises and restarts it).
start "" /min powershell -NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -File "%~dp0start-edge.ps1"
