# Modernizare frontend — faza 11: experiența fiecărei pagini

Implementată și verificată local la 1 noiembrie 2026. Include ajustarea cerută
în timpul lucrului: carduri mai mici în secțiunea „De unde începem?” de pe Acasă.

## Parcursul principal

Acasă are acum introducerea compactă, clasele și pașii de învățare aprobați
anterior. Acțiunea principală duce direct la alegerea clasei; utilizatorul
conectat poate continua și din profil. Animația WebM și meniul ei de click
dreapta rămân disponibile. Fundalul rămâne uniform și întunecat.

Clasele sunt o componentă comună pentru Acasă și catalog. Fiecare card are o
singură legătură, cu un nume accesibil care precizează clasa și destinația.
Nu sunt afișate numere inventate de exerciții sau promisiuni de disponibilitate.
Lista de pe Acasă folosește clasele acceptate de model, fără interogări noi.

La cererea utilizatorului, doar varianta de pe Acasă este mai compactă:

- La 887 px: patru coloane, două rânduri, carduri de 76 px; grila măsoară
  168 px înălțime, față de aproximativ 432 px anterior.
- De la 760 px în sus: patru coloane. Sub acest prag: două coloane.
- Pe telefoane de cel mult 380 px, cifra mare decorativă este ascunsă;
  denumirea completă a clasei rămâne, evitând împărțirea ei nefirească pe rânduri.
- Cardurile catalogului își păstrează dimensiunea mai generoasă.

## Revizuire pe pagini

| Pagină | Scop și acțiune principală | Decizie în această fază |
| --- | --- | --- |
| Acasă | Alegerea clasei și începerea învățării | Introducere compactă, clase accesibile direct, trei pași de învățare; profil ca acțiune secundară. |
| Chestionare | Găsirea clasei | Componenta comună de clase și explicație scurtă a traseului. |
| Clasă | Alegerea capitolului | Revenire la catalog, progres explicat și procent vizibil; capitolele fără întrebări indică pregătirea în locul unei bare de progres goale. |
| Capitol/categorie | Alegerea lecției | Traseu de revenire, introducere scurtă, progres semantic; lecțiile fără întrebări invită la vizualizare, fără a promite începerea unui exercițiu disponibil. |
| Lecție | Următorul pas potrivit progresului | Acțiunea calculată de aplicație rămâne dominantă; cele două moduri sunt secundare și explicate. Resetarea se află într-un `details` separat și păstrează confirmarea existentă. |
| Examen | Găsirea materiei examenului | Traseu de revenire; linkul unui capitol spune „Vezi lecțiile”, nu „Deschide lecția”. |
| Capitol de examen | Alegerea unei lecții | Traseu de revenire semantic, păstrând lista și etichetele examenului. |
| Antrenare | Rezolvarea exercițiului curent | Păstrată interfața verificată în fazele 7–10: feedback, retry, navigare, focus și comenzile locale. Nu s-au adăugat tranziții care ar întârzia răspunsul sau manipula desenul. |
| Chestionar generat | Trimiterea răspunsului curent | Indicator nativ pentru întrebările deja parcurse; la prima întrebare este 0, fără a număra întrebarea curentă drept rezolvată. |
| Chestionar clasic | Completarea întregului formular | Păstrate grupurile, opțiunile obligatorii, starea indisponibilă și protecția trimiterii; nu primește indicatorul secvențial al modului generat. |
| Rezultat generat | Înțelegerea scorului și continuarea | Scor dominant, XP real din context, continuare în Antrenare înaintea explicațiilor; generarea unui alt test rămâne o acțiune secundară. |
| Rezultat clasic | Revizuirea punctajului și răspunsurilor | Punctaj dominant și acțiuni înaintea listei lungi; revizuirea existentă și accesul de la final sunt păstrate. |
| Profil | Reluarea învățării și recapitularea | „Clasa mea” și următorul pas rămân prioritare; Battle Pass devine secundar. Numele barei XP și textele de recapitulare sunt clarificate. |
| Editare profil | Salvarea preferințelor | Păstrată perechea existentă Salvează/Anulează și feedbackul formularului; nu s-au schimbat opțiunile sau datele. |
| Conectare | Autentificarea | Google este marcat „în curând”, într-un buton dezactivat; nu mai este un link `#` prezentat drept autentificare funcțională. |
| Înregistrare | Crearea contului | Aceeași prezentare explicită a indisponibilității Google; se păstrează criteriile și validarea parolei. |
| Raportare problemă | Trimiterea feedbackului | Confirmarea reușitei are și o cale de întoarcere la chestionare. Nu s-au trimis rapoarte în verificarea vizuală. |
| Battle Pass | Consultarea recompenselor reale | Păstrate nivelurile, stările și datele existente; nu s-au inventat recompense, confetti sau progres. |
| Laborator | Explorarea formulelor și figurilor | Păstrate zonele distincte pentru ecuație, funcție și triunghi, cu loading/retry. Nu primește cardurile de navigare ale catalogului. |
| Analitice | Compararea intervalelor | Filtrele sunt o navigare denumită, cu perioada curentă explicită și celelalte intervale secundare. Tabelele rămân derulabile local. |
| 404 | Recuperarea unei navigări eșuate | Păstrate explicația și cele două ieșiri existente: Acasă și raportare. |
| 500 | Recuperarea după eroare | Păstrate referința raportului și ieșirile existente. Previzualizarea nu a declanșat intenționat o eroare reală. |

Nu sunt adăugate explicații matematice, indicii sau pași inventați. Conținutul
educațional și recomandările continuă să provină din datele și serviciile existente.

## Implementare și verificare

- Stilurile noi sunt în `page-experience.css`, încărcat doar de cele zece
  șabloane de parcurs care îl folosesc. Cardurile de navigare, rezultatele și
  formularele păstrează tratamente distincte.
- Nu există JavaScript nou în această fază. Sunt păstrate preferința de mișcare
  redusă, focusul, dialogul și meniul contextual al animației.
- **97 teste JavaScript trecute.**
- **84 teste Django distincte trecute în loturile relevante**: lotul principal
  de 83, plus testul nou al capitolului fără exerciții; lotul final de 11
  reverifică stările și cele cinci cazuri de experiență a paginilor.
- Cazurile noi verifică: toate clasele de pe Acasă fără acces la DB, progresul
  corect al întrebărilor parcurse, poziția continuării înaintea explicațiilor,
  Google indisponibil și lipsa unei bare de progres fără exerciții.
- 93 verificări DOM/layout: 22 adrese reale și nouă previzualizări sintetice,
  la 320, 887 și 1366 px. Fără overflow orizontal al documentului; un `main`,
  un H1 și referințe `aria-controls`/`aria-describedby` valide în toate probele.
- Previzualizările acoperă înregistrarea anonimă, cele două formulare de test,
  cele două rezultate, analiticele, confirmarea feedbackului și erorile 404/500.
  Folosesc șabloanele reale cu contexte fictive, fără creare de conturi,
  încercări, rapoarte sau răspunsuri în baza utilizatorului. Fișierele temporare
  sunt eliminate după verificare.
- În browser: Acasă → alegerea clasei → clasa a VIII-a; deschiderea secțiunii
  de opțiuni a lecției, fără activarea resetării; inspecție vizuală a rezultatului
  generat și a cardurilor compacte pe desktop și telefon.
- `manage.py check` și `git diff --check`: fără erori. Git semnalează convențiile
  existente LF/CRLF.

[Registrul verificărilor](page_experience_phase11_measurements.json).

![Clase compacte la 887 px](screenshots/faza-11-clase-compacte.png)

## Limite

Verificările de viewport nu înlocuiesc testarea pe dispozitive fizice sau cu
cititor de ecran. Previzualizările sintetice validează prezentarea stărilor,
nu un flux nou de înregistrare sau punctare în producție. Linkurile sociale
din subsol rămân placeholder-ele existente. Demo și admin sunt păstrate.
