# Checklist deploy producție

## Înainte de go-live

- [ ] `python manage.py check --deploy` fără erori critice
- [ ] `DEBUG=False`
- [ ] `SECRET_KEY` setat (valoare lungă, aleatoare)
- [ ] `ALLOWED_HOSTS` include domeniul de producție
- [ ] PostgreSQL configurat (`DATABASE_URL`)
- [ ] `python manage.py migrate`
- [ ] `python manage.py collectstatic --noinput`
- [ ] Superuser creat: `python manage.py createsuperuser`
- [ ] `python manage.py seed_battlepass` (prima instalare)
- [ ] `CSRF_TRUSTED_ORIGINS` cu URL HTTPS
- [ ] `CORS_ALLOWED_ORIGINS` configurat (dacă folosești API mobil)
- [ ] Backup automat la 12 ore configurat (vezi secțiunea Backup mai jos)

## Backup bază de date (la 12 ore)

Backup-urile se salvează în `backups/` (compresate `.gz`). Se păstrează ultimele **14** copii (~7 zile la interval de 12h).

### Manual

```bash
python manage.py backup_db
```

### Scheduler integrat (Docker)

Serviciul `backup` din `docker-compose.yml` rulează automat:

```bash
docker compose up -d backup
```

### VPS / cron (fără Docker)

La fiecare 12 ore:

```cron
0 */12 * * * cd /cale/catre/FoculMatematic && /cale/catre/venv/bin/python manage.py backup_db >> /var/log/focul_backup.log 2>&1
```

Sau proces dedicat:

```bash
python manage.py run_backup_scheduler
```

### Variabile

| Variabilă | Implicit | Descriere |
|-----------|----------|-----------|
| `BACKUP_INTERVAL_HOURS` | `12` | Interval între backup-uri |
| `BACKUP_RETENTION` | `14` | Număr backup-uri păstrate |

Pentru PostgreSQL, `pg_dump` trebuie instalat pe server (inclus în Dockerfile).

## Script release

```bash
pip install -r requirements.txt
python manage.py collectstatic --noinput
python manage.py migrate
gunicorn FoculMatematicProiect.wsgi --bind 0.0.0.0:$PORT
```

## Variante hosting

### PaaS (Render, Railway, Fly.io)

1. Conectează repository-ul
2. Setează env vars din `.env.example`
3. Adaugă PostgreSQL managed → copiază `DATABASE_URL`
4. Build: `pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate`
5. Start: `gunicorn FoculMatematicProiect.wsgi --bind 0.0.0.0:$PORT`

### VPS (Nginx + Gunicorn)

1. Instalează Python, PostgreSQL, Nginx
2. Clonează proiectul, configurează `.env`
3. Rulează migrări și collectstatic
4. Systemd service pentru Gunicorn
5. Nginx reverse proxy cu HTTPS (Let's Encrypt)

### Docker

```bash
docker compose up --build
docker compose exec web python manage.py createsuperuser
docker compose exec web python manage.py seed_battlepass
```
