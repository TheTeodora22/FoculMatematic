"""Generează lecția despre numere raționale pozitive și ordinea operațiilor."""

import json
from pathlib import Path


def interactive(text, kind, data, explanation):
    return {"text": text, "type": kind, "format": "interactive", "points": 10,
            "explanation": explanation, "interactive": data}


def grid(text, correct, wrong, explanation):
    values = [str(correct), *(str(value) for value in wrong)]
    assert len(values) == 4 and len(set(values)) == 4
    order = [1, 3, 0, 2]
    return {"text": text, "type": "multiple_choice", "format": "grid", "points": 10,
            "explanation": explanation,
            "options": [{"text": values[index], "is_correct": index == 0} for index in order]}


def true_false(text, answer, explanation):
    return {"text": text, "type": "multiple_choice", "format": "true_false", "points": 10,
            "explanation": explanation,
            "options": [{"text": "Adevărat", "is_correct": answer},
                        {"text": "Fals", "is_correct": not answer}]}


def match(text, pairs, explanation):
    return interactive(text, "base_match", {"pairs": [{"left": left, "right": right} for left, right in pairs],
                                               "right_order": [2, 0, 3, 1]}, explanation)


def missing(text, expression, fields, answers, explanation):
    return interactive(text, "decimal_workbench", {"mode": "missing", "expression": expression,
                                                       "fields": [{"key": key, "label": label} for key, label in fields],
                                                       "answers": answers}, explanation)


def compare(text, left, right, left_label, right_label, relation, explanation):
    return interactive(text, "fraction_compare", {"mode": "symbol", "left": left, "right": right,
                                                     "left_label": left_label, "right_label": right_label,
                                                     "relation": relation}, explanation)


def order(text, items, direction, correct_order, display_order, explanation):
    data = {"mode": "order", "direction": direction,
            "items": [{"label": label, "numerator": numerator, "denominator": denominator}
                      for label, numerator, denominator in items],
            "correct_order": correct_order, "display_order": display_order}
    return interactive(text, "fraction_compare", data, explanation)


def sequence(text, expression, steps, display_order, explanation):
    return interactive(text, "operation_sequence", {"expression": expression, "steps": steps,
                                                        "display_order": display_order,
                                                        "correct_order": list(range(len(steps)))}, explanation)


def detective(text, steps, error_index, explanation):
    return interactive(text, "divisibility_error", {"steps": steps, "error_index": error_index}, explanation)


def parentheses(text, tokens, open_index, close_index, explanation):
    return interactive(text, "parentheses_drag", {"tokens": tokens, "correct_open_index": open_index,
                                                     "correct_close_index": close_index}, explanation)


def build_questions():
    questions = [
        match("Potrivește fiecare fracție ordinară cu forma zecimală și procentuală echivalentă.",
              [("1/2", "0,5 = 50%"), ("3/4", "0,75 = 75%"),
               ("1/5", "0,2 = 20%"), ("5/4", "1,25 = 125%")],
              "Fracția, scrierea zecimală și procentul pot reprezenta același număr rațional pozitiv."),
        match("Unește fiecare fracție zecimală cu celelalte două forme ale aceluiași număr.",
              [("0,25", "1/4 = 25%"), ("0,6", "3/5 = 60%"),
               ("1,5", "3/2 = 150%"), ("0,125", "1/8 = 12,5%")],
              "Transformăm fracția ordinară prin împărțire și procentul prin înmulțire cu 100."),
        match("Potrivește procentele cu reprezentările lor echivalente.",
              [("10%", "0,1 = 1/10"), ("40%", "0,4 = 2/5"),
               ("80%", "0,8 = 4/5"), ("200%", "2 = 2/1")],
              "Un procent arată câte sutimi sunt luate: 40% = 40/100 = 0,4."),

        missing("Completează celelalte forme ale numărului 0,375.", "0,375 = fracție ordinară = procent",
                [("fraction", "Fracția ordinară"), ("percent", "Procentul (fără semnul %)")],
                {"fraction": "3/8", "percent": "37,5"},
                "0,375 = 375/1000 = 3/8, iar 0,375 · 100 = 37,5%."),
        missing("Completează trio-ul de reprezentări pentru 4/5.", "4/5 = fracție zecimală = procent",
                [("decimal", "Fracția zecimală"), ("percent", "Procentul (fără semnul %)")],
                {"decimal": "0,8", "percent": "80"},
                "4 : 5 = 0,8, iar 0,8 = 80%."),
        missing("Completează trio-ul de reprezentări pentru 125%.", "125% = fracție zecimală = fracție ordinară",
                [("decimal", "Fracția zecimală"), ("fraction", "Fracția ordinară ireductibilă")],
                {"decimal": "1,25", "fraction": "5/4"},
                "125% = 125/100 = 1,25 = 5/4."),

        grid("Care cartonaș NU reprezintă același număr ca 0,5?", "1/5", ["50%", "1/2", "5/10"],
             "1/5 = 0,2; celelalte trei forme sunt egale cu 0,5."),
        grid("Găsește intrusul dintre reprezentările numărului 0,75.", "7,5%", ["75%", "3/4", "75/100"],
             "7,5% = 0,075, nu 0,75."),
        grid("Care reprezentare nu este echivalentă cu 1,25?", "1/4", ["125%", "5/4", "1,250"],
             "1/4 = 0,25, în timp ce celelalte reprezintă 1,25."),

        compare("Alege semnul corect.", [3, 4], [7, 10], "3/4", "0,7", ">",
                "3/4 = 0,75, iar 0,75 > 0,7."),
        compare("Compară cele două forme fără a le confunda.", [2, 5], [39, 100], "40%", "0,39", ">",
                "40% = 0,40, care este mai mare decât 0,39."),
        compare("Alege relația corectă dintre cele două reprezentări.", [6, 5], [6, 5], "1,2", "120%", "=",
                "120% = 120/100 = 1,2."),

        order("Ordonează crescător cele patru reprezentări.",
              [("3/4", 3, 4), ("0,6", 3, 5), ("80%", 4, 5), ("0,55", 11, 20)],
              "asc", [3, 1, 0, 2], [2, 0, 3, 1], "Valorile sunt 0,75; 0,6; 0,8 și 0,55."),
        order("Ordonează descrescător numerele raționale.",
              [("125%", 5, 4), ("6/5", 6, 5), ("1,05", 21, 20), ("0,9", 9, 10)],
              "desc", [0, 1, 2, 3], [2, 0, 3, 1], "Scrise zecimal, valorile sunt 1,25; 1,2; 1,05 și 0,9."),
        order("Așază în ordine crescătoare formele date.",
              [("1/8", 1, 8), ("15%", 3, 20), ("0,2", 1, 5), ("0,05", 1, 20)],
              "asc", [3, 0, 1, 2], [1, 3, 2, 0], "Valorile sunt 0,125; 0,15; 0,2 și 0,05."),

        sequence("Construiește traseul complet al calculelor.", "0,5 · [3/4 + 0,25] : 2,5",
                 ["3/4 = 0,75", "0,75 + 0,25 = 1", "0,5 · 1 = 0,5", "0,5 : 2,5 = 0,2"],
                 [2, 0, 3, 1], "Transformăm forma diferită, calculăm paranteza, apoi operațiile de același ordin de la stânga la dreapta."),
        sequence("Așază calculele în ordinea corectă.", "(2,4 + 1,6) : 0,5 − 3",
                 ["2,4 + 1,6 = 4", "4 : 0,5 = 8", "8 − 3 = 5"], [1, 2, 0],
                 "Paranteza se calculează înaintea împărțirii și a scăderii."),
        sequence("Construiește rezolvarea pas cu pas.", "3/5 · (2,5 − 0,5) + 1,2",
                 ["2,5 − 0,5 = 2", "3/5 · 2 = 1,2", "1,2 + 1,2 = 2,4"],
                 [2, 0, 1], "Calculăm paranteza, apoi efectuăm înmulțirea și adunarea."),
        sequence("Ordonează cartonașele pentru a rezolva expresia.", "20% · 35 + 1,5",
                 ["20% = 0,2", "0,2 · 35 = 7", "7 + 1,5 = 8,5"], [2, 0, 1],
                 "Procentul se transformă în 0,2, apoi se respectă prioritatea înmulțirii."),

        missing("Completează toate rezultatele intermediare.", "2,4 · 4,2 − 3,2 : 4/5",
                [("a", "2,4 · 4,2"), ("b", "3,2 : 4/5"), ("result", "Rezultatul final")],
                {"a": "10,08", "b": "4", "result": "6,08"},
                "4/5 = 0,8; obținem 10,08 − 4 = 6,08."),
        missing("Calculează pe etape, respectând paranteza.", "25,41 − 3 · (1,2 + 0,7)",
                [("a", "Paranteza"), ("b", "Produsul"), ("result", "Rezultatul final")],
                {"a": "1,9", "b": "5,7", "result": "19,71"},
                "1,2 + 0,7 = 1,9; apoi 3 · 1,9 = 5,7 și 25,41 − 5,7 = 19,71."),
        missing("Completează traseul expresiei.", "20 + 1,7 − 6,3",
                [("a", "20 + 1,7"), ("result", "Rezultatul final")],
                {"a": "21,7", "result": "15,4"}, "Adunarea și scăderea se efectuează de la stânga la dreapta."),
        missing("Calculează împărțirile succesive.", "8,24 : 10 : 2",
                [("a", "8,24 : 10"), ("result", "Rezultatul final")],
                {"a": "0,824", "result": "0,412"}, "Operațiile sunt de același ordin, deci lucrăm de la stânga la dreapta."),
        missing("Completează rezultatele intermediare.", "(2,73 + 0,27) : 0,5 − 4,25",
                [("a", "Paranteza"), ("b", "Împărțirea"), ("result", "Rezultatul final")],
                {"a": "3", "b": "6", "result": "1,75"}, "Paranteza dă 3, apoi 3 : 0,5 = 6 și 6 − 4,25 = 1,75."),
        missing("Alege o formă comună și completează calculele.", "3/8 · 32 + 0,625 · 8",
                [("a", "3/8 · 32"), ("b", "0,625 · 8"), ("result", "Rezultatul final")],
                {"a": "12", "b": "5", "result": "17"}, "Cele două produse sunt 12 și 5, iar suma este 17."),

        detective("Detectivul greșelilor: apasă primul pas incorect.",
                  ["2,4 · 4,2 − 3,2 : 0,8", "= 10,08 − 4", "= 14,08"], 2,
                  "Ultima operație este o scădere: 10,08 − 4 = 6,08."),
        detective("Găsește prima transformare greșită.",
                  ["0,5 · [3/4 + 0,1(6)] : 2,5", "0,1(6) = 1/5", "3/4 + 1/5 = 19/20", "rezultatul este 0,19"], 1,
                  "0,1(6) = 1/6, nu 1/5."),
        detective("Verifică rezolvarea și apasă primul pas greșit.",
                  ["30% din 80 + 1/4 din 20", "30% = 0,03", "0,03 · 80 + 5", "= 7,4"], 1,
                  "30% = 0,30; calculul corect este 24 + 5 = 29."),

        parentheses("Trage parantezele astfel încât expresia să aibă valoarea 16.", ["3", "+ 1", "· 4"], 0, 2,
                    "(3 + 1) · 4 = 16."),
        parentheses("Așază parantezele pentru a obține rezultatul 2.", ["8", "− 2", ": 3"], 0, 2,
                    "(8 − 2) : 3 = 2."),
        parentheses("Plasează parantezele astfel încât rezultatul să fie 8.", ["2,5", "+ 1,5", "· 2"], 0, 2,
                    "(2,5 + 1,5) · 2 = 8."),
        parentheses("Așază parantezele pentru ca rezultatul să fie 2,4.", ["6", ": 0,5", "+ 2"], 1, 3,
                    "6 : (0,5 + 2) = 2,4."),

        grid("Pentru 3/4 · 20, ce formă face calculul cel mai direct?", "Fracția 3/4", ["0,75%", "75", "7,5"],
             "20 se împarte exact la 4: 20 : 4 · 3 = 15."),
        grid("Pentru 25% din 80, ce scriere permite cel mai rapid calcul mintal?", "1/4 din 80", ["25 · 80", "0,25% din 80", "25/10 din 80"],
             "25% = 1/4, iar sfertul lui 80 este 20."),

        missing("Transformă înainte de a calcula.", "2/5 · 15 + 0,3",
                [("decimal", "2/5 scris zecimal"), ("product", "Produsul"), ("result", "Rezultatul final")],
                {"decimal": "0,4", "product": "6", "result": "6,3"}, "2/5 = 0,4; apoi 0,4 · 15 + 0,3 = 6,3."),
        missing("Transformă procentul și continuă calculul.", "60% · 45 − 7",
                [("decimal", "60% scris zecimal"), ("product", "Produsul"), ("result", "Rezultatul final")],
                {"decimal": "0,6", "product": "27", "result": "20"}, "60% = 0,6; 0,6 · 45 = 27, iar 27 − 7 = 20."),

        grid("Ce număr trebuie pus în căsuță pentru ca 0,5 · □ + 1 = 6?", "10", ["2,5", "5", "12"],
             "Scădem 1: 0,5 · □ = 5, apoi împărțim la 0,5 și obținem 10."),
        grid("Alege cartonașul care completează egalitatea 3/4 · □ = 6.", "8", ["4,5", "6,75", "12"],
             "□ = 6 : 3/4 = 6 · 4/3 = 8."),

        missing("În trei zile s-au vândut 12,56 kg, 41,275 kg și 29,11 kg de cafea. Un kilogram costă 10 lei. Calculează încasarea.",
                "(12,56 + 41,275 + 29,11) · 10",
                [("mass", "Cantitatea totală (kg)"), ("money", "Încasarea (lei)")],
                {"mass": "82,945", "money": "829,45"}, "Cantitatea totală este 82,945 kg, iar încasarea este 829,45 lei."),
        missing("Un turist parcurge 24 km în trei zile: 3/8 din traseu în prima zi și 0,6 din rest în a doua zi. Câți kilometri parcurge în a treia zi?",
                "24 km: ziua I = 3/8 din traseu; ziua II = 0,6 din rest",
                [("day1", "Ziua I (km)"), ("day2", "Ziua II (km)"), ("day3", "Ziua III (km)")],
                {"day1": "9", "day2": "9", "day3": "6"}, "În prima zi parcurge 9 km; rămân 15 km, din care 0,6 înseamnă 9 km; restul este 6 km."),
        missing("Douăzeci de vite consumă zilnic câte 12 kg de hrană. Cât consumă în 5 zile?",
                "20 · 12 · 5", [("daily", "Consum într-o zi (kg)"), ("total", "Consum în 5 zile (kg)")],
                {"daily": "240", "total": "1200"}, "Într-o zi consumă 20 · 12 = 240 kg, iar în 5 zile 1 200 kg."),
        missing("Adi și Ioana au de rezolvat 32 de probleme. Adi rezolvă 3/8 din ele, iar Ioana 0,625 din ele. Cu câte probleme rezolvă Ioana mai mult?",
                "3/8 · 32 și 0,625 · 32",
                [("adi", "Problemele lui Adi"), ("ioana", "Problemele Ioanei"), ("difference", "Diferența")],
                {"adi": "12", "ioana": "20", "difference": "8"}, "Adi rezolvă 12, Ioana 20, deci Ioana rezolvă cu 8 probleme mai mult."),

        true_false("Numerele 0,5, 1/2 și 50% reprezintă același număr rațional pozitiv.", True,
                   "Toate cele trei scrieri au valoarea 0,5."),
        true_false("În expresia 2,4 + 1,6 · 5 se efectuează mai întâi adunarea.", False,
                   "Înmulțirea are prioritate: se calculează mai întâi 1,6 · 5."),

        grid("Calculează 2,4 + 1,6 · 5.", "10,4", ["20", "12", "8"],
             "Mai întâi 1,6 · 5 = 8, apoi 2,4 + 8 = 10,4."),
        grid("Care este valoarea expresiei (4/5 + 0,2) · 3?", "3", ["2,6", "1", "0,3"],
             "4/5 = 0,8; în paranteză obținem 1, apoi 1 · 3 = 3."),
        grid("Calculează 50% · 18 + 1/2 · 6.", "12", ["9", "21", "24"],
             "50% din 18 este 9, iar jumătate din 6 este 3; suma este 12."),
    ]
    assert len(questions) == 47
    assert len({question["text"] for question in questions}) == len(questions)
    return questions


def main():
    target = Path(__file__).resolve().parents[1] / "clasa_5_numere_rationale_pozitive_ordinea_operatiilor.json"
    payload = {"title": "Număr rațional pozitiv; ordinea efectuării operațiilor cu numere raționale pozitive",
               "description": "Clasa a 5-a · Fracții zecimale", "difficulty": "medium",
               "questions": build_questions()}
    target.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Am scris {len(payload['questions'])} întrebări în {target}.")


if __name__ == "__main__":
    main()
