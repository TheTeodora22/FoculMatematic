"""Generează lecția despre introducerea și scoaterea întregilor din fracție."""

import json
from pathlib import Path


def grid(text, correct, wrong, explanation):
    values = [str(correct), *(str(value) for value in wrong)]
    assert len(values) == 4 and len(set(values)) == 4
    order = [2, 0, 3, 1]
    return {"text": text, "type": "multiple_choice", "format": "grid", "points": 10,
            "explanation": explanation,
            "options": [{"text": values[index], "is_correct": index == 0} for index in order]}


def true_false(text, answer, explanation):
    return {"text": text, "type": "multiple_choice", "format": "true_false", "points": 10,
            "explanation": explanation,
            "options": [{"text": value, "is_correct": value == answer} for value in ("Adevărat", "Fals")]}


def mixed_to_fraction(whole, numerator, denominator):
    result = whole * denominator + numerator
    return {"text": f"Transformă numărul mixt {whole} {numerator}/{denominator} într-o fracție.",
            "type": "fraction_visual", "format": "interactive", "points": 10,
            "explanation": f"{whole} · {denominator} + {numerator} = {result}, deci obținem {result}/{denominator}.",
            "interactive": {"mode": "mixed_to_fraction", "whole": whole, "numerator": numerator,
                            "denominator": denominator, "answers": {"result": result}}}


def fraction_to_mixed(numerator, denominator):
    whole, remainder = divmod(numerator, denominator)
    return {"text": f"Scoate întregii din fracția {numerator}/{denominator}.",
            "type": "fraction_visual", "format": "interactive", "points": 10,
            "explanation": f"{numerator} : {denominator} = {whole}, rest {remainder}, deci {numerator}/{denominator} = {whole} {remainder}/{denominator}.",
            "interactive": {"mode": "fraction_to_mixed", "numerator": numerator,
                            "denominator": denominator, "answers": {"whole": whole, "remainder": remainder}}}


def build_questions():
    questions = [
        grid("Ce fracție obținem introducând întregii din 2 3/4?", "11/4", ["8/4", "9/4", "11/3"], "2 · 4 + 3 = 11, iar numitorul rămâne 4."),
        grid("Transformă 1 1/2 într-o fracție supraunitară.", "3/2", ["2/2", "2/3", "1/3"], "1 · 2 + 1 = 3."),
        grid("Care este forma de fracție a numărului mixt 3 5/8?", "29/8", ["24/8", "29/5", "8/29"], "3 · 8 + 5 = 29."),
        grid("Introdu întregii în fracția 4 2/7.", "30/7", ["28/7", "18/7", "30/2"], "4 · 7 + 2 = 30."),
        grid("Ce număr mixt corespunde fracției 23/8?", "2 7/8", ["3 1/8", "2 3/8", "7 2/8"], "23 : 8 = 2, rest 7."),
        grid("Scoate întregii din fracția 41/5.", "8 1/5", ["7 6/5", "8 5/1", "9 1/5"], "41 : 5 = 8, rest 1."),
        grid("Transformă fracția 62/11 în număr mixt.", "5 7/11", ["6 2/11", "5 6/11", "7 5/11"], "62 : 11 = 5, rest 7."),
        grid("Ce obținem când scoatem întregii din 27/9?", "3", ["2 9/9", "3 1/9", "9/3"], "27 se împarte exact la 9, deci partea fracționară dispare."),
        grid("În egalitatea 38/6 = 6 2/6, ce reprezintă numărul 6 din fața fracției?", "Câtul împărțirii 38 : 6", ["Restul împărțirii", "Numitorul inițial", "Numărătorul inițial"], "Partea întreagă este câtul împărțirii numărătorului la numitor."),
        grid("În transformarea 52/9 = 5 7/9, ce reprezintă 7?", "Restul împărțirii 52 : 9", ["Câtul împărțirii", "Numitorul fracției", "Numărul de întregi"], "Restul devine numărătorul părții fracționare."),
        grid("Între ce numere naturale consecutive se află 13/4?", "3 și 4", ["2 și 3", "4 și 5", "12 și 13"], "13/4 = 3 1/4."),
        grid("Între ce numere naturale consecutive se află 29/6?", "4 și 5", ["3 și 4", "5 și 6", "28 și 29"], "29/6 = 4 5/6."),
        grid("Un buștean de 12 m este tăiat în 5 părți egale. Cât măsoară fiecare parte, ca număr mixt?", "2 2/5 m", ["2 1/5 m", "3 2/5 m", "5 2/12 m"], "12/5 = 2 2/5."),
        grid("Pe un platou încap 7 brioșe. Câte platouri reprezintă 18 brioșe?", "2 4/7 platouri", ["3 1/7 platouri", "2 3/7 platouri", "7 4/18 platouri"], "18 : 7 = 2, rest 4."),
        grid("Șase greutăți identice cântăresc împreună 23 kg. Cât cântărește una?", "3 5/6 kg", ["4 1/6 kg", "3 4/6 kg", "6 5/23 kg"], "23/6 = 3 5/6."),
        grid("Care relație descrie corect introducerea întregilor din n a/b?", "(n · b + a)/b", ["(n + b) · a/b", "(n · a + b)/a", "(n + a)/(b + n)"], "Înmulțim partea întreagă cu numitorul și adunăm numărătorul."),
        true_false("La introducerea întregilor în fracție, numitorul rămâne neschimbat.", "Adevărat", "Se modifică doar numărătorul: n · b + a."),
        true_false("În 31/7 = 4 3/7, numărul 3 este câtul împărțirii 31 : 7.", "Fals", "4 este câtul, iar 3 este restul."),
        true_false("Dacă numărătorul se împarte exact la numitor, rezultatul este un număr natural.", "Adevărat", "Restul este zero, deci nu mai există parte fracționară."),
        true_false("Fracția 17/5 este egală cu numărul mixt 3 2/5.", "Adevărat", "17 : 5 = 3, rest 2."),
    ]

    for whole, numerator, denominator in [(2,3,4), (3,2,7), (4,3,5), (6,5,9)]:
        questions.append(mixed_to_fraction(whole, numerator, denominator))
    for numerator, denominator in [(19,5), (43,8), (64,9), (73,12)]:
        questions.append(fraction_to_mixed(numerator, denominator))

    assert len(questions) == 28
    return questions


def main():
    target = Path(__file__).resolve().parents[1] / "clasa_5_fractii_ordinare_introducerea_si_scoaterea_intregilor.json"
    payload = {"title": "Introducerea și scoaterea întregilor dintr-o fracție",
               "description": "Clasa a 5-a · Fracții ordinare", "difficulty": "easy",
               "questions": build_questions()}
    target.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Am scris {len(payload['questions'])} întrebări în {target}.")


if __name__ == "__main__":
    main()
