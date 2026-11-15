# Modernizare frontend — faza 9: accesibilitate

Implementată și verificată local în sesiunea 31 octombrie–1 noiembrie 2026.
Ținta este WCAG 2.2 AA unde se aplică; această verificare nu constituie o
certificare a întregului site. Referință: [W3C WCAG 2.2 Quick Reference](https://www.w3.org/WAI/WCAG22/quickref/).

## Probleme corectate

- Reperul `main` lipsea din majoritatea paginilor. Acum șablonul comun are
  un singur `main`, cu destinația legăturii „Sari la conținut”; antetul și
  subsolul rămân în afara lui. Acasă și laboratorul nu mai introduc repere
  `main` imbricate. Profilul are un H1 accesibil, ascuns vizual.
- Etichetele vizibile ale formularelor sunt păstrate. Un template tag asociază
  instrucțiunile și erorile prin `aria-describedby` direct la randarea Django,
  setează `aria-invalid` pentru erori și completează scopul câmpurilor de cont
  prin `autocomplete`. Asocierile nu depind de JavaScript. Laboratorul folosește
  același renderer, fără referințe la erori client inexistente.
- Grupurile de răspunsuri au `legend` accesibil. Tabelul criteriilor de
  divizibilitate are antete de rând/coloană explicite; profilul și analiticele
  au antete de coloană, inclusiv nume pentru coloana de acțiuni.
- SVG-urile de statistică interactive foloseau `role="img"`, care ascundea
  semantic controalele descendente. Acum sunt grupuri cu controale denumite și
  stare `aria-pressed`. Graficele de construire și cele rezolvate rămân imagini,
  fără opriri de focus care nu execută o acțiune.
- Selectarea unei bare/punct actualizează starea în loc să reconstruiască
  formularul. Sliderul actualizează numai desenul și valoarea afișată, păstrând
  nodul input, focusul și ascultătorii săi. Observatorul responsive nu mai
  reține SVG-urile înlocuite.
- La redesenarea celorlalte exerciții, focusul revine la controlul echivalent
  din aceeași întrebare. Dacă acel control dispare sau devine dezactivat,
  focusul merge la titlul întrebării. Nu se mută focusul dacă utilizatorul a
  ales deja alt element sau dacă se schimbă întrebarea. Restaurarea nu derulează
  pagina. Săgețile sliderelor și zonelor derulabile își păstrează funcția locală.
- Focusul pe grafic are contur închis de 3 px, vizibil pe fundalul alb.
- Animația decorativă de pe Acasă are comandă „Oprește/Pornește animația” și
  mesaj de stare. Fără JavaScript se afișează imaginea statică. Preferința de
  mișcare redusă pornește cu imagine statică; activarea ei în timpul sesiunii
  oprește animația. Reluarea rămâne o alegere explicită a utilizatorului.
- Culorile rezultatelor folosesc tokenurile comune. Pe suprafața `#312c32`,
  textul de eroare trece de la aproximativ 3,28:1 la 6,71:1; succesul are
  8,44:1. Acestea sunt calcule pentru perechile specificate, nu o scanare a
  tuturor pixelilor și stărilor site-ului. Cardurile blocate din Battle Pass
  nu mai estompează tot textul prin opacitate. Textul copyright are greutate
  400, iar legătura din activitatea profilului păstrează culoarea lizibilă la hover.

## Verificări efectuate

- **89 teste JavaScript trecute**, inclusiv nouă cazuri pentru animație,
  semantica graficului, slider, selecție și restaurarea focusului.
- **57 teste Django trecute**: antrenare, navigare, stări UI, formulare,
  analitice și laborator. Trei cazuri noi verifică asocierile server-side,
  reperul unic și imaginea statică implicită.
- `manage.py check`, verificarea sintaxei JavaScript și `git diff --check`:
  fără erori; Git semnalează doar convențiile existente LF/CRLF.
- 14 măsurători în browser: Acasă, login, profil, catalog, statistică,
  vectori și laborator, la 320 și 1366 px. Toate au un singur `main`, un H1,
  fără inputuri neetichetate sau referințe ARIA inexistente în verificările
  descrise. Niciuna nu produce overflow orizontal al documentului.
- Tastatură: Tab → legătura de salt → Enter focalizează `main-content`.
  Space oprește animația și actualizează comanda/mesajul. Enter/Space aleg
  bara și păstrează focusul. Două săgeți consecutive modifică același slider.
  În tabelul de divizibilitate, Space păstrează celula focalizată, iar Tab
  continuă la celula următoare.
- Meniu desktop: Enter deschide, Tab intră în opțiuni, Escape închide și
  întoarce focusul. Meniu mobil: dialogul primește focus și izolează fundalul;
  Escape închide cu animația existentă și revine la burger.
- Exemple măsurate la desktop: butonul „Verifică răspunsul” aproximativ
  192 × 46 px; celulele de navigare aproximativ 30 × 30 px. Punctele graficului
  sunt mai mici și distanțate; toate sunt accesibile și din tastatură.

Registru: [accessibility_phase9_measurements.json](accessibility_phase9_measurements.json).
Dovadă vizuală: [focus pe grafic](screenshots/faza-9-focus-grafic.png).

Comenzi de regresie:

```powershell
node --test scripts/test_navigation.cjs scripts/test_ui_components.cjs scripts/test_training_p0.cjs scripts/test_training_states.cjs scripts/test_training_boot.cjs scripts/test_math_demo_boot.cjs scripts/test_training_accessibility.cjs scripts/test_training_geometry_keyboard.cjs scripts/test_vector_workbench.cjs scripts/test_responsive.cjs scripts/test_accessibility.cjs
.\.venv\Scripts\python.exe manage.py test quizzes.tests.TrainingTests quizzes.tests.NavigationTests quizzes.test_ui_states accounts.test_ui_components accounts.test_accessibility analytics.tests FoculMatematic.test_math_demo --verbosity 1
```

## Limite și verificări înainte de lansare

- Nu s-a făcut o sesiune reală cu NVDA/VoiceOver: trebuie ascultate ordinea
  anunțurilor, formulele KaTeX, graficele JSXGraph și feedbackul exercițiilor.
  Inspectarea arborelui accesibil nu înlocuiește această probă.
- Mișcarea redusă este acoperită de cod, CSS și teste simulate; nu a fost
  verificată vizual prin schimbarea preferinței reale a sistemului.
- Viewportul de 320 px nu este echivalent cu o probă reală de zoom 200% sau
  cu preferințe de spațiere a textului. Aceste probe, modul forced-colors și
  verificarea completă a țintelor în toate familiile de exerciții rămân manuale.
- Linkurile Google și rețele sociale existente au încă destinații `#`.
  Sunt funcționalități placeholder, nu integrări disponibile. Înainte de
  lansare trebuie completate destinațiile sau prezentată explicit indisponibilitatea.

Faza 10 (performanță) nu este începută în această etapă.
