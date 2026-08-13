#!/usr/bin/env bash

set -Eeuo pipefail

# Backup comprimat pentru baza de date Focul Matematic.
# - PostgreSQL când DATABASE_URL este definit.
# - SQLite în caz contrar.
#
# Rulare unică (potrivită pentru cron):
#   ./scripts/backup_database.sh
#
# Rulare continuă, la fiecare 12 ore:
#   ./scripts/backup_database.sh --loop

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd -- "${SCRIPT_DIR}/.." && pwd)"

BACKUP_DIR="${BACKUP_DIR:-${PROJECT_DIR}/backups}"
SQLITE_DB_PATH="${SQLITE_DB_PATH:-${PROJECT_DIR}/db.sqlite3}"
RETENTION_DAYS="${BACKUP_RETENTION_DAYS:-30}"
INTERVAL_HOURS="${BACKUP_INTERVAL_HOURS:-12}"
PYTHON_BIN="${PYTHON_BIN:-python3}"
LOCK_DIR="${BACKUP_DIR}/.backup.lock"

umask 077

log() {
    printf '[%s] %s\n' "$(date --iso-8601=seconds)" "$*"
}

fail() {
    log "EROARE: $*" >&2
    exit 1
}

is_positive_integer() {
    [[ "$1" =~ ^[1-9][0-9]*$ ]]
}

validate_config() {
    is_positive_integer "${RETENTION_DAYS}" || \
        fail "BACKUP_RETENTION_DAYS trebuie să fie un număr întreg pozitiv."
    is_positive_integer "${INTERVAL_HOURS}" || \
        fail "BACKUP_INTERVAL_HOURS trebuie să fie un număr întreg pozitiv."
}

acquire_lock() {
    mkdir -p -- "${BACKUP_DIR}"
    if ! mkdir -- "${LOCK_DIR}" 2>/dev/null; then
        fail "Un alt backup pare să ruleze deja (${LOCK_DIR})."
    fi
}

release_lock() {
    rmdir -- "${LOCK_DIR}" 2>/dev/null || true
}

backup_postgresql() {
    command -v pg_dump >/dev/null 2>&1 || \
        fail "pg_dump nu este instalat. Instalează pachetul postgresql-client."
    command -v gzip >/dev/null 2>&1 || fail "gzip nu este instalat."

    local timestamp destination temporary
    timestamp="$(date '+%Y%m%d_%H%M%S')"
    destination="${BACKUP_DIR}/postgres_${timestamp}.sql.gz"
    temporary="${destination}.tmp"

    trap 'rm -f -- "${temporary:-}"; release_lock' EXIT
    log "Creez backup PostgreSQL..."
    pg_dump --no-owner --no-acl "${DATABASE_URL}" | gzip -9 > "${temporary}"
    [[ -s "${temporary}" ]] || fail "Backupul PostgreSQL rezultat este gol."
    mv -- "${temporary}" "${destination}"
    log "Backup creat: ${destination}"
}

backup_sqlite() {
    command -v "${PYTHON_BIN}" >/dev/null 2>&1 || \
        fail "${PYTHON_BIN} nu este instalat."
    command -v gzip >/dev/null 2>&1 || fail "gzip nu este instalat."
    [[ -f "${SQLITE_DB_PATH}" ]] || \
        fail "Nu am găsit baza SQLite la ${SQLITE_DB_PATH}."

    local timestamp destination temporary snapshot
    timestamp="$(date '+%Y%m%d_%H%M%S')"
    destination="${BACKUP_DIR}/sqlite_${timestamp}.sqlite3.gz"
    temporary="${destination}.tmp"
    snapshot="${BACKUP_DIR}/.sqlite_${timestamp}.tmp"

    trap 'rm -f -- "${temporary:-}" "${snapshot:-}"; release_lock' EXIT
    log "Creez backup SQLite consistent..."
    "${PYTHON_BIN}" - "${SQLITE_DB_PATH}" "${snapshot}" <<'PY'
import sqlite3
import sys

source_path, destination_path = sys.argv[1:]
with sqlite3.connect(source_path) as source:
    with sqlite3.connect(destination_path) as destination:
        source.backup(destination)
PY
    gzip -9 -c -- "${snapshot}" > "${temporary}"
    [[ -s "${temporary}" ]] || fail "Backupul SQLite rezultat este gol."
    mv -- "${temporary}" "${destination}"
    rm -f -- "${snapshot}"
    log "Backup creat: ${destination}"
}

delete_expired_backups() {
    local retention_minutes deleted
    retention_minutes=$((RETENTION_DAYS * 24 * 60))
    deleted=0

    while IFS= read -r -d '' expired; do
        rm -f -- "${expired}"
        log "Backup expirat șters: ${expired}"
        deleted=$((deleted + 1))
    done < <(
        find "${BACKUP_DIR}" -maxdepth 1 -type f \
            \( -name 'postgres_*.sql.gz' -o -name 'sqlite_*.sqlite3.gz' \) \
            -mmin "+${retention_minutes}" -print0
    )

    log "Curățare terminată: ${deleted} backup(uri) mai vechi de ${RETENTION_DAYS} zile."
}

run_backup() {
    acquire_lock
    trap release_lock EXIT

    if [[ -n "${DATABASE_URL:-}" ]]; then
        backup_postgresql
    else
        backup_sqlite
    fi

    delete_expired_backups
    release_lock
    trap - EXIT
}

main() {
    local backup_status
    validate_config

    case "${1:-}" in
        "")
            run_backup
            ;;
        --loop)
            while true; do
                set +e
                (set -Eeuo pipefail; run_backup)
                backup_status=$?
                set -e
                if ((backup_status != 0)); then
                    log "Backupul a eșuat; voi încerca din nou la următorul interval." >&2
                fi
                log "Următorul backup va începe peste ${INTERVAL_HOURS} ore."
                sleep "$((INTERVAL_HOURS * 60 * 60))"
            done
            ;;
        -h|--help)
            printf 'Utilizare: %s [--loop]\n' "$0"
            printf 'Fără opțiuni: execută un singur backup. --loop: repetă la fiecare %s ore.\n' "${INTERVAL_HOURS}"
            ;;
        *)
            fail "Opțiune necunoscută: $1 (folosește --help)"
            ;;
    esac
}

main "$@"
