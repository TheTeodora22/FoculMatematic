# Elemente de trigonometrie — creare și verificare separate

**Finalizat: 585 de grile originale, importate în cele nouă lecții.** Lotul a fost
început la 30 octombrie 2026 și integrarea finală a fost verificată la 31 octombrie.
La cererea utilizatorului au lucrat doi agenți: `trigo_writer` a creat problemele,
iar `trigo_verifier` le-a verificat independent și a cerut corecturi. Coordonatorul
a făcut importul după acceptarea explicită a întregului lot.

| Lecție existentă | Grile | Quiz ID | Tipuri G3 |
|---|---:|---:|---|
| Unghiuri și arce | 35 | 219 | §1: 7 × 5 |
| Generalizarea noțiunii de unghi | 40 | 220 | §2: 8 × 5 |
| Sinus, cosinus, tangentă, cotangentă | 80 | 221 | §3.1: 16 × 5 |
| Semnul funcțiilor trigonometrice | 25 | 222 | §3.2: 5 × 5 |
| Reducerea la primul cadran | 40 | 223 | §3.3: 8 × 5 |
| Paritate, imparitate și periodicitate | 45 | 224 | §3.4: 9 × 5 |
| Relații ale aceluiași unghi | 75 | 225 | §4: 15 × 5 |
| Suma și diferența unghiurilor | 105 | 226 | §5: 21 × 5 |
| Transformări, sume și produse | 140 | 227 | §6: 17 × 5; §7: 11 × 5 |
| **Total** | **585** | | **117 etichete × 5** |

Sursa tipologică: `D:/Carti Mate/output/catalog/G3_catalog.md`, p. 204–229.
Enunțurile și datele sunt originale. Secțiunea §7 se integrează ca aplicații
de sume și produse în lecția existentă 9, fără adăugarea sau mutarea lecțiilor.
Lecțiile erau goale la începutul sarcinii.

## Metoda de audit

Generatorul publică datele originale și expresiile nesimplificate pentru audit;
verificatorul nu importă generatorul și nu preia un rezultat `expected`.
Opțiunile sunt legate de forma LaTeX afișată și comparate matematic cu rezultatul
recalculat independent. Domeniile sunt verificate pe expresia originală, înainte
ca simplificarea să poată elimina un numitor nul sau un pol al tangentei.

Se verifică unitățile unghiurilor, cadranele și frontierele, semnele radicalilor,
domeniile tangentei/cotangentei, paritatea pe domenii simetrice și diferența
dintre perioadă garantată și perioadă principală. Neperiodicitatea frecvențelor
incomensurabile necesită raționament analitic, nu doar eșantioane numerice.
Un audit simbolic nu înlocuiește demonstrațiile generale ale tuturor tipurilor
olimpice; adaptările de calcul/concluzie și cazurile parțiale sunt declarate.

Fișierele de lucru:

- `data/quizzes/generators/gen_clasa_9_trigonometrie.py`, modulul
  `trigonometrie_advanced.py` și `trigonometry_type_names.json`, deținute de autor.
- `scripts/verify_clasa_9_trigonometrie.py` și
  `scripts/verify_trigonometrie_rendering.cjs`, deținute de verificator.
- Rapoartele separate `trigonometrie_autor.md` și `trigonometrie_verificare.md`.

## Rezultate și limite

Au trecut toate cele **2340 de opțiuni**, cu patru opțiuni distincte matematic
și o singură cheie corectă pentru fiecare grilă. Cele 585 de enunțuri sunt unice
în întregul capitol, iar regenerarea celor nouă surse este identică octet cu octet.
**4996 de fragmente matematice** au trecut randarea KaTeX strictă cu parserul
și versiunea folosite efectiv în Antrenare. `manage.py check` nu raportează probleme.

În timpul revizuirii au fost corectate o formulare cu simbolul ± care producea
o comandă KaTeX invalidă și cinci enunțuri duplicate între lecțiile 8 și 9.
Sumele finite au primit și variantele cu x=2π: expresia inițială este definită,
dar formula închisă uzuală ar produce 0/0, astfel se calculează direct.
Verificatorul a respins și șase coruperi deliberate în memorie: cheie schimbată,
binding diferit față de enunț, text incompatibil al opțiunii, limite modificate
ale unei sume, singularitate în expresia inițială și etichetă ambiguă de paritate.

**355 de grile** sunt marcate `partial_explicit_case`: calcule sau concluzii
concrete care nu înlocuiesc demonstrația generală ori dificultatea integrală a
tipului original. Restul de 230 sunt marcate `adapted_grid`. Etichetele de
catalog indică sursa tipologică, nu certifică toate problemele din culegere.
Rapoartele separate ale autorului și verificatorului detaliază această limită.

Importul a fost tranzacțional și limitat la cele nouă fișiere `u07`, apoi repetat
pentru verificarea stabilității celor 585 de ID-uri și 2340 de opțiuni. Nu existau
întrebări sau progres anterior în aceste lecții. Întrebările, opțiunile și progresul
celorlalte capitole sunt neschimbate, comparate înainte și după import.
Nu s-au schimbat manifestul, schema DB, conturile, backendul sau frontendul.

Pagina capitolului și prima/ultima întrebare din fiecare lecție au trecut
randarea prin view-urile Django, fără răspunsuri trimise sau sesiuni de test
persistate. În browser sunt confirmate toate totalurile și afișarea sumei
cosinusurilor la x=2π, fără erori JavaScript. Serverul local rulează pe portul 8000.

```powershell
.\.venv\Scripts\python.exe -X utf8 data/quizzes/generators/gen_clasa_9_trigonometrie.py
.\.venv\Scripts\python.exe -X utf8 scripts/verify_clasa_9_trigonometrie.py
node scripts/verify_trigonometrie_rendering.cjs
```

[Deschide capitolul local](http://127.0.0.1:8000/quizzes/clasa/9/trigonometrie/).
