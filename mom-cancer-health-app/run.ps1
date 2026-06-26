# Launch Care Companion (normal mode)
$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ProjectRoot

$Python = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $Python)) {
    Write-Host "Setting up environment (first run)..." -ForegroundColor Yellow
    uv venv .venv --python 3.12
    uv pip install --python .venv -r requirements.txt
}

$env:KIVY_NO_ARGS = "1"
& $Python HealthApp.py @args
