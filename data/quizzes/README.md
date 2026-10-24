# Chestionare (sursă de adevăr)

Fișierele JSON din subdirectoarele `clasa_5`, `clasa_6`, ..., `clasa_12`
sunt **sursa principală** a întrebărilor.
Rămân în Git — nu se pierd la modificări de cod sau la `migrate`.

`chapters.json` rămâne în rădăcina acestui director, iar generatoarele sunt
păstrate separat în `generators/`.
În manifest, fiecare subiect folosește calea relativă completă, de exemplu
`clasa_5/clasa_5_operatii_adunarea_numerelor_naturale.json`.

## Format

### Afișarea formulelor în versiunea web

Enunțurile, opțiunile și explicațiile acceptă LaTeX delimitat prin `\(...\)` pentru formule în text și `\[...\]` pentru formule pe rând separat. În JSON, barele inverse se dublează:

```json
{"text": "Calculați \\(\\sum_{k=1}^{n} \\frac{1}{k(k+1)}\\)."}
```

KaTeX 0.19.0 și fonturile sunt servite local din `static/vendor/katex-0.19.0/`, cu licența inclusă. Nu se folosește un CDN la afișare. Delimitatorul `$` nu este activat.

Pentru banca existentă, stratul de afișare recunoaște și notațiile Unicode uzuale pentru sume, produse, fracții, radicali, puteri și indici. Le transformă în LaTeX numai la afișare; sursa întrebării și cheia de corectare rămân textul original. Fragmentele incomplete sau nerecunoscute rămân text simplu. Formulele noi complexe trebuie scrise explicit în LaTeX.

În paginile HTML, conținutul matematic este marcat prin `data-math-content`. Randarea acoperă Antrenare (inclusiv navigare și explicații încărcate dinamic), chestionarul clasic, chestionarul generat și paginile de rezultat. Nu se randează câmpurile de introducere sau datele JSON ale exercițiilor interactive. Această integrare este pentru web; aplicația React Native nu este modificată.

Verificare: `node scripts/verify_math_rendering.cjs` testează gruparea operatorilor și randarea fragmentelor matematice din cele 315 grile ale secțiunii 4. Testul matematic al răspunsurilor rămâne `scripts/verify_clasa_9_inductie_numarare.py`.

Un fișier = un chestionar. Exemplu: `clasa_8/algebra_clasa_8.json`

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

### Clasa a IX-a: Mulțimea numerelor reale

Capitolul are șase lecții distincte în ordinea cuprinsului Burtea:
1.1. Operații algebrice, 1.2. Ordonare, 1.3. Modul, 1.4. Aproximări,
1.5. Parte întreagă și fracționară, 1.6. Operații cu intervale.
Fiecare are propriul JSON `clasa_9/clasa_9_numere_reale_1_*.json`.
Toate cele șase lecții au exerciții; 1.5 și 1.6 au câte 80 de grile.

`generators/gen_clasa_9_numere_reale_operatii.py` reproduce cele șase fișiere
și actualizează manifestul. Generatorul de structură păstrează aceeași împărțire.
La primul import într-o bază cu vechea lecție reunită, `seed_quizzes` mută
întrebările în noile lecții, păstrând ID-urile, opțiunile și progresul elevilor.
Reorganizarea este tranzacțională și idempotentă. O întrebare veche fără
destinație oprește importul, fără să fie ștearsă.

```bash
python manage.py seed_quizzes
```

Un singur fișier:

```bash
python manage.py seed_quizzes --file clasa_8/algebra_clasa_8.json
```

Pentru compatibilitate, `--file algebra_clasa_8.json` caută automat fișierul
și în subdirectoarele claselor, dacă numele este unic.

Comanda este **idempotentă**: o poți rula după fiecare `migrate`, reset DB sau deploy.
Actualizează quiz-urile existente (după `title`) și șterge întrebări/opțiuni care nu mai apar în JSON.

## Workflow cu poze

1. Trimite pozele în chat
2. Se adaugă/actualizează un fișier `.json` aici
3. Rulezi `python manage.py seed_quizzes`
4. Commit la JSON în Git — datele sunt salvate permanent
