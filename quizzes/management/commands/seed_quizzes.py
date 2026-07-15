from django.core.management.base import BaseCommand, CommandError

from quizzes.seed_loader import SeedValidationError, load_all_quizzes, quizzes_data_dir


class Command(BaseCommand):
    help = (
        "Încarcă chestionare din data/quizzes/*.json. "
        "Sigur de rulat repetat după migrate sau reset DB."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--file",
            help="Încarcă un singur fișier JSON (ex: algebra_clasa_8.json).",
        )

    def handle(self, *args, **options):
        data_dir = quizzes_data_dir()
        if not data_dir.exists():
            raise CommandError(
                f"Directorul {data_dir} nu există. Creează-l și adaugă fișiere .json."
            )

        try:
            results = load_all_quizzes(data_dir, only_file=options.get("file"))
        except SeedValidationError as exc:
            raise CommandError(str(exc)) from exc
        except FileNotFoundError as exc:
            raise CommandError(str(exc)) from exc

        if not results:
            self.stdout.write(
                self.style.WARNING(
                    f"Niciun fișier .json găsit în {data_dir} "
                    "(fișierele care încep cu _ sunt ignorate)."
                )
            )
            return

        created_count = 0
        updated_count = 0
        for quiz, created, filename in results:
            q_count = quiz.questions.count()
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f"[nou] {filename} -> {q_count} intrebari (id quiz={quiz.pk})"
                    )
                )
            else:
                updated_count += 1
                self.stdout.write(
                    f"[actualizat] {filename} -> {q_count} intrebari (id quiz={quiz.pk})"
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"Gata: {created_count} noi, {updated_count} actualizate."
            )
        )
