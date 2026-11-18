#!/usr/bin/env sh
set -eu
cd "$(dirname "$0")"
docker compose up --build --wait
docker compose exec -T app python scripts/smoke.py
