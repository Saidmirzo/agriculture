#!/usr/bin/env bash

set -Eeuo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

PYTHON_BIN="python3"
if command -v python3.11 >/dev/null 2>&1; then
    PYTHON_BIN="python3.11"
elif command -v python3 >/dev/null 2>&1; then
    PYTHON_BIN="python3"
fi

export DB_ENGINE="sqlite"
export DATABASE_NAME="db.sqlite3"

echo "[INFO] Running migrations using SQLite..."
$PYTHON_BIN manage.py migrate --noinput

echo "[INFO] SQLite migration complete. Database file: $SCRIPT_DIR/db.sqlite3"
