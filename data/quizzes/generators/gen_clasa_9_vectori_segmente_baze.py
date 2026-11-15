"""60 grile originale: G1 §1 și §3, câte cinci adaptări pentru fiecare tip.

Nu modifică interactivele, baza de date sau alte bănci de întrebări.
"""
import json
import re
from fractions import Fraction as F
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "clasa_9"
BANK = "vectori_segmente_baze_v1"
FILES = {
    1: ROOT / "clasa_9_u05_l01_segmente_orientate_relatia_de_echipolenta.json",
    4: ROOT / "clasa_9_u05_l04_descompunerea_unui_vector_dupa_doi_vectori_necoliniari.json",
}
NAMES = {
    1: ["Direcții determinate de puncte", "Semidrepte cu același sens sau sens opus",
        "Echipolență pe rețea", "Reprezentanții unui vector liber",
        "Vectori opuși și coliniari", "Configurație construită prin echipolență"],
    4: ["Descompunere pe laturile triunghiului", "Schimbarea bazei folosind mediane",
        "Componente egale în modul", "Descompunere după două ceviene",
        "Descompunere cu raport de împărțire", "Descompunere în patrulatere și hexagoane"],
}


def pair(v):
    return "(" + "; ".join(str(F(c)) for c in v) + ")"


def add(a, b):
    return tuple(F(x) + F(y) for x, y in zip(a, b))


def sub(a, b):
    return tuple(F(x) - F(y) for x, y in zip(a, b))


def mul(k, a):
    return tuple(F(k) * F(x) for x in a)


def serial(value):
    if isinstance(value, (list, tuple)):
        return [serial(x) for x in value]
    if isinstance(value, dict):
        return {key: serial(x) for key, x in value.items()}
    if isinstance(value, F):
        return str(value)
    return value


def item(lesson, family, variant, text, answer, explanation, verification, wrong=None):
    if isinstance(answer, tuple):
        alternatives = [answer, add(answer, (1, 0)), add(answer, (0, 1)), sub(answer, (1, 1))]
        answers = [pair(v) for v in alternatives]
        verification = {**verification, "answer_kind": "pair"}
    elif isinstance(answer, (int, F)):
        answers = [str(answer), str(answer + 1), str(answer - 1), str(answer + 2)]
        verification = {**verification, "answer_kind": "number"}
    else:
        answers = [answer, *wrong]
        verification = {**verification, "answer_kind": "text"}
    assert len(set(answers)) == 4
    correct = ((family - 1) * 5 + variant - 1) % 4
    answers.insert(correct, answers.pop(0))
    return {
        "text": text, "type": "multiple_choice", "format": "grid", "points": 10,
        "explanation": explanation,
        "options": [{"text": value, "is_correct": index == correct} for index, value in enumerate(answers)],
        "practice_scope": {
            "bank": BANK, "lesson": lesson, "catalog": "G1_catalog.md",
            "section": "1" if lesson == 1 else "3", "family": family,
            "family_name": NAMES[lesson][family - 1], "variant": variant,
            "pages": "162–163" if lesson == 1 else "176",
            "adaptation": "Exercițiu original; tipul de construcție/demonstrație este adaptat în grilă cu justificare în explicație.",
        },
        "verification": serial(verification),
    }


def build_lesson1():
    questions = []
    configurations = [
        [(0, 0), (4, 0), (4, 2), (0, 2)],
        [(0, 0), (3, 0), (1, 4)],
        [(-2, 1), (0, 1), (3, 1), (7, 1)],
        [(0, 0), (3, 1), (5, 4), (2, 3)],
        [(-2, -2), (2, -2), (2, 2), (-2, 2), (0, 0)],
    ]
    for j, points in enumerate(configurations, 1):
        directions = set()
        for i, p in enumerate(points):
            for q in points[i + 1:]:
                dx, dy = sub(q, p)
                directions.add("vertical" if dx == 0 else F(dy, dx))
        labels = ", ".join(chr(65 + i) + pair(p) for i, p in enumerate(points))
        slopes = ", ".join("verticală" if d == "vertical" else "pantă " + str(d)
                           for d in sorted(directions, key=str))
        questions.append(item(1, 1, j,
            f"Se dau punctele {labels}. Câte direcții distincte au dreptele determinate de câte două puncte? Dreptele paralele au aceeași direcție.",
            len(directions),
            "Grupăm dreptele paralele. Pentru o dreaptă neverticală direcția este determinată de panta Δy/Δx; toate verticalele au aceeași direcție. "
            + f"Direcțiile distincte sunt: {slopes}. Rezultă {len(directions)} direcții, indiferent de sensul în care parcurgem dreapta.",
            {"mode": "directions", "points": points}))

        a = (j, -j); u = (j + 1, 2); b = add(a, u)
        c = (-j - 2, j + 3); k = [-3, 2, -1, 4, 3][j - 1]; d = add(c, mul(k, u))
        answer = "Aceeași direcție și același sens" if k > 0 else "Aceeași direcție și sensuri opuse"
        others = ["Direcții diferite", "Semidrepte fără direcție",
                  "Aceeași direcție și sensuri opuse" if k > 0 else "Aceeași direcție și același sens"]
        questions.append(item(1, 2, j,
            f"Pentru A{pair(a)}, B{pair(b)}, C{pair(c)}, D{pair(d)}, comparați direcția și sensul semidreptelor [AB și [CD.",
            answer,
            f"Deplasările sunt AB={pair(u)} și CD={pair(mul(k, u))}={k}·AB. Ambele sunt nenule. Multiplicarea cu un număr "
            + ("pozitiv păstrează sensul" if k > 0 else "negativ inversează sensul")
            + "; proporționalitatea păstrează direcția. Originile diferite nu schimbă această clasificare.",
            {"mode": "rays", "A": a, "B": b, "C": c, "D": d}, others))

        a = (-j, j); b = (j + 2, -2); u = sub(b, a)
        starts = [(j, 2), (-3, j), (2, -j), (-j - 3, 4)]
        vectors = [u, mul(-1, u), mul(2, u), (u[1], -u[0])]
        segments = {"CD": [starts[0], add(starts[0], vectors[0])],
                    "EF": [starts[1], add(starts[1], vectors[1])],
                    "GH": [starts[2], add(starts[2], vectors[2])],
                    "IJ": [starts[3], add(starts[3], vectors[3])]}
        description = "; ".join(name[0] + pair(p) + ", " + name[1] + pair(q)
                                for name, (p, q) in segments.items())
        questions.append(item(1, 3, j,
            f"Pe o rețea se dau A{pair(a)}, B{pair(b)} și {description}. Care segment orientat este echipolent cu AB?",
            "CD",
            f"AB=B−A={pair(u)}. CD are exact aceeași deplasare {pair(u)}; EF are deplasarea opusă, GH are modul dublu, iar IJ are altă direcție. Echipolența cere simultan aceeași direcție, același sens și același modul.",
            {"mode": "equipollent", "A": a, "B": b, "segments": segments}, ["EF", "GH", "IJ"]))

        width, height = j + 1, j + 2
        points = [(x, y) for y in range(height + 1) for x in range(width + 1)]
        count = width * height
        questions.append(item(1, 4, j,
            f"În rețeaua finită formată din toate punctele întregi (x; y) cu 0≤x≤{width} și 0≤y≤{height}, câte segmente orientate reprezintă vectorul liber (1; 1)? Ambele capete trebuie să aparțină rețelei.",
            count,
            f"Pentru origine (x; y), vârful trebuie să fie (x+1; y+1). Astfel 0≤x≤{width-1} și 0≤y≤{height-1}: sunt {width} alegeri pentru x și {height} pentru y, deci {count} reprezentanți. Enumerarea este completă deoarece deplasarea fixează unic vârful pentru fiecare origine admisă.",
            {"mode": "representatives", "points": points, "vector": [1, 1]}))

        u = (j + 1, -j - 2)
        candidates = {"v": mul(-1, u), "w": mul(-2, u), "r": mul(3, u), "s": (u[1], -u[0])}
        desc = ", ".join(name + "=" + pair(v) for name, v in candidates.items())
        questions.append(item(1, 5, j,
            f"Vectorii considerați sunt u={pair(u)} și {desc}. Care vector este opusul lui u (nu doar un vector coliniar cu sens opus)?",
            "v",
            f"Opusul este −u={pair(mul(-1, u))}=v. Vectorul w=−2u are sens opus, dar modul dublu, deci nu este opusul. Vectorul r=3u are același sens. Vectorul s are determinant nenul cu u, fiind perpendicular pe u. Doar v îndeplinește egalitatea v=−u.",
            {"mode": "opposite", "u": u, "candidates": candidates}, ["w", "r", "s"]))

        cases = [((3, 0), (0, 3)), ((4, 0), (0, 2)), ((5, 0), (3, 4)), ((4, 0), (1, 2)), ((2, 1), (-1, 2))]
        u, v = cases[j - 1]; a = (j, -2 * j); b = add(a, u); d = add(a, v)
        dot = sum(x * y for x, y in zip(u, v)); equal = sum(x*x for x in u) == sum(y*y for y in v)
        shapes = ["Pătrat", "Dreptunghi care nu este pătrat", "Romb care nu este pătrat", "Paralelogram care nu este nici dreptunghi, nici romb"]
        answer = shapes[0 if dot == 0 and equal else 1 if dot == 0 else 2 if equal else 3]
        c = add(b, v)
        questions.append(item(1, 6, j,
            f"Se dau A{pair(a)}, B{pair(b)}, D{pair(d)}. Se construiește C astfel încât segmentele orientate BC și AD să fie echipolente. Care este cea mai precisă clasificare a patrulaterului ABCD?",
            answer,
            f"Echipolența BC=AD dă C=B+D−A={pair(c)}, deci și DC=AB: ABCD este paralelogram. Vectorii laturilor alăturate sunt AB={pair(u)}, AD={pair(v)} și sunt necoliniari. Pătratele lungimilor sunt AB²={sum(x*x for x in u)}, AD²={sum(x*x for x in v)}, BD²={sum(x*x for x in sub(b,d))}. "
            + ("Relația BD²=AB²+AD² și reciproca teoremei lui Pitagora dau AB⊥AD. " if dot == 0 else "Deoarece BD²≠AB²+AD², laturile alăturate nu sunt perpendiculare. ")
            + ("Laturile au lungimi egale. " if equal else "Laturile au lungimi diferite. ")
            + f"Rezultă: {answer.lower()}.",
            {"mode": "quadrilateral", "A": a, "B": b, "D": d}, [shape for shape in shapes if shape != answer]))
    return sorted(questions, key=lambda q: (q["practice_scope"]["family"], q["practice_scope"]["variant"]))


def build_lesson4():
    questions = []
    for j in range(1, 6):
        k = [-3, -1, 1, 2, 5][j - 1]
        answer = (F(k, 2), F(k, 2))
        questions.append(item(4, 1, j,
            f"În triunghiul necoliniar ABC, M este mijlocul lui BC. În baza u=AB, v=AC, ce coeficienți (α; β) are vectorul {k}·AM=αu+βv?",
            answer,
            "Din formula mijlocului, AM=(AB+AC)/2=(u+v)/2. "
            + f"Înmulțind cu {k}, obținem coeficienții {pair(answer)}. Baza este formată din doi vectori necoliniari, deci acești coeficienți sunt unici.",
            {"mode": "median", "k": k}))

        k, t = j, j - 3
        target = (F(k, 2) + t, F(k, 2))
        # BN=(-1,1/2), CP=(1/2,-1) in the side basis (AB,AC).
        alpha = -F(4, 3) * target[0] - F(2, 3) * target[1]
        beta = -F(2, 3) * target[0] - F(4, 3) * target[1]
        questions.append(item(4, 2, j,
            f"În triunghiul necoliniar ABC, M, N și P sunt mijloacele lui BC, CA și AB. Determinați (α; β) astfel încât {k}·AM+({t})·AB=α·BN+β·CP.",
            (alpha, beta),
            "În baza u=AB, v=AC avem AM=(u+v)/2, BN=−u+v/2 și CP=u/2−v. "
            + f"Vectorul cerut are coeficienții {pair(target)}. Egalarea coeficienților dă −α+β/2={target[0]} și α/2−β={target[1]}. Determinantul sistemului este 3/4, nenul. Soluția este α={alpha}, β={beta}; înlocuirea în cele două ecuații confirmă descompunerea.",
            {"mode": "median_basis", "k": k, "t": t}))

        ab, ac = j + 2, 2*j + 5
        ratio = F(ab, ac)
        questions.append(item(4, 3, j,
            f"În triunghiul ABC, AB={ab}, AC={ac}, iar D este interior segmentului BC. Se scrie AD=α·AB+β·AC, cu α,β>0 și α+β=1. Dacă vectorii componenți α·AB și β·AC au module egale, cât este raportul BD/DC?",
            ratio,
            f"D∈BC implică BD/DC=β/α. Egalitatea modulelor este α·{ab}=β·{ac}, nu α=β. Prin urmare β/α={ab}/{ac}={ratio}. Coeficienții sunt α={F(ac, ab+ac)}, β={F(ab, ab+ac)}, ambii pozitivi. Componentele formează un romb, iar AD are direcția bisectoarei interioare. Lungimile AB și AC sunt diferite, deci D nu este mijlocul lui BC.",
            {"mode": "equal_components", "AB": ab, "AC": ac}))

        r, s = F(j, j+1), F(1, j+1)
        determinant = 1 - r*s
        answer = (1/determinant, -r/determinant)
        questions.append(item(4, 4, j,
            f"În pătratul ABCD, M∈BC și N∈DC sunt interioare laturilor și BM:MC={j}:1, DN:NC=1:{j}. Determinați (α; β) din AB=α·AM+β·AN.",
            answer,
            f"În baza u=AB, v=AD avem AM=u+({r})v și AN=({s})u+v. Relația cerută devine α+({s})β=1, ({r})α+β=0. Determinantul este 1−({r})·({s})={determinant}≠0, deci AM și AN sunt necoliniari. Rezultă α={answer[0]}, β={answer[1]}; substituția reconstituie u.",
            {"mode": "cevians", "BM_MC": [j, 1], "DN_NC": [1, j]}))

        p, q = j + 1, j + 3
        answer = (F(q, p+q), F(p, p+q))
        questions.append(item(4, 5, j,
            f"În triunghiul necoliniar ABC, punctul D este interior lui BC și BD:DC={p}:{q}. Care sunt coeficienții (α; β) în AD=α·AB+β·AC?",
            answer,
            f"D=B+({F(p,p+q)})(C−B). Scăzând A, obținem AD=({F(q,p+q)})AB+({F(p,p+q)})AC. Coeficienții {pair(answer)} sunt pozitivi și au suma 1; raportul β/α={p}/{q} reproduce BD/DC. Coeficientul extremității B este ponderea opusă, q/(p+q).",
            {"mode": "division", "BD_DC": [p, q]}))

        targets = {"AB": (1, 0), "AD": (2, 2), "AF": (0, 1), "BC": (1, 1), "CE": (-1, 1)}
        target_name = list(targets)[j-1]; target = targets[target_name]
        answer = (F(2*target[0]-target[1], 3), F(2*target[1]-target[0], 3))
        questions.append(item(4, 6, j,
            f"ABCDEF este un hexagon regulat cu vârfurile în această ordine. În baza u=AC, v=AE, determinați (α; β) din {target_name}=αu+βv.",
            answer,
            "Notăm e=AB și f=AF, vectori necoliniari. Simetria hexagonului și regula poligonului dau BC=e+f, AC=2e+f, AD=2e+2f și AE=e+2f. "
            + f"Astfel {target_name} are coeficienții {pair(target)} în baza (e,f). Egalând coeficienții în α(2e+f)+β(e+2f), obținem 2α+β={target[0]}, α+2β={target[1]}. Determinantul este 3, nenul; soluția este {pair(answer)}. Aceasta justifică și necoliniaritatea bazei (AC,AE).",
            {"mode": "hexagon", "target": target_name}))
    return sorted(questions, key=lambda q: (q["practice_scope"]["family"], q["practice_scope"]["variant"]))


def update_file(path, generated):
    """Preserve every retained JSON object byte-for-byte, including CRLF."""
    path = Path(path); raw = path.read_bytes().decode("utf-8")
    match = re.search(r'"questions"\s*:\s*\[', raw)
    if not match:
        raise ValueError("Lipsește questions")
    start = pos = match.end(); decoder = json.JSONDecoder(); retained = []
    while True:
        if raw[pos] == ",":
            pos += 1
        leading = pos
        while raw[pos].isspace():
            pos += 1
        if raw[pos] == "]":
            end = pos
            break
        value, next_pos = decoder.raw_decode(raw, pos)
        if value.get("practice_scope", {}).get("bank") != BANK:
            retained.append(raw[leading:next_pos])
        pos = next_pos
    newline = "\r\n" if "\r\n" in raw else "\n"
    additions = [newline + newline.join("    " + line for line in json.dumps(q, ensure_ascii=False, indent=2).splitlines()) for q in generated]
    updated = raw[:start] + ",".join(retained + additions) + newline + "  " + raw[end:]
    assert len(json.loads(updated)["questions"]) == len(retained) + len(generated)
    path.write_bytes(updated.encode("utf-8"))


def update_files():
    for lesson, builder in [(1, build_lesson1), (4, build_lesson4)]:
        generated = builder()
        assert len(generated) == 30
        assert len({q["text"] for q in generated}) == 30
        update_file(FILES[lesson], generated)
        print(f"Lesson {lesson}: 30 grids; existing questions preserved.")


if __name__ == "__main__":
    update_files()
