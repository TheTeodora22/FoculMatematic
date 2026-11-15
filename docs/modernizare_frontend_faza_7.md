# Modernizare frontend — faza 7: încărcare, gol, eroare și succes

Implementată la 31 octombrie 2026.

## Antrenare: salvare confirmată și reîncercare

- Status într-o regiune live permanentă, cu spațiu rezervat, în afara cardului
  reconstruit: salvare în curs, rezultat confirmat sau salvare neconfirmată.
- Rezultatul și progresul continuă să fie confirmate exclusiv din răspunsul
  serverului. O eroare de rețea nu este prezentată ca dovadă că serverul nu a salvat.
- Limită de 20 de secunde pentru cererea de salvare, inclusiv citirea răspunsului,
  prin AbortController; timerul se eliberează atât la succes, cât și la eroare.
- Mesaje în română pentru conexiune întreruptă, termen depășit și răspuns imposibil de citit.
- Panou de eroare cu Reîncearcă salvarea și Raportează problema.
- Reîncercarea trimite formularul curent prin requestSubmit, folosind validarea
  lui nativă și handlerul existent. Nu există retrimiteri automate.
- La grile, opțiunea selectată rămâne bifată în timpul salvării și după eroare.
  A fost corectată condiția care o păstra numai în anumite stări de feedback.
- Se păstrează protecțiile existente: un singur submit în curs, confirmarea
  întrebării originale și evitarea aplicării răspunsului peste o altă întrebare.
- Încărcarea inițială folosește un indicator peste spațiul ocupat de conținutul
  serverului, fără un skeleton artificial sau o întârziere intenționată.
- Recuperarea independentă training-boot.js este păstrată.

Răspunsul este păstrat în starea paginii curente. Nu s-a implementat un nou
sistem de drafturi persistente între reîncărcări, file sau dispozitive.
Anularea cererii în browser nu garantează anularea procesării pe server.

## Stări fără conținut

Componenta includes/state_panel.html și stilurile ui-states.css oferă un titlu,
o explicație și, când este util, o acțiune reală de continuare.

Aplicate pentru:

- clase fără capitole;
- capitole fără lecții;
- capitole de examen fără subiecte și examene încă în pregătire;
- lecții fără întrebări;
- chestionare clasice fără întrebări;
- Battle Pass fără sezon sau fără recompense;
- analitice fără date în perioada aleasă.

Lecțiile fără întrebări nu mai propun pornirea modurilor indisponibile sau
resetarea unui progres gol. Rutele și regulile backend rămân aceleași.
Starea goală ilustrată din profil și paginile existente 404/500, care au
deja explicații și acțiuni de recuperare, au fost păstrate.

## Formulare și laborator

- Starea de trimitere din faza 5 este aplicată și chestionarului clasic,
  chestionarului generat și celor două formulare de ecuații din laborator.
- Butoanele cu name/value își păstrează explicit acțiunea POST când sunt
  dezactivate: de exemplu, action=new pentru Altă ecuație. Câmpul temporar
  este eliminat când pagina revine din Back/Forward cache.
- Controalele deja dezactivate nu sunt marcate ca dezactivate de noul handler.
- Statusurile laboratorului au ID-uri distincte și sunt în afara formularelor aria-busy.
- Laboratorul are o cale de recuperare independentă, math-demo-boot.js:
  script lipsă, eroare de inițializare sau încărcare peste 15 secunde.
- La eșec se afișează un mesaj și un buton explicit de reîncărcare;
  formularul ecuației rămâne disponibil.
- O inițializare reușită târziu poate închide starea de eroare.
- Indicatorii de lucru respectă prefers-reduced-motion; mesajul textual rămâne disponibil.

Paginilor deja randate de Django nu li s-au adăugat skeleton-uri sau cereri
suplimentare doar pentru un efect vizual. Stările de succes și eroare ale
formularelor folosesc în continuare răspunsul backend și mesajele existente.

## Verificări

- 72 teste JavaScript distincte trecute, în loturi relevante: navigare,
  componente comune, salvare, recuperare la boot, slider accesibil,
  tastatură geometrică și atelier vectorial.
- Cazuri noi: cerere blocată/anulată, eroare de rețea, JSON invalid, eroare HTTP,
  selecție păstrată, reîncercare pe întrebarea curentă, stări live și recuperarea graficelor.
- 58 teste Django trecute în două loturi: 31 pentru stări/Antrenare/navigare și
  27 pentru teste clasice/generate, examene, laborator și componente de formular.
- Sintaxa JS, manage.py check și diff --check au trecut.
- Bază de test separată; nu s-au trimis răspunsuri sau formulare pe contul
  utilizatorului pentru simularea erorilor în browser.
- Browser: o lecție reală fără întrebări afișează panoul și acțiunea de revenire,
  fără butoanele de pornire/resetare indisponibile.
- La 390 px: lecția goală are scrollWidth=clientWidth=390 px; Antrenarea și
  laboratorul au 375 px utili și același scrollWidth, cu scrollbar vertical.
- În Antrenare, loaderul dispare, layoutul devine vizibil, iar KaTeX și SVG-ul
  exercițiului vectorial se afișează normal.
- Laborator: două grafice SVG inițializate, starea loading încheiată, eroare ascunsă;
  ambele formulare au statusul separat de aria-busy și acțiunea new este păstrată.
- Erorile de rețea/script și cererile blocate au fost simulate în teste izolate,
  nu prin întreruperea conexiunii utilizatorului.
- Fără erori de consolă observate în fila verificată; viewportul temporar resetat.
- Nu s-au măsurat Core Web Vitals sau comportamentul cu cititor de ecran în acest lot.

Captură: [Lecție fără întrebări](screenshots/faza-7-lectie-goala.png).

## Fișiere principale

Noi: templates/includes/state_panel.html, static/core/css/ui-states.css,
static/core/js/math-demo-boot.js, scripts/test_training_states.cjs,
scripts/test_math_demo_boot.cjs și quizzes/test_ui_states.py.

Modificate: training.js, ui-components.js, math-demo.js, form_status.html,
training.html, math_demo.html, base.html, șabloanele de catalog/examene/teste,
Battle Pass și analitice; testele relevante au fost extinse.

Versiunea de cache a resurselor acestui lot: 20261031-phase7-2.
Nu s-au modificat formulele, punctajele, schema bazei de date sau regulile de progres.

Faza 7 este gata pentru revizuire. Urmează faza 8: verificare responsive
pe mobil mic/mare, tabletă, laptop și desktop mare.
