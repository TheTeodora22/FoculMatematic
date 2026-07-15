# Focul Matematic

Aplicație web Django pentru exersarea matematicii prin quiz-uri, cu conturi de utilizator, progresie XP, battle pass și API REST pentru aplicația mobilă.

## Cerințe

- Python 3.10+
- pip
- Node.js 18+ (pentru app mobilă)

## Setup local (backend)

1. **Intră în directorul proiectului:**

   ```bash
   cd FoculMatematic
   ```

2. **Mediu virtual și dependențe:**

   ```bash
   python -m venv venv
   .\venv\Scripts\Activate.ps1   # Windows
   pip install -r requirements.txt
   ```

3. **Variabile de mediu:**

   ```powershell
   Copy-Item .env.example .env
   ```

   Pentru dev local: `DEBUG=True`, `SECRET_KEY` orice valoare, `ALLOWED_HOSTS=localhost,127.0.0.1`.

4. **Migrări și date demo:**

   ```bash
   python manage.py migrate
   python manage.py seed_battlepass
python manage.py seed_quizzes
   python manage.py createsuperuser
   ```

5. **Pornește serverul:**

   ```bash
   python manage.py runserver
   ```

   Web: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)  
   API: [http://127.0.0.1:8000/api/v1/](http://127.0.0.1:8000/api/v1/)

## App mobilă (Expo)

Vezi [`../FoculMatematicMobile/README.md`](../FoculMatematicMobile/README.md).

```bash
cd ../FoculMatematicMobile
npm install
cp .env.example .env
npx expo start
```

Setează `EXPO_PUBLIC_API_URL` la IP-ul mașinii tale (sau `http://10.0.2.2:8000` pe Android emulator).

## API REST

Autentificare JWT. Endpoints principale:

| Method | Path | Descriere |
|--------|------|-----------|
| POST | `/api/v1/auth/register/` | Înregistrare |
| POST | `/api/v1/auth/token/` | Login → access + refresh |
| GET | `/api/v1/quizzes/` | Listă quiz-uri |
| GET | `/api/v1/quizzes/{id}/` | Detalii quiz (fără răspunsuri corecte) |
| POST | `/api/v1/quizzes/{id}/submit/` | Trimite răspunsuri |
| GET | `/api/v1/attempts/{id}/` | Rezultat attempt |
| GET/PATCH | `/api/v1/profile/` | Profil utilizator |
| GET | `/api/v1/battlepass/` | Battle pass |

## Variabile de mediu

| Variabilă | Descriere |
|-----------|-----------|
| `SECRET_KEY` | Cheie secretă Django (obligatorie în producție) |
| `DEBUG` | `True` dev, `False` producție |
| `ALLOWED_HOSTS` | Hosturi permise, separate prin virgulă |
| `DATABASE_URL` | PostgreSQL (opțional în dev; obligatoriu în prod) |
| `CSRF_TRUSTED_ORIGINS` | URL-uri HTTPS pentru CSRF |
| `CORS_ALLOWED_ORIGINS` | Origini permise pentru API mobil |
| `BACKUP_INTERVAL_HOURS` | Interval backup DB (implicit 12) |
| `BACKUP_RETENTION` | Câte backup-uri se păstrează (implicit 14) |

## Deploy producție (generic)

Ghid complet: [`deploy/checklist.md`](deploy/checklist.md)

### PaaS (Render, Railway, Fly.io)

1. Conectează repository-ul
2. Setează env vars din `.env.example`
3. Adaugă PostgreSQL → `DATABASE_URL`
4. Build: `pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate`
5. Start: `gunicorn FoculMatematicProiect.wsgi --bind 0.0.0.0:$PORT`

### VPS

Nginx → Gunicorn, PostgreSQL, HTTPS (Let's Encrypt). Vezi `deploy/checklist.md`.

### Docker

```bash
docker compose up --build
docker compose exec web python manage.py createsuperuser
docker compose exec web python manage.py seed_battlepass
python manage.py seed_quizzes
```

### Verificare înainte de deploy

```bash
python manage.py check --deploy
```

## Structura proiectului

- `FoculMatematicProiect/` — setări globale
- `FoculMatematic/` — pagina de start
- `accounts/` — profil, XP, teme CSS
- `quizzes/` — quiz-uri
- `battlepass/` — recompense
- `api/` — REST API (JWT)
- `data/quizzes/` — chestionare în JSON (sursă de adevăr, versionată în Git)
- `static/` — CSS și assets
- `deploy/` — checklist deploy
- `../FoculMatematicMobile/` — app Expo

## Backup bază de date

Backup automat la fiecare **12 ore**. Fișierele sunt în `backups/` (`.gz`).

```bash
# Backup manual
python manage.py backup_db

# Scheduler continuu (VPS / proces separat)
python manage.py run_backup_scheduler

# Docker: serviciul backup pornește cu compose
docker compose up -d backup
```

Cron pe VPS (la 12 ore): `0 */12 * * * cd /path/FoculMatematic && python manage.py backup_db`

Variabile: `BACKUP_INTERVAL_HOURS=12`, `BACKUP_RETENTION=14` (ultimele 14 copii).

## Comenzi utile

```bash
python manage.py ensure_profiles
python manage.py seed_battlepass
python manage.py seed_quizzes
python manage.py test
python manage.py collectstatic --noinput
```
