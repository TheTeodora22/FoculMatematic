"""Generează lecția despre împărțirea fracțiilor zecimale."""

import json
from pathlib import Path


TITLE = "Împărțirea unei fracții zecimale cu un număr finit de zecimale nenule la un număr natural nenul; împărțirea a două fracții zecimale cu un număr finit de zecimale nenule; transformarea unei fracții zecimale periodice în fracție ordinară"


def iq(text, kind, data, explanation):
    return {"text": text, "type": kind, "format": "interactive", "points": 10, "interactive": data, "explanation": explanation}


def decimal(text, mode, data, answers, explanation):
    return iq(text, "decimal_workbench", {"mode": mode, **data, "answers": answers}, explanation)


def remainders(digits, divisor):
    current, result = 0, []
    for digit in digits:
        current = current * 10 + int(digit)
        result.append(current % divisor)
        current %= divisor
    return result


def column(original_dividend, original_divisor, normalized_dividend, normalized_divisor, quotient, label):
    calculation_base = normalized_dividend.replace(",", "").lstrip("0") or "0"
    dividend_places = len(normalized_dividend.split(",")[1]) if "," in normalized_dividend else 0
    quotient_places = len(quotient.split(",")[1]) if "," in quotient else 0
    added_zeros = max(0, quotient_places - dividend_places)
    calculation = calculation_base + "0" * added_zeros
    rests = remainders(calculation, normalized_divisor)
    labels = [f"Rest după cifra {index + 1}" for index in range(len(calculation_base))]
    labels += [f"Rest după coborârea zeroului {index + 1}" for index in range(added_zeros)]
    labels[-1] = "Rest final"
    changed = str(original_divisor) != str(normalized_divisor)
    instruction = "Am mutat virgula în ambele numere până când împărțitorul a devenit natural. Completează câtul și resturile." if changed else "Împarte ca la numere naturale, fără să pierzi poziția virgulei din deîmpărțit."
    return iq(
        f"Împarte în coloană {original_dividend} : {original_divisor} ({label}).",
        "column_division",
        {"dividend": normalized_dividend, "divisor": normalized_divisor, "display_dividend": normalized_dividend, "display_divisor": normalized_divisor, "quotient": quotient, "remainder": rests[-1], "remainders": rests, "calculation_base": calculation_base, "calculation_digits": calculation, "step_labels": labels, "instruction": instruction},
        f"Împărțirea echivalentă este {normalized_dividend} : {normalized_divisor}, iar câtul este {quotient}.",
    )


def comma(label, digits, position, answer):
    return decimal(
        f"Așază virgula după împărțirea la o putere a lui 10 ({label}).", "comma",
        {"digits": digits, "places": len(digits) - position}, {"position": str(position)},
        f"Mutăm virgula spre stânga cu numărul cerut de poziții și obținem {answer}.",
    )


def shift(label, items):
    categories = [{"value": "1", "label": "× 1"}, {"value": "10", "label": "× 10"}, {"value": "100", "label": "× 100"}, {"value": "1000", "label": "× 1 000"}]
    answers = {f"class:{item['id']}": item["factor"] for item in items}
    return decimal(
        f"Transformă împărțitorii în numere naturale ({label}).", "classification",
        {"instruction": "Alege puterea lui 10 cu care trebuie înmulțite ambele numere.", "items": [{"id": item["id"], "label": item["label"]} for item in items], "categories": categories},
        answers, "Numărăm zecimalele împărțitorului și înmulțim ambele numere cu puterea lui 10 corespunzătoare.",
    )


def missing(label, expression, answer, explanation=None, text=None):
    return decimal(
        text or f"Calculează împărțirea din seria {label}.", "missing",
        {"expression": expression, "fields": [{"key": "missing", "label": "Răspuns"}]}, {"missing": answer},
        explanation or f"Rezultatul corect este {answer}.",
    )


def detective(label, steps, error_index, explanation):
    return iq(f"Detectivul greșelilor {label}: apasă primul pas greșit.", "divisibility_error", {"steps": steps, "error_index": error_index}, explanation)


def periodic(label, source, numerator, denominator, explanation):
    return decimal(
        f"Transformă numărul periodic {source} în fracție ordinară ({label}).", "conversion",
        {"source": source, "target_kind": "fraction", "fields": [{"key":"numerator","label":"Numărător"},{"key":"denominator","label":"Numitor"}]},
        {"numerator": str(numerator), "denominator": str(denominator)}, explanation,
    )


def build_questions():
    questions = []

    for row in [
        ("12,75", "3", "12,75", 3, "4,25", "A"),
        ("72,15", "5", "72,15", 5, "14,43", "B"),
        ("12,9", "3", "12,9", 3, "4,3", "C"),
        ("169,36", "8", "169,36", 8, "21,17", "D"),
        ("3,21", "0,5", "32,1", 5, "6,42", "E"),
        ("435,2", "0,04", "43520", 4, "10880", "F"),
        ("157,293", "1,25", "15729,3", 125, "125,8344", "G"),
        ("15,2", "0,8", "152", 8, "19", "H"),
    ]:
        questions.append(column(*row))

    questions += [
        comma("A", "237", 1, "2,37"),
        comma("B", "1245", 1, "1,245"),
        comma("C", "002134", 1, "0,02134"),
        comma("D", "00004", 1, "0,0004"),
        comma("E", "129567", 1, "1,29567"),
    ]

    questions += [
        shift("A", [{"id":"a","label":"3,21 : 0,5","factor":"10"},{"id":"b","label":"435,2 : 0,04","factor":"100"},{"id":"c","label":"157,293 : 1,25","factor":"100"}]),
        shift("B", [{"id":"a","label":"2,4 : 0,8","factor":"10"},{"id":"b","label":"31,08 : 0,008","factor":"1000"},{"id":"c","label":"23,46 : 3","factor":"1"}]),
        shift("C", [{"id":"a","label":"70,23 : 2,4","factor":"10"},{"id":"b","label":"850,8 : 0,15","factor":"100"},{"id":"c","label":"44 : 0,055","factor":"1000"}]),
        shift("D", [{"id":"a","label":"18,9 : 3,2","factor":"10"},{"id":"b","label":"44,85 : 2,5","factor":"10"},{"id":"c","label":"72,066 : 6","factor":"1"}]),
    ]

    questions += [
        missing("A", "14,3 : 5 = □", "2,86"),
        missing("B", "12,7 : 20 = □", "0,635"),
        missing("C", "55,79 : 4 = □", "13,9475"),
        missing("D", "129,567 : 100 = □", "1,29567"),
        missing("E", "2,(4) + 3,1(2) = □", "5,5(6)", "2,(4)=22/9 și 3,1(2)=281/90; suma este 501/90=5,5(6)."),
    ]

    questions += [
        detective("A", ["23,7 : 10", "Mutăm virgula o poziție spre dreapta", "Obținem 2,37"], 1, "La împărțirea cu 10, virgula se mută o poziție spre stânga."),
        detective("B", ["3,21 : 0,5", "Înmulțim numai împărțitorul cu 10", "Obținem 3,21 : 5", "Câtul este 0,642"], 1, "Trebuie să înmulțim ambele numere cu 10: 32,1 : 5 = 6,42."),
        detective("C", ["0,(29) are perioada 29", "Scriem 29 la numărător", "La numitor scriem 9", "Fracția este 29/9"], 2, "Pentru două cifre în perioadă, numitorul este 99; fracția este 29/99."),
        detective("D", ["8,2(7)", "Scădem numărul fără paranteză: 827 − 82 = 745", "Numitorul este 90", "Simplificăm 745/90 la 149/9"], 3, "Simplificarea corectă este 745/90 = 149/18."),
    ]

    questions += [
        periodic("A", "4,(7)", 43, 9, "4,(7)=4+7/9=43/9."),
        periodic("B", "0,(29)", 29, 99, "Perioada are două cifre, deci 0,(29)=29/99."),
        periodic("C", "1,(0258)", 3419, 3333, "1,(0258)=10257/9999, iar prin simplificare obținem 3419/3333."),
        periodic("D", "11,(8)", 107, 9, "11,(8)=11+8/9=107/9."),
        periodic("E", "0,(031)", 31, 999, "Perioada are trei cifre, deci numitorul inițial este 999."),
        periodic("F", "8,2(7)", 149, 18, "(827−82)/90=745/90=149/18."),
        periodic("G", "0,23(731)", 5927, 24975, "(23731−23)/99900=23708/99900=5927/24975."),
        periodic("H", "2,4(09)", 53, 22, "(2409−24)/990=2385/990=53/22."),
        periodic("I", "0,1(6)", 1, 6, "(16−1)/90=15/90=1/6."),
    ]

    questions += [
        missing("P1", "12,75 : 3 = □ lei", "4,25", text="Ioana plătește 12,75 lei pentru 3 creioane identice. Cât costă un creion?", explanation="Un creion costă 4,25 lei."),
        missing("P2", "6,5 : 10 = □ t", "0,65", text="Zece țevi identice cântăresc 6,5 tone. Cât cântărește o țeavă?", explanation="O țeavă cântărește 0,65 t."),
        missing("P3", "120,48 : 60 × 12 = □ g", "24,096", text="60 de ace cântăresc 120,48 g. Cât cântăresc 12 ace?", explanation="Un ac cântărește 2,008 g, iar 12 ace cântăresc 24,096 g."),
        missing("P4", "2,345 : 10 = □ kg", "0,2345", text="Zece caiete identice cântăresc 2,345 kg. Cât cântărește un caiet?", explanation="Un caiet cântărește 0,2345 kg."),
        missing("P5", "263 : 100 = □", "2,63", text="Determină numărul de 100 de ori mai mic decât 263.", explanation="Împărțim la 100 și obținem 2,63."),
        missing("P6", "31,08 : 8 = □", "3,885", text="Opt recipiente conțin împreună 31,08 l. Câți litri sunt într-un recipient?", explanation="Într-un recipient sunt 3,885 l."),
        missing("P7", "44,85 : 2,5 = □ km", "17,94", text="Un traseu de 44,85 km este de 2,5 ori mai lung decât alt traseu. Care este lungimea traseului mai scurt?", explanation="44,85 : 2,5 = 448,5 : 25 = 17,94 km."),
    ]

    assert len(questions) == 42, len(questions)
    return questions


def main():
    output = Path(__file__).resolve().parent.parent / "clasa_5_fractii_zecimale_impartirea.json"
    payload = {"title": TITLE, "description": "Clasa a 5-a · Fracții zecimale", "difficulty": "medium", "questions": build_questions()}
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Scrise {len(payload['questions'])} exerciții în {output.name}")


if __name__ == "__main__":
    main()
