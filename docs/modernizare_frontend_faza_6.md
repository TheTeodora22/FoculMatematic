# Modernizare frontend — faza 6: efecte vizuale selective

Implementată la 31 octombrie 2026, după alegerile utilizatorului:

- Acasă: fundal întunecat uniform, accent pe titlu și butoane.
- Antet compact: roșu ușor transparent cu blur la derulare.

## Implementare

- Introducerea de pe Acasă are explicit fundalul comun #252129, fără gradient.
  Reorganizarea ei în parcurs de învățare rămâne în faza dedicată paginilor.
- Antetul compact folosește rgba(186,57,45,.92): opacitate 92%, transparență 8%.
- Blur de 12 px, limitat la suprafața antetului și activ doar în starea compactă.
- Pentru browsere fără suport de blur, suprafața rămâne opacă, #ba392d.
  Ramura transparentă este condiționată de @supports, inclusiv prefixul WebKit.
- Logo-ul și burgerul rămân negre; linkurile din antet rămân albe.
- Meniul lateral păstrează transparența și animațiile deja aprobate.
- Nu s-au adăugat efecte pe toate cardurile, biblioteci sau animații permanente.
- Mutarea programatică a focusului în submeniul desktop, revenirea la butonul
  său și revenirea la burger folosesc preventScroll, pentru a păstra poziția paginii.

Valorile sunt centralizate în design-tokens.css. Componentele modificate:
ui-components.css, frontend-polish.css, ui-components.js și FMJava.js.
base.html are versiuni de cache phase6-1 pentru resursele modificate.

## Contrastul suprafeței compacte

Calcul sRGB pentru nuanța aleasă, compusă peste extremele negru/alb ale
conținutului din spate. Blurul produce culori intermediare:

| Fundal din spate | Culoare compusă RGB | Negru pe suprafață | Alb pe suprafață |
| --- | --- | --- | --- |
| Negru | 171,12 / 52,44 / 41,40 | 3,27:1 | 6,43:1 |
| Alb | 191,52 / 72,84 / 61,80 | 4,25:1 | 4,94:1 |

Acestea sunt calcule ale suprafeței compacte, nu o certificare a tuturor
stărilor și elementelor site-ului. Antetul extins păstrează gradientul anterior.

## Verificări

- manage.py check: fără probleme.
- 21 teste JavaScript de navigare și componente trecute; testul de focus
  verifică și opțiunea preventScroll pentru intrarea/ieșirea din submeniu.
- Browser la 1366 px: culoare calculată rgba(186,57,45,.92), blur(12px),
  fără imagine de fundal în starea compactă; documentul nu depășește lățimea utilă.
- Verificare directă prin clic și taste: la scrollY=718, deschiderea meniului,
  ArrowDown către primul link și Escape au păstrat scrollY=718.
- La 390 px: antet compact cu același blur, lățime utilă și scrollWidth 375 px;
  meniul mobil se deschide și se închide normal.
- Acasă: culoare calculată rgb(37,33,41), background-image=none.
- Fără erori de consolă observate în fila verificată. Viewportul temporar resetat.
- Ramura fără suport de blur este prezentă în CSS; nu s-a testat pe un browser
  fizic fără suport. Nu s-au măsurat FPS sau Core Web Vitals în acest lot.

Captură: [Antet compact](screenshots/faza-6-antet.png).

Faza 6 este gata pentru revizuire. Urmează faza 7: stări de încărcare,
conținut gol, eroare și succes, după discutarea rezultatului curent.
