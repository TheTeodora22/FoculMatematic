from datetime import datetime, timedelta
from pathlib import Path
import sqlite3

from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Salvează o copie SQLite în backups/db-YYYYMMDD-HHMMSS.sqlite3"

    def add_arguments(self, parser):
        parser.add_argument(
            "--keep-days",
            type=int,
            default=30,
            help="Șterge backup-uri mai vechi de N zile (0 = nu șterge nimic).",
        )

    def handle(self, *args, **options):
        db = settings.DATABASES["default"]
        if db["ENGINE"] != "django.db.backends.sqlite3":
            self.stderr.write(self.style.ERROR("backup_database: doar SQLite este suportat."))
            return

        db_path = Path(db["NAME"])
        if not db_path.is_file():
            self.stderr.write(self.style.ERROR(f"Fișierul bazei lipsește: {db_path}"))
            return

        backups_dir = Path(settings.BASE_DIR) / "backups"
        backups_dir.mkdir(parents=True, exist_ok=True)

        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        out_path = backups_dir / f"db-{stamp}.sqlite3"

        self.stdout.write(f"Backup: {db_path} → {out_path}")

        src = sqlite3.connect(str(db_path))
        try:
            dest = sqlite3.connect(str(out_path))
            try:
                src.backup(dest)
            finally:
                dest.close()
        finally:
            src.close()

        self.stdout.write(self.style.SUCCESS(f"Gata: {out_path}"))

        keep_days = options["keep_days"]
        if keep_days > 0:
            cutoff = datetime.now() - timedelta(days=keep_days)
            removed = 0
            for p in sorted(backups_dir.glob("db-*.sqlite3")):
                if p == out_path:
                    continue
                try:
                    if datetime.fromtimestamp(p.stat().st_mtime) < cutoff:
                        p.unlink()
                        removed += 1
                except OSError:
                    pass
            if removed:
                self.stdout.write(f"Șterse {removed} backup(uri) mai vechi de {keep_days} zile.")
