#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
if [[ -x .venv/bin/python ]]; then
  exec .venv/bin/python manage.py backup_database "$@"
else
  exec python3 manage.py backup_database "$@"
fi
