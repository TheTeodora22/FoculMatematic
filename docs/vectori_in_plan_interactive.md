# Vectori în plan — atelier interactiv

Stadiu actualizat la 30 octombrie 2026: **337 întrebări încărcate local: 325 grile noi și cele 12 interactive păstrate**. Totaluri pe lecții: 33, 28, 243 și 33. Atelierul SVG și verificarea exactă pe server sunt integrate în Antrenare. Conturile demo/admin sunt păstrate. Secțiunile de proiectare de mai jos sunt istoric; rezultatul extinderii și limitele adaptărilor sunt la final.

## Domeniul exact

Manifestul `data/quizzes/chapters.json` definește capitolul de clasa a IX-a `vectori-plan`, cu patru lecții:

| Lecție | Fișier în `data/quizzes/clasa_9/` | Stare inițială, înainte de implementare |
|---|---|---|
| Segmente orientate. Relația de echipolență | `clasa_9_u05_l01_segmente_orientate_relatia_de_echipolenta.json` | Gol |
| Vectorul de poziție al unui punct. Vectorul lui Thales | `clasa_9_u05_l02_vectorul_de_pozitie_al_unui_punct_vectorul_lui_thales.json` | Gol |
| Operații cu vectori în plan. Adunarea și înmulțirea cu scalari | `clasa_9_u05_l03_operatii_cu_vectori_in_plan_adunarea_si_inmultirea_cu_scalari.json` | Gol |
| Descompunerea unui vector după doi vectori necoliniari | `clasa_9_u05_l04_descompunerea_unui_vector_dupa_doi_vectori_necoliniari.json` | Gol |

Sursa principală este `D:/Carti Mate/output/catalog/G1_catalog.md`:

- §1, p. 162–163: 6 tipuri despre segmente orientate și echipolență.
- §2.1, p. 163–169: 28 tipuri despre suma și diferența vectorilor.
- §2.2, p. 170–175: 20 tipuri despre înmulțirea cu scalari.
- §3, p. 176: 6 tipuri despre descompunere după doi vectori necoliniari.

Propunerea inițială cuprindea doar cele 12 exemple interactive de mai jos. Extinderea ulterioară adaugă 300 de grile, câte cinci adaptări pentru fiecare dintre cele 60 de tipuri relevante, plus 25 originale despre vectori de poziție. Adaptările nu pretind întreaga dificultate a demonstrațiilor originale. Secțiunea G1 §4 despre reper cartezian nu este adăugată automat: capitolul curent din manifest nu o listează separat.

Titlul lecției 2 nu are o secțiune omonimă distinctă în G1. G2 începe cu „Vectorul de poziție al unui punct în plan”, dar aparține capitolului următor din aplicație; nu importăm toate tipurile G2 aici. Pentru lecția 2 propunem doar fundamentul originii/vectorului de poziție și identitatea mijlocului. Denumirea „Vectorul lui Thales” și asocierea exactă la paginile sursă trebuie confirmate înainte de a atribui acea tipologie unui exercițiu. Nu o confundăm automat cu teorema lui Thales.

## De ce nu folosim direct motorul geometric existent

`geometry_canvas` are funcții utile pentru SVG, puncte deplasabile, selecție, suport tactil și tastatură. Dar motorul actual nu reprezintă și nu validează operații vectoriale:

- `geometryEmbeddedShape` știe linie/semidreaptă/segment și relații de drepte, nu un vector finit etichetat cu origine și vârf.
- `geometryPointCanvas` păstrează poziții în coordonate de ecran, într-o suprafață de 440×180, și limitează deplasarea; nu definește un reper matematic sau o bază oblică.
- `submit_geometry_canvas_answer` validează unele configurații față de ținte în pixeli, implicit cu toleranță de 38. Aceasta nu demonstrează egalitatea vectorilor: aceeași deplasare poate fi realizată oriunde, iar vârful greșit, apropiat vizual, poate fi acceptat.
- `construct_figure` verifică instrumentul și punctele selectate, nu ecuația CD=AB. Semidreapta nu este un substitut corect pentru segmentul orientat.
- `seed_loader` are o listă de moduri admise; un mod vectorial nou nu poate fi activat numai printr-un JSON.

Folosirea unui formular algebric doar pentru a introduce coordonate ar produce completări, nu atelierul vizual cerut. Recomandarea este un tip dedicat **`vector_workbench`**, păstrând ideile bune de accesibilitate ale atelierului geometric și un validator vectorial exact pe server.

## Primul lot propus: 12 exerciții

Coordonatele sunt în unități matematice; originea ecranului și pixeli/unitate sunt detalii de afișare. Unde lecția nu predă coordonate explicit, rețeaua poate fi descrisă ca deplasări de pătrățele.

| ID / lecție | Interacțiune și cerință | Rezultat verificat | Metodă / scop |
|---|---|---|---|
| V01 / 1 | Selectează toate segmentele echipolente cu AB, A(0,0), B(3,2); candidați CD, DC, EF, C(−2,1), D(1,3), E(4,4), F(1,2). | Numai CD | Aceeași deplasare (3,2); sensul opus este exclus. G1 §1 tip 3. |
| V02 / 1 | Clasifică EF față de AB în configurația V01. | Vectori opuși | EF=(−3,−2); distingem opoziția de egalitate. G1 §1 tip 5. |
| V03 / 1 | Mută D astfel încât CD=AB, A(1,1), B(4,3), C(−2,0). | D(1,2) | D=C+(B−A). G1 §1 tip 6. |
| V04 / 2 | Alege originea O(1,−2), apoi construiește săgeata spre A(4,3). | OA=(3,5) | Vector de poziție relativ la o origine precizată. Asociere exactă la catalog încă de confirmat. |
| V05 / 2 | Mută originea de la O(1,−2) la P(−1,1), fără să muți A(4,3). | PA=(5,2) | PA=OA−OP. Asociere exactă la catalog încă de confirmat. |
| V06 / 2 | Plasează mijlocul M al lui AB, A(0,0), B(6,4). Compară OM cu (OA+OB)/2. | M(3,2) | Identitatea mijlocului; G1 §2.2 tip 1. |
| V07 / 3 | Transportă v=(−1,2) la vârful lui u=(3,1), apoi trasează rezultanta. | u+v=(2,3) | Regula triunghiului, G1 §2.1 tip 1. |
| V08 / 3 | Construiește −2u pentru u=(3,1). | (−6,−2) | Sens opus și lungime dublă; G1 §2.2 tip 4. |
| V09 / 3 | Închide poligonul cu u=(2,1), v=(−1,3), alegând w. | w=(−1,−4) | u+v+w=0; G1 §2.1 tip 16. |
| V10 / 4 | Ajustează coeficienții a,b pentru u=(2,0), v=(1,2), w=(5,6). | a=1, b=3 | Pregătire pentru descompunere; bază oblică, nu presupunem proiecții ortogonale. |
| V11 / 4 | Descompune mediana AM după AB=(4,0), AC=(0,6). | a=b=1/2; AM=(2,3) | Identitatea medianei; G1 §3 tip 1. |
| V12 / 4 | În pătratul A(0,0), B(6,0), C(6,6), D(0,6), M mijlocul BC, N mijlocul CD. Descompune AB după AM,AN. | AB=(4/3)AM−(2/3)AN | Sistem în baza oblică; G1 §3 tip 4. |

Datele exacte sunt în [exemplele de proiectare](vectori_in_plan_interactive.examples.json). Fișierul este marcat `design_only_not_importable`, în `docs/`, și nu respectă intenționat formatul unui quiz live. Soluțiile din el sunt pentru verificare/proiectare, nu date trimise viitorului elev.

## Cum ar arăta exercițiile

1. **Echipolență:** săgeți finite și etichete de origine/vârf; selecție prin clic/atingere sau Tab+Spațiu. Feedback după verificare: „Lungimea este aceeași, dar sensul este opus”, nu doar roșu/verde.
2. **Transport:** un vector de referință fix și o copie transportabilă; elevul mută copia păstrând componentele. Pentru V03, D se poate muta separat, dar verificarea compară D−C cu B−A.
3. **Adunare:** mod triunghi și, ulterior, paralelogram. Săgeata rezultantă nu se dezvăluie înainte de răspuns. Transportul trebuie validat dacă cerința îl solicită, nu doar poziția finală a rezultantei.
4. **Scalar:** câmp numeric exact și slider auxiliar cu pas explicit; scalar negativ inversează sensul, 0 afișează vectorul nul ca punct etichetat, fără direcție fictivă. V08 cere construcția finală, nu doar glisarea cursorului la un răspuns afișat în enunț.
5. **Descompunere:** doi vectori de bază vizibili, două componente etichetate și o sumă construită în direct. Câmpurile acceptă fracții exacte pentru V11–V12; sliderul este opțional, nu singura cale de a introduce 4/3.

## Contract matematic și accesibilitate

- Coordonatele/pasul rețelei sunt întregi sau fracții raționale. Serverul convertește la fracții exacte și respinge NaN, infinit, booleeni și componente lipsă.
- Pentru egalitate: B−A=D−C. Pentru opoziție: B−A=−(D−C). Pentru vectori nenuli coliniari: determinantul este zero. Vectorii nuli sunt tratați separat; nu li se cere „același sens”.
- Pentru au+bv=w: determinantul bazei trebuie să fie nenul; coeficienții trebuie verificați prin recombinare. Configurațiile degenerative sunt respinse la import.
- Punctele se fixează pe rețeaua matematică. O toleranță în pixeli poate decide doar ce nod a ales elevul, înainte de validare; nu înlocuiește egalitatea matematică pe server. Zoomul și dimensiunea ecranului nu schimbă răspunsul corect.
- O construcție cu mai multe poziții corecte se validează prin proprietate, nu prin compararea cu un singur desen țintă. Originea unui vector liber poate varia.
- Fiecare punct/vector/câmp are nume accesibil, descriere și stare; coordonatele sau deplasările au alternativă textuală. Direcția, sensul și numele nu sunt codificate numai prin culoare.
- Tab schimbă obiectul; săgețile mută obiectul selectat cu o unitate de rețea, Shift+săgeți cu un pas mai mare; Enter/Spațiu selectează sau confirmă, Escape anulează manipularea. Aceste taste trebuie să blocheze navigarea globală anterior/următor numai în atelier/câmpuri, fără să o elimine în restul paginii.
- Pentru telefon: ținte tactile de minimum 44×44 în desen, butoane deplasare pentru alternativa la drag, posibilitatea introducerii coordonatelor și adaptare fără scroll orizontal al întregii pagini.
- Modificarea desenului păstrează focusul. Mesajele de stare nu anunță fiecare pixel al glisării; se anunță valoarea stabilizată. Verificarea și erorile folosesc regiuni live persistente.
- Salvarea urmează noua regulă comună: progres confirmat numai după server; cererile întârziate se aplică întrebării originale, iar o eroare permite reîncercarea fără pierderea construcției.
- Payloadul public conține configurația inițială și cerința, nu `expected`, cheia `answers` sau rezultanta finală ascunsă. Soluțiile rămân în datele serverului.

## Implementare propusă în pași

1. Agreăm acest lot și clarificăm nomenclatura lecției 2; nu este nevoie să mutăm capitolele existente.
2. Adăugăm `vector_workbench` în model, migrare, validator de import, payload fără soluții și verificator server pentru cele șapte familii fundamentale: selecție/echipolență, clasificare, transport, poziție/mijloc, sumă/închidere, scalar și descompunere.
3. Extindem atelierul SVG cu un strat matematic separat de pixeli; săgeți finite, origine/vârf, reper opțional și bază oblică. Acest pas necesită coordonare cu agentul frontend care deține `training.js` și CSS-ul comun.
4. Implementăm întâi V01/V03/V07/V08; apoi V10/V11 cu fracții și bază oblică. V04–V06 și V12 urmează după clarificarea mapării și verificarea didactică.
5. Teste unitare pentru toate exemplele și cazurile limită; teste de respingere pentru răspuns greșit/chei suplimentare/alt utilizator; teste de accesibilitate, tastatură și touch; apoi import țintit al lotului, fără schimbarea progresului existent.

Fișiere identificate în planul inițial: `quizzes/models.py` + migrare, `quizzes/seed_loader.py`, `quizzes/mode_services.py`, rutarea de submit/payload din `quizzes/views.py`, `static/core/js/training.js` sau un modul dedicat încărcat de acesta și CSS-ul atelierului. Backendul din această listă este acum implementat; frontendul este coordonat separat.

## Verificare realizată și limite

Comandă din directorul backend:

```powershell
.\.venv\Scripts\python.exe scripts/verify_vectori_interactive_design.py
```

Verificatorul recalculează exact deplasările, translațiile, mijlocul, sumele, scalarul, închiderea și coeficienții de bază cu fracții; verifică și scalarul 0, fracții negative, vector nul și bază coliniară. Nu încarcă Django, nu scrie în baza de date și nu susține că interacțiunile sunt implementate/testate în browser.

Nu există încă o acoperire integrală a celor 60 de tipuri G1 relevante; nu au fost create grile de umplutură doar pentru a mări numărul. Acesta este un punct de pornire verificat pentru atelierul vizual solicitat.

## Implementare backend — rezultat 30.10.2026

- `quizzes/vector_workbench.py`: calcul exact din datele problemei, validare strictă a configurației și răspunsului, fără încredere într-un rezultat transmis de browser.
- `quizzes/models.py` și migrarea `0038_vector_workbench`: tipul de întrebare înregistrat.
- `quizzes/seed_loader.py`: respinge modurile/configurațiile nevalide și chei de soluție injectate în datele publice.
- `quizzes/mode_services.py` și `quizzes/views.py`: ruta existentă `training_submit`, `values` JSON; progresul aparține exclusiv utilizatorului autentificat.
- Payloadul public ascunde explicația înainte de răspunsul corect. `solvedValues` apare numai pentru starea corectă salvată, astfel încât reîncărcarea să poată afișa construcția confirmată; pentru fracții sunt trimise șiruri exacte `a/b`.
- `data/quizzes/generators/gen_clasa_9_vectori_interactive.py`: reproduce cele 12 exemple, păstrează textul și ID-urile de atelier V01–V12 și nu înlocuiește alte exerciții din fișiere.

**Verificări trecute:** 16 teste Django dedicate (`manage.py test quizzes.test_vector_workbench`), toate cele 12 exemple recalculate independent inclusiv datele generate, `manage.py check`, `makemigrations --check --dry-run` și verificarea diferențelor. Testele includ răspuns corect/greșit, transportul cozii la adunare, fracții și notație românească, scalar nul, bază coliniară, valori nefinite/prea lungi, chei falsificate, autentificare, alt utilizator/alt subiect, încărcare fără soluție și reîncărcare după rezolvare, precum și import repetat pe bază de test fără pierderea progresului.

Comenzi:

```powershell
.\.venv\Scripts\python.exe data/quizzes/generators/gen_clasa_9_vectori_interactive.py
.\.venv\Scripts\python.exe scripts/verify_vectori_interactive_design.py
.\.venv\Scripts\python.exe manage.py test quizzes.test_vector_workbench
```

Au trecut suplimentar cele 34 de teste existente `TrainingTests` și `SeedQuizzesTests`: **50 de teste backend trecute** în total.

Migrarea a fost aplicată local, iar cele patru lecții au fost importate țintit de două ori: ID **210** (V01–V03), **211** (V04–V06), **212** (V07–V09), **213** (V10–V12), câte trei întrebări fiecare. Verificarea importului repetat a confirmat păstrarea ID-urilor, textelor, ordinii, configurațiilor și progresului existent pentru întrebările vizate. Serverul comun nu a fost repornit de acest agent; coordonatorul gestionează integrarea și repornirea.

Aceste rezultate nu certifică utilizarea reală cu NVDA, VoiceOver, iPhone sau Android.

## Integrare și verificare în browser — 30.10.2026

- Frontend dedicat în `static/core/js/vector-workbench.js` și `vector-workbench.css`: selectare, puncte deplasabile, transport, scalar, închidere și descompunere în bază oblică. Permite mouse/touch, tastatură și câmpuri cu fracții exacte.
- Corecția vizuală cerută de utilizator: capete de săgeată compacte, colorate, independente de grosimea liniilor; puncte mai mici, etichete cu evitare a suprapunerilor și încadrare adaptată datelor. Descompunerea inițială nu mai repetă trei etichete pentru vectorul nul.
- Redimensionarea recalculează etichetele, capetele și zonele de atingere, inclusiv pentru construcțiile deja rezolvate. Nu schimbă răspunsul și nu trimite cereri de salvare.
- **40 teste JavaScript trecute:** 18 vectoriale și 22 regresii pentru Antrenare. Comandă: `node --test scripts/test_vector_workbench.cjs scripts/test_training_p0.cjs scripts/test_training_accessibility.cjs scripts/test_training_boot.cjs scripts/test_training_geometry_keyboard.cjs`.
- Coordonatorul a parcurs în browser toate cele 12 exemple într-o bază SQLite separată de baza de lucru: răspuns corect, răspuns greșit la echipolență, transport incorect respins chiar cu rezultantă corectă, construcție din tastatură, minus Unicode, virgulă zecimală și fracții. Reîncărcarea a păstrat selecția și coeficienții corecți, dezactivând editarea.
- Desenul a fost inspectat vizual pentru echipolență și descompunerea cu coeficienți 4/3 și −2/3; s-a verificat și schimbarea 390 px → lățimea normală fără reîncărcare, pentru a elimina etichetele rămase supradimensionate după redimensionare. Aceasta este o emulare de lățime, nu un test pe telefon fizic.
- Serverul local principal a fost pornit cu integrarea actualizată. Lecțiile disponibile: `/quizzes/subiect/210/antrenare/0/`, respectiv 211, 212 și 213.

La încheierea etapei interactive lotul era introductiv: 12 interactive. Nu s-a inventat o asociere de catalog pentru „Vectorul lui Thales”.

## Extindere cu grile — 30 octombrie 2026

| Lecție | Grile noi | Interactive păstrate | Total | Quiz ID |
|---|---:|---:|---:|---:|
| Segmente orientate și echipolență | 30 | 3 | 33 | 210 |
| Vectorul de poziție | 25 | 3 | 28 | 211 |
| Operații cu vectori | 240 | 3 | 243 | 212 |
| Descompunerea unui vector | 30 | 3 | 33 | 213 |
| **Total** | **325** | **12** | **337** | |

Toate grilele au patru opțiuni distincte, un singur răspuns corect și explicație.
Metadatele `practice_scope` indică familia, varianta și adaptarea, iar `verification`
conține datele pentru audit; nu sunt adăugate în payloadul public al Antrenării.
Cele 25 de grile originale de poziție rămân fără atribuire de catalog fictivă.
Lecția de operații are dificultatea Greu, în acord cu raționamentele incluse.

**Limite didactice:** grilele de demonstrație cer o concluzie, un coeficient sau
calculul într-o configurație explicită; argumentul este în explicație. În special,
G1 §2.1 tip27 este un caz simetric de vectori unitari în semiplan, nu demonstrația
estimării generale; §2.2 tip16 este un caz de aliniere pe prelungirea unei drepte,
nu întreaga configurație de ceviene. Tipurile de construcție nu cer un desen nou
interactiv. Numărătoarea reprezintă 60 de etichete de catalog adaptate, nu o
certificare a acoperirii integrale a dificultății tuturor problemelor originale.

Generatorul coordonator este `data/quizzes/generators/gen_clasa_9_vectori_grile.py`.
Acesta apelează modulele `gen_clasa_9_vectori_segmente_baze.py`,
`gen_clasa_9_vectori_pozitie.py` și `gen_clasa_9_vectori_operatii.py`.
Regenerarea păstrează obiectele interactive și nu scrie în baza de date.

```powershell
.\.venv\Scripts\python.exe data/quizzes/generators/gen_clasa_9_vectori_grile.py
.\.venv\Scripts\python.exe scripts/verify_vectori_segmente_baze.py
.\.venv\Scripts\python.exe scripts/verify_vectori_pozitie.py
.\.venv\Scripts\python.exe scripts/verify_vectori_operatii.py
.\.venv\Scripts\python.exe scripts/verify_vectori_interactive_design.py
node scripts/verify_vectori_rendering.cjs
```

Auditurile sunt independente de generatoare. Au trecut toate cele 325 de grile:
enumerări de direcții și reprezentanți, sisteme în baze oblice, rapoarte și ecuații
afine, coarde, hexagon regulat, intersecția diagonalelor și secțiunea trapezului,
fracții exacte și degenerări. Concluziile teoremelor sunt revizuite cu ipotezele
lor; auditul nu este un demonstrator automat de geometrie euclidiană.
**2463 de fragmente matematice** au trecut randarea KaTeX strictă.

Importul a fost făcut numai pentru cele patru fișiere, tranzacțional, și repetat
pentru verificarea idempotentei. ID-urile celor 12 întrebări interactive, ordinea,
configurațiile și explicațiile sunt neschimbate; nu existau înregistrări de progres
pentru aceste întrebări în baza locală la import. Numerele 33/28/243/33 sunt
confirmate pe pagina capitolului. Prima grilă nouă de operații este verificată în
browser fără trimiterea unui răspuns pe contul utilizatorului.
