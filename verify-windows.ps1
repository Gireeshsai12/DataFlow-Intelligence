$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
docker compose up --build --wait
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
docker compose exec -T app python scripts/smoke.py
exit $LASTEXITCODE
