# Mulțimea numerelor reale — lecții separate

Structura urmărește subcapitolele din cuprinsul culegerii Burtea IX.
În aplicație, capitolul „Mulțimea numerelor reale” are următoarele lecții:

| Subcapitol | Fișier în `data/quizzes/clasa_9/` | Exerciții |
|---|---|---:|
| 1.1. Operații algebrice cu numere reale | `clasa_9_numere_reale_1_1_operatii_algebrice.json` | 131 |
| 1.2. Ordonarea numerelor reale | `clasa_9_numere_reale_1_2_ordonare.json` | 84 |
| 1.3. Modulul unui număr real | `clasa_9_numere_reale_1_3_modul.json` | 81 |
| 1.4. Aproximări prin lipsă sau prin adaos | `clasa_9_numere_reale_1_4_aproximari.json` | 40 |
| 1.5. Parte întreagă. Parte fracționară | `clasa_9_numere_reale_1_5_parte_intreaga_fractionara.json` | 0 |
| 1.6. Operații cu intervale de numere reale | `clasa_9_numere_reale_1_6_intervale.json` | 0 |

Ultimele două sunt structură pregătită, nu lecții finalizate. Numărul total
de exerciții rămâne 336. Exercițiile și variantele de răspuns sunt identice
cu cele din vechiul fișier reunit. Patru comparații preexistente sunt acum
la 1.2, iar afirmația despre √(a²) este la 1.3; celelalte 50 de exerciții
preexistente sunt la 1.1.

Generatorul principal produce fișierele separat. `chapters.json` și
generatorul de structură folosesc aceeași definiție a celor șase lecții.
Fișierul agregat vechi și lecția goală „Puteri, radicali și operații cu
intervale” au fost înlocuite.

`python manage.py seed_quizzes` adaptează automat bazele existente.
Vechea lecție își păstrează ID-ul și devine 1.1; vechiul placeholder gol
devine 1.6. Întrebările sunt mutate prin schimbarea lecției lor, păstrând
ID-urile și referințele din progres, răspunsuri și sesiuni istorice.
Operația este în tranzacția importului și refuză întrebări nemapate ori
destinații conflictuale. La importurile următoare nu se repetă mutarea.

Validare: 13 teste de seed și reorganizare, inclusiv păstrarea ID-urilor
întrebărilor/opțiunilor/progresului, import repetat și rollback la întrebare
nemapată. În baza locală au fost comparate toate cele 336 de ID-uri, toate
opțiunile și referințele de progres, înainte și după două importuri.
