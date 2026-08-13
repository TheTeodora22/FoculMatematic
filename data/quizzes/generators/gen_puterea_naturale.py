"""Generează lecția despre puteri cu grile, adevărat/fals și activități interactive."""

import json
from pathlib import Path


SUPERSCRIPT = str.maketrans("0123456789", "⁰¹²³⁴⁵⁶⁷⁸⁹")


def notation(base, exponent):
    return f"{base}{str(exponent).translate(SUPERSCRIPT)}"


def q(text, correct, wrong, explanation):
    options = [str(correct), *(str(value) for value in wrong)]
    assert len(options) == 4 and len(set(options)) == 4
    order = [1, 0, 3, 2]
    return {
        "text": text,
        "type": "multiple_choice",
        "format": "grid",
        "points": 10,
        "explanation": explanation,
        "options": [
            {"text": options[index], "is_correct": index == 0}
            for index in order
        ],
    }


def tf(text, answer, explanation):
    return {
        "text": text,
        "type": "multiple_choice",
        "format": "true_false",
        "points": 10,
        "explanation": explanation,
        "options": [
            {"text": "Adevărat", "is_correct": answer},
            {"text": "Fals", "is_correct": not answer},
        ],
    }


def iq(text, question_type, interactive, explanation):
    return {
        "text": text,
        "type": question_type,
        "format": "interactive",
        "points": 10,
        "explanation": explanation,
        "interactive": interactive,
    }


def power_data(base, exponent, mode, missing=None):
    data = {
        "mode": mode,
        "base": base,
        "exponent": exponent,
        "value": base ** exponent,
        "factors": [base] * exponent,
    }
    if missing:
        data["missing"] = missing
    return data


def build_questions():
    questions = []

    calculations = [
        ("Calculează 2⁵.", 32, [10, 16, 25], "2⁵ = 2 · 2 · 2 · 2 · 2 = 32."),
        ("Care este valoarea lui 3⁴?", 81, [12, 27, 64], "3⁴ = 3 · 3 · 3 · 3 = 81."),
        ("Calculează 10⁴.", 10_000, [40, 1_000, 100_000], "O putere a lui 10 are atâtea zerouri cât arată exponentul."),
        ("Calculează 7² + 2³.", 57, [49, 56, 64], "7² + 2³ = 49 + 8 = 57."),
        ("Calculează 5³ − 3².", 116, [16, 98, 122], "5³ − 3² = 125 − 9 = 116."),
        ("Care este valoarea expresiei 2⁴ · 3?", 48, [24, 32, 64], "Mai întâi calculăm puterea: 2⁴ · 3 = 16 · 3 = 48."),
        ("Calculează 4³ + 6².", 100, [76, 88, 120], "4³ + 6² = 64 + 36 = 100."),
        ("Care este rezultatul lui 1²⁰²⁶ + 9²?", 82, [81, 83, 2_027], "Orice putere a lui 1 este 1, deci 1 + 81 = 82."),
    ]
    for item in calculations:
        questions.append(q(*item))

    questions.extend([
        q("În scrierea 8⁵, care este exponentul?", 5, [8, 13, 40], "Exponentul este numărul mic scris în dreapta sus; el arată câți factori egali cu 8 apar."),
        q("În scrierea 6³, care este baza?", 6, [3, 18, 216], "Baza este numărul care se înmulțește cu el însuși."),
        q("Ce produs reprezintă 4⁵?", "4 · 4 · 4 · 4 · 4", ["5 · 5 · 5 · 5", "4 · 5", "4 + 4 + 4 + 4 + 4"], "Exponentul 5 cere cinci factori egali cu baza 4."),
        q("Care putere este egală cu 7 · 7 · 7?", "7³", ["3⁷", "7²", "21³"], "Produsul conține trei factori egali cu 7, deci este 7³."),
        q("Ce număr trebuie pus în locul lui n pentru ca 3ⁿ = 81?", 4, [3, 9, 27], "3 · 3 · 3 · 3 = 81, deci exponentul este 4."),
        q("Ce număr trebuie pus în locul lui a pentru ca a³ = 125?", 5, [3, 15, 25], "125 = 5 · 5 · 5, deci baza este 5."),
    ])

    questions.extend([
        q("Un pătrat are latura de 12 cm. Care este aria lui, scrisă mai întâi ca putere?", "12² = 144 cm²", ["2¹² = 4 096 cm²", "12 · 2 = 24 cm²", "12³ = 1 728 cm²"], "Aria pătratului este latura la puterea a doua: 12² = 144 cm²."),
        q("Horia citește 2 pagini în prima zi și dublează zilnic numărul. Câte pagini citește în ziua a șasea?", 64, [12, 32, 128], "În ziua a șasea citește 2⁶ = 64 de pagini."),
        q("Pe prima căsuță a unei table sunt 2 boabe, iar pe fiecare căsuță următoare numărul se dublează. Câte boabe sunt pe căsuța a opta?", 256, [16, 128, 512], "Pe căsuța a opta sunt 2⁸ = 256 de boabe."),
        q("Care este ultima cifră a lui 2²⁰²⁶?", 4, [2, 6, 8], "Ultimele cifre se repetă 2, 4, 8, 6. Deoarece 2 026 dă restul 2 la împărțirea cu 4, ultima cifră este 4."),
        q("Care este ultima cifră a lui 7¹⁰³?", 3, [1, 7, 9], "Ciclul este 7, 9, 3, 1. Exponentul 103 dă restul 3 la împărțirea cu 4."),
        q("Care dintre numere este pătrat perfect?", 625, [125, 250, 575], "625 = 25², deci este pătrat perfect."),
    ])

    questions.extend([
        tf("Puterea 5⁴ conține patru factori egali cu 5.", True, "5⁴ = 5 · 5 · 5 · 5."),
        tf("Egalitatea 3⁴ = 4³ este adevărată.", False, "3⁴ = 81, iar 4³ = 64."),
        tf("Orice putere nenulă a numărului 1 este egală cu 1.", True, "Produsul oricâtor factori egali cu 1 rămâne 1."),
        tf("Numărul 225 este un pătrat perfect.", True, "225 = 15²."),
        tf("Ultima cifră a oricărei puteri nenule a lui 5 este 0.", False, "Orice putere nenulă a lui 5 se termină în 5."),
        tf("Numărul 90 poate fi pătratul unui număr natural.", False, "9² = 81 și 10² = 100, iar 90 este între aceste pătrate consecutive."),
    ])

    for base, exponent in [(3, 4), (6, 3), (2, 6), (9, 3)]:
        factors = " · ".join([str(base)] * exponent)
        questions.append(iq(
            f"Scrie produsul {factors} sub forma unei puteri.",
            "power_builder",
            power_data(base, exponent, "compose"),
            f"Sunt {exponent} factori egali cu {base}, deci obținem {notation(base, exponent)}.",
        ))

    for base, exponent in [(5, 4), (7, 3), (2, 7), (4, 5)]:
        questions.append(iq(
            f"Desfă {notation(base, exponent)} într-un produs de factori egali.",
            "power_builder",
            power_data(base, exponent, "expand"),
            f"Exponentul {exponent} arată că baza {base} apare de {exponent} ori ca factor.",
        ))

    match_sets = [
        [(2, 5), (3, 3), (5, 2)],
        [(4, 3), (6, 2), (10, 3)],
        [(7, 2), (3, 4), (2, 6)],
        [(9, 2), (5, 3), (8, 2)],
    ]
    for index, entries in enumerate(match_sets):
        pairs = []
        for base, exponent in entries:
            expanded = " · ".join([str(base)] * exponent)
            pairs.append({"left": notation(base, exponent), "right": f"{expanded} = {base ** exponent}"})
        questions.append(iq(
            "Unește cu forma echivalentă puterile " + ", ".join(notation(base, exponent) for base, exponent in entries) + ".",
            "power_match",
            {"pairs": pairs, "right_order": [[2, 0, 1], [1, 2, 0], [2, 1, 0], [1, 0, 2]][index]},
            "Baza se repetă ca factor de atâtea ori cât arată exponentul.",
        ))

    table_sets = [
        [(2, 5, "base"), (3, 4, "exponent"), (5, 3, "value")],
        [(4, 3, "value"), (6, 2, "base"), (10, 4, "exponent")],
        [(7, 2, "exponent"), (2, 8, "value"), (9, 2, "base")],
        [(3, 5, "value"), (8, 2, "exponent"), (5, 4, "base")],
    ]
    for rows in table_sets:
        questions.append(iq(
            "Completează celulele libere pentru puterile cu bazele " + ", ".join(str(base) for base, _, _ in rows) + ".",
            "power_table",
            {"rows": [{"base": base, "exponent": exponent, "value": base ** exponent, "missing": missing} for base, exponent, missing in rows]},
            "Pe fiecare rând folosim relația: valoarea = baza înmulțită cu ea însăși de câte ori arată exponentul.",
        ))

    for base, exponent, length in [(12, 37, 4), (7, 46, 4), (9, 125, 2), (5, 2_026, 1)]:
        cycle = [pow(base, power, 10) for power in range(1, length + 1)]
        questions.append(iq(
            f"Descoperă ultima cifră a lui {notation(base, exponent)}.",
            "power_cycle",
            {"base": base, "exponent": exponent, "cycle": cycle, "last_digit": pow(base, exponent, 10)},
            f"Ciclul are {length} poziții; poziția exponentului în ciclu indică ultima cifră.",
        ))

    missing_items = [(5, 4, "base"), (3, 5, "exponent"), (7, 3, "value"), (10, 6, "exponent")]
    for base, exponent, missing in missing_items:
        labels = {"base": "baza", "exponent": "exponentul", "value": "valoarea"}
        visible_hint = {
            "base": f"□{str(exponent).translate(SUPERSCRIPT)} = {base ** exponent}",
            "exponent": f"{base}□ = {base ** exponent}",
            "value": f"{notation(base, exponent)} = □",
        }[missing]
        questions.append(iq(
            f"Completează {labels[missing]} lipsă din egalitatea {visible_hint}.",
            "power_builder",
            power_data(base, exponent, "missing", missing),
            f"Egalitatea completă este {notation(base, exponent)} = {base ** exponent}.",
        ))

    for side in [3, 4, 5, 6]:
        questions.append(iq(
            f"Pătratul desenat are câte {side} pătrățele pe fiecare latură. Scrie numărul total ca putere și calculează-l.",
            "power_square",
            {"side": side, "value": side ** 2},
            f"Sunt {side} rânduri a câte {side} pătrățele: {notation(side, 2)} = {side ** 2}.",
        ))

    assert len(questions) == 54
    return questions


def main():
    target = Path(__file__).resolve().parents[1] / "clasa_5_operatii_puterea_cu_exponent_natural.json"
    payload = {
        "title": "Puterea cu exponent natural a unui număr natural. Pătratul unui număr natural",
        "description": "Clasa a 5-a · Operații cu numere naturale",
        "difficulty": "easy",
        "questions": build_questions(),
    }
    target.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Am scris {len(payload['questions'])} întrebări în {target}.")


if __name__ == "__main__":
    main()
