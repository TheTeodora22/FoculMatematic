"""Generează lecția introductivă despre fracții ordinare."""

import json
from pathlib import Path


def grid(text, correct, wrong, explanation, fmt="grid"):
    options = [str(correct), *(str(value) for value in wrong)]
    assert len(options) == 4 and len(set(options)) == 4
    order = [2, 0, 3, 1]
    return {"text": text, "type": "multiple_choice", "format": fmt, "points": 10,
            "explanation": explanation,
            "options": [{"text": options[i], "is_correct": i == 0} for i in order]}


def interactive(text, kind, data, explanation):
    return {"text": text, "type": kind, "format": "interactive", "points": 10,
            "explanation": explanation, "interactive": data}


def true_false(text, answer, explanation):
    return {"text": text, "type": "multiple_choice", "format": "true_false", "points": 10,
            "explanation": explanation,
            "options": [{"text": value, "is_correct": value == answer} for value in ("Adevărat", "Fals")]}


def visual(text, mode, n, d, explanation, **extra):
    data = {"mode": mode, "numerator": n, "denominator": d, **extra}
    return interactive(text, "fraction_visual", data, explanation)


def build_questions():
    questions = [
        grid("Ce arată numărătorul unei fracții?", "Câte părți egale au fost luate", ["În câte părți a fost împărțit întregul", "Mărimea întregului", "Câte fracții sunt echivalente"], "Numărătorul arată numărul părților luate."),
        grid("Ce arată numitorul unei fracții?", "În câte părți egale este împărțit întregul", ["Câte părți au fost luate", "Câte procente lipsesc", "Valoarea numărătorului"], "Numitorul indică numărul total de părți egale."),
        grid("Un întreg este împărțit în 8 părți egale și sunt luate 3. Ce fracție s-a luat?", "3/8", ["8/3", "5/8", "3/5"], "S-au luat 3 dintre cele 8 părți egale."),
        grid("Cum se numește fracția 4/7?", "subunitară", ["echiunitară", "supraunitară", "procent"], "4 < 7, deci fracția este subunitară."),
        grid("Cum se numește fracția 7/7?", "echiunitară", ["subunitară", "supraunitară", "ireductibilă"], "Numărătorul este egal cu numitorul."),
        grid("Cum se numește fracția 9/5?", "supraunitară", ["subunitară", "echiunitară", "procentuală"], "9 > 5, deci fracția este supraunitară."),
        grid("Care fracție este echivalentă cu 2/3?", "6/9", ["4/9", "6/8", "8/9"], "Am înmulțit numărătorul și numitorul cu 3."),
        grid("Care pereche NU conține fracții echivalente?", "3/5 și 9/20", ["1/2 și 4/8", "2/3 și 6/9", "3/4 și 12/16"], "3 · 20 ≠ 5 · 9, deci fracțiile nu sunt echivalente."),
        grid("Ce înseamnă 35%?", "35 din 100", ["35 din 10", "100 din 35", "3 din 5"], "Procent înseamnă «la sută»."),
        grid("Care scriere este corectă?", "25% = 25/100", ["25% = 25/10", "25% = 100/25", "25% = 1/25"], "Orice procent p% se scrie p/100."),
        true_false("Numitorul arată câte părți egale formează întregul.", "Adevărat", "Aceasta este semnificația numitorului."),
        true_false("Fracția 4/4 este subunitară.", "Fals", "4/4 este echiunitară, deoarece numărătorul este egal cu numitorul."),
        true_false("Fracțiile 2/3 și 6/9 sunt echivalente.", "Adevărat", "2 · 9 = 3 · 6 = 18."),
        true_false("Pentru orice număr natural p, p% înseamnă p/100.", "Adevărat", "Simbolul % înseamnă «la sută»."),
    ]

    for n, d, shape in [(2, 5, "bar"), (3, 8, "circle"), (4, 6, "grid"), (1, 4, "circle"), (7, 10, "bar")]:
        questions.append(visual(f"Colorează {n}/{d} din întreg.", "color", n, d,
            f"Trebuie colorate {n} dintre cele {d} părți egale.", shape=shape,
            answers={"selected": ",".join(str(i) for i in range(n))}))

    reading_prompts = [
        "Scrie fracția reprezentată de banda colorată.",
        "Ce fracție din disc este colorată?",
        "Scrie fracția arătată de mozaic.",
        "Ce parte din cerc a fost colorată? Scrie răspunsul ca fracție.",
        "Ce fracție din tablă este colorată?",
    ]
    for prompt, (n, d, shape) in zip(reading_prompts, [(3, 7, "bar"), (5, 8, "circle"), (4, 9, "grid"), (2, 5, "circle"), (7, 10, "grid")]):
        questions.append(visual(prompt, "read", n, d,
            f"Sunt colorate {n} dintre cele {d} părți egale, deci fracția este {n}/{d}.",
            shape=shape, answers={"numerator": n, "denominator": d}))

    for n, d, shape in [(2, 3, "bar"), (4, 7, "circle"), (5, 5, "grid"), (6, 8, "bar"), (3, 10, "grid")]:
        questions.append(visual(f"Construiește fracția {n}/{d} și urmărește cum se schimbă desenul.", "construct", n, d,
            f"Fracția cerută are numărătorul {n} și numitorul {d}.", shape=shape,
            answers={"numerator": n, "denominator": d}))

    repairs = [
        (8, 5, "subunitară", 4, "Scrie cel mai mare numărător natural care transformă fracția într-una subunitară."),
        (3, 7, "echiunitară", 7, "Schimbă numărătorul astfel încât fracția să fie echiunitară."),
        (4, 4, "supraunitară", 5, "Scrie cel mai mic numărător natural care face fracția supraunitară."),
        (9, 6, "echiunitară", 6, "Schimbă numărătorul astfel încât fracția să fie echiunitară."),
        (5, 8, "supraunitară", 9, "Scrie cel mai mic numărător natural care face fracția supraunitară."),
    ]
    for n, d, target, answer, text in repairs:
        questions.append(visual(f"În fracția {n}/{d}, {text[0].lower() + text[1:]}", "repair", n, d,
            f"Răspunsul este {answer}/{d}: comparăm numărătorul cu numitorul {d}.",
            editable="numerator", target_label=target, answers={"numerator": answer}))

    domino_sets = [
        ([{"left":"1/2","right":"3/4"},{"left":"6/8","right":"2/3"},{"left":"4/6","right":"25%"},{"left":"1/4","right":"3/5"}], [2,0,3,1]),
        ([{"left":"2/5","right":"1/2"},{"left":"5/10","right":"3/4"},{"left":"9/12","right":"1/3"},{"left":"2/6","right":"4/5"}], [1,3,0,2]),
        ([{"left":"20%","right":"2/5"},{"left":"4/10","right":"3/5"},{"left":"6/10","right":"1/4"},{"left":"25/100","right":"7/8"}], [3,1,0,2]),
        ([{"left":"3/9","right":"1/2"},{"left":"4/8","right":"2/7"},{"left":"6/21","right":"75%"},{"left":"3/4","right":"5/6"}], [2,0,3,1]),
    ]
    for set_index, (tiles, display) in enumerate(domino_sets, start=1):
        questions.append(interactive(f"Construiește lanțul care începe cu piesa {tiles[0]['left']} | {tiles[0]['right']}; laturile vecine trebuie să fie echivalente.",
            "fraction_domino", {"tiles": tiles, "correct_order": [0,1,2,3], "display_order": display},
            "Verificăm fiecare îmbinare prin amplificare, simplificare sau transformare în procent."))

    for n, d, percent in [(1, 2, 50), (1, 4, 25), (3, 5, 60), (7, 10, 70)]:
        questions.append(visual(f"Transformă fracția {n}/{d} într-o fracție cu numitorul 100 și apoi în procent.",
            "percent", n, d, f"{n}/{d} = {percent}/100 = {percent}%.",
            answers={"hundredths": percent, "percent": percent}))

    assert len(questions) == 42
    return questions


def build_amplification_questions():
    questions = []
    for n, d, factor in [(1, 3, 4), (2, 5, 3), (3, 7, 2), (4, 9, 5), (5, 8, 4), (7, 10, 3)]:
        questions.append(visual(f"Amplifică fracția {n}/{d} cu {factor}.", "equivalent", n, d,
            f"Înmulțim ambii termeni cu {factor}: {n * factor}/{d * factor}.", factor=factor,
            answers={"factor": factor, "numerator": n * factor, "denominator": d * factor}))
    return questions


def main():
    target = Path(__file__).resolve().parents[1] / "clasa_5_fractii_ordinare.json"
    payload = {"title": "Fracții ordinare. Fracții echivalente. Procente",
               "description": "Clasa a 5-a · Fracții ordinare", "difficulty": "medium",
               "questions": build_questions()}
    target.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Am scris {len(payload['questions'])} întrebări în {target}.")

    amplification_target = Path(__file__).resolve().parents[1] / "clasa_5_fractii_ordinare_cmmdc_amplificarea_si_simplificarea.json"
    amplification_payload = {
        "title": "Cel mai mare divizor comun a două numere naturale. Amplificarea și simplificarea fracțiilor. Fracții ireductibile",
        "description": "Clasa a 5-a · Fracții ordinare",
        "difficulty": "easy",
        "questions": build_amplification_questions(),
    }
    amplification_target.write_text(json.dumps(amplification_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Am mutat {len(amplification_payload['questions'])} întrebări în {amplification_target}.")


if __name__ == "__main__":
    main()
