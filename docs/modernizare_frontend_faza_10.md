# Modernizare frontend — faza 10: performanță

Implementată și verificată local la 1 noiembrie 2026. Faza 11 nu este începută.

## Rezultate verificabile

| Resursă | Înainte | După | Schimbare |
| --- | ---: | ---: | --- |
| Animație Acasă | GIF 1.739.930 B | WebM 162.381 B | −90,7% |
| `fm-app.css`, pe toate paginile | 134.357 B | 42.913 B | −68,1% |
| Stiluri specifice exercițiilor | în fișierul comun | 91.337 B, doar la Antrenare | încărcare condiționată |
| KaTeX + renderer și CSS matematic | 310.292 B pe toate paginile | doar în teste, rezultate, Antrenare și laborator | eliminate de pe Acasă, catalog, cont/profil |

Dimensiunile sunt ale fișierelor necomprimate, nu transferuri măsurate în
producție. Împreună, resursele optimizate de pe Acasă economisesc aproximativ
1,98 MB înainte de compresie/cache, ținând cont și de creșterea mică a
controlului animației. Biblioteca matematică rămâne disponibilă pe toate cele
șase șabloane care afișează formule.

## Implementare

- Animația originală este transcodificată local cu FFmpeg în VP9/WebM, fără
  biblioteci noi în aplicație. Fișierul GIF original este păstrat în proiect.
  Elementul video are dimensiuni explicite, poster static, `preload="none"`,
  `muted`, `loop` și `playsinline`. Sursa video este setată numai când animația
  trebuie pornită. Mișcarea redusă nu solicită fișierul video până la o alegere
  explicită. Pauza păstrează cadrul curent; refuzul redării automate revine
  la o comandă de pornire, fără promisiuni respinse netratate.
- CSS-ul exercițiilor este separat la limita secțiunii dedicate, fără ștergerea
  selectorilor folosiți dinamic. Noul fișier este inserat în aceeași poziție a
  cascadei, înaintea ajustărilor vizuale comune. Clasele mutate nu sunt folosite
  în celelalte șabloane HTML verificate.
- Fontul Montserrat este declarat direct în antet, cu `preconnect` pentru
  Google Fonts și domeniul fișierelor. S-a eliminat `@import` din CSS; se
  păstrează familia, greutățile și `display=swap`, inclusiv diacriticele.
- Logo-urile comune au dimensiunile intrinseci 706 × 72. Imaginea din subsol
  folosește încărcare lazy; logo-ul vizibil din antet rămâne încărcat normal.
  Fișierele logo sunt mici și nu au primit variante suplimentare inutile.
- Rendererul matematic nu mai rescanează toate formulele la orice modificare
  a containerului. Acum grupează într-un cadru doar rădăcinile matematice
  adăugate/modificate. Modificarea unui slider, a unui mesaj sau a graficului
  fără formule nu programează o randare matematică. Actualizarea întrebărilor
  și stratul MathML continuă să funcționeze.
- Saltul de la conținutul inițial la formularul interactiv putea muta subsolul
  și introduce bara de derulare după primul layout. Pagina de Antrenare
  rezervă cel puțin înălțimea viewportului minus antet; `scrollbar-gutter:
  stable` evită și deplasarea orizontală provocată de scrollbar.
- Nu s-au introdus frameworkuri sau biblioteci pentru efecte. Scripturile mari
  de Antrenare rămân limitate la acea pagină; JSXGraph rămâne în laborator.

## Măsurători locale și limite

Un instrument opțional, activat prin `?frontend_perf=1`, colectează în memorie
LCP, CLS cu ferestre de sesiune, evenimente lente, long tasks și Resource Timing.
Publică datele într-un nod JSON din antet (`frontend-performance`), fără
transmitere în rețea, stocare persistentă sau interfață pentru utilizator.
Pe paginile normale acest script nu se încarcă. Antrenarea normalizează URL-ul
prin comportamentul existent; instrumentul rămâne activ pentru navigarea
inițială care a primit parametrul.

| Probă desktop, 1366 × 900 | Inițial | Final |
| --- | ---: | ---: |
| Acasă: LCP local | 432 ms | 264 ms |
| Acasă: CLS observat | 0,0262 | 0 |
| Antrenare statistică: LCP local | 316 ms | 708 ms |
| Antrenare statistică: CLS observat | 0,0094 | 0 |
| Durata maximă observată a interacțiunilor, șase săgeți pe slider | 32 ms | 48 ms |

Acestea sunt eșantioane individuale pe serverul Django de dezvoltare, cu cache
mixt și fără limitare controlată de CPU/rețea. Nu demonstrează o îmbunătățire
generală a timpilor: în eșantionul final încărcarea antrenării a fost mai lentă.
Durata maximă a evenimentelor nu este metrica INP de teren. Intrările cu zero
octeți pot proveni din cache/revalidare sau restricțiile Resource Timing;
dimensiunile din primul tabel au fost verificate separat pe disc.

În timpul investigației a fost observat și un CLS de aproximativ 0,74 la
inițializarea formularului. Datele intermediare sunt păstrate în registrul de
după modificări; corecția spațiului rezervat a eliminat deplasarea în proba
finală. Nu se pretinde un scor Lighthouse sau o validare Core Web Vitals în
producție. Pentru acea concluzie sunt necesare rulări repetate cu cache rece,
profil mobil controlat și măsurători ale utilizatorilor reali.

Registre: [înainte](performance_phase10_before.json),
[după și investigație](performance_phase10_after.json),
[pagini și resurse condiționate](performance_phase10_pages.json).

## Verificare funcțională

- **94 teste JavaScript trecute**, inclusiv cinci teste noi pentru bugetele
  resurselor, redarea/pauza și eșecul video, plus observatorul matematic.
- **57 teste Django trecute** pentru Antrenare, navigare, formulare,
  accesibilitate, stări UI, analitice și laborator.
- 14 verificări de pagină la 320 și 1366 px: Acasă, profil, catalog,
  statistică, tabel de divizibilitate, vectori și laborator. Fără overflow
  orizontal al documentului; CSS-ul exercițiilor apare doar în Antrenare,
  iar biblioteca matematică doar unde este necesară.
- Formulele se afișează și după schimbarea întrebării: probă la vectori,
  șapte elemente KaTeX în noua întrebare. Sliderul păstrează focusul și
  răspunde la șase săgeți consecutive. WebM redă efectiv și Space îl oprește.
- `manage.py check`, verificările de sintaxă și `git diff --check` fără erori.

![Animația optimizată, oprită din tastatură](screenshots/faza-10-acasa-webm.png)

## Referințe

- [web.dev: optimizarea încărcării fonturilor](https://web.dev/articles/optimize-webfont-loading).
- [MDN: datele Performance API](https://developer.mozilla.org/en-US/docs/Web/API/Performance_API/Performance_data).
- [MDN: LargestContentfulPaint](https://developer.mozilla.org/en-US/docs/Web/API/LargestContentfulPaint).

Compresia HTTP, politica de cache a fișierelor statice și măsurarea de teren
trebuie verificate pe infrastructura de lansare. Nu s-au modificat serverul
de producție, autentificarea, punctajele, datele întrebărilor sau schema bazei.
