# Modernizare frontend — faza 4: sistemul de mișcare

Implementată la 31 octombrie 2026, conform direcției de animație moderată.

## Contractul comun

`static/core/css/motion.css` definește:

| Token | Valoare normală | Scop |
| --- | --- | --- |
| --fm-duration-fast | 150 ms | Hover, culori, apăsare |
| --fm-duration-standard | 220 ms | Schimbări de stare și accordion |
| --fm-duration-enter | 280 ms | Intrări de panou |
| --fm-duration-exit | 220 ms | Ieșiri de panou |
| --fm-duration-progress | 350 ms | Actualizarea progresului existent |
| --fm-ease-standard | cubic-bezier(.2,0,0,1) | Interacțiuni |
| --fm-ease-enter | cubic-bezier(.22,1,.36,1) | Intrări |
| --fm-ease-exit | cubic-bezier(.4,0,1,1) | Ieșiri |

Utilitare disponibile: `fm-motion-fade-in`, `fm-motion-rise-in`,
`fm-motion-scale-in` și `fm-motion-hover-lift`. Intrările sunt scurte și
nu depind de JavaScript pentru a face conținutul vizibil. Ridicarea este
limitată la linkuri/butoane, mouse și dispozitive cu hover; nu se aplică
automat cardurilor informative. Nu se aplică utilitarele pe nodurile
KaTeX sau pe elementele din desenele matematice.

În acest lot, fade-in este aplicat mesajelor Django deja existente.
Celelalte utilitare sunt disponibile pentru intervențiile pe componente,
fără introducerea automată a efectelor pe toate paginile.

## Aplicări și corecții

- Meniul lateral: intrare 280 ms, ieșire 220 ms, transformare orizontală.
- Backdrop: opacitate în loc de animarea culorii de fundal.
- Butoane: culori, borduri, umbră și apăsare cu durată comună de 150 ms.
- Dropdownuri, indicatoare de accordion și linkuri comune: durate/easing din tokenuri.
- Progres XP și progres de învățare: durată comună de 350 ms.
- Cele trei `transition: all` din CSS-ul vechi de navigare au fost înlocuite
  cu proprietăți explicite.
- Închiderea meniului citește durata efectivă a animației din CSS.
  Timerul de rezervă folosește durata respectivă plus o marjă de 64 ms.
  Nu mai depinde de o copie numerică a duratei din CSS.
- `animationend` și `animationcancel` finalizează închiderea; lipsa animației
  sau durata zero duc la închidere imediată.
- Focusul și scrollul se refac numai la închiderea dialogului; fundalul
  rămâne inert pe durata ieșirii.
- Pictograma de închidere este deschisă la culoare pe fundalul întunecat.
  S-a eliminat regula veche pentru primul element al listei care îi anula
  filtrul; burgerul din antet rămâne negru, conform preferinței utilizatorului.

Nu s-au introdus biblioteci de animație, observatori de scroll, întârzieri
ale navigării sau tranziții globale de pagină. Accordionul și barele de
progres păstrează proprietățile existente max-height/width pentru a menține
compatibilitatea cu logica lor; nu pretindem că toate animațiile sunt exclusiv
transform/opacity sau că performanța a fost măsurată în profiler.

## Mișcare redusă

- Tokenurile de durată devin 0 ms, iar deplasările devin zero.
- Utilitarele de intrare și animațiile dialogului sunt dezactivate.
- Ieșirea dialogului este imediată când matchMedia raportează reduce.
- Tranzițiile decorative ale unor controale matematice sunt oprite și ele
  în regula redusă, fără modificarea calculelor sau a stării exercițiului.
- Alternativa statică a GIF-ului de pe Acasă rămâne păstrată.

Ramura JavaScript pentru reduce este acoperită automat. Regulile CSS pentru
reduce au fost confirmate în CSSOM-ul browserului. Browserul de test a avut
preferința normală; nu a fost schimbată preferința globală a utilizatorului
și nu se declară făcut un test vizual cu sistemul în modul reduce.

## Verificări

- `node --test scripts/test_navigation.cjs`: 11 teste trecute.
- Cazuri noi: durata CSS diferită, animație anulată, animație absentă/durată zero.
- Cazuri păstrate: Escape, clic exterior, resize, navigare prin link,
  restaurarea focusului/scrollului și izolarea tastelor de Antrenare.
- `node --check static/core/js/FMJava.js`: trecut.
- `manage.py check`: fără probleme.
- Variabile CSS definite și blocuri echilibrate; verificarea diferențelor
  de whitespace a trecut.
- Browser, pagina clasei a V-a: intrare calculată 0,28 s, ieșire 0,22 s,
  accordion 0,22 s; Escape și clic pe închidere funcționale; cicluri repetate.
- După ieșire: dialog închis, aria-expanded=false, focus pe burger, scroll refăcut.
- Verificare la 390 px și dimensiunea implicită a browserului; fără erori
  de consolă observate în fila verificată.
- Pictograma de închidere are filtrul calculat brightness(0) invert(1).
- Viewportul temporar a fost resetat și meniul de test a fost închis.

Resursele modificate au versiunea de cache `20261031-phase4-3`.
Captură: [Meniul lateral](screenshots/faza-4-meniu.png).

## Fișiere și etapă următoare

- Nou: static/core/css/motion.css.
- Modificate: static/core/css/FMStyle.css, fm-app.css, frontend-polish.css;
  static/core/js/FMJava.js; templates/base.html; scripts/test_navigation.cjs.
- Raportul și captura sunt în docs.

Nu s-au modificat rutele, backendul, progresul sau JavaScriptul matematic.
Faza 4 este gata pentru revizuire. Urmează faza 5 — microinteracțiunile
componentelor — după discutarea acestui rezultat.
