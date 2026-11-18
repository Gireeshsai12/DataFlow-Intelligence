$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
docker compose up --build --wait
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
Write-Output "Dashboard http://localhost:8000 | API http://localhost:8000/docs"
