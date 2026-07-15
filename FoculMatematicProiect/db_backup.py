import gzip
import os
import shutil
import sqlite3
import subprocess
from datetime import datetime
from pathlib import Path

from django.conf import settings
from django.db import connection


def backup_dir() -> Path:
    path = Path(getattr(settings, "BACKUP_DIR", settings.BASE_DIR / "backups"))
    path.mkdir(parents=True, exist_ok=True)
    return path


def retention_count() -> int:
    return int(getattr(settings, "BACKUP_RETENTION", 14))


def _timestamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def _is_sqlite() -> bool:
    return connection.settings_dict["ENGINE"] == "django.db.backends.sqlite3"


def _is_postgresql() -> bool:
    return connection.settings_dict["ENGINE"] == "django.db.backends.postgresql"


def _backup_sqlite(dest: Path) -> None:
    db_name = str(connection.settings_dict["NAME"])
    db_path = Path(db_name)

    if db_path.exists() and not db_name.startswith(":"):
        with open(db_path, "rb") as src, gzip.open(dest, "wb") as out:
            shutil.copyfileobj(src, out)
        return

    raw_conn = connection.connection
    if raw_conn is None:
        connection.ensure_connection()
        raw_conn = connection.connection

    tmp_path = dest.with_suffix("")
    tmp_sqlite = sqlite3.connect(str(tmp_path))
    try:
        raw_conn.backup(tmp_sqlite)
    finally:
        tmp_sqlite.close()

    with open(tmp_path, "rb") as src, gzip.open(dest, "wb") as out:
        shutil.copyfileobj(src, out)
    tmp_path.unlink(missing_ok=True)


def create_backup() -> Path:
    """Creează un backup și returnează calea fișierului."""
    dest_dir = backup_dir()
    stamp = _timestamp()

    if _is_sqlite():
        dest = dest_dir / f"sqlite_{stamp}.sqlite3.gz"
        _backup_sqlite(dest)
        return dest

    if _is_postgresql():
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            raise RuntimeError("DATABASE_URL lipsește pentru backup PostgreSQL.")
        dest = dest_dir / f"postgres_{stamp}.sql.gz"
        result = subprocess.run(
            ["pg_dump", "--no-owner", "--no-acl", database_url],
            capture_output=True,
            check=False,
        )
        if result.returncode != 0:
            stderr = result.stderr.decode("utf-8", errors="replace")
            raise RuntimeError(f"pg_dump a eșuat: {stderr}")
        with gzip.open(dest, "wb") as out:
            out.write(result.stdout)
        return dest

    engine = connection.settings_dict["ENGINE"]
    raise RuntimeError(f"Backup nesuportat pentru engine: {engine}")


def prune_old_backups() -> int:
    """Șterge backup-uri vechi, păstrând ultimele BACKUP_RETENTION fișiere."""
    dest_dir = backup_dir()
    files = sorted(
        dest_dir.glob("*"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    removed = 0
    for old in files[retention_count() :]:
        old.unlink(missing_ok=True)
        removed += 1
    return removed
