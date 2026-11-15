# Modernizare frontend — faza 3: sistemul vizual

Implementată la 31 octombrie 2026, pe direcția confirmată în faza 2.

## Ce s-a implementat

- `static/core/css/design-tokens.css`: sursa comună pentru culori, Montserrat
  și fonturi de rezervă, greutăți, scara tipografică, spațiere, raze, umbre,
  lățimi, indicatorul de focus și nivelurile de suprapunere.
- Fundal `#252129`, carduri `#312c32`, suprafețe ridicate `#403641`:
  cardurile sunt mai deschise decât fundalul, cu profunzime discretă.
- Culori semantice pentru succes, eroare, avertizare, informare și dezactivare;
  variantele existente de mesaje folosesc aceste culori, fără un nou sistem de toasturi.
- Titluri H1–H4 și titlu display, dimensiuni fluide pentru titlurile mari,
  text secundar, etichete și butoane conectate la variabile.
- Scara de spațiere: 4/8/12/16/24/32/48/64 px la dimensiunea standard a rădăcinii.
- Carduri, panouri de autentificare, butoane, câmpuri, navigare, profil,
  feedback de Antrenare și footer conectate treptat la tokenuri.
- Panourile de autentificare folosesc suprafață solidă și umbră discretă;
  transparența solicitată rămâne pe meniul lateral.
- Butoanele dezactivate au culori dedicate și nu primesc stilul de hover activ.
- Imaginea geometrică are o suprafață cu colțuri rotunjite care integrează
  fundalul opac al GIF-ului pe noul fundal al paginii.
- Resursele CSS modificate au versiunea de cache `20261031-phase3-2` în base.html.

Nu s-a adăugat un nou strat global de corecții: s-au migrat reguli existente
din FMStyle.css, fm-app.css și frontend-polish.css. Nu s-au adăugat dependențe.

## Convenții pentru fazele următoare

- Culorile componentelor comune se aleg din `--fm-*`; valorile specifice
  desenelor matematice pot rămâne locale pentru a nu afecta semnificația lor.
- Suprafețe: `bg` → `surface` → `surface-raised`; roșul rămâne culoarea acțiunii principale.
- Raze: control 8 px, buton 12 px, card 14 px, panou 16 px.
- Lățimi: conținut 80 rem, profil 56 rem, formular 28 rem, meniu lateral 23 rem.
- Pragurile responsive existente rămân 640/960/1280 px, scrise literal în
  media queries. Variabilele CSS nu înlocuiesc pragurile acestor expresii.
- Nivelurile pentru dropdown și antet sunt rezervate pentru implementarea
  navigării fixe; dialogul nativ folosește top layer.
- Tema întunecată este direcția acestui lot. Nu s-a implementat o nouă temă luminoasă.

## Preferințe păstrate

Logo negru și mai mare, text alb în antet, burger negru fără pătrat, meniu
lateral transparent cu animațiile existente și umbra exactă de pe profil.
Nu s-au modificat JavaScriptul exercițiilor, rutele, baza de date, progresul
sau regulile desenelor SVG/KaTeX.

## Verificări

- `manage.py check`: fără probleme.
- `node --test scripts/test_navigation.cjs`: 8 teste trecute.
- Verificarea referințelor la variabilele `--fm-*`: fără referințe nedefinite
  în cele patru fișiere CSS comune. Blocurile CSS sunt echilibrate.
- Browser integrat: Acasă, profil, clasa a IX-a, login și Antrenare vectorială.
- La 390 px, clasa a IX-a, login și Antrenare: lățime utilă și scrollWidth 375 px.
- La 320 px, profil: lățime utilă și scrollWidth 305 px.
- La 1366 px, clasa a IX-a: lățime utilă și scrollWidth 1351 px;
  navigarea desktop încape, H1 este 40 px, butoanele principale au minimum 44 px.
- KaTeX și SVG-ul din întrebarea vectorială se afișează pe mobil.
- Umbra profilului calculată în browser păstrează straturile 0/12/48/−14
  la opacitate 0,20 și 0/4/20/−8 la opacitate 0,12.
- Versiunea finală a tokenurilor a fost confirmată în browser; fără erori
  în consola filei verificate. Dimensiunea temporară a browserului a fost resetată.

Rapoarte de contrast calculate pentru perechi opace din paletă:

| Pereche | Raport |
| --- | --- |
| Text / fundal | 13,19:1 |
| Text / card | 11,40:1 |
| Text secundar / card | 6,81:1 |
| Text buton / roșu principal | 6,04:1 |
| Succes / fundal succes | 7,35:1 |
| Eroare / fundal eroare | 6,08:1 |
| Avertizare / fundal avertizare | 8,06:1 |
| Informare / fundal informare | 7,62:1 |
| Bordură control / fundal câmp | 4,29:1 |

Aceste calcule nu certifică toate stările, transparențele sau contrastul
logo-ului/burgerului pe gradientul antetului. Verificarea completă a
accesibilității rămâne în faza dedicată. Nu s-au măsurat Core Web Vitals.

Captură: [Clasa a IX-a, desktop](screenshots/faza-3-clasa-9.png).

## Limitele lotului și următorul pas

Rămân valori locale în componentele specifice și stilurile inline;
migrarea lor se continuă când acele componente sunt tratate în fazele următoare.
Animațiile, antetul fix/compact și reorganizarea paginii principale au etapele
lor de implementare. În această fază nu sunt declarate realizate.

Faza 3 este gata pentru revizuire împreună. Urmează faza 4 — sistemul de mișcare,
după discutarea rezultatului acestei faze.
