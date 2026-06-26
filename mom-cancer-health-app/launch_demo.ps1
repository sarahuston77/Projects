# Launch in demo mode — best for screenshots and demo videos
# - Shows an active reminder
# - Seeds sample weekly history
# - Skips audio
# - Auto-saves a screenshot to demo/screenshots/

$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ProjectRoot

$Python = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $Python)) {
    Write-Host "Setting up environment (first run)..." -ForegroundColor Yellow
    uv venv .venv --python 3.12
    uv pip install --python .venv -r requirements.txt
}

Write-Host ""
Write-Host "Care Companion — Demo Mode" -ForegroundColor Cyan
Write-Host "  Window opens at 1280x800 for clean captures." -ForegroundColor Gray
Write-Host "  Screenshot auto-saves to docs/screenshots/" -ForegroundColor Gray
Write-Host "  Use Win+Shift+S or Xbox Game Bar (Win+G) to record video." -ForegroundColor Gray
Write-Host ""

$env:KIVY_NO_ARGS = "1"
& $Python HealthApp.py --demo --no-audio --screenshot
