Set-Location $PSScriptRoot

if (!(Test-Path ".\\.venv\\Scripts\\python.exe")) {
  Write-Host "Virtualenv not found. Create it first:" -ForegroundColor Yellow
  Write-Host "  python -m venv .venv" -ForegroundColor Yellow
  Write-Host "  .\\.venv\\Scripts\\python -m pip install -r requirements.txt" -ForegroundColor Yellow
  exit 1
}

.\\.venv\\Scripts\\python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000



