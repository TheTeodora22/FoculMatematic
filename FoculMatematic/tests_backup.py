from pathlib import Path

from django.core.management import call_command
from django.test import TestCase, override_settings


@override_settings(BACKUP_DIR=Path(__file__).resolve().parent / "test_backups")
class BackupDbTests(TestCase):
    def tearDown(self):
        backup_dir = Path(__file__).resolve().parent / "test_backups"
        if backup_dir.exists():
            for f in backup_dir.glob("*"):
                f.unlink()
            backup_dir.rmdir()

    def test_backup_db_creates_file(self):
        call_command("backup_db")
        backup_dir = Path(__file__).resolve().parent / "test_backups"
        files = list(backup_dir.glob("sqlite_*.sqlite3.gz"))
        self.assertEqual(len(files), 1)
        self.assertGreater(files[0].stat().st_size, 0)
