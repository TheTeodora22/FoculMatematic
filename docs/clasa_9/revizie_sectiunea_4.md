# Revizia grilelor 4.1 și 4.2

24 octombrie 2026 · `codex/clasa-a-9-a`

## Rezultat și întinderea verificării

Au fost recitite cele 63 de familii, împreună cu enunțurile, variantele și explicațiile produse de fiecare. Un verificator separat recalculează răspunsul la fiecare grilă din datele enunțului și testează fiecare opțiune, fără a importa formulele sau cheia generatorului.

Lotul revizuit păstrează **315 grile: 150 la inducție și 165 la numărare**. Verificatorul confirmă **315/315 grile cu un singur răspuns corect, din 1.260 de opțiuni**. Cele 63 de tipuri au câte cinci grile. Nu s-au adăugat interactive.

Au fost îmbunătățite **67 de grile** din 14 familii. 47 au enunțuri schimbate, 47 au opțiuni schimbate și 42 au explicații schimbate; categoriile se suprapun. Toate cele 315 primesc metadate despre întinderea sarcinii.

## Probleme găsite și remedii

| Familie | Constatare | Remediu |
|---|---|---|
| 4.1, tip 1 | Variantele false erau deja eliminate la n=1; explicația generală folosea convergență, mult peste cerința grilei | Variante fracționare care trec testul n=1, cu contraexemple ulterioare explicite; argument universal elementar pentru valoarea corectă |
| 4.1, tip 2 | Cele cinci variante schimbau doar coeficientul aceleiași sume de pătrate | Cinci puteri diferite, 1–5; baza și identitatea exactă F(n+1)−F(n)=(n+1)^p |
| 4.1, tip 9 | Pentru produsele scurte, punctele de suspensie puteau repeta vizual ultimul factor | Toți factorii sunt scriși explicit |
| 4.1, tip 17 | Formulare greoaie despre divizibilitate | Se cere explicit cel mai mare D garantat să dividă N |
| 4.1, tip 23 | O singură substituție în identitatea deja afișată | Două aplicații succesive, pentru un produs de trei sume de pătrate |
| 4.1, tip 24 | Toate grilele foloseau doar schimbarea ultimului semn | Două grile testează blocul care extinde reprezentarea și adaugă 4; explicațiile dau baze pentru toate resturile modulo 4 |
| 4.1, tip 25 | Rafinarea repetată pornind de la un singur pătrat verifica doar ordinele 1 modulo 3 | Baze construibile 6/7/8 și rafinare +3; metoda acoperă toate ordinele ≥6 |
| 4.1, tipurile 26 și 30 | Construcțiile alese produceau doar un tip de paritate a numărului de laturi | Baze pentru ambele parități și numărarea explicită a laturilor; condiții de simetrie și lipsă de degenerări |
| 4.2, tip 5 | Explicația conținea termenul de programare „left” | Capătul inferior este numit și înlocuit numeric |
| 4.2, tip 12 | Lotul trata doar cazul fără repetare | Se cer împreună numărările cu și fără repetare; se distinge ordinea de simpla alegere a cifrelor |
| 4.2, tip 16 | Variante numerice generice, puțin informative | Variante care reflectă ignorarea nevidității, omiterea corecției finale sau confundarea obiectelor distincte cu cele identice |
| 4.2, tip 18 | Șablonul numeric putea propune 10 la o întrebare care cere o cifră | Variante strict între 0 și 9, inclusiv confuzii cu pozițiile vecine |
| 4.2, tip 32 | Notația {1,…,1} din primul exemplu era nefirească | Mulțimile sunt scrise integral |

## Cum se verifică

Din rădăcina backendului:

```powershell
$env:PYTHONIOENCODING = 'utf-8'
.\.venv\Scripts\python.exe scripts/verify_clasa_9_inductie_numarare.py
```

Scriptul verifică aritmetica exactă a opțiunilor numerice și identitățile polinomiale ale formulării inductive. Pentru numărare, reconstruiește cazurile prin enumerarea alegerilor, distribuțiilor, perechilor, divizorilor și soluțiilor întregi. Folosește direct factorialul pentru exponenți și zerouri, reconstruiește concatenarea și numără cifrele paginării.

Pentru geometrie verifică explicit tilingurile de bază 6/7/8: toate piesele sunt în pătrat, ariile se însumează la aria lui, iar interioarele nu se suprapun. Repetă apoi rafinările necesare exemplelor. Construiește și exemple de linii frânte simetrice și verifică vârfurile interioare și lipsa coliniarităților. Numărarea laturilor se face din contur și din segmentele frontierelor. Congruența pieselor rezultă din simetria stipulată în enunț, nu dintr-o comparație aproximativă de lungimi.

La pragurile exponențiale, verificarea pragului și a eșecului anterior este completată de inegalitatea raporturilor care închide inducția pentru toți indicii ulteriori. Un test finit nu este folosit drept demonstrație universală. Pentru sumele de puteri și blocul de patru pătrate, egalitățile sunt certificate prin operații exacte asupra coeficienților polinoamelor, nu numai prin valori de probă.

## Limitele concluziei

Aceasta este o revizie internă a grilelor create și a încadrării lor în catalog. Nu este o evaluare de către un profesor extern și nu certifică transcrierea sau dificultatea fiecărei probleme din scanare. Nu include o verificare vizuală a ecranelor aplicației.

`catalog.task_scope` diferențiază cele 225 de aplicații numerice, 20 de formule/argumente generale, 55 de cazuri particulare sau pași ai metodei și 15 construcții ghidate. La 4.1, unele sarcini sunt introductive față de familia olimpică din catalog. Acoperirea declarată este după tipologie și nu trebuie citită ca 315 de probleme independente cu dificultatea integrală a sursei. Metadatele rămân în JSON și nu modifică interfața sau modelul bazei de date.
