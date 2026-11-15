# Funcția de gradul I — acoperire și verificare

Data: 30 octombrie 2026.

Au fost completate exclusiv cele cinci lecții existente din capitolul „Funcția de gradul I”, clasa a IX-a. Sursa tipologiei este `D:/Carti Mate/output/catalog/A3_catalog.md`, p. 116–128. Lecțiile erau goale în JSON și în baza locală înaintea acestui lot.

| Lecție din aplicație | Secțiune catalog | Tipuri | Grile | ID quiz local |
|---|---|---:|---:|---:|
| Definiție și reprezentare grafică | A3.1, p. 116–119 | 21 | 105 | 198 |
| Interpretarea proprietăților. Monotonie și semn | A3.2, p. 120–121 | 10 | 50 | 199 |
| Inecuații și studiul semnului | A3.3, p. 122–124 | 14 | 70 | 200 |
| Poziția relativă a două drepte | A3.4, p. 125–126 | 8 | 40 | 201 |
| Sisteme de ecuații și inecuații | A3.5, p. 126–128 | 10 | 50 | 202 |
| **Total** | | **63** | **315** | |

Fiecare tip are cinci variante originale. Fiecare întrebare are patru opțiuni distincte, exact una corectă și o explicație în română. Nu sunt transcrieri din scanările culegerii. Tipurile din A3.4 includ rezolvarea sistemelor și interpretarea lor geometrică și se află în lecția despre poziția dreptelor, conform ordinii celor cinci secțiuni din catalog.

## Ce este acoperit

- Interceptări, distanțe și arii, reconstrucția funcțiilor, compuneri, involuții și parametri.
- Domenii restrânse, legi pe ramuri, parte întreagă și sign, prelungiri pare și impare, distanțe pe axă și valori iraționale.
- Monotonie, salturi la praguri, compuneri pe ℚ/ℝ∖ℚ, condiții diofantice și parametri.
- Semne, rapoarte și poli, funcții max/min și module, discuții după coeficient nul/pozitiv/negativ și condiții uniforme pe interval.
- Toate pozițiile a două drepte: verticale paralele, perpendiculare, coincidente și secante neperpendiculare.
- Sisteme liniare, reciproce, module, expresii raționale comune, cazuri singulare și probabilitatea soluției unice.
- Sisteme de inecuații, capete mobile, intersecții parametrice, pozitivitate simultană și semne contrare.

## Adaptarea la formatul grilă

Cerințele grafice se rezolvă prin alegerea perechilor de puncte, a legii pe ramuri sau a descrierii complete a graficului. La reconstrucția poligonală sunt date coordonatele și semidreptele în cuvinte; nu este inclusă o imagine a desenului. Acoperirea este tipologică, nu verificarea abilității de a trasa efectiv un grafic.

Cerințele de demonstrație sunt transformate în alegerea unei caracterizări, a formulei sau a parametrului; explicația prezintă argumentul și cazurile relevante. Nu pretindem că selectarea unei grile echivalează cu redactarea unei demonstrații. Revizuirea independentă de către un profesor rămâne utilă.

## Reproducere și verificare

Din directorul backend:

```powershell
.\.venv\Scripts\python.exe data/quizzes/generators/gen_clasa_9_gradul_i.py
.\.venv\Scripts\python.exe scripts/verify_clasa_9_gradul_i.py
```

Generatorul produce numai cele cinci JSON-uri `clasa_9_u03_l01`–`l05`. În fiecare întrebare, `catalog` păstrează secțiunea, tipul și numărul variantei. Metadatele `verification` păstrează valorile matematice ale opțiunilor în ordinea afișării; nu se importă în modelul întrebării.

Verificatorul nu importă generatorul. Folosește fracții exacte, substituție în ecuațiile inițiale, eliminare gaussiană, determinanți și produse scalare, enumerare pentru constrângerile întregi și probabilități, precum și verificarea fiecărei celule determinate de capete și poli pentru mulțimile de soluții. Pentru funcțiile pe ramuri verifică valorile la praguri și în ramuri. De asemenea, verifică corespondența dintre valorile opțiunilor din metadate și textul afișat.

Rezultate locale:

- 315 întrebări, 63 de tipuri × 5 variante, 1.260 de opțiuni verificate; exact o opțiune validă matematic pentru fiecare întrebare.
- Enunțuri unice în fiecare lecție, explicații prezente, opțiuni de cel mult 255 de caractere, format validat de loaderul Django.
- Regenerare identică la compararea SHA-256 pentru toate cele cinci JSON-uri.
- 2.914 fragmente matematice acceptate de KaTeX cu `throwOnError: true`; aceasta verifică sintaxa, nu aspectul tuturor paginilor pe mobil.
- Import local țintit prin `seed_quizzes --file clasa_9/<nume>.json`, fără importarea întregii bănci.
- Importul repetat păstrează ID-urile celor 315 întrebări și 1.260 de opțiuni și înregistrările de progres aferente. La primul import lecțiile erau goale; nu au fost necesare mutări între capitole.
- `manage.py check` fără probleme.

Acest lot nu schimbă frontendul, modelele, rutele sau conturile demo/admin și nu adaugă exerciții în alte capitole.
