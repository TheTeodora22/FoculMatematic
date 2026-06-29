# AGENTS.md

## Cursor Cloud specific instructions

This repo is a single **Django 4.2 monolith** ("Focul Matematic", a Romanian math-quiz web app) backed by a file-based **SQLite** database (`db.sqlite3`, committed with seed data). All Django apps (`accounts`, `quizzes`, `battlepass`, `FoculMatematic`) run inside one web process. Python 3.12 is used. There are no auxiliary services (no Redis/Celery/external DB).

### Environment requirements (non-obvious)
- A `.env` file at the repo root is **required** and is gitignored, so it will not be in a fresh checkout. `settings.py` reads `SECRET_KEY` with no default (the app fails without it) and `DEBUG` (must be `True` for local dev so `localhost`/`127.0.0.1`/`testserver` are added to `ALLOWED_HOSTS`). The startup/update script creates a dev `.env` if one is missing.
- Dependencies (`Django==4.2.11`, `python-dotenv`) are in `requirements.txt`. `pip install` lands in `~/.local`; the `django-admin` script is not on `PATH`, but this does not matter because everything is run via `python manage.py`.

### Running / testing (run via `python manage.py`)
- Run the app (dev): `python manage.py runserver 0.0.0.0:8000` (serves the whole product on port 8000).
- Apply DB schema: `python manage.py migrate`.
- System check / "lint": `python manage.py check` (no separate linter/formatter is configured in this repo).
- Tests: `python manage.py test` (the repo currently contains 0 tests).

### Notes
- There is no signup/registration view wired up; create users via `python manage.py createsuperuser` or the Django shell. The seeded DB already contains a quiz ("Test Quiz Flow") and users.
- Quiz scoring submits the selected **option id** (form field `q_<question_id>`), not the answer text; selecting the option flagged `is_correct=True` yields full points.
