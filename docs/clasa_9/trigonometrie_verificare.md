# Elemente de trigonometrie — verificare independentă

Verificatorul este separat de autorul problemelor. Nu importă generatorul,
nu modifică întrebări sau cheia de răspuns și nu importă date în Django.
Verdict final la 30 octombrie 2026: **ACCEPTAT — 585 de grile / 2340 de opțiuni**,
117 familii de catalog × 5 variante, în cele nouă lecții existente.
Totalurile sunt **35 / 40 / 80 / 25 / 40 / 45 / 75 / 105 / 140**.
Enunțurile sunt distincte atât pe lecție, cât și global.

## Metodă

`scripts/verify_clasa_9_trigonometrie.py` citește datele originale și expresia
cerută. Are parser AST cu operații matematice permise explicit, fără `eval`,
`sympify` pe șiruri, `parse_expr` sau importarea formulei răspunsului din generator.

- Verifică legătura fiecărei expresii și fiecărui binding cu enunțul efectiv.
- Evaluează expresia înainte de anulări algebrice, verificând fiecare numitor,
  domeniul tangentei/cotangentei, radicalii și realitatea valorii.
- Compară toate cele patru opțiuni cu rezultatul recalculat și verifică
  distinctivitatea matematică, exact un răspuns corect și rezultatul din explicație.
- Verifică separat unitățile unghiulare, arcele majore, cazurile isoscelului,
  cadranele/axele și datele configurațiilor geometrice.
- Semnele la argumente raționale în radiani sunt stabilite prin limite raționale
  ale lui π și cadrane, fără simplă aproximare zecimală a funcției.
- La paritate verifică și domeniul; opțiunile formează o partiție disjunctă,
  inclusiv funcția zero, atât pară cât și impară.
- Pentru sume/produse armonice finite, perioada principală se bazează pe
  frecvențele Fourier cu coeficienți nenuli. Independența exponențialelor impune
  faze întregi pentru fiecare frecvență; gcd-ul frecvențelor raționale dă cea mai
  mică perioadă, nu doar una garantată. La modul/pătrat se verifică și rețeaua
  zerourilor, iar tangenta/cotangenta păstrează domeniul natural.
- Neperiodicitatea exemplului cu frecvențe 1 și √2 se verifică prin raportul
  irațional al frecvențelor efective. Explicația elevului folosește separat
  părțile pară și impară ale funcției, care ar avea aceeași perioadă; auditul
  verifică și această descompunere. Nu este dedusă din eșantioane numerice.
- Sumele și produsele finite se recalculează din fiecare termen inițial,
  inclusiv limitele indicelui afișate. Unde numitorii sunt nenuli, rezultatul
  este comparat suplimentar cu o formulă închisă independentă. Pentru x=2π,
  suma sinusurilor este 0 și suma celor șase cosinusuri este 6; nu se folosește
  formula transformată care ar introduce 0/0 într-o expresie inițial definită.
- Recuperările din sume sau din date în cadrane sunt verificate prin sisteme
  algebrice sau produse de vectori unitari complecși, cu selecția semnelor și
  verificarea existenței. Înjumătățirea are sinus pozitiv pentru x∈(0,2π),
  dar cosinusul jumătății poate fi negativ.

În primul lot s-au respins suplimentar trei coruperi intenționate în memorie:
cheie de răspuns schimbată, binding diferit față de enunț și text de opțiune
incompatibil cu valoarea ei. Parserul respinge și numitori zero, tg(π/2), ctg(0),
radicali negativi sau cod arbitrar. Aceste verificări nu modifică sursele.
Au fost respinse încă trei coruperi: limite de sumare schimbate numai în
metadate, expresie inițială singulară și etichetă de paritate ambiguă.

## Probleme găsite și remedieri confirmate

1. Explicația neperiodicității conținea «±a, ±a√2», interpretată de rendererul
   automat ca o comandă KaTeX invalidă `\pma`. Autorul a folosit întâi LaTeX
   explicit și apoi un argument elementar prin paritate. Rularea strictă finală
   a trecut pentru toate cele **4996 de fragmente matematice**.
2. Cinci enunțuri ale produselor de cosinusuri erau identice între lecțiile 8
   și 9. La solicitarea coordonatorului, autorul a schimbat argumentul în familia
   §7.3; auditul global confirmă **585 de enunțuri distincte** și răspunsuri corecte.
3. La solicitarea verificării de frontieră, autorul a introdus variante cu x=2π
   la sumele de sinusuri și cosinusuri, cu explicații separate pentru formula
   închisă neaplicabilă. Sumele directe și explicațiile sunt corecte.

Nu au rămas erori matematice sau de randare cunoscute în lotul verificat.
Verificatorul nu a modificat generatoarele sau întrebările și nu a scris în DB;
importul și verificările de păstrare a progresului sunt coordonate separat.

## Rulare

```powershell
.\.venv\Scripts\python.exe -X utf8 scripts/verify_clasa_9_trigonometrie.py
node scripts/verify_trigonometrie_rendering.cjs
```

În timpul construirii loturilor se pot folosi `--partial` și `--lesson N` la
verificatorul matematic, respectiv `--partial` la cel de randare. Rularea completă
cere toate cele 585 de întrebări și câte cinci variante pentru fiecare tip G3.
Randarea folosește parserul și versiunea KaTeX efective din pagina Antrenare.

## Limite

Auditul recalculează variantele concrete și validează raționamente specifice.
Nu este un demonstrator automat general de identități sau teoreme. Enunțurile și
explicațiile sunt și revizuite matematic; adaptările de demonstrații în calcule
numerice sau cazuri particulare trebuie declarate în metadatele fiecărei grile.
În lot, **355 de grile** sunt marcate `partial_explicit_case`, iar **230** sunt
`adapted_grid`. Numărul celor 117 etichete de catalog nu certifică dificultatea
integrală a demonstrațiilor originale; auditul acceptă variantele concrete și
limitele declarate, nu o afirmație de acoperire integrală a tuturor subcazurilor.
