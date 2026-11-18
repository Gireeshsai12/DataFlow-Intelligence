#!/usr/bin/env sh
set -eu
cd "$(dirname "$0")"
output=${1:-bi-output}
docker compose exec -T app python -m app.bi export /tmp/dataflow-bi
mkdir -p "$output"
docker compose cp app:/tmp/dataflow-bi/. "$output"
