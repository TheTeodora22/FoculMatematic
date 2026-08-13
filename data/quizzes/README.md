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
- `format`: `grid`, `true_false` sau `interactive`. Dacă lipsește, este dedus automat din tipul întrebării.
- Formatul `true_false` acceptă exact opțiunile `Adevărat` și `Fals`.
- Fișierele care încep cu `_` sunt ignorate (template-uri)

### Exercițiu interactiv cu paranteze

Acest tip apare în modul **Antrenare**. Elevul trage parantezele în pozițiile corecte:

```json
{
  "text": "Încadrează termenii care au suma 100.",
  "type": "parentheses_drag",
  "points": 10,
  "explanation": "36 + 64 = 100.",
  "interactive": {
    "tokens": ["36", "+ 64", "+ 20"],
    "correct_open_index": 0,
    "correct_close_index": 2
  }
}
```

Indicii reprezintă spațiile dintre elementele expresiei: `0` este înaintea
primului element, iar lungimea listei este poziția de după ultimul element.
Exercițiile interactive sunt omise momentan din testele generate și din
chestionarul clasic cu grile.

### Exerciții interactive pentru scădere

În modul **Antrenare** sunt acceptate și următoarele tipuri:

- `column_subtraction`: `minuend`, `subtrahend`, `correct_result` și lista booleană `borrow_columns`;
- `column_addition`: `addend1`, `addend2`, `correct_result` și lista booleană `carry_columns`;
- `column_multiplication`: `multiplicand`, un `multiplier` de o cifră, `correct_result` și lista `carry_columns`;
- `missing_digits`: cele trei rânduri (`minuend`, `subtrahend`, `result`) și pozițiile ascunse din `missing`, de exemplu `"result:2"`;
- `error_spotting`: calculul afișat, rezultatul corect și `error_column` (indice de la stânga, începând cu 0);
- `parentheses_target`: aceleași poziții ca la parantezele interactive, plus rezultatul `target`;
- `input_output`: regula `add`, `subtract` sau `multiply`, valoarea aplicată și rânduri cu exact o valoare `null`.

Validatorul verifică automat calculele, coloanele de împrumut și pozițiile declarate înainte ca exercițiile să intre în baza de date.

Pentru lecția despre factor comun există și:

- `factor_builder`: elevul completează factorul comun, termenii din paranteză și rezultatul;
- `factor_error`: elevul selectează primul pas greșit dintr-o rezolvare;
- `factor_match`: elevul potrivește forma desfăcută cu forma factorizată.

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
