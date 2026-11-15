# Laborator matematic

URL: `/laborator-matematic/`.

Proiectul existent folosește mediul `.venv`, configurația
`FoculMatematicProiect.settings`, aplicația `FoculMatematic` pentru pagina principală,
`quizzes` pentru exerciții și KaTeX local pentru formule. Nu există un bundler JS
pentru site (proiectul mobil este separat). Demonstrația nu schimbă exercițiile,
progresul sau schema bazei de date.

## Pornire în PowerShell

Din `D:\Projects\Focul Matematic\FoculMatematic`:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe manage.py runserver 127.0.0.1:8000
```

Deschide http://127.0.0.1:8000/laborator-matematic/ . JSXGraph necesită acces
la CDN jsDelivr; ecuația și verificarea serverului funcționează și fără JS.

## Organizare și limite

- `FoculMatematic/math_tools/quadratics.py`: generare, LaTeX și verificare SymPy
  1.14.0. Două rădăcini întregi distincte în [-9, 9], coeficient principal nenul.
- `FoculMatematic/math_demo.py`: formular Django, CSRF și exercițiu păstrat în
  sesiunea serverului. Browserul primește ecuația și un identificator aleator,
  fără un câmp de soluții. Ecuația permite în mod firesc deducerea soluțiilor.
  Identificatorul respinge răspunsurile trimise din pagini rămase pe un exercițiu vechi.
- `templates/math_demo.html`: pagină separată, stilul și KaTeX existente.
- `static/core/js/math-demo.js` și `css/math-demo.css`: grafic dinamic și triunghi
  JSXGraph 1.12.2, încărcat exclusiv pe această pagină. Coeficienți între -10 și 10,
  pas 0.1; a=0 afișează o funcție de grad inferior. Punctele triunghiului sunt mobile.

Nu există parsare de expresii arbitrare, `eval`, modele noi sau migrare. Formularul
acceptă numai întregi limitați în [-100, 100]. Sesiunile folosesc backendul existent
al proiectului; exercițiul nou înlocuiește exercițiul vechi din aceeași sesiune.
Serviciul matematic poate fi reutilizat de generatoare viitoare. Integrarea în
evaluarea antrenamentelor existente nu face parte din această demonstrație.

## Verificare

```powershell
.\.venv\Scripts\python.exe manage.py check
.\.venv\Scripts\python.exe manage.py test FoculMatematic.test_math_demo
node --check static/core/js/math-demo.js
```

În browser: verifică un răspuns greșit, apoi cele două rădăcini în orice ordine;
generează altă ecuație; schimbă coeficienții, inclusiv a=0; mută vârfurile triunghiului.

Verificare efectuată la 30.10.2026: `manage.py check` fără probleme; 8 teste
noi ale demonstrației și 16 teste existente `quizzes.test_vector_workbench` trecute;
18 teste JavaScript `scripts/test_vector_workbench.cjs` trecute. În browser au fost
verificate răspunsul greșit/corect, schimbarea ecuației, modificarea tuturor celor
trei coeficienți, schimbarea efectivă a traseului SVG și deplasarea unui vârf cu
săgeata dreapta. Consola browserului nu a raportat erori sau avertismente.

Documentație oficială consultată:
[SymPy instalare](https://docs.sympy.org/latest/install.html),
[SymPy parsare și avertisment eval](https://docs.sympy.org/latest/modules/parsing.html),
[JSXGraph pornire](https://jsxgraph.org/home/start/gettingstarted/),
[JSXGraph versiuni](https://github.com/jsxgraph/jsxgraph/releases).
