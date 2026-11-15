# Revizuire vizuală frontend — 31 octombrie 2026

Intervenție pe interfața Django existentă, cu păstrarea identității cromatice,
a conținutului, a datelor și a logicii de exerciții. Coordonatorul verifică
separat paginile în browser; acest raport descrie implementarea și testele locale.

## Probleme concrete și remedieri

- **Header prea lat pe mobil.** Dimensiunile rigide ale logo-ului, gap-ul de
  2.5rem și marginile navigării depășeau viewportul de 390px și pe paginile
  de profil/antrenare. Headerul are clase explicite, logo flexibil, gap și
  margini controlate. Navigarea completă începe de la 1281px, iar pragul
  de închidere automată a meniului mobil este sincronizat în JavaScript.
- **Acasă: ierarhie și CTA.** Titlul dimensionat în vw, textul de 2vw și
  spațierea verticală mare împingeau CTA-urile sub primul ecran. Hero-ul
  folosește un grid adaptabil, tipografie fluidă limitată, spațiere coerentă
  și linkuri reale pentru navigare. S-a eliminat structura invalidă
  `button > a` și glow-ul continuu al CTA-urilor.
- **Meniu mobil cu interacțiuni incomplete.** Linkurile `#` în elemente
  `li onclick` au fost înlocuite cu butoane semantice. Dialogul nativ
  gestionează fundalul inert, focusul și Escape; închiderea restaurează
  scrollul anterior și starea `aria-expanded`. Grupurile pliate sunt
  `inert` și `aria-hidden`, astfel încât linkurile ascunse nu primesc focus.
- **Contrast și focus.** Headerul și butoanele folosesc text deschis pe
  roșu închis, submeniurile au hover lizibil, iar textul secundar are
  contrast îmbunătățit. Controalele comune au focus vizibil, există un
  link de sărire la conținut, iar butoanele principale au cel puțin 44px
  înălțime. Exemple calculate de contrast: text `#fff1e8` pe `#b84021`
  5.01:1, text secundar `#c1b5ac` pe `#352f36` 6.50:1 și bordura
  secundară `#b39aab` pe `#403641` 4.46:1.
- **Carduri și Antrenare.** Spațierea, bordurile și umbrele sunt consecvente;
  răspunsul selectat și focusul radio sunt mai clare. Săgețile desktop
  au ținte de 44px, iar grila de întrebări are celule de 30px (32px pe mobil)
  cu spațiu de 6px. Nu se schimbă stările sau salvarea progresului.
- **Profil.** Umbra moale cerută anterior este păstrată explicit; avatarul
  nu mai are haloul puternic, iar textul de pe gradient are contrast mai bun.
- **Mișcare redusă.** Pentru `prefers-reduced-motion`, hero-ul servește o
  imagine statică existentă în locul GIF-ului, iar tranzițiile și animațiile
  decorative vizate sunt oprite. GIF-ul rămâne pentru preferința standard.

## Fișiere

- `templates/base.html`: clasele headerului, dialogul și controalele mobile,
  skip link, stylesheet și versiuni de cache.
- `templates/index.html`: hero semantic, CTA-uri link și imagine adaptată
  preferinței de mișcare.
- `static/core/css/frontend-polish.css`: variabile comune și reguli vizuale
  limitate la componente, fără reguli globale pe KaTeX sau SVG.
- `static/core/css/fm-app.css`: pragurile de navigare sincronizate și două
  valori de culoare comune conectate la variabile; modificările altora păstrate.
- `static/core/js/FMJava.js`: ciclul dialogului și stările accordionului.
- `scripts/test_navigation.cjs`: teste ale handlerelor reale de navigare.

## Verificări locale și limite

`manage.py check`, `node --check static/core/js/FMJava.js` și diferențele de
whitespace au trecut. Cele 46 de teste JavaScript au trecut: șase de navigare
și 40 de regresii pentru salvare, accesibilitate, boot, tastatură și atelierul
de vectori. Testele nav acoperă deschidere/închidere, refacerea scrollului și
focusului, plierea grupurilor, navigarea prin link, resize desktop, backdrop și
izolarea tastelor față de scurtăturile din Antrenare. Comportamentul nativ al
focusului și Escape au fost verificate în browser de coordonator;
nu sunt deduse numai din mock-ul testului Node.

Cele 26 de teste Django `NavigationTests` și `TrainingTests` au trecut pe baza
de test separată. Versiunile de cache pentru toate cele trei resurse modificate
sunt actualizate în `base.html`, inclusiv `fm-app.css`; coordonatorul a detectat
că URL-ul vechi servea în browser pragul anterior de navigare.

## QA în browser — coordonator

- Paginile Acasă, clasa a IX-a, profil și Antrenare au fost inspectate vizual
  în browserul integrat, la dimensiuni de mobil și desktop.
- La viewport 390 px, lățimea utilă este 375 px din cauza scrollbarului. Înainte,
  headerul împingea documentul la 404 px; după corecție, scrollWidth=clientWidth=375 px
  pe liste, profil și Antrenare. La 320 px, Acasă are 305 px utili și 305 px scrollWidth.
- La 1366 px, navigarea completă este vizibilă și încape: marginea din dreapta
  a logo-ului este 403.55 px, începutul navigării 552.31 px, finalul 1283.45 px,
  în lățimea utilă 1351 px. Nu există suprapunere între logo și linkuri.
- Meniul mobil se deschide cu focus pe închidere; accordionul Clase expune
  linkurile, navigarea către o clasă funcționează, Escape închide dialogul și
  focusul revine la butonul de deschidere. Starea aria-expanded revine la false.
- Pe desktop, Tab de pe Clase expune submeniul și mută focusul pe Clasa a 5-a;
  linkul către clasa a IX-a a fost urmat cu succes.
- În Antrenare, ArrowRight în dialog a păstrat întrebarea 3; după Escape,
  aceeași tastă în afara dialogului a trecut normal la întrebarea 4. Nu s-a
  trimis niciun răspuns și nu s-a scris progres de test.
- Atelierul vectorial se redimensionează și rămâne vizibil. Profilul păstrează
  exact cele două straturi ale umbrei moi: 0/12/48/−14 la opacitate 0,20 și
  0/4/20/−8 la opacitate 0,12. Nu s-au modificat calculele sau marcajele SVG.
- Nu au fost observate erori JavaScript în paginile verificate. Viewportul
  temporar este resetat după testare. Preferința reduced-motion este implementată
  în CSS/picture; nu s-a schimbat preferința globală a sistemului utilizatorului.

QA a identificat și resurse vechi păstrate în cache; versiunile finale sunt
`foundations-3`, `visual-3`, `dialog-3`. Instanțele locale vechi de dezvoltare
au fost oprite, iar verificarea finală s-a făcut cu o singură instanță pe 8000.

Nu este o certificare WCAG completă, un audit cu cititor de ecran sau un test
pe toate dispozitivele fizice. Checklistul de lansare nu a fost bifat ca verificat
în producție. Nu s-au modificat backendul, schema DB, conturile, matematica,
progresul sau regulile interne ale desenelor geometrice.
