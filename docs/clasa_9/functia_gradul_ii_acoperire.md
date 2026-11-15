# Funcția de gradul al II-lea — grile și audit

Rezultat la 30 octombrie 2026: **480 de grile originale**, importate în cele șapte
lecții existente ale capitolului `/quizzes/clasa/9/functia-gradul-doi/`.

| Lecție | Grile noi | Quiz ID | Tipuri de catalog folosite |
|---|---:|---:|---|
| Forma canonică, maximul și minimul | 60 | 203 | A4 §1: 1, 2, 4–9, 12–14, 24 |
| Simetrie și intersecții cu axele | 30 | 204 | A4 §1: 10, 19–23 |
| Reprezentare grafică și imagine | 30 | 205 | A4 §1: 3, 11, 15–18 |
| Relațiile lui Viète | 75 | 206 | A4 §2: 1–15 |
| Monotonie și semn | 155 | 207 | A4 §3: 1–9; §4: 1–22 |
| Dreaptă și parabolă | 75 | 208 | A4 §5: 1–15 |
| Sisteme cu ecuații de gradul al II-lea | 55 | 209 | A4 §6: 1–9; §2: 16–17 |
| **Total** | **480** | | **96 etichete de catalog × 5 variante** |

Sursa tipologică este `D:/Carti Mate/output/catalog/A4_catalog.md`, p. 129–149.
Enunțurile și datele sunt originale, nu transcrieri ale exercițiilor din culegere.
Cele șapte lecții erau goale în sursă și în baza locală înaintea importului.
Nu s-au schimbat manifestul, arhitectura, conturile, alte capitole sau schema DB.

## Ce este și ce nu este acoperit

Fiecare grilă are patru opțiuni distincte matematic, un răspuns corect și explicație.
Demonstrațiile și construcțiile sunt adaptate în calcule, concluzii sau identificări;
explicația arată metoda. Nu sunt adăugate exerciții interactive și nu se cere
trasarea efectivă a graficelor.

Metadatele `practice_scope` includ numele exact al tipului, secțiunea, paginile,
varianta, adaptarea și `coverage`. Valoarea `partial_case` este folosită pentru
cazurile simplificate sau particulare: A4 §1 tipurile 11, 15, 19; §2 tipurile 9,
10, 14; §3 tipurile 2, 8; §4 tipurile 8, 13, 17, 19; §5 tipurile 10, 12, 13;
§6 tipul 6. Restul au `adapted_grid`, ceea ce descrie formatul adaptat și nu
certifică echivalența dificultății cu o demonstrație deschisă.

Limite deosebit de importante:

- A4 §2 tipul 10 este simplificat la rădăcini în progresie aritmetică. Nu impune
  condiția mai puternică potrivit căreia a, x₁, b, x₂, c sunt toate în aceeași PA.
- Graficul standard și graficul pe ramuri sunt adaptate în identificarea vârfului
  și evaluări. Imaginea pe interval este verificată inclusiv la capete deschise.
- Discuțiile complete după un parametru includ aici și cazuri explicite de grad
  degenerat, fără a pretinde că aceste cazuri sunt întreaga discuție.
- Extremul pe interval mobil, modulul și minimele de funcții sunt adaptate în
  evaluări concrete; nu sunt toate ramurile unei funcții globale.
- Poziționarea rădăcinilor în interior/exterior are și grile de cardinal într-un
  interval explicit, fără toată clasificarea parametrizată din problema-sursă.
- Tangența la o curbă cu modul este cerută pe semidreapta x≥0, cu contact admis.
  Cazul trigonometric fixează unghiul; locul contactelor este explicat, iar grila
  cere o instanță numerică. Construirea unei familii de parabole cu două tangențe
  este restrânsă la o familie cu un coeficient necunoscut.

Prin urmare totalul de 96 de etichete folosite nu trebuie confundat cu acoperirea
integrală a dificultății și a tuturor cerințelor din catalog.

## Organizare și reproducere

- `data/quizzes/generators/gen_clasa_9_gradul_ii.py`: generator determinist, păstrează
  întrebările care nu aparțin propriei bănci `gradul_ii_a4_v1`.
- `data/quizzes/generators/quadratic_type_names.json`: denumirile celor 96 de tipuri.
- `scripts/verify_clasa_9_gradul_ii.py`: audit independent, fără importul generatorului.
- `scripts/verify_gradul_ii_rendering.cjs`: randare prin parserul și KaTeX locale.

```powershell
.\.venv\Scripts\python.exe data/quizzes/generators/gen_clasa_9_gradul_ii.py
.\.venv\Scripts\python.exe scripts/verify_clasa_9_gradul_ii.py
node scripts/verify_gradul_ii_rendering.cjs
.\.venv\Scripts\python.exe manage.py check
```

Generatorul nu importă date în Django. Pentru un import ulterior, utilizați
comanda existentă `manage.py seed_quizzes --file clasa_9/NUME_FISIER.json`, cu
fiecare dintre cele șapte fișiere u04; păstrați backupul și progresul existente.
Importul inițial a folosit direct `load_quiz_file` pentru a atinge exclusiv cele
șapte lecții, cu capitolul și ordinea lor existente.

## Verificare efectuată

Auditul a trecut **480 de grile și 1920 de opțiuni**. Cele 55 de operații de audit
recalculează răspunsurile din ecuații și condiții: sisteme liniare, vârf, imagine,
Viète, rădăcini transformate, semn, inecuații, monotonie, tangențe, sisteme și
intersecții. Parsarea metadatelor folosește un AST cu operații și constructori
matematici permiși, fără `eval`, fără parsare SymPy a unor șiruri de intrare și
fără a citi un câmp cu răspunsul așteptat. Opțiunile de audit sunt comparate cu
LaTeX-ul afișat și cu cheia de corectitudine, iar rezultatul din explicație este
verificat. Datele enunțurilor și argumentele au fost revizuite și manual; auditul
nu reprezintă înțelegerea automată a limbii naturale sau un demonstrator geometric.

Se disting rădăcinile reale de cele complexe, rădăcinile distincte de multiplicitate,
semnul strict de cel slab și capetele incluse/excluse. Sunt tratate gradul degenerat,
numitorii nuli, domeniul substituției x²≥0, radicalii principali și validarea
contactului pe ramura cu modul. Tangențele sunt obținute algebric prin discriminant;
derivatele sunt folosite numai în verificatorul independent pentru control.

Au trecut **4313 fragmente** prin randarea strictă KaTeX și `manage.py check`.
Generatorul a fost regenerat cu rezultat identic octet cu octet pentru toate cele
șapte fișiere. Importul a fost repetat
tranzacțional și a păstrat toate ID-urile întrebărilor și opțiunilor după primul
import. Nu existau întrebări/progres anterioare în aceste șapte lecții. Numărul
întrebărilor din celelalte capitole este neschimbat.

Pagina capitolului și prima/ultima întrebare din fiecare lecție au fost randate
prin view-urile Django, cu un utilizator existent, fără autentificare nouă,
trimitere de răspunsuri sau modificarea progresului. Acesta este un control al
template-urilor și payloadului, nu un test pe telefon fizic sau cu cititor de ecran.
