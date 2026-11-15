# Verificări automate P0

Data rulării: 29 octombrie 2026. Testele cer comportamentul dorit și eșuează cât timp problema există. Nu folosesc `expectedFailure` și nu repară codul aplicației. Prin urmare, și rularea generală `manage.py test` va rămâne roșie până la rezolvarea problemelor sau aprobarea unei schimbări a cerințelor.

Din directorul backend `FoculMatematic`, rulează:

```powershell
.\.venv\Scripts\python.exe manage.py test quizzes.test_launch_p0 --verbosity 2
node --test scripts/test_training_p0.cjs
```

Testele Django creează și distrug o bază separată de test. Nu rulează seed pe baza locală reală. Testele de conținut citesc JSON-urile, fără să le modifice. Testele JavaScript execută handlerii reali din training.js într-un mediu simulat cu răspunsuri de rețea controlate; nu folosesc rețeaua, conturile sau browserul utilizatorului. Nu substituie testarea pe dispozitive reale.

## Rezultatul inițial

| Verificare | Rezultat | Punct checklist |
|---|---|---|
| Aceeași cerere de test clasic trimisă din nou | Eșuează: XP crește de la 10 la 20 | P0-18 |
| Conturile demo/admin într-o bază trecută de la DEBUG=True la False | Eșuează pentru ambele conturi: parolele cunoscute încă autentifică | P0-25 |
| Pagina de recuperare se poate deschide | Trece; corectează suspiciunea inițială privind șablonul absent | P0-09 |
| Link către recuperare în login | Eșuează: link absent | P0-09 |
| Soluția nu este trimisă anticipat în payloadul de antrenare | Eșuează: correctOptionId este prezent | P0-27 |
| O opțiune de la altă întrebare este respinsă fără XP | Trece | P0-27 |
| Fiecare întrebare are explicație | Eșuează: 50 lipsă în lecția de scriere/citire a numerelor naturale | P0-20 |
| Grilele au un răspuns corect și texte distincte | Eșuează: variante duplicate la întrebările 35 și 37 din aceeași lecție | P0-21 |
| Salvare eșuată la grilă: întrebarea rămâne de rezolvat | Eșuează: rămâne marcată corect | P0-17 |
| Navigare în timpul salvării unei grile | Eșuează: răspunsul întârziat randează întrebarea curentă, diferită | P0-17 |
| Navigare în timpul salvării unui interactiv | Eșuează: se colorează celula întrebării următoare | P0-17 |
| Salvare reușită fără navigare | Trece | Control JS |
| Salvare eșuată la interactiv fără navigare | Trece: eroare vizibilă și progres nemarcat | Control JS |

Total: **13 teste, 4 trec și 9 eșuează**. Django raportează 7 eșecuri de aserțiune pentru 6 metode eșuate, deoarece conturile demo și admin sunt două subteste ale aceleiași metode. JavaScript: 2 trecute, 3 eșuate.

Rapoarte locale de rulare: `logs/audit_p0_regression_backend.txt` și `logs/audit_p0_regression_frontend.txt`. Aceste fișiere sunt ignorate de Git; testele și acest document pot fi păstrate în repository.

## Limitele testelor

Testul despre cheia de corectare presupune că soluțiile nu trebuie expuse înainte de răspuns. Dacă afișarea lor în Antrenare este o decizie de produs acceptată, trebuie schimbată explicit această cerință; testul nu demonstrează divulgarea unei parole.

Testul de XP verifică retransmiterea aceleiași cereri, nu interzicerea tuturor încercărilor noi legitime. Nu simulează încă cereri simultane pe PostgreSQL. Concurența, livrarea reală a emailului, restaurarea backupului, HTTPS de producție, accesibilitatea integrală și echivalența matematică a variantelor rămân verificări separate.
