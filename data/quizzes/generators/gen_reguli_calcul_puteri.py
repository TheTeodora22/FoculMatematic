"""Generează lecția „Reguli de calcul cu puteri”."""

import json
from pathlib import Path


SUP = str.maketrans("0123456789", "⁰¹²³⁴⁵⁶⁷⁸⁹")


def p(base, exponent):
    return f"{base}{str(exponent).translate(SUP)}"


def q(text, correct, wrong, explanation):
    values = [str(correct), *(str(value) for value in wrong)]
    assert len(values) == 4 and len(set(values)) == 4
    return {"text": text, "type": "multiple_choice", "format": "grid", "points": 10,
            "explanation": explanation,
            "options": [{"text": values[i], "is_correct": i == 0} for i in [1, 0, 3, 2]]}


def tf(text, answer, explanation):
    return {"text": text, "type": "multiple_choice", "format": "true_false", "points": 10,
            "explanation": explanation,
            "options": [{"text": "Adevărat", "is_correct": answer}, {"text": "Fals", "is_correct": not answer}]}


def iq(text, kind, data, explanation):
    return {"text": text, "type": kind, "format": "interactive", "points": 10,
            "explanation": explanation, "interactive": data}


def chain(text, expression, stages, explanation):
    normalized = [
        {"label": label, "base": base, "exponent": exponent}
        for label, base, exponent in stages
    ]
    return iq(text, "power_rule_chain", {"expression": expression, "stages": normalized}, explanation)


def build_questions():
    questions = [
        q("Scrie 7⁴ · 7³ sub forma unei singure puteri.", "7⁷", ["7¹²", "49⁷", "7¹"], "La înmulțirea puterilor cu aceeași bază adunăm exponenții: 4 + 3 = 7."),
        q("Care este forma simplificată a lui 13¹¹ · 13²³?", "13³⁴", ["13²⁵³", "169³⁴", "13¹²"], "Păstrăm baza 13 și adunăm exponenții: 11 + 23 = 34."),
        q("Calculează folosind o singură putere: 5⁹ · 5⁴.", "5¹³", ["5³⁶", "25¹³", "5⁵"], "5⁹ · 5⁴ = 5⁹⁺⁴ = 5¹³."),
        q("Ce rezultat obții pentru 2¹⁵ · 2⁶ · 2?", "2²²", ["2²¹", "2⁹⁰", "6²²"], "Scriem 2 = 2¹, apoi 15 + 6 + 1 = 22."),
        q("Scrie 9²¹ : 9⁸ sub forma unei singure puteri.", "9¹³", ["9²⁹", "9¹⁶⁸", "1¹³"], "La împărțire scădem exponenții: 21 − 8 = 13."),
        q("Care este rezultatul lui 23¹² : 23¹²?", "23⁰ = 1", ["23¹", "23²⁴", "0"], "Exponenții se scad: 12 − 12 = 0, iar orice număr nenul la puterea 0 este 1."),
        q("Simplifică 5³¹ : 5²⁷.", "5⁴", ["5⁵⁸", "1⁴", "5³"], "31 − 27 = 4."),
        q("Scrie 14⁴⁵ : 14²⁰ ca o singură putere.", "14²⁵", ["14⁶⁵", "14²⁰", "1²⁵"], "Păstrăm baza și calculăm 45 − 20 = 25."),
        q("Simplifică (3⁴)⁵.", "3²⁰", ["3⁹", "15²⁰", "3¹"], "La puterea unei puteri înmulțim exponenții: 4 · 5 = 20."),
        q("Care este forma unei singure puteri pentru (7³)⁶?", "7¹⁸", ["7⁹", "42¹⁸", "7²"], "3 · 6 = 18."),
        q("Simplifică ((2²)³)⁴.", "2²⁴", ["2⁹", "2¹⁴", "24²"], "Înmulțim exponenții: 2 · 3 · 4 = 24."),
        q("Scrie (4 · 5)³ folosind puterile factorilor.", "4³ · 5³", ["4³ · 5", "4 · 5³", "20⁶"], "Puterea unui produs se distribuie fiecărui factor."),
        q("Care expresie este egală cu 35⁴?", "5⁴ · 7⁴", ["5⁴ + 7⁴", "5 · 7⁴", "5² · 7²"], "35 = 5 · 7, deci 35⁴ = 5⁴ · 7⁴."),
        q("Scrie 12⁶ : 6⁶ sub forma unei singure puteri.", "2⁶", ["6⁰", "18⁶", "2¹²"], "Puterile au același exponent: 12⁶ : 6⁶ = (12 : 6)⁶ = 2⁶."),
        q("Transformă 8⁵ · 6⁵ într-o singură putere.", "48⁵", ["14⁵", "48¹⁰", "8³⁰"], "Pentru același exponent, înmulțim bazele și păstrăm exponentul."),
        q("Simplifică 3⁵ · 3⁷ : 3⁴.", "3⁸", ["3¹⁶", "3⁶", "3¹⁴"], "Exponentul final este 5 + 7 − 4 = 8."),
        q("Scrie 2⁴ · 5⁴ · 10³ ca o singură putere.", "10⁷", ["10¹¹", "7¹⁰", "10¹²"], "2⁴ · 5⁴ = 10⁴, apoi 10⁴ · 10³ = 10⁷."),
        q("Care dintre expresii este un pătrat perfect pentru orice număr natural a?", "a⁶", ["a⁵", "a⁷", "a⁹"], "a⁶ = (a³)²; o putere cu exponent par este pătratul unei puteri."),
    ]

    questions += [
        tf("Pentru a⁵ · a³ se păstrează baza și se adună exponenții.", True, "a⁵ · a³ = a⁸."),
        tf("Egalitatea (a⁴)³ = a⁷ este corectă.", False, "Exponenții se înmulțesc: (a⁴)³ = a¹²."),
        tf("Dacă a este nenul, atunci a⁹ : a⁹ = 1.", True, "a⁹ : a⁹ = a⁰ = 1."),
        tf("Puterea unui produs se calculează prin (a · b)ⁿ = aⁿ · bⁿ.", True, "Exponentul se distribuie ambilor factori."),
        tf("Egalitatea a⁸ : a³ = a⁵ este valabilă pentru a nenul.", True, "Scădem exponenții: 8 − 3 = 5."),
    ]

    chain_specs = [
        ("Completează exponenții pentru 5³ · 5⁷ : 5⁴.", "5³ · 5⁷ : 5⁴", [("5³ · 5⁷", 5, 10), ("5¹⁰ : 5⁴", 5, 6)], "3 + 7 = 10, apoi 10 − 4 = 6."),
        ("Transformă pas cu pas 2⁶ · 2⁵ · 2².", "2⁶ · 2⁵ · 2²", [("2⁶ · 2⁵", 2, 11), ("2¹¹ · 2²", 2, 13)], "Adunăm pe rând exponenții."),
        ("Simplifică în doi pași 7²⁰ : 7⁸ · 7³.", "7²⁰ : 7⁸ · 7³", [("7²⁰ : 7⁸", 7, 12), ("7¹² · 7³", 7, 15)], "Mai întâi scădem, apoi adunăm exponenții."),
        ("Ridică puterea la putere și completează rezultatul.", "(3⁵)⁴", [("5 · 4", 3, 20)], "La puterea unei puteri înmulțim exponenții."),
        ("Simplifică expresia ((5²)³)².", "((5²)³)²", [("(5²)³", 5, 6), ("(5⁶)²", 5, 12)], "2 · 3 = 6, apoi 6 · 2 = 12."),
        ("Unește mai întâi factorii cu același exponent.", "2⁶ · 5⁶ · 10³", [("2⁶ · 5⁶", 10, 6), ("10⁶ · 10³", 10, 9)], "2⁶ · 5⁶ = 10⁶, apoi adunăm 6 + 3."),
        ("Transformă câtul și apoi simplifică.", "18⁵ : 6⁵ · 3²", [("18⁵ : 6⁵", 3, 5), ("3⁵ · 3²", 3, 7)], "Aplicăm regula aceluiași exponent, apoi adunăm exponenții."),
        ("Completează traseul pentru 4³ · 2³ · 8².", "4³ · 2³ · 8²", [("4³ · 2³", 8, 3), ("8³ · 8²", 8, 5)], "4³ · 2³ = (4 · 2)³ = 8³, apoi 8³ · 8² = 8⁵."),
        ("Redu expresia 11¹⁷ : 11⁵ : 11⁴.", "11¹⁷ : 11⁵ : 11⁴", [("11¹⁷ : 11⁵", 11, 12), ("11¹² : 11⁴", 11, 8)], "Scădem succesiv: 17 − 5 − 4 = 8."),
        ("Calculează exponenții din (2³)⁴ · 2⁵.", "(2³)⁴ · 2⁵", [("(2³)⁴", 2, 12), ("2¹² · 2⁵", 2, 17)], "3 · 4 = 12, apoi 12 + 5 = 17."),
        ("Simplifică 6⁹ : 6³ · 6² : 6⁴.", "6⁹ : 6³ · 6² : 6⁴", [("6⁹ : 6³", 6, 6), ("6⁶ · 6²", 6, 8), ("6⁸ : 6⁴", 6, 4)], "Calculăm de la stânga la dreapta: 9 − 3 + 2 − 4 = 4."),
        ("Scrie produsul 25⁴ · 4⁴ · 10² ca o putere a lui 10.", "25⁴ · 4⁴ · 10²", [("25⁴ · 4⁴", 100, 4), ("100⁴", 10, 8), ("10⁸ · 10²", 10, 10)], "25⁴ · 4⁴ = 100⁴ = 10⁸, apoi obținem 10¹⁰."),
        ("Completează simplificarea lui 9⁷ : 3⁷ · 3⁴.", "9⁷ : 3⁷ · 3⁴", [("9⁷ : 3⁷", 3, 7), ("3⁷ · 3⁴", 3, 11)], "(9 : 3)⁷ = 3⁷, apoi 7 + 4 = 11."),
        ("Transformă 16³ · 4² într-o putere a lui 2.", "16³ · 4²", [("16³", 2, 12), ("4²", 2, 4), ("2¹² · 2⁴", 2, 16)], "16 = 2⁴ și 4 = 2², deci 12 + 4 = 16."),
    ]
    questions += [chain(*spec) for spec in chain_specs]

    match_sets = [
        [("7⁴ · 7³", "7⁷"), ("5¹¹ : 5⁶", "5⁵"), ("(2³)⁴", "2¹²")],
        [("3⁵ · 4⁵", "12⁵"), ("18⁶ : 6⁶", "3⁶"), ("(5²)³", "5⁶")],
        [("2⁷ · 2 · 2³", "2¹¹"), ("9¹⁵ : 9¹⁰", "9⁵"), ("25⁴ · 4⁴", "100⁴")],
        [("(7⁴)²", "7⁸"), ("6³ · 5³", "30³"), ("12⁹ : 12⁴", "12⁵")],
        [("4⁶ · 2⁶", "8⁶"), ("(3⁵)³", "3¹⁵"), ("10¹² : 10⁷", "10⁵")],
    ]
    for index, pairs in enumerate(match_sets):
        questions.append(iq("Potrivește fiecare expresie cu forma sa simplificată: " + ", ".join(left for left, _ in pairs) + ".", "power_match",
                            {"pairs": [{"left": left, "right": right} for left, right in pairs], "right_order": [[2, 0, 1], [1, 2, 0], [2, 1, 0], [1, 0, 2], [0, 2, 1]][index]},
                            "Aplicăm regula indicată de baze și exponenți."))

    errors = [
        (["4³ · 4⁵", "= 4³·⁵", "= 4¹⁵"], 1),
        (["7¹² : 7⁴", "= 7¹²⁺⁴", "= 7¹⁶"], 1),
        (["(5³)⁴", "= 5³⁺⁴", "= 5⁷"], 1),
        (["3⁶ · 2⁶", "= (3 · 2)⁶", "= 6⁷"], 2),
        (["18⁵ : 6⁵", "= (18 : 6)⁵", "= 3⁶"], 2),
    ]
    for index, (steps, error_index) in enumerate(errors):
        questions.append(iq(f"Apasă primul pas greșit din rezolvarea care pornește de la {steps[0]}.", "factor_error",
                            {"steps": steps, "error_index": error_index},
                            "Verificăm regula aplicată și calculul exponentului."))

    assert len(questions) == 47
    return questions


def main():
    target = Path(__file__).resolve().parents[1] / "clasa_5_operatii_reguli_de_calcul_cu_puteri.json"
    payload = {"title": "Reguli de calcul cu puteri", "description": "Clasa a 5-a · Operații cu numere naturale",
               "difficulty": "easy", "questions": build_questions()}
    target.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Am scris {len(payload['questions'])} întrebări în {target}.")


if __name__ == "__main__":
    main()
