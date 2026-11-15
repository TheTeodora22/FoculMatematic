# Aplicații ale trigonometriei în geometrie — grile și audit

Rezultat la 30 octombrie 2026: **545 de grile originale importate și verificate**
în cele trei lecții existente.

| Lecție | Grile | Quiz ID | Sursă tipologică |
|---|---:|---:|---|
| Produs scalar, unghiul vectorilor, cosinus și sinusuri | 230 | 228 | G4 §1: 26 × 5; §2: 20 × 5 |
| Aplicații vectoriale și relația lui Leibniz | 115 | 229 | G4 §3: 23 × 5 |
| Rezolvarea triunghiurilor, raze și arii | 200 | 230 | G4 §4.1: 15 × 5; §4.2: 8 × 5; §4.3: 17 × 5 |
| **Total** | **545** | | **109 etichete de catalog × 5 variante** |

Sursa tipologică este `D:/Carti Mate/output/catalog/G4_catalog.md`, p. 230–245.
Enunțurile și datele sunt originale. Cele trei lecții erau goale în surse și în
baza locală înainte de extindere. Nu sunt necesare modele sau migrări noi.

## Domeniu și limite

Fiecare grilă are patru opțiuni distincte matematic, un răspuns corect și explicație.
Verificările folosesc calcule exacte SymPy, fracții, radicali și configurații
geometrice explicite. Demonstrațiile și construcțiile catalogului sunt adaptate
în calcule sau concluzii; unele etichete sunt numai cazuri particulare declarate,
fără pretenția dificultății integrale a problemelor olimpice.

Se precizează nondegenerarea triunghiurilor, laturile și vectorii nenuli,
convenția unghiurilor și a rapoartelor, poziția punctelor și condițiile în care
se aplică formulele pentru arii, circumrază, rază înscrisă sau triunghi ortic.
La locuri geometrice și optimizare se verifică și cazurile de frontieră.

## Reproducere

Generatorul coordonator actualizează doar cele trei surse și nu scrie în DB:

```powershell
.\.venv\Scripts\python.exe -X utf8 data/quizzes/generators/gen_clasa_9_g4.py
.\.venv\Scripts\python.exe -X utf8 scripts/verify_g4_scalar_cosinus.py
.\.venv\Scripts\python.exe -X utf8 scripts/verify_g4_vectoriale.py
.\.venv\Scripts\python.exe -X utf8 scripts/verify_g4_triunghiuri.py
node scripts/verify_g4_rendering.cjs
.\.venv\Scripts\python.exe -X utf8 manage.py check
```

Modulele sunt `gen_clasa_9_g4_scalar_cosinus.py`, `gen_clasa_9_g4_vectoriale.py`
și `gen_clasa_9_g4_triunghiuri.py`. Verificatoarele sunt independente de
generatoare și recalculează răspunsurile din datele problemelor. Nu este un
demonstrator automat general de geometrie: explicațiile au și revizuire matematică.

## Adaptări particulare declarate

- Lecția 1: G4 §1 tipurile 13, 14, 16–18, 20–22, 24–26 și §2 tipurile
  5, 6, 8–12, 14, 15, 17, 18, 20 sunt marcate `partial_case`.
  Sunt 115 grile de calcul/concluzie, cu configurații și ipoteze explicite,
  care nu înlocuiesc demonstrațiile integrale originale. Cele patru
  perpendiculare au o configurație convexă efectivă cu drepte distincte.
- Lecția 2: tipurile 12 și 16 sunt configurații proprii, marcate parțial.
  Tipul 12 folosește inverse de produse de distanțe pe secante, nu expresia
  originală nespecificată în catalog. Tipul 16 folosește un cerc explicit
  pe care trei distanțe pozitive satisfac Pitagora.
- Lecția 3: toate cerințele precizează elementul calculat; nu se pretinde
  rezolvarea completă a fiecărui triunghi atunci când se cere doar o latură,
  un cosinus sau o arie. §4.1 tipul 14 folosește patru proiecții date pe
  diagonale, iar §4.3 tipul 13 folosește criteriul medianei cu verificarea
  ariei: ambele sunt adaptări parțiale declarate. Alte identități și exemple
  sunt marcate drept calcule sau concluzii în cazuri explicite.

## Verificări și import

Au trecut auditurile independente ale tuturor celor **2180 de opțiuni**:
920 în lecția 1, 460 în lecția 2 și 800 în lecția 3. S-au verificat și
ramurile unghiurilor obtuze, vectorii nenuli, reconstrucțiile de triunghiuri,
locurile geometrice vide/punct/cerc, minimul pe segment cu ambele capete,
numărul configurațiilor din două laturi și arie (0/1/2), circumcercurile și
incercurile subtriunghiurilor, orticul acut și Bretschneider în patrulatere
convexe, inclusiv neinscriptibile.

Verificatoarele păstrează întregii și fracțiile exacte inclusiv în calculele
intermediare. Răspunsurile cu radicali sunt comparate algebric; formele LaTeX
echivalente nu sunt respinse doar pentru că au serializări diferite.
**5789 de fragmente matematice** au trecut KaTeX strict, iar regenerarea
celor trei surse este identică octet cu octet.

Importul a fost limitat la cele trei fișiere `u08`, tranzacțional, și repetat:
ID-urile celor 545 de întrebări și cele 2180 de opțiuni rămân stabile.
Nu existau întrebări sau progres anterior în lecții. Întrebările, opțiunile
și progresul celorlalte capitole au fost comparate înainte/după și sunt
neschimbate. Nu s-au schimbat manifestul, conturile, backendul, frontendul
sau schema bazei de date.

Pagina capitolului și prima/ultima întrebare a fiecărei lecții au trecut
randarea prin view-urile Django fără răspunsuri trimise sau sesiuni de test
persistate. În browser sunt confirmate totalurile 230/115/200 și afișarea
unei grile cu radicali și unghi, fără erori JavaScript. Serverul local este
pornit pe portul 8000.

[Deschide capitolul](http://127.0.0.1:8000/quizzes/clasa/9/aplicatii-trigonometrie-geometrie/).
