# Modernizare frontend — faza 8: responsive

Implementată și verificată local la 31 octombrie 2026.

## Matricea verificată

| Profil de ecran | Viewport CSS |
| --- | --- |
| Mobil mic | 320 × 740 |
| Mobil mare | 390 × 844 |
| Tabletă | 768 × 1024 |
| Laptop | 1024 × 768 |
| Desktop | 1366 × 900 |
| Desktop mare | 1920 × 1080 |

168 combinații finale: 21 pagini/cazuri din aplicație și șapte șabloane
randate cu date sintetice, la fiecare dintre cele șase dimensiuni.

Paginile reale includ Acasă, catalog, clasă, capitol, lecție, lecție goală,
profil, editare, login, feedback, Battle Pass, laborator, cele două examene
și șapte familii de Antrenare: vectori, grilă, tabel, statistică, împărțire,
geometrie și fracții.

Datele sintetice acoperă înregistrarea anonimă, analiticele, un profil cu nume
și numere lungi, cele două pagini de rezultat și cele două formulare de test.
Au fost folosite șabloanele reale cu contexte fictive, fără creare de conturi
sau încercări pe baza utilizatorului. Previzualizările temporare au fost șterse.
Adresele lor rămân în registrul măsurătorilor doar pentru identificarea cazurilor.

## Probleme găsite și corectate

### Grafic prea mic pe mobil

Graficul de statistică se încadra în ecran, dar etichetele lui măsurau aproximativ
5 px înălțime la 320 px. Acum are o lățime minimă de 640 px într-o zonă cu
derulare orizontală locală; etichetele măsoară aproximativ 15 px în verificarea
din browser. Pagina păstrează lățimea ecranului.

Coordonatele, viewBox-ul 620 × 300, valorile și alegerea răspunsului sunt păstrate.
Pe ecrane suficient de late graficul se încadrează și nu afișează instrucțiunea de derulare.

### Tabele late, greu de folosit fără mouse

Zonele cu depășire reală primesc focus din tastatură, nume accesibil și o
instrucțiune scurtă înaintea conținutului. Săgețile derulează nativ zona și
nu schimbă întrebarea din Antrenare. Când conținutul încape, dispar instrucțiunea
și oprirea suplimentară de Tab generată de script.

Aplicat tabelelor de criterii, statistice, zecimale, procente, activității
profilului, analiticelor și graficului statistic. Tabelele de profil și analitice
păstrează o lățime minimă lizibilă și se derulează local pe mobil.

Prima coloană a tabelului de criterii rămâne vizibilă pentru contextul rândului.
Focusul din tastatură deplasează zona cât este necesar pentru a nu lăsa celula
ascunsă în spatele acestei coloane. Focusul prin clic nu mută butonul de sub pointer.

Poziția orizontală este păstrată la reconstruirea aceleiași întrebări.
Observerii vechilor elemente sunt deconectați; schimbările interne din KaTeX
și deplasarea desenelor nu declanșează scanarea întregului document.

### Text înghesuit în butoane

Pe ecrane mici, acțiunile de autentificare și acțiunile lecției/rezultatului
se așază pe rânduri separate. Textul poate ocupa mai multe rânduri fără o
înălțime fixă care să-l taie. Controalele păstrează suprafețe utile de apăsare.

### Grilă de întrebări dependentă de tooltip

Celulele afișează acum numărul întrebării, atât în HTML-ul serverului, cât și
după inițializarea JavaScript. Au și eticheta Întrebarea N; aria-current și
stările de progres sunt păstrate. Numerele nu depind de hover pe mobil.

O bancă reală cu 315 întrebări a fost verificată la 320 px: ultima celulă
afișează 315, are clientWidth=scrollWidth=32 px și font de 13 px.

## Rezultatele verificării

- Cele 168 de măsurători finale nu indică depășirea documentului, conținut HTML
  decupat accidental, text de buton care depășește controlul sau suprapunere logo–meniu.
- Au fost verificate și elementele aflate sub primul ecran; zonele cu derulare
  intenționată sunt diferențiate de conținutul ascuns prin overflow.
- Stratul MathML invizibil al KaTeX este exclus din raportarea decupării:
  ascunderea lui vizuală este intenționată și necesară structurii accesibile.
- Pragul navigării: burger la 1280 px, șapte elemente desktop la 1281 px,
  fără suprapunere cu logo-ul.
- Landscape 844 × 390: dialogul are 390 px înălțime; ultimul link este accesibil,
  cu marginea inferioară la 378 px. Nu s-a activat deconectarea.
- Pe grafic, ArrowRight a derulat local 40 px fără schimbarea întrebării.
- După selectarea unei bare și reconstruirea întrebării, selecția 0 și
  scrollLeft=40 au fost păstrate. La 1920 px selecția a rămas, iar zona
  care încăpea nu mai avea oprirea de Tab generată de script.
- În tabel, focusul ajuns inițial sub coloana fixă este adus în zona vizibilă:
  marginea controlului 170,73 px, marginea coloanei 162,44 px.
- Niciun răspuns nu a fost trimis în browser pentru aceste teste; selecția
  graficului a fost doar o modificare temporară în pagină.
- Viewportul temporar a fost resetat; nu au fost observate erori în consola filei verificate.

## Teste și artefacte

- 80 de cazuri JavaScript distincte trecute în loturile relevante, inclusiv
  opt teste noi pentru overflow, focus, restaurarea poziției, coordonatele graficului
  și numerotarea fără tooltip.
- 46 teste Django trecute: Antrenare, navigare, stări, componente și analitice.
- Test nou pentru numerotarea serverului, inclusiv fără JavaScript.
- manage.py check, verificarea sintaxei JS, referințele CSS și diff --check trecute.
- [Măsurători complete](responsive_phase8_measurements.json).
- [Grafic pe mobil](screenshots/faza-8-grafic-mobil.png).
- [Tabel pe mobil](screenshots/faza-8-tabel-mobil.png).

Noi: static/core/js/responsive.js și scripts/test_responsive.cjs.
Modificate: CSS-ul comun și componentele, training.js, training.html,
base.html, șablonul analiticelor și testul de randare a grilei.
Versiuni de cache: phase8-4 pentru stilurile/markupul acestui lot și phase8-5
pentru ultimul reglaj al scriptului de focus.

## Limite și pas următor

Verificările sunt făcute în browserul integrat, cu viewporturi CSS. Nu sunt
teste pe telefoane/tablete fizice și nu certifică separat Safari, Firefox sau Edge.
Zoomul browserului, cititorul de ecran și auditul WCAG complet nu sunt declarate
verificate în acest lot. Nu s-au măsurat Core Web Vitals.

Nu s-au modificat punctajele, regulile matematice, datele contului sau backendul.
Faza 8 este gata pentru revizuire. Urmează faza 9: accesibilitate.
