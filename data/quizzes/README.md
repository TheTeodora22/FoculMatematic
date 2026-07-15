# Chestionare (sursă de adevăr)

Fișierele JSON din acest folder sunt **sursa principală** a întrebărilor.
Rămân în Git — nu se pierd la modificări de cod sau la `migrate`.

## Format

Un fișier = un chestionar. Exemplu: `algebra_clasa_8.json`

```json
{
  "title": "Algebră clasa 8",
  "description": "Opțional",
  "difficulty": "easy",
  "questions": [
    {
      "text": "Cât face 2x + 3 = 7?",
      "points": 10,
      "options": [
        {"text": "x = 2", "is_correct": true},
        {"text": "x = 3", "is_correct": false},
        {"text": "x = 4", "is_correct": false}
      ]
    }
  ]
}
```

- `difficulty`: `easy`, `medium` sau `hard`
- `questions`: listă de întrebări (poate fi goală pentru capitole fără exerciții încă)
- Fiecare întrebare: minim 2 opțiuni, **exact una** cu `"is_correct": true`
- Fișierele care încep cu `_` sunt ignorate (template-uri)

## Încărcare în baza de date

```bash
python manage.py seed_quizzes
```

Un singur fișier:

```bash
python manage.py seed_quizzes --file algebra_clasa_8.json
```

Comanda este **idempotentă**: o poți rula după fiecare `migrate`, reset DB sau deploy.
Actualizează quiz-urile existente (după `title`) și șterge întrebări/opțiuni care nu mai apar în JSON.

## Workflow cu poze

1. Trimite pozele în chat
2. Se adaugă/actualizează un fișier `.json` aici
3. Rulezi `python manage.py seed_quizzes`
4. Commit la JSON în Git — datele sunt salvate permanent
