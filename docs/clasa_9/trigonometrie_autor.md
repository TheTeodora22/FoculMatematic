# Elemente de trigonometrie — raportul autorului

Lot original pentru cele nouă lecții existente, creat la 30 octombrie 2026.
Sursa tipologică este `D:/Carti Mate/output/catalog/G3_catalog.md`, p. 204–229.

| Lecție | Sursa G3 | Grile |
|---|---|---:|
| Unghiuri și arce | §1, 7 tipuri × 5 | 35 |
| Generalizarea noțiunii de unghi | §2, 8 × 5 | 40 |
| Funcții trigonometrice în triunghi dreptunghic | §3.1, 16 × 5 | 80 |
| Semnul funcțiilor trigonometrice | §3.2, 5 × 5 | 25 |
| Reducere la primul cadran | §3.3, 8 × 5 | 40 |
| Paritate, imparitate și periodicitate | §3.4, 9 × 5 | 45 |
| Relații ale aceluiași unghi | §4, 15 × 5 | 75 |
| Suma și diferența unghiurilor | §5, 21 × 5 | 105 |
| Transformări, sume și produse finite | §6 și §7, (17+11) × 5 | 140 |
| **Total** | **117 etichete × 5** | **585** |

Ultima lecție găzduiește și aplicațiile de sume/produse finite din §7, păstrând
manifestul și cele nouă lecții existente. Nu a fost creată o lecție nouă și nu
au fost modificate alte capitole.

## Fișiere și reproducere

- `data/quizzes/generators/gen_clasa_9_trigonometrie.py`: API
  `build_banks() -> dict[int, list]` și `update_files(lessons=None)`.
- `data/quizzes/generators/trigonometrie_advanced.py`: cele 245 de grile pentru
  lecțiile 8–9, apelate numai de generatorul principal.
- `data/quizzes/generators/trigonometry_type_names.json`: cele 117 denumiri
  de tip din catalog, păstrate local pentru reproducere independentă de calea D:.
- Modificate exclusiv cele nouă surse `clasa_9_u07_l*.json`.

```powershell
.\.venv\Scripts\python.exe -X utf8 data/quizzes/generators/gen_clasa_9_trigonometrie.py
```

Opțional `--lessons 1 2 3` actualizează numai lecțiile alese. Generatorul nu
scrie în baza de date și păstrează obiectele întrebărilor din afara băncii sale.
Scrierea fiecărui JSON este atomică, pentru ca verificatorul paralel să nu citească
un fișier incomplet. Toate cele 585 de enunțuri sunt distincte global, nu doar
în interiorul fiecărei lecții. Opțiunile au maximum 87 de caractere în acest lot,
sub limita de 255 a modelului.

## Date pentru verificatorul independent

`practice_scope` conține banca, secțiunea, tipul, numele, varianta, paginile și
limita adaptării. `verification` conține operația și datele originale; nu conține
un câmp de rezultat corect. `option_values` leagă semantic opțiunile de forma lor
LaTeX, fără a înlocui recalcularea independentă.

La evaluări, `expression` păstrează formula originală cu simboluri și `givens`
leagă simbolurile de datele numerice afișate în enunț. Formula LaTeX este construită
fără reducerea identităților la răspuns. La sume și produse, termenul, indicele,
limitele și datele sunt păstrate separat. Codurile interne pentru semne, cadrane
și paritate sunt afișate elevului ca etichete naturale, nu ca numere tehnice.

## Limite și cazuri importante

**355 de grile** sunt marcate `partial_explicit_case`: demonstrațiile sau
problemele complexe sunt adaptate în calcule, concluzii ori configurații explicite.
Explicațiile prezintă metoda și condițiile; numărul etichetelor nu certifică
acoperirea integrală a dificultății tuturor problemelor originale.

Exemple de limite declarate: aria paralelogramului este dată direct din laturi
și unghi; nu reproduce condiția de diagonală din catalog. Neperiodicitatea este
tratată prin suma `sin(ax)+cos(a√2x)`, nu prin produsul din exemplul de catalog.
Produsele înjumătățite și produsele afine în cosinus au un număr explicit mic de
factori. Sumele ponderate sunt calculate exact în variante finite, fără pretenția
unei demonstrații olimpice generale.

Sunt tratate explicit:

- măsura completă față de reducerea modulo un tur, radiani față de grade;
- arcul opus unui unghi înscris, inclusiv arcul mai mare decât semicercul;
- ambiguitatea unghiului isoscel, inclusiv coincidența echilaterală;
- semnul nul și funcțiile nedefinite, fără a interpreta un produs cu un factor
  nedefinit ca fiind zero;
- paritatea pe domenii simetrice și clasificarea separată a funcției zero;
- perioadă candidată față de perioadă principală, frecvențe comensurabile,
  perioade micșorate de modul/pătrat și neperiodicitate;
- cadranele și ordinea valorilor recuperate dintr-o sumă;
- semnul radicalilor pentru unghiuri înjumătățite și cosinusul unui unghi obtuz;
- domeniile fracțiilor înainte de simplificare și numitorii intermediari;
- sumele finite la `x=2π`: suma sinusurilor este 0, iar suma celor șase cosinusuri
  este 6, deși formula închisă cu `sin(x/2)` nu se aplică (ar produce 0/0).

Importul, verificarea progresului și acceptarea finală sunt coordonate de agentul
principal după verdictul verificatorului independent. Autorul nu a importat date
și nu a modificat backendul, frontendul, conturile sau schema DB.

## Rezultat înainte de integrare

Reproducerea completă a celor nouă surse a trecut comparația octet cu octet.
Verificatorul independent a transmis acceptarea finală pentru toate cele
**585 de grile și 2340 de opțiuni**, cu unicitate globală și verificarea domeniilor.
Randarea strictă KaTeX a trecut pentru **4996 de fragmente**. După această
acceptare nu au mai fost modificate întrebările sau opțiunile.
