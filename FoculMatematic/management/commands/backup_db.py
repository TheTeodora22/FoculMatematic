from django.core.management.base import BaseCommand

from FoculMatematicProiect.db_backup import create_backup, prune_old_backups


class Command(BaseCommand):
    help = "Creează un backup al bazei de date și elimină copiile vechi."

    def handle(self, *args, **options):
        path = create_backup()
        removed = prune_old_backups()
        self.stdout.write(self.style.SUCCESS(f"Backup creat: {path}"))
        if removed:
            self.stdout.write(f"Backup-uri vechi șterse: {removed}")
