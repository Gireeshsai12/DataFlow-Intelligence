param([string]$OutputPath = (Join-Path $PSScriptRoot 'bi-output'))
$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot
docker compose exec -T app python -m app.bi export /tmp/dataflow-bi
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
New-Item -ItemType Directory -Force -Path $OutputPath | Out-Null
docker compose cp 'app:/tmp/dataflow-bi/.' "$OutputPath"
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
Write-Output "BI exports copied to $OutputPath"
