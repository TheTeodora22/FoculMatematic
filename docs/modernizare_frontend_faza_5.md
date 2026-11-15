# Modernizare frontend — faza 5: microinteracțiuni

Implementată la 31 octombrie 2026, pe direcția vizuală aprobată.

## Navigare și antet

- Antet sticky cu spațiu rezervat stabil în pagină: 88 px pe desktop,
  76 px pe mobil; la derulare devine compact, de 68 px.
- Compactare peste 80 px de scroll; revenire sub 24 px, pentru a evita
  oscilațiile în jurul unui singur prag. Logo-ul se micșorează discret.
- Indicator vizibil pentru pagina curentă, pe linkurile reale de navigare.
- Clase și Examene pe desktop sunt butoane cu aria-expanded și aria-controls,
  în locul linkurilor către #. Submeniurile închise sunt inert.
- Enter/clic comută deschiderea; ArrowDown deschide și focalizează primul link;
  Escape închide și restaurează focusul; Tab și clic exterior închid natural.
- Linkurile devin imediat focusabile; doar opacitatea este animată la intrare.
- Submeniurile au un panou comun și derulare proprie când înălțimea ecranului este mică.
- Tastele folosite în submeniul desktop deschis nu ajung la comenzile Antrenării.
- Meniul mobil păstrează dialogul, transparența și animațiile existente.

## Butoane și carduri

- Feedback scurt la apăsare, focus vizibil și stări dezactivate păstrate.
- Cardurile de navigare primesc o bordură mai clară când linkul lor este
  focalizat sau survolat. Cardurile informative nu primesc cursor sau ridicare artificială.
- Acțiunile Salvează/Anulează din profil sunt primară/secundară și se pot
  așeza pe rânduri separate. Textul Anulează are contrast lizibil.

## Formulare

- Componente comune: includes/form_field.html și includes/form_status.html.
- Etichete vizibile pentru login, înregistrare, feedback și editarea profilului.
- Erori de server păstrate vizibil; descrieri și erori asociate câmpurilor în JS.
- Validare inline bazată pe validitatea nativă, cu mesaje în română,
  fără modificarea regulilor backend. Mesajele native ale browserului pot
  urma limba browserului; nu s-a înlocuit mecanismul său de validare.
- Un singur handler comun pentru arătarea/ascunderea parolei, cu aria-pressed
  și aria-controls. Scriptul existent al criteriilor din înregistrare este păstrat.
- Trimiterea formularelor marcate data-ui-form afișează indicator de lucru,
  dezactivează butonul și previne trimiterea repetată în aceeași pagină.
- Statusul live este în afara formularului aria-busy, pentru a nu fi blocat
  de starea ocupată a acestuia. Textul butonului rămâne stabil.
- pageshow reface controalele după revenirea prin Back/Forward cache.
- Formularele exercițiilor nu au data-ui-form și nu sunt preluate de noul cod.

## Mesaje

Mesajele Django existente folosesc role=status sau role=alert, intrare discretă
și închidere explicită. Nu expiră automat. Închiderea ultimului mesaj mută
focusul la conținut; dacă mai există mesaje, următorul buton de închidere primește focus.
Nu s-a adăugat un al doilea sistem de toasturi sau o bibliotecă externă.

## Verificări

- 21 teste JavaScript trecute: 11 pentru meniul lateral și 10 pentru componentele noi.
- 15 teste Django acoperite: șase pentru componentele randate și nouă pentru
  înregistrare, feedback și navigare. Un test nou a avut inițial o căutare prea
  largă, care confunda data-status-id cu id; aserțiunea a fost corectată și
  toate cele șase teste de componente au trecut la rerulare. Celelalte nouă trecuseră.
- Verificarea sintaxei JS, manage.py check, referințele CSS și diff --check trecute.
- Browser: Chestionare, clasa a V-a, login, editare profil, feedback și Antrenare vectorială.
- La 1366 px: antetul compact măsoară 68 px, rămâne la top=0, iar documentul
  are scrollWidth=clientWidth=1351 px pe pagina clasei.
- La 320 px, login și editare profil: scrollWidth=clientWidth=305 px.
- La 390 px, editare profil: scrollWidth=clientWidth=375 px; selecturile au minimum 44 px.
- ArrowDown focalizează efectiv Clasa a 5-a; Escape revine la butonul Clase.
- În Antrenare, ArrowRight în submeniu a păstrat întrebarea index 2; după
  Escape, ArrowRight în afara submeniului a trecut normal la index 3.
- Meniul mobil se deschide și se închide cu antetul deja compact.
- Login: controlul parolei este reversibil, iar câmpul gol afișează
  „Completează acest câmp.” și aria-invalid=true, fără trimiterea formularului.
- Statusul live al formularului a fost confirmat în afara formularului ocupat.
- Înregistrarea redirecționează utilizatorul deja conectat către Acasă,
  conform comportamentului existent. Randarea anonimă a noilor câmpuri este
  acoperită automat; nu declarăm o verificare vizuală a ei în această sesiune.
- Nu s-au trimis formulare și nu s-au schimbat datele contului în testarea din browser.
- Fără erori de consolă observate; viewportul temporar resetat, meniul de test închis.

Ramura de mișcare redusă elimină tranzițiile noilor componente și rotirea
indicatorului de lucru. Preferința globală a sistemului nu a fost schimbată.
Testarea completă cu cititor de ecran și matricea de browsere rămân în fazele dedicate.

## Fișiere

Noi: static/core/js/ui-components.js, static/core/css/ui-components.css,
templates/includes/form_field.html, templates/includes/form_status.html,
scripts/test_ui_components.cjs, accounts/test_ui_components.py.

Modificate: templates/base.html, registration/login.html, registration/register.html,
feedback/report.html, accounts/profile_edit.html și regulile vechi de dropdown
din static/core/css/FMStyle.css și fm-app.css.

Versiune resurse noi/modificate: 20261031-phase5-4. Nu s-au modificat rutele,
validarea backend, regulile recompenselor sau codul de salvare al exercițiilor.

Capturi: [Navigare desktop](screenshots/faza-5-navigare.png),
[Formular profil pe mobil](screenshots/faza-5-formular.png).

## Următoarea fază

Faza 5 este gata pentru revizuire. Faza 6 evaluează efectele decorative;
orice efect major va fi discutat înainte de implementare, conform cerinței inițiale.
