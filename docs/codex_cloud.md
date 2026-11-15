# Focul Matematic în Codex Cloud

Repository: https://github.com/TheTeodora22/FoculMatematic

Ramura cu sursele locale pregătite pentru cloud: `codex/cloud-focul-matematic`.
Ramura `main` nu include încă toate modificările locale din această versiune.

## Pregătire într-un mediu Linux nou

Din rădăcina repository-ului:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
test -f .env || cp .env.example .env
python manage.py check
python manage.py migrate --noinput
python manage.py seed_battlepass
python manage.py seed_quizzes
```

Fișierul `.env.example` configurează dezvoltarea locală cu SQLite și `DEBUG=True`.
Baza de date și conturile demo sunt create în mediul cloud. Datele utilizatorilor
din baza de date de pe PC nu sunt sincronizate prin Git.

Pentru previzualizare: `python manage.py runserver 0.0.0.0:8000`.
Adaugă domeniul de previzualizare în `ALLOWED_HOSTS` și, pentru formulare,
originea HTTPS în `CSRF_TRUSTED_ORIGINS` din `.env`.

## Continuarea lucrului de la distanță

Deschide chatul cloud din Codex pe web sau mobil, folosind același cont și
workspace. Continuă instrucțiunile în acel chat. Modificările de cod se
sincronizează cu PC-ul prin commit și push/pull pe ramura de lucru.
Nu comite `.env`, baze de date, medii virtuale sau fișiere temporare.
