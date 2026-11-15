# Coliniaritate, concurență și paralelism — grile și audit

Rezultat la 30 octombrie 2026: **425 de grile originale importate și verificate**,
în cele cinci lecții existente.

| Lecție | Grile | Quiz ID | Sursă tipologică |
|---|---:|---:|---|
| Vectorul de poziție al unui punct în plan | 85 | 214 | G2 §1: 17 × 5 |
| Teorema lui Thales | 25 | 215 | Cinci familii originale × 5 |
| Centrul de greutate al unui triunghi | 100 | 216 | G2 §2: 20 × 5 |
| Teorema bisectoarei. Relația lui Sylvester | 130 | 217 | G2 §3: 26 × 5 |
| Teorema lui Menelau | 85 | 218 | G2 §4: 17 × 5 |
| **Total** | **425** | | **80 etichete G2 × 5 + 25 originale** |

Catalogul folosit: `D:/Carti Mate/output/catalog/G2_catalog.md`, p. 185–203.
Datele și enunțurile sunt originale. G2 nu conține o secțiune separată Thales;
cele 25 de grile ale acestei lecții nu primesc atribuiri de catalog inventate.
Lecțiile erau goale în baza locală înainte de extindere. Nu sunt necesare modele
sau migrări noi și nu se schimbă arhitectura, conturile ori lecțiile altor capitole.

## Acoperire și limite didactice

Fiecare grilă are patru opțiuni distincte matematic, un singur răspuns corect și
explicație. Se folosesc fracții exacte, coordonate, ponderi baricentrice, rapoarte
orientate, configurații de intersecții și teoreme cu ipoteze explicite.
Problemele de demonstrație, construcție și loc geometric sunt adaptate în
calcule, concluzii sau configurații concrete. Numărul etichetelor nu certifică
acoperirea integrală a dificultății originale, mai ales pentru tipurile olimpice.

Adaptări parțiale declarate:

- G2 §1: tipurile 6, 9, 11–14; §2: tipurile 3, 5, 6, 15, 16. Sunt configurații
  afine proprii, cu ipoteze explicite; de exemplu, patrulaterul centrelor se
  construiește din triunghiurile OAB/OBC/OCD/ODA, nu din cele patru triplete
  arbitrare de vârfuri ale unui patrulater.
- G2 §3: tipurile 7, 8, 9, 10, 12, 13, 14, 26. Tipul 26 calculează proiecția
  unui mijloc pe bisectoare și nu demonstrează configurația originală mai grea
  a celor patru proiecții. Trisecția și intersecțiile folosesc configurații
  definite complet în enunț.
- G2 §4: tipurile 4, 7, 9, 16 sunt marcate parțial. Tipul 16 determină
  circumcentrul din rapoarte de distanțe egale cu 1; nu se inventează
  echivalența cu Van Aubel neprecizată în catalog. Celelalte tipuri folosesc
  de asemenea adaptări de calcul sau cazuri explicite, cu această limită
  menționată în metadate/explicație.

Pappus, Desargues, Pascal, Newton–Gauss și Van Aubel au configurații efective,
cu intersecții finite verificate exact, nu doar numele teoremei într-o întrebare.
Convenția Menelau este precizată: pentru X=U+t(V−U), raportul orientat
UX/XV=t/(1−t); produsul celor trei rapoarte ciclice este −1. Ceva pentru puncte
interioare folosește rapoarte pozitive și produs 1. Bisectoarele exterioare au
intersecții finite; triunghiul ortic folosește triunghiuri ascuțite, iar rapoartele
Euler exclud coincidența centrelor.

## Reproducere

Generatorul coordonator nu importă în baza de date și păstrează întrebările
existente în afara băncilor pe care le deține.

```powershell
.\.venv\Scripts\python.exe -X utf8 data/quizzes/generators/gen_clasa_9_g2.py
.\.venv\Scripts\python.exe -X utf8 scripts/verify_g2_pozitie_centre.py
.\.venv\Scripts\python.exe -X utf8 scripts/verify_g2_thales.py
.\.venv\Scripts\python.exe -X utf8 scripts/verify_g2_bisectoare.py
.\.venv\Scripts\python.exe -X utf8 scripts/verify_g2_menelau.py
node scripts/verify_g2_rendering.cjs
.\.venv\Scripts\python.exe -X utf8 manage.py check
```

Modulele de generare sunt `gen_clasa_9_g2_pozitie_centre.py`,
`gen_clasa_9_g2_thales.py`, `gen_clasa_9_g2_bisectoare.py`,
`gen_clasa_9_g2_menelau.py`. Auditurile nu importă generatoarele și recalculează
răspunsurile din datele geometrice. Sunt verificate toate cele **1700 de opțiuni**,
ponderile și domeniile, nedegenerarea, sisteme de intersecție, coliniaritatea,
paralelismul, distanțele și cercul celor nouă puncte. Concluziile și explicațiile
au și revizuire matematică; nu este un demonstrator automat general de geometrie.

## Rezultatul verificării și importului

Au trecut toate cele patru audituri independente, **4531 de fragmente KaTeX**
și `manage.py check`. Regenerarea celor cinci surse este identică octet cu octet.
Chei de răspuns corupte intenționat au fost respinse suplimentar de verificatoare.

Importul a fost tranzacțional și limitat la cele cinci fișiere `u06`. Importul
repetat păstrează toate cele 425 de ID-uri de întrebare și cele 1700 de opțiuni.
Lecțiile erau goale înainte de prima încărcare și nu aveau progres existent.
Întrebările, opțiunile și progresul tuturor celorlalte capitole au fost comparate
înainte și după import și sunt neschimbate.

Pagina capitolului și prima/ultima întrebare din fiecare lecție au fost randate
prin view-urile Django cu un utilizator autentificat, fără răspunsuri trimise sau
sesiuni de test persistate. În browser sunt confirmate totalurile 85/25/100/130/85
și afișarea grilei Pascal de la finalul lecției Menelau, fără erori JavaScript.
Serverul de dezvoltare a fost pornit pe portul 8000.

[Deschide capitolul local](http://127.0.0.1:8000/quizzes/clasa/9/coliniaritate-concurenta-paralelism/).
