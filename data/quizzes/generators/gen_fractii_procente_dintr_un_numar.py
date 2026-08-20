"""Generează lecția despre fracții și procente dintr-o cantitate."""

import json
from fractions import Fraction
from pathlib import Path


def grid(text, correct, wrong, explanation):
    values, order = [str(correct), *map(str, wrong)], [2, 0, 3, 1]
    return {"text": text, "type": "multiple_choice", "format": "grid", "points": 10,
            "explanation": explanation,
            "options": [{"text": values[i], "is_correct": i == 0} for i in order]}


def true_false(text, answer, explanation):
    return {"text": text, "type": "multiple_choice", "format": "true_false", "points": 10,
            "explanation": explanation,
            "options": [{"text": value, "is_correct": value == answer} for value in ("Adevărat", "Fals")]}


def interactive(text, mode, data, explanation):
    return {"text": text, "type": "fraction_percent", "format": "interactive", "points": 10,
            "explanation": explanation, "interactive": {"mode": mode, **data}}


def field(key, label):
    return {"key": key, "label": label}


def natural(numerator, denominator, number):
    result = Fraction(numerator * number, denominator)
    assert result.denominator == 1
    return interactive(
        f"Calculează {numerator}/{denominator} din {number}.", "natural",
        {"expression": f"{numerator}/{denominator} · {number}",
         "instruction": "Transformă expresia într-un produs și calculează.",
         "fields": [field("product_numerator", "Numărătorul produsului"), field("result", "Rezultat")],
         "answers": {"product_numerator": numerator * number, "result": result.numerator}},
        f"{numerator}/{denominator} din {number} este {numerator} · {number} : {denominator} = {result.numerator}.")


def fraction_of_fraction(left, right):
    result = Fraction(*left) * Fraction(*right)
    return interactive(
        f"Calculează {left[0]}/{left[1]} din {right[0]}/{right[1]}.", "fraction",
        {"expression": f"{left[0]}/{left[1]} · {right[0]}/{right[1]}",
         "instruction": "Înmulțește fracțiile și scrie rezultatul ireductibil.",
         "fields": [field("numerator", "Numărător rezultat"), field("denominator", "Numitor rezultat")],
         "answers": {"numerator": result.numerator, "denominator": result.denominator}},
        f"Produsul celor două fracții este {result.numerator}/{result.denominator}.")


def unit_path(part_num, part_den, known, target_num):
    unit = known // part_num
    result = unit * target_num
    return interactive(
        f"Dacă {part_num}/{part_den} dintr-o cantitate înseamnă {known}, află cât reprezintă {target_num}/{part_den}.", "unit_path",
        {"expression": f"{part_num}/{part_den} → {known}; {target_num}/{part_den} → ?",
         "instruction": "Treci mai întâi printr-o singură parte egală.",
         "path": [{"top": f"{part_num}/{part_den}", "bottom": str(known)}, {"top": f"1/{part_den}", "bottom": "?"}, {"top": f"{target_num}/{part_den}", "bottom": "?"}],
         "fields": [field("unit", f"Valoarea lui 1/{part_den}"), field("result", "Valoarea cerută")],
         "answers": {"unit": unit, "result": result}},
        f"O parte valorează {known} : {part_num} = {unit}, iar {target_num} părți valorează {result}.")


def generic(text, mode, expression, instruction, fields, answers, explanation, **extra):
    return interactive(text, mode, {"expression": expression, "instruction": instruction,
                                    "fields": [field(*item) for item in fields], "answers": answers, **extra}, explanation)


def visual_grid(percent):
    return interactive(f"Reprezintă {percent}% pe grila de 100 de pătrățele.", "grid",
                       {"target": percent, "answers": {"selected": percent}},
                       f"{percent}% înseamnă {percent} din 100 de pătrățele.")


def slider(percent, step, initial):
    return interactive(f"Așază cursorul la {percent}%.", "slider",
                       {"target": percent, "step": step, "initial": initial, "answers": {"percent": percent}},
                       f"Cursorul trebuie așezat la {percent} din 100.")


def price(text, initial, percent, increase):
    change = initial * percent // 100
    final = initial + change if increase else initial - change
    word = "majorării" if increase else "reducerii"
    label_word = "majorare" if increase else "reducere"
    return generic(text, "price", f"{percent}% din {initial}", f"Calculează valoarea {word}, apoi prețul final.",
                   [("change", f"Valoarea {word}"), ("final", "Preț final")],
                   {"change": change, "final": final},
                   f"{percent}% din {initial} este {change}; prețul final este {final}.",
                   initial=initial, change_label=f"{percent}% {label_word}")


def table(text, total, rows):
    answers = {f"value_{index}": total * percent // 100 for index, (_, percent) in enumerate(rows)}
    return interactive(text, "table", {"total": total,
        "rows": [{"label": label, "percent": percent} for label, percent in rows], "answers": answers},
        "Fiecare valoare este procentul indicat din total; valorile trebuie să însumeze totalul.")


def order_case(text, steps, order):
    return interactive(text, "order_steps", {"steps": steps, "display_order": order,
        "answers": {"order": ",".join(map(str, range(len(steps))))}},
        "Transformăm procentul sau fracția, calculăm partea și apoi formulăm răspunsul.")


def error_case(text, steps, error_index, explanation):
    return interactive(text, "error", {"steps": steps, "answers": {"error_index": error_index}}, explanation)


def match_case(text, pairs, order):
    return interactive(text, "match", {"pairs": [{"left": a, "right": b} for a, b in pairs],
        "result_order": order, "answers": {f"match_{i}": i for i in range(len(pairs))}},
        "Transformăm fiecare enunț în înmulțirea corespunzătoare și calculăm.")


def build_questions():
    q = [
        grid("Cât este 3/5 din 20?", 12, [8, 15, 60], "3/5 · 20 = 12."),
        grid("Cât este 25% din 200?", 50, [25, 75, 125], "25/100 · 200 = 50."),
        grid("Cât este 2/3 din 3/4?", "1/2", ["2/7", "5/7", "6/12"], "2/3 · 3/4 = 1/2."),
        grid("Un produs de 240 lei are o reducere de 10%. Care este reducerea?", "24 lei", ["10 lei", "216 lei", "264 lei"], "10% din 240 este 24."),
        grid("Dacă 2/5 dintr-un număr este 30, numărul este:", 75, [12, 60, 150], "Întregul este 30 : 2/5 = 75."),
        true_false("Pentru a afla 4/7 din 35, putem calcula 4/7 · 35.", "Adevărat", "O fracție dintr-un număr se calculează prin înmulțire."),
        true_false("15% din 80 este egal cu 15 · 80.", "Fals", "15% înseamnă 15/100."),
        true_false("3/4 din 2/5 se calculează prin produsul 3/4 · 2/5.", "Adevărat", "O fracție dintr-o fracție este produsul lor."),
    ]
    q += [natural(*case) for case in [(1,4,100),(2,3,336),(2,5,75),(3,7,777),(4,9,162)]]
    q += [fraction_of_fraction(*case) for case in [((1,3),(3,7)),((3,4),(4,3)),((2,5),(15,19)),((5,12),(18,5))]]
    q += [unit_path(*case) for case in [(5,8,40,3),(2,7,10,7),(3,5,24,1),(4,9,36,7)]]
    q += [
        generic("Află numărul dacă 3/5 din el este 24.", "missing", "3/5 din □ = 24", "Completează întregul.", [("whole","Întregul")], {"whole":40}, "24 : 3/5 = 40."),
        generic("Află numărul dacă 15% din el este 45.", "missing", "15% din □ = 45", "Completează întregul.", [("whole","Întregul")], {"whole":300}, "45 : 15/100 = 300."),
        generic("Completează procentul: □% din 200 = 30.", "missing", "□% din 200 = 30", "Află ce parte din 200 reprezintă 30.", [("percent","Procent")], {"percent":15}, "30/200 = 15/100, deci 15%."),
        generic("Completează numărătorul: □/7 din 35 = 20.", "missing", "□/7 · 35 = 20", "Află numărătorul fracției.", [("numerator","Numărător")], {"numerator":4}, "O șeptime din 35 este 5, iar 20 conține 4 asemenea părți."),
        generic("Află fracția din 60 care este egală cu 45.", "missing", "□/□ din 60 = 45", "Scrie fracția în formă ireductibilă.", [("numerator","Numărător"),("denominator","Numitor")], {"numerator":3,"denominator":4}, "45/60 se simplifică la 3/4."),
    ]
    q += [
        generic("Transformă 25% în fracție și calculează 25% din 80.", "convert", "25% = □/100 = □/□; apoi din 80", "Completează transformarea și rezultatul.", [("hundredths","Numărător din 100"),("numerator","Numărător ireductibil"),("denominator","Numitor ireductibil"),("result","Rezultat")], {"hundredths":25,"numerator":1,"denominator":4,"result":20}, "25% = 25/100 = 1/4, iar 1/4 din 80 este 20."),
        generic("Transformă 40% în fracție și calculează 40% din 350.", "convert", "40% = □/100 = □/□; apoi din 350", "Completează transformarea și rezultatul.", [("hundredths","Numărător din 100"),("numerator","Numărător ireductibil"),("denominator","Numitor ireductibil"),("result","Rezultat")], {"hundredths":40,"numerator":2,"denominator":5,"result":140}, "40% = 2/5, iar 2/5 din 350 este 140."),
        generic("Transformă 150% în fracție și calculează 150% din 40.", "convert", "150% = □/100 = □/□; apoi din 40", "Completează transformarea și rezultatul.", [("hundredths","Numărător din 100"),("numerator","Numărător ireductibil"),("denominator","Numitor ireductibil"),("result","Rezultat")], {"hundredths":150,"numerator":3,"denominator":2,"result":60}, "150% = 3/2, iar 3/2 din 40 este 60."),
    ]
    q += [visual_grid(p) for p in (15,35,72)]
    q += [slider(25,5,0), slider(65,5,10)]
    q += [
        price("Un televizor costă 2 400 lei și primește o reducere de 12%.",2400,12,False),
        price("Prețul unei tone de combustibil este 4 800 lei și crește cu 3%.",4800,3,True),
        price("Un ghiozdan de 320 lei este redus cu 15%.",320,15,False),
    ]
    q += [
        table("Distribuie bugetul de 1 000 lei conform procentelor.",1000,[("Cărți",35),("Materiale",25),("Transport",20),("Activități",20)]),
        table("Completează cheltuielile din suma de 180 000 lei.",180000,[("Masă",52),("Întreținere",23),("Transport",9),("Activități",12),("Altele",4)]),
    ]
    q += [
        order_case("Așază pașii pentru calculul lui 30% din 250.",["Scriem 30% = 30/100.","Înmulțim 30/100 cu 250.","Simplificăm și obținem 75.","Formulăm răspunsul: 75."],[2,0,3,1]),
        order_case("Construiește rezolvarea: 3/5 dintr-un drum de 45 km.",["Identificăm întregul: 45 km.","Scriem produsul 3/5 · 45.","Calculăm 45 : 5 · 3 = 27.","Răspundem: 27 km."],[1,3,0,2]),
        error_case("Identifică primul pas greșit în calculul lui 20% din 60.",["20% = 20/100.","20/100 · 60 = 1200/100.","1200/100 = 120."],2,"1200/100 este 12, nu 120."),
        error_case("Găsește primul pas greșit pentru 3/4 din 28.",["Scriem 3/4 · 28.","Calculăm 28 : 3 = 9 rest 1.","Înmulțim rezultatul cu 4."],1,"Împărțim mai întâi 28 la numitorul 4, apoi înmulțim cu 3."),
        match_case("Potrivește fiecare expresie cu rezultatul ei.",[("1/4 din 80","20"),("30% din 90","27"),("2/3 din 45","30")],[2,0,1]),
        match_case("Potrivește fiecare situație cu schema corectă.",[("Reducere de 15% din 200","200 − 15/100 · 200"),("Majorare de 10% a lui 500","500 + 10/100 · 500"),("3/5 din 40","3/5 · 40")],[1,2,0]),
        generic("Într-o echipă, 3/5 dintre cei 20 de elevi sunt în clasa a V-a. Câți elevi sunt în clasa a V-a?", "problem", "3/5 din 20", "Scrie calculul intermediar și răspunsul.", [("unit","Valoarea unei cincimi"),("result","Număr de elevi")], {"unit":4,"result":12}, "O cincime din 20 este 4, iar trei cincimi înseamnă 12 elevi."),
    ]
    assert len(q) == 46
    assert len({item["text"] for item in q}) == 46
    return q


def main():
    target = Path(__file__).resolve().parents[1] / "clasa_5_fractii_si_procente_dintr_un_numar.json"
    payload = {"title": "Fracții/procente dintr-un număr natural sau dintr-o fracție ordinară",
               "description": "Clasa a 5-a · Fracții ordinare", "difficulty": "easy",
               "questions": build_questions()}
    target.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Am scris {len(payload['questions'])} întrebări în {target}.")


if __name__ == "__main__":
    main()
