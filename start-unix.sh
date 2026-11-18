#!/usr/bin/env sh
set -eu
cd "$(dirname "$0")"
docker compose up --build --wait
echo "Dashboard http://localhost:8000 | API http://localhost:8000/docs"
