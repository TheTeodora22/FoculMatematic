"""Generează prima lecție interactivă de algebră pentru clasa a IX-a."""
import json
from pathlib import Path


def alg(text, mode, data, answers, explanation):
    return {
        "text": text, "type": "algebra_workbench", "format": "interactive", "points": 10,
        "explanation": explanation, "interactive": {"mode": mode, **data, "answers": answers},
    }


def field(key, label):
    return {"key": key, "label": label}


def grid(text, correct, wrong, explanation):
    values = [correct, *wrong]
    order = [1, 3, 0, 2]
    return {
        "text": text, "type": "multiple_choice", "format": "grid", "points": 10,
        "explanation": explanation,
        "options": [{"text": values[index], "is_correct": index == 0} for index in order],
    }


def build_questions():
    q = []

    # 1. Simplifică expresia
    q += [
        alg("Simplifică expresia și scrie rezultatul final.", "simplify", {"expression": "(2x − 3)² − (x − 3)²", "fields": [field("result", "Rezultat")]}, {"result": "3x²−6x"}, "Dezvoltăm cele două pătrate și reducem termenii asemenea: 4x²−12x+9−x²+6x−9=3x²−6x."),
        alg("Simplifică folosind formula diferenței de pătrate.", "simplify", {"expression": "(2√2 − 3a)(2√2 + 3a)", "fields": [field("result", "Rezultat")]}, {"result": "8−9a²"}, "Aplicăm (u−v)(u+v)=u²−v²: (2√2)²−(3a)²=8−9a²."),
        alg("Simplifică puterile, pentru a ≠ 0.", "simplify", {"expression": "a⁵ · a² : a³", "fields": [field("result", "Rezultat")]}, {"result": "a⁴"}, "Adunăm exponenții la înmulțire și îl scădem la împărțire: a^(5+2−3)=a⁴."),
        alg("Calculează puterea monomului.", "simplify", {"expression": "(−2a)³", "fields": [field("result", "Rezultat")]}, {"result": "−8a³"}, "Ridicăm la cub atât coeficientul, cât și litera: (−2)³a³=−8a³."),
        alg("Simplifică expresia cu radicali.", "simplify", {"expression": "√50 − 2√8", "fields": [field("result", "Rezultat")]}, {"result": "√2"}, "√50=5√2 și 2√8=4√2, deci diferența este √2."),
    ]

    # 2. Completează regula
    q += [
        alg("Completează formula pătratului unei sume.", "complete_rule", {"expression": "(a + b)² = a² + □ + b²", "fields": [field("missing", "Termenul lipsă")]}, {"missing": "2ab"}, "Termenul din mijloc este dublul produsului: 2ab."),
        alg("Completează regula puterilor cu aceeași bază.", "complete_rule", {"expression": "aᵐ · aⁿ = a□", "fields": [field("missing", "Exponentul rezultat")]}, {"missing": "m+n"}, "La înmulțirea puterilor cu aceeași bază, exponenții se adună."),
        alg("Completează regula împărțirii puterilor, a ≠ 0.", "complete_rule", {"expression": "aᵐ : aⁿ = a□", "fields": [field("missing", "Exponentul rezultat")]}, {"missing": "m−n"}, "La împărțire, exponenții se scad."),
        alg("Completează proprietatea elementului neutru.", "complete_rule", {"expression": "a · □ = a", "fields": [field("missing", "Numărul lipsă")]}, {"missing": "1"}, "Numărul 1 este element neutru pentru înmulțire."),
    ]

    # 3. Adevărat sau fals
    q += [
        alg("Decide dacă afirmația este adevărată sau falsă.", "true_false", {"expression": "Pentru orice a real, √(a²) = a.", "choices": ["Adevărat", "Fals"]}, {"choice": 1}, "În general √(a²)=|a|. Egalitatea cu a este sigură numai pentru a≥0."),
        alg("Decide dacă afirmația este adevărată sau falsă.", "true_false", {"expression": "Pentru a,b ≥ 0, √a · √b = √(ab).", "choices": ["Adevărat", "Fals"]}, {"choice": 0}, "Aceasta este regula produsului radicalilor pentru numere nenegative."),
        alg("Decide dacă afirmația este adevărată sau falsă.", "true_false", {"expression": "(a + b)² = a² + b² pentru orice a,b reale.", "choices": ["Adevărat", "Fals"]}, {"choice": 1}, "Lipsește termenul 2ab; formula corectă este a²+2ab+b²."),
        alg("Decide dacă afirmația este adevărată sau falsă.", "true_false", {"expression": "Orice număr rațional este număr real.", "choices": ["Adevărat", "Fals"]}, {"choice": 0}, "Mulțimea numerelor raționale este inclusă în mulțimea numerelor reale."),
    ]
    for question in q[-4:]:
        question["format"] = "true_false"

    # 4. Potrivește expresia cu rezultatul
    q += [
        alg("Potrivește fiecare expresie cu forma sa simplificată.", "match", {"pairs": [{"left": "(a+b)²", "right": "a²+2ab+b²"}, {"left": "(a−b)²", "right": "a²−2ab+b²"}, {"left": "(a−b)(a+b)", "right": "a²−b²"}], "options": ["a²−b²", "a²+2ab+b²", "a²−2ab+b²"]}, {"match:0": 1, "match:1": 2, "match:2": 0}, "Folosim cele trei identități remarcabile fundamentale."),
        alg("Potrivește fiecare putere cu rezultatul corect.", "match", {"pairs": [{"left": "2³·2⁴", "right": "2⁷"}, {"left": "5⁶:5²", "right": "5⁴"}, {"left": "(3²)⁴", "right": "3⁸"}], "options": ["3⁸", "2⁷", "5⁴"]}, {"match:0": 1, "match:1": 2, "match:2": 0}, "La produs adunăm exponenții, la cât îi scădem, iar la puterea unei puteri îi înmulțim."),
        alg("Potrivește radicalii cu formele simplificate.", "match", {"pairs": [{"left": "√12", "right": "2√3"}, {"left": "√45", "right": "3√5"}, {"left": "√72", "right": "6√2"}], "options": ["6√2", "2√3", "3√5"]}, {"match:0": 1, "match:1": 2, "match:2": 0}, "Scoatem de sub radical cel mai mare factor pătrat perfect."),
    ]

    # 5. Detectivul greșelilor
    q += [
        alg("Găsește primul pas greșit în dezvoltare.", "error", {"steps": ["(a+3)²", "= a²+3a+9", "= a²+6a+9"]}, {"error": 1}, "La pătratul sumei termenul din mijloc este 2·a·3=6a; pasul 2 este primul greșit."),
        alg("Găsește primul pas greșit în calculul puterilor.", "error", {"steps": ["a⁵·a³:a²", "= a⁸:a²", "= a⁴"]}, {"error": 2}, "a⁸:a²=a⁶, nu a⁴."),
        alg("Găsește primul pas greșit în simplificarea radicalului.", "error", {"steps": ["√48", "= √(16·3)", "= 16√3", "= 4√3"]}, {"error": 2}, "√16=4, deci primul pas greșit este 16√3."),
        alg("Găsește primul pas greșit în regula semnelor.", "error", {"steps": ["−(2a−5)", "= −2a−5", "Forma corectă este −2a+5"]}, {"error": 1}, "Minusul din fața parantezei schimbă semnul fiecărui termen."),
    ]

    # 6. Construiește identitatea
    q += [
        alg("Construiește membrul drept al identității.", "identity_builder", {"target": "(a+b)² = ?", "pieces": ["a²", "+2ab", "+b²", "−2ab"]}, {"pieces": "0,1,2"}, "Pătratul unei sume este a²+2ab+b²."),
        alg("Construiește membrul drept al identității.", "identity_builder", {"target": "(x−y)² = ?", "pieces": ["x²", "−2xy", "+y²", "+2xy"]}, {"pieces": "0,1,2"}, "Pătratul diferenței este x²−2xy+y²."),
        alg("Construiește membrul drept al identității.", "identity_builder", {"target": "(m−n)(m+n) = ?", "pieces": ["m²", "−n²", "+n²", "−2mn"]}, {"pieces": "0,1"}, "Produsul sumei și diferenței este diferența pătratelor."),
    ]

    # 7. Paranteze și ordinea calculelor
    q += [
        alg("Alege parantezarea care produce rezultatul 49.", "parentheses", {"expression": "10 − 3 · 2 + 5", "choices": ["(10−3)·(2+5)", "10−(3·2)+5", "(10−3·2)+5", "10−3·(2+5)"]}, {"choice": 0}, "(10−3)·(2+5)=7·7=49."),
        alg("Alege parantezarea care produce rezultatul 64.", "parentheses", {"expression": "12 − 4 · 3 + 5", "choices": ["(12−4)·(3+5)", "12−(4·3)+5", "(12−4·3)+5", "12−4·(3+5)"]}, {"choice": 0}, "(12−4)·(3+5)=8·8=64."),
        alg("Alege ordinea corectă a operațiilor.", "parentheses", {"expression": "3 + 2·(5−1)²", "choices": ["paranteză, putere, înmulțire, adunare", "putere, paranteză, adunare, înmulțire", "adunare, paranteză, putere, înmulțire", "înmulțire, putere, paranteză, adunare"]}, {"choice": 0}, "Se calculează întâi paranteza, apoi puterea, înmulțirea și la final adunarea."),
    ]

    # 8. Radicali cu pași
    q += [
        alg("Simplifică radicalul completând etapele.", "radical_steps", {"expression": "√75", "stages": ["Descompune 75 ca produs între un pătrat perfect și alt factor.", "Scoate pătratul perfect de sub radical."], "fields": [field("decomposition", "Descompunere"), field("result", "Rezultat final")]}, {"decomposition": "25·3", "result": "5√3"}, "75=25·3, deci √75=5√3."),
        alg("Simplifică radicalul completând etapele.", "radical_steps", {"expression": "√98", "stages": ["Identifică factorul pătrat perfect.", "Simplifică."], "fields": [field("decomposition", "Descompunere"), field("result", "Rezultat final")]}, {"decomposition": "49·2", "result": "7√2"}, "98=49·2, deci √98=7√2."),
        alg("Introdu factorul sub radical, pentru x≥0.", "radical_steps", {"expression": "3√5", "stages": ["Ridică factorul exterior la pătrat.", "Înmulțește sub radical."], "fields": [field("square", "Pătratul factorului"), field("result", "Rezultat final")]}, {"square": "9", "result": "√45"}, "3√5=√(3²·5)=√45."),
        alg("Calculează produsul radicalilor.", "radical_steps", {"expression": "√6 · √24", "stages": ["Unește radicalii.", "Extrage rădăcina."], "fields": [field("product", "Radicalul obținut"), field("result", "Rezultat final")]}, {"product": "√144", "result": "12"}, "√6·√24=√144=12."),
    ]

    # 9. Compară valori
    q += [
        alg("Compară cele două numere.", "compare", {"expression": "√50  □  7", "choices": ["<", "=", ">"]}, {"choice": 2}, "Deoarece 50>49, rezultă √50>√49=7."),
        alg("Compară cele două numere.", "compare", {"expression": "3√2  □  √18", "choices": ["<", "=", ">"]}, {"choice": 1}, "√18=√(9·2)=3√2."),
        alg("Compară puterile.", "compare", {"expression": "2⁶  □  4³", "choices": ["<", "=", ">"]}, {"choice": 1}, "4³=(2²)³=2⁶."),
        alg("Compară numerele reale.", "compare", {"expression": "−√9  □  −2", "choices": ["<", "=", ">"]}, {"choice": 0}, "−√9=−3, iar −3<−2."),
    ]

    # 10. Valoarea necunoscută
    q += [
        alg("Determină numărul real pozitiv x.", "unknown", {"expression": "x² = 81, x>0", "fields": [field("x", "x") ]}, {"x": "9"}, "Numărul pozitiv al cărui pătrat este 81 este 9."),
        alg("Determină x.", "unknown", {"expression": "√x = 7", "fields": [field("x", "x") ]}, {"x": "49"}, "Ridicăm la pătrat: x=49."),
        alg("Determină x, știind că x ≠ 0.", "unknown", {"expression": "x⁵ : x² = 27", "fields": [field("x", "x") ]}, {"x": "3"}, "x³=27, deci x=3."),
        alg("Determină suma a+b.", "unknown", {"expression": "(a+b)²=121 și a+b>0", "fields": [field("sum", "a+b") ]}, {"sum": "11"}, "Din (a+b)²=121 și condiția de pozitivitate rezultă a+b=11."),
    ]

    # 11. Verifică identitatea pentru valori date
    q += [
        alg("Calculează ambii membri și verifică identitatea.", "verify_identity", {"identity": "(a+b)² = a²+2ab+b²", "values": ["a=2", "b=3"], "fields": [field("left", "Membrul stâng"), field("right", "Membrul drept")]}, {"left": "25", "right": "25", "verdict": 0}, "Ambii membri sunt egali cu 25, deci identitatea se verifică."),
        alg("Calculează ambii membri și verifică egalitatea propusă.", "verify_identity", {"identity": "(a−b)² = a²−b²", "values": ["a=5", "b=2"], "fields": [field("left", "Membrul stâng"), field("right", "Membrul drept")]}, {"left": "9", "right": "21", "verdict": 1}, "9≠21; egalitatea propusă nu este o identitate."),
        alg("Calculează ambii membri și verifică identitatea.", "verify_identity", {"identity": "(a−b)(a+b)=a²−b²", "values": ["a=7", "b=4"], "fields": [field("left", "Membrul stâng"), field("right", "Membrul drept")]}, {"left": "33", "right": "33", "verdict": 0}, "(7−4)(7+4)=3·11=33 și 49−16=33."),
    ]

    # 12. Sortează pe familii
    q += [
        alg("Încadrează fiecare număr în cea mai mică mulțime indicată.", "classify", {"pairs": [{"left": "7", "right": "N"}, {"left": "−4", "right": "Z"}, {"left": "2/3", "right": "Q"}, {"left": "√2", "right": "R\\Q"}], "options": ["N", "Z", "Q", "R\\Q"]}, {"match:0": 0, "match:1": 1, "match:2": 2, "match:3": 3}, "7 este natural, −4 este întreg, 2/3 este rațional, iar √2 este irațional."),
        alg("Încadrează expresiile după tip.", "classify", {"pairs": [{"left": "a⁵", "right": "putere"}, {"left": "√13", "right": "radical"}, {"left": "(a+b)²", "right": "expresie algebrică"}], "options": ["putere", "radical", "expresie algebrică"]}, {"match:0": 0, "match:1": 1, "match:2": 2}, "Recunoaștem forma dominantă a fiecărei expresii."),
        alg("Încadrează fiecare număr în cea mai mică mulțime indicată.", "classify", {"pairs": [{"left": "0", "right": "N"}, {"left": "−11", "right": "Z"}, {"left": "0,(3)", "right": "Q"}, {"left": "π", "right": "R\\Q"}], "options": ["N", "Z", "Q", "R\\Q"]}, {"match:0": 0, "match:1": 1, "match:2": 2, "match:3": 3}, "0 este natural în convenția lecției; zecimala periodică este rațională, iar π este irațional."),
    ]

    # 13. Media aritmetică
    q += [
        alg("Calculează media aritmetică a numerelor.", "average", {"expression": "6, 9, 12", "fields": [field("sum", "Suma"), field("count", "Numărul valorilor"), field("mean", "Media") ]}, {"sum": "27", "count": "3", "mean": "9"}, "Media este 27:3=9."),
        alg("Determină numărul lipsă folosind media aritmetică.", "average", {"expression": "Media numerelor 8, x și 14 este 11.", "fields": [field("total", "Suma celor trei numere"), field("x", "x") ]}, {"total": "33", "x": "11"}, "Suma trebuie să fie 3·11=33, deci x=33−8−14=11."),
        alg("Calculează media aritmetică.", "average", {"expression": "√4, √9, √25", "fields": [field("values", "Valorile obținute"), field("mean", "Media") ]}, {"values": "2,3,5", "mean": "10/3"}, "Valorile sunt 2,3,5; suma este 10, deci media este 10/3."),
    ]

    # 14. Lanț de transformări
    q += [
        alg("Alege transformarea corectă la fiecare pas.", "transform_chain", {"expression": "(x+2)²−x²", "steps": [{"options": ["x²+4x+4−x²", "x²+2x+4−x²", "2x²+4"]}, {"options": ["4x+4", "2x+4", "x²+4"]}]}, {"step:0": 0, "step:1": 0}, "Dezvoltăm pătratul sumei, apoi reducem termenii x²."),
        alg("Alege transformarea corectă la fiecare pas.", "transform_chain", {"expression": "√108", "steps": [{"options": ["√(36·3)", "√(18·6)", "√(9·9)"]}, {"options": ["6√3", "3√12", "18√3"]}]}, {"step:0": 0, "step:1": 0}, "108=36·3, iar √36=6."),
        alg("Alege transformarea corectă la fiecare pas.", "transform_chain", {"expression": "a⁷:a²·a", "steps": [{"options": ["a⁵·a", "a⁹·a", "a⁵:a"]}, {"options": ["a⁶", "a⁵", "a⁴"]}]}, {"step:0": 0, "step:1": 0}, "Întâi a⁷:a²=a⁵, apoi a⁵·a=a⁶."),
    ]

    # 15. Grile simple
    q += [
        grid("Elementul neutru al adunării în R este:", "0", ["1", "−1", "nu există"], "Pentru orice a real, a+0=a."),
        grid("Inversul numărului real nenul a este:", "1/a", ["−a", "a", "0"], "a·(1/a)=1 pentru a≠0."),
        grid("Rezultatul lui (2³)⁴ este:", "2¹²", ["2⁷", "2⁸", "8⁴"], "La puterea unei puteri înmulțim exponenții: 3·4=12."),
        grid("Forma simplificată a lui √32 este:", "4√2", ["16√2", "2√8", "8√2"], "√32=√(16·2)=4√2."),
        grid("Care număr este irațional?", "√7", ["0,25", "−3", "2/9"], "√7 nu poate fi scris ca raport al două numere întregi."),
    ]

    totals = {}
    for question in q:
        totals[question["text"]] = totals.get(question["text"], 0) + 1
    occurrences = {}
    for question in q:
        base = question["text"]
        if totals[base] > 1:
            occurrences[base] = occurrences.get(base, 0) + 1
            question["text"] = f"{base.rstrip('.')} — varianta {occurrences[base]}."

    assert len(q) == 55, len(q)
    assert len({question["text"] for question in q}) == 55
    return q


def main():
    output = Path(__file__).resolve().parents[1] / "clasa_9_u01_l01_multimea_numerelor_reale_operatii_ordonare_modul_si_aproximari.json"
    payload = {
        "title": "Mulțimea numerelor reale. Operații algebrice, puteri și radicali",
        "description": "Clasa a 9-a · Mulțimi și elemente de logică matematică",
        "difficulty": "medium",
        "questions": build_questions(),
    }
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Scrise {len(payload['questions'])} exerciții în {output.name}")


if __name__ == "__main__":
    main()
