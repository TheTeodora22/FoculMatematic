import os
import time

from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Rulează backup_db la fiecare 12 ore (configurabil prin BACKUP_INTERVAL_HOURS)."

    def handle(self, *args, **options):
        interval_hours = float(os.getenv("BACKUP_INTERVAL_HOURS", "12"))
        interval_seconds = int(interval_hours * 3600)
        self.stdout.write(
            self.style.SUCCESS(
                f"Scheduler backup pornit: la fiecare {interval_hours:g} ore."
            )
        )

        while True:
            try:
                call_command("backup_db")
            except Exception as exc:
                self.stderr.write(self.style.ERROR(f"Backup eșuat: {exc}"))
            self.stdout.write(f"Următorul backup în {interval_hours:g} ore...")
            time.sleep(interval_seconds)
