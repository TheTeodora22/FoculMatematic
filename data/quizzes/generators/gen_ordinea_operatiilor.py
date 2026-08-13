"""Generează lecția despre ordinea efectuării operațiilor și paranteze."""

import json
from pathlib import Path


def q(text, correct, wrong, explanation):
    values = [str(correct), *(str(value) for value in wrong)]
    assert len(values) == 4 and len(set(values)) == 4
    return {"text": text, "type": "multiple_choice", "format": "grid", "points": 10,
            "explanation": explanation,
            "options": [{"text": values[index], "is_correct": index == 0} for index in [1, 3, 0, 2]]}


def tf(text, answer, explanation):
    return {"text": text, "type": "multiple_choice", "format": "true_false", "points": 10,
            "explanation": explanation,
            "options": [{"text": "Adevărat", "is_correct": answer}, {"text": "Fals", "is_correct": not answer}]}


def iq(text, kind, data, explanation):
    return {"text": text, "type": kind, "format": "interactive", "points": 10,
            "explanation": explanation, "interactive": data}


def build_questions():
    questions = [
        q("Calculează 5 · 6 + 2 · 12.", 54, [42, 72, 360], "Înmulțirile se efectuează înaintea adunării: 30 + 24 = 54."),
        q("Care este valoarea expresiei 32 + 5 · 14 − 7?", 95, [511, 448, 102], "Mai întâi 5 · 14 = 70, apoi 32 + 70 − 7 = 95."),
        q("Calculează 5 · 3² − 7 · 2² + 6² : 5.", 24, [4, 52, 120], "Puterile: 9, 4 și 36; apoi 45 − 28 + 36 : 5 nu este exact. Expresia corectă folosește 35 : 5 = 7."),
        q("Care operație se efectuează prima în 18 + 4 · 7?", "4 · 7", ["18 + 4", "18 + 7", "Adunarea finală"], "Înmulțirea are prioritate față de adunare."),
        q("Care este primul calcul din 2 + 3³ · 4?", "3³", ["2 + 3", "3 · 4", "2 + 4"], "Puterile se calculează înaintea înmulțirilor și adunărilor."),
        q("Calculează 48 : 6 · 3 + 2.", 26, [4, 8, 38], "Împărțirea și înmulțirea au același ordin și se fac de la stânga la dreapta: 48 : 6 = 8, 8 · 3 = 24, apoi +2."),
        q("Care este valoarea lui 100 − 5 · (6 + 3)?", 55, [855, 570, 145], "Mai întâi paranteza: 9; apoi 5 · 9 = 45; la final 100 − 45 = 55."),
        q("Calculează 10 + 9 · [8 + 7 · (6 + 5 · 10)].", 3610, [730, 910, 3690], "Începem cu paranteza rotundă, apoi pătrată: 6 + 50 = 56, 8 + 7 · 56 = 400, iar 10 + 9 · 400 = 3 610."),
        q("În expresia 72 : (8 + 1), ce se calculează prima dată?", "8 + 1", ["72 : 8", "72 : 1", "Împărțirea finală"], "Operațiile din paranteze se efectuează înaintea celor din exterior."),
        q("Care este rezultatul lui 3 · 8 : 4 + 6 · 2 − 18?", 0, [6, 12, 24], "3 · 8 : 4 = 6 și 6 · 2 = 12; apoi 6 + 12 − 18 = 0."),
    ]

    # Înlocuim o expresie intenționat neexactă din listă cu una potrivită clasei a V-a.
    questions[2] = q("Calculează 5 · 3² − 7 · 2² + 35 : 5.", 24, [4, 52, 120], "Puterile se calculează primele: 45 − 28 + 7 = 24.")

    questions += [
        tf("Înmulțirea și împărțirea se efectuează înaintea adunării și scăderii.", True, "Ele sunt operații de ordinul al doilea."),
        tf("Într-un șir de înmulțiri și împărțiri calculăm întotdeauna mai întâi toate înmulțirile.", False, "Operațiile de același ordin se efectuează de la stânga la dreapta."),
        tf("În expresia 4 + 3² · 5, puterea se calculează prima.", True, "Ridicarea la putere are prioritate."),
        tf("Într-o expresie cu (), [] și {}, începem întotdeauna cu acoladele.", False, "Calculăm din interior spre exterior: rotunde, apoi pătrate, apoi acolade."),
    ]

    sequences = [
        ("8 + 3 · 5", ["3 · 5", "8 + 15"], [1, 0]),
        ("2 + 3² · 4", ["3²", "9 · 4", "2 + 36"], [2, 0, 1]),
        ("48 : 6 · 3 + 2", ["48 : 6", "8 · 3", "24 + 2"], [1, 2, 0]),
        ("100 − 5 · (6 + 3)", ["6 + 3", "5 · 9", "100 − 45"], [2, 0, 1]),
        ("72 : (8 + 1) · 5", ["8 + 1", "72 : 9", "8 · 5"], [1, 2, 0]),
        ("4 + 2³ · 5 − 6", ["2³", "8 · 5", "4 + 40", "44 − 6"], [3, 1, 0, 2]),
        ("90 : 5 · 2 + 3", ["90 : 5", "18 · 2", "36 + 3"], [2, 0, 1]),
        ("{10 + [8 · (6 + 2)]} : 2", ["6 + 2", "8 · 8", "10 + 64", "74 : 2"], [3, 0, 2, 1]),
        ("[40 − (18 : 3)] · 2", ["18 : 3", "40 − 6", "34 · 2"], [1, 2, 0]),
        ("5² + 36 : 6 · 2", ["5²", "36 : 6", "6 · 2", "25 + 12"], [2, 0, 3, 1]),
        ("120 : {5 · [2 + (7 − 3)]}", ["7 − 3", "2 + 4", "5 · 6", "120 : 30"], [1, 3, 0, 2]),
        ("3 · [20 − 2 · (4 + 1)]", ["4 + 1", "2 · 5", "20 − 10", "3 · 10"], [2, 0, 3, 1]),
    ]
    for expression, steps, display_order in sequences:
        questions.append(iq(f"Construiește ordinea completă a calculelor din {expression}.", "operation_sequence",
                            {"expression": expression, "steps": steps, "display_order": display_order, "correct_order": list(range(len(steps)))},
                            "Respectăm parantezele, apoi puterile, operațiile de ordinul al doilea și la final adunările sau scăderile."))

    workbenches = [
        ("6 · 9 + 4", [("6 · 9", 54), ("54 + 4", 58)]),
        ("80 − 7 · 6", [("7 · 6", 42), ("80 − 42", 38)]),
        ("3² + 5 · 8", [("3²", 9), ("5 · 8", 40), ("9 + 40", 49)]),
        ("64 : 8 · 5 − 7", [("64 : 8", 8), ("8 · 5", 40), ("40 − 7", 33)]),
        ("120 : (7 + 3) + 4", [("7 + 3", 10), ("120 : 10", 12), ("12 + 4", 16)]),
        ("5 · [18 − (9 + 3)]", [("9 + 3", 12), ("18 − 12", 6), ("5 · 6", 30)]),
        ("2⁴ · 3 + 10", [("2⁴", 16), ("16 · 3", 48), ("48 + 10", 58)]),
        ("100 − 36 : 6 · 4", [("36 : 6", 6), ("6 · 4", 24), ("100 − 24", 76)]),
        ("{50 − [3 · (8 + 2)]} · 2", [("8 + 2", 10), ("3 · 10", 30), ("50 − 30", 20), ("20 · 2", 40)]),
        ("7 + 5² − 18 : 3", [("5²", 25), ("18 : 3", 6), ("7 + 25 − 6", 26)]),
        ("144 : [3 · (6 + 2)]", [("6 + 2", 8), ("3 · 8", 24), ("144 : 24", 6)]),
        ("4 · {30 − [2³ + 7]}", [("2³", 8), ("8 + 7", 15), ("30 − 15", 15), ("4 · 15", 60)]),
    ]
    for expression, stages in workbenches:
        questions.append(iq(f"Completează rezultatele intermediare pentru {expression}.", "operation_workbench",
                            {"expression": expression, "stages": [{"expression": label, "answer": answer} for label, answer in stages]},
                            "Fiecare rând folosește rezultatul corect al etapei precedente."))

    parentheses = [
        (["8", "+ 4", "· 3"], 0, 2, 36),
        (["72", ": 8", "+ 1"], 1, 3, 8),
        (["42", "− 18", ": 6"], 0, 2, 4),
        (["6", "+ 2", "· 5"], 0, 2, 40),
        (["90", ": 5", "+ 4"], 1, 3, 10),
        (["7", "· 8", "− 3"], 1, 3, 35),
        (["120", ": 10", "− 4"], 1, 3, 20),
        (["100", "− 5", "· 6"], 0, 2, 570),
    ]
    for tokens, open_index, close_index, target in parentheses:
        expression = " ".join(tokens)
        questions.append(iq(f"Așază parantezele în {expression} pentru a obține {target}.", "parentheses_target",
                            {"tokens": tokens, "correct_open_index": open_index, "correct_close_index": close_index, "target": target},
                            f"Parantezele schimbă ordinea calculelor și conduc la rezultatul {target}."))

    errors = [
        (["15 + 4 · 3", "= 19 · 3", "= 57"], 1, "15 + 4 · 3"),
        (["48 : 6 · 2", "= 48 : 12", "= 4"], 1, "48 : 6 · 2"),
        (["3² + 5 · 4", "= 6 + 20", "= 26"], 1, "3² + 5 · 4"),
        (["100 − 5 · (7 + 1)", "= 100 − 5 · 8", "= 95 · 8", "= 760"], 2, "100 − 5 · (7 + 1)"),
        (["72 : (6 + 3)", "= 72 : 9", "= 9"], 2, "72 : (6 + 3)"),
        (["5 + 24 : 6 · 2", "= 5 + 4 · 2", "= 9 · 2", "= 18"], 2, "5 + 24 : 6 · 2"),
        (["2³ · 5 − 7", "= 6 · 5 − 7", "= 30 − 7", "= 23"], 1, "2³ · 5 − 7"),
        (["{20 + [3 · (8 − 2)]} : 2", "= {20 + [3 · 6]} : 2", "= 20 + 18 : 2", "= 29"], 2, "{20 + [3 · (8 − 2)]} : 2"),
    ]
    for steps, error_index, expression in errors:
        questions.append(iq(f"Apasă primul pas greșit din rezolvarea expresiei {expression}.", "factor_error",
                            {"steps": steps, "error_index": error_index},
                            "Primul pas greșit este cel care nu respectă prioritatea operațiilor sau calculează incorect."))

    assert len(questions) == 54
    assert len({question["text"] for question in questions}) == len(questions)
    return questions


def main():
    target = Path(__file__).resolve().parents[1] / "clasa_5_operatii_cu_numere_naturale.json"
    payload = {"title": "Ordinea efectuării operațiilor; utilizarea parantezelor: rotunde, pătrate și acolade",
               "description": "Clasa a 5-a · Operații cu numere naturale", "difficulty": "medium",
               "questions": build_questions()}
    target.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Am scris {len(payload['questions'])} întrebări în {target}.")


if __name__ == "__main__":
    main()
