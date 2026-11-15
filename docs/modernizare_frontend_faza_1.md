# Modernizare frontend — faza 1: audit

Data: 31 octombrie 2026. Stare: audit de cod și inventar; fără modificări ale interfeței în această fază.
Fiecare fază va fi discutată cu utilizatorul înainte de trecerea la următoarea.

## Domeniu și limite

Inventariate 24 de șabloane HTML, cele șase fișiere CSS din static/core/css,
structura navigării și scripturile existente. Inspectate șabloanele comune și
familiile de pagini: Acasă, cont, catalog, lecții, teste, rezultate, Antrenare,
Battle Pass, laborator, analitice și erori.

Raportul anterior frontend_visual_review.md conține verificări vizuale anterioare.
Acestea nu certifică schimbările ulterioare ale logo-ului și meniului.
Nu s-au făcut măsurători noi LCP/INP/CLS sau o parcurgere completă în browsere în
această fază. Contrastul actual al tuturor stărilor, cititorul de ecran, zoomul
și toate dimensiunile de ecran rămân de verificat practic.
Checklistul de lansare conține constatări istorice: acestea trebuie reconciliate
cu codul actual, nu copiate ca probleme încă prezente. De exemplu, acum există
training-boot.js și mesaje live pentru progres și salvare.

## Arhitectura actuală

- Django 4.2.11, șabloane server, JavaScript simplu; fără necesitatea unui framework nou.
- base.html încarcă FMStyle.css, fm-app.css și frontend-polish.css în această ordine.
- fm-app.css: 3.806 linii și 57 declarații !important; frontend-polish.css: 274 linii și șase !important.
- Stiluri și scripturi suplimentare pentru matematică, laborator și atelierul vectorial.
- KaTeX pentru formule, JSXGraph în laborator; logica matematică se păstrează.
- Montserrat importat prin CSS de la Google; Font Awesome 4.7 din CDN.
- Stiluri inline în majoritatea șabloanelor și blocuri style pentru unele componente.
- Meniul mobil folosește dialog nativ, stări ARIA, restaurarea focusului și animații CSS coordonate din JS.

## Ce păstrăm

- Identitatea roșu închis, suprafețele întunecate și textul deschis.
- Preferințele deja stabilite: logo negru și mai mare, text alb în antet,
  burger negru fără pătrat, meniu lateral ușor transparent cu animații de intrare/ieșire.
- Umbra discretă de pe profil și ierarhia îmbunătățită a paginii principale.
- Navigarea clase → capitol → lecție, cardurile de progres și explicațiile matematice.
- Focusul vizibil, skip link, dialogul nativ și izolarea scurtăturilor de Antrenare.
- Comportamentul cu mișcare redusă și imaginea statică alternativă GIF-ului.
- Datele, rutele, formularele, progresul și integrările existente.

## Audit prioritizat

| Prioritate | Constatare și dovadă | Recomandare | Validare necesară |
| --- | --- | --- | --- |
| Mare | Aceleași componente primesc reguli din trei straturi CSS; apar suprascrieri !important, inclusiv pentru logo și autentificare. | Consolidare treptată pe componente și variabile, fără încă un strat global de corecții. | Compararea vizuală înainte/după pe paginile reprezentative. |
| Mare | Culorile, spațierile, raza, umbrele și tipografia sunt parțial centralizate; multe valori rămân locale. | Definirea unui set comun de tokenuri și migrarea componentelor pe rând. | Contrast și verificarea tuturor stărilor componentei. |
| Mare | Login și feedback afișează câmpuri fără etichete vizibile în șablon; erorile au stiluri locale. profile_edit combină p cu div. | Etichete vizibile, structură HTML validă și asociere consecventă câmp–descriere–eroare. | DOM randat, tastatură și cititor de ecran; aria-label existent nu înlocuiește nevoia vizuală de etichetă. |
| Mare | Navigarea desktop folosește linkuri # pentru Clase/Examene; nu are aceeași stare explicită de expandare ca mobilul. | Comenzi de deschidere semantice și navigare activă clară; păstrarea accesului prin tastatură. | Clic, touch, Tab, Escape și revenirea focusului. |
| Mare | Logo-ul și burgerul negre sunt pe un gradient roșu închis; vizibilitatea trebuie măsurată după preferințele recente. | Măsurarea contrastului; dacă este insuficient, discutăm nuanța antetului păstrând cerința de elemente negre. | Contrast pe zona cea mai închisă a gradientului. Nu declarăm eșec măsurat fără test. |
| Medie | Acasă are ierarhie clară, dar GIF-ul existent are 1.739.930 octeți. Fontul folosește @import, iar iconurile depind de CDN. | Evaluarea unui format animat eficient sau a imaginii statice; optimizarea încărcării fontului și a iconurilor folosite. | Măsurători înainte/după pe mobil; dimensiunea singură nu dovedește LCP slab. |
| Medie | Duratele/easing-urile sunt dispersate; meniul are 280 ms intrare, 220 ms ieșire și temporizator de rezervă în JS. Există trei transition: all în CSS vechi. | Tokenuri de mișcare și tranziții pe proprietăți explicite; verificarea întreruperii/repetării rapide. | Mișcare normală/redusă, deschidere–închidere rapidă, Escape și redimensionare. |
| Medie | Mesajele globale Django sunt o listă; feedbackul în formulare, rezultate și Battle Pass are stiluri diferite. | Componente comune pentru informare, eroare, succes și stare goală. | Anunțuri accesibile, evitarea mesajelor duplicate și păstrarea acțiunilor utile. |
| Medie | Cardurile de clase, lecții, statistici și recompense au scopuri diferite dar se bazează mult pe .card și stiluri inline. | Variante clare: navigare, statistică, progres, rezultat. Doar cardurile cu acțiune primesc indicii de interactivitate. | Coerență vizuală și identificarea rapidă a acțiunii principale. |
| Medie | Rezultatele și tabelele analitice au structură utilă, dar multe spațieri locale. Tabelele au deja overflow-x:auto. | Ierarhie comună pentru scor, explicații și următorul pas; păstrarea derulării locale a tabelelor. | Ecran mic, zoom, formule lungi, antete de tabel. |
| Mică | Linkurile sociale și Google au href=# în base/login. | Înainte de lansare: destinații reale sau prezentare clară a disponibilității, conform deciziei de produs. | Verificarea destinațiilor. Demo/admin rămân disponibile în dezvoltare. |

## Priorități pe familii de pagini

| Familie | Scop și acțiune principală | Îmbunătățirea propusă |
| --- | --- | --- |
| Acasă | Elevul intră în chestionare. | Păstrarea CTA dominant; alegerea între imagine statică și animație optimizată. |
| Catalog/clasă/capitol/examen | Găsirea lecției. | Carduri de navigare consecvente, traseu de revenire clar și progres lizibil. |
| Lecție | Alegerea modului de lucru. | Diferențiere clară între Antrenare și test; explicații scurte pentru opțiuni. |
| Antrenare | Rezolvarea întrebării și înțelegerea explicației. | Prioritate formulelor, răspunsului și salvării; feedback discret, fără mutarea focusului sau ascunderea conținutului util. |
| Test/generare/rezultate | Finalizare și înțelegerea scorului. | Buton principal clar, stări de trimitere, rezultat și următoarea acțiune. |
| Profil/editare | Reluarea învățării și gestionarea contului. | Păstrarea rezumatului și umbrei; ierarhie pentru progres și formular coerent. |
| Login/register/feedback | Completarea sigură a formularului. | Etichete, erori și stări consecvente; fără animații care întârzie tastarea. |
| Battle Pass | Înțelegerea progresului și recompenselor. | Distincție accesibilă între blocat/deblocat/obținut; mai multă structură decât o listă uniformă. |
| Laborator | Explorarea matematicii. | Panouri clare, status vizibil și păstrarea spațiului pentru grafic. |
| Analitice | Compararea datelor. | Filtru activ explicit, tabele lizibile, stări goale utile. |
| 404/500 | Recuperarea traseului. | Păstrarea acțiunilor de revenire și raportare, cu aspect comun. |

## Unde ajută mișcarea

- Meniu lateral și submeniuri: continuitate între stări; verificăm animațiile existente.
- Butoane: răspuns vizual scurt la apăsare, hover și focus.
- Progres și feedback de răspuns: actualizare discretă după confirmarea salvării.
- Explicații și indicii: apariție scurtă, fără întârzierea accesului la conținut.
- Notificări: intrare/ieșire discretă, fără a pierde un mesaj important.

Evităm animațiile permanente pe carduri, glow continuu, parallax în Antrenare,
count-up care întârzie citirea scorului, scroll reveal care ascunde lecțiile și
tranziții de pagină care întârzie navigarea. Skeleton doar unde există o așteptare
asincronă reală; nu se adaugă artificial paginilor deja randate de server.

## Planul fazelor, de discutat pe rând

1. Audit: acest document, discutarea priorităților și completarea verificărilor lipsă.
2. Direcție vizuală: alegem 2–3 alternative concrete pentru suprafețe/carduri,
   antet și nivelul animațiilor, în loturi mici de întrebări.
3. Sistem vizual: culori, tipografie, spațiere, suprafețe și componente de bază.
4. Sistem de mișcare: durate/easing comune, mișcare redusă și utilitare selective.
5. Interacțiuni: navigare, butoane, formulare, dialoguri și mesaje.
6. Efecte decorative: numai în locuri aprobate; recomandare inițială: efecte discrete.
7. Stări: încărcare, gol, eroare, succes și recuperare.
8. Responsive: matrice mobil mic/mare, tabletă, laptop și desktop mare.
9. Accesibilitate: tastatură, contrast, zoom, semantică și verificări asistive.
10. Performanță: măsurători și optimizări justificate de rezultate.
11. Revizuire pe pagină: scop, acțiune principală și consistență.
12. Verificare și raportare: comparații vizuale și teste pentru comportamentele modificate.

## Recomandare pentru discuția din faza 2

Direcție recomandată: identitatea actuală rafinată, cu suprafețe întunecate simple,
roșu folosit pentru acțiunile principale, umbre moi și mișcare discretă.
Alternative de prezentat: suprafețe plate vs. profunzime discretă; antet normal
vs. compact la derulare; mișcare restrânsă vs. moderată pe profil/recompense.
Nu introducem încă o temă, biblioteci sau efecte decorative în această fază.

Deciziile vizuale se iau împreună; următoarea fază nu a fost începută.
