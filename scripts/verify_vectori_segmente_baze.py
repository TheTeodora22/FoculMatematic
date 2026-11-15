"""Audit exact și independent pentru cele 60 grile G1 §1/§3.

Nu importă generatorul și nu scrie în bază. Reface calculele din datele
problemei, inclusiv enumerări finite și sisteme în baze geometrice.
"""
import json
from collections import Counter
from itertools import combinations, permutations
from pathlib import Path

import sympy as S

ROOT = Path(__file__).resolve().parents[1]
BANK = "vectori_segmente_baze_v1"
PATHS = [ROOT / "data/quizzes/clasa_9" / name for name in (
    "clasa_9_u05_l01_segmente_orientate_relatia_de_echipolenta.json",
    "clasa_9_u05_l04_descompunerea_unui_vector_dupa_doi_vectori_necoliniari.json")]


def vector(value):
    return S.Matrix([x if isinstance(x, S.Basic) else S.Rational(x) for x in value])


def pair_option(text):
    assert text.startswith("(") and text.endswith(")")
    return vector(text[1:-1].split(";"))


def expected(data):
    mode = data["mode"]
    if mode == "directions":
        directions = set()
        for p, q in combinations(map(vector, data["points"]), 2):
            v = q - p
            assert v != S.zeros(2, 1)
            direction = (S.Integer(0), S.Integer(1)) if v[0] == 0 else (S.Integer(1), v[1]/v[0])
            directions.add(direction)
        return S.Integer(len(directions))
    if mode == "rays":
        u = vector(data["B"]) - vector(data["A"])
        v = vector(data["D"]) - vector(data["C"])
        assert S.Matrix.hstack(u, v).det() == 0 and u.dot(u) != 0 and v.dot(v) != 0
        return "Aceeași direcție și același sens" if u.dot(v) > 0 else "Aceeași direcție și sensuri opuse"
    if mode == "equipollent":
        target = vector(data["B"]) - vector(data["A"])
        matches = [name for name, (p, q) in data["segments"].items() if vector(q) - vector(p) == target]
        assert len(matches) == 1
        return matches[0]
    if mode == "representatives":
        points = [vector(p) for p in data["points"]]
        target = vector(data["vector"])
        return S.Integer(sum(q - p == target for p, q in permutations(points, 2)))
    if mode == "opposite":
        target = -vector(data["u"])
        matches = [name for name, v in data["candidates"].items() if vector(v) == target]
        assert len(matches) == 1
        return matches[0]
    if mode == "quadrilateral":
        a, b, d = [vector(data[key]) for key in ("A", "B", "D")]
        c = b + d - a
        assert b - a == c - d and d - a == c - b
        u, v = b - a, d - a
        assert S.Matrix.hstack(u, v).det() != 0
        perpendicular = (b - d).dot(b - d) == u.dot(u) + v.dot(v)
        equal = u.dot(u) == v.dot(v)
        if perpendicular and equal:
            return "Pătrat"
        if perpendicular:
            return "Dreptunghi care nu este pătrat"
        if equal:
            return "Romb care nu este pătrat"
        return "Paralelogram care nu este nici dreptunghi, nici romb"
    # Use an arbitrary noncollinear triangle, then solve in actual coordinates.
    a = vector([2, -1]); b = vector([7, 1]); c = vector([-1, 6])
    sides = S.Matrix.hstack(b-a, c-a)
    assert sides.det() != 0
    if mode == "median":
        m = (b+c)/2
        return sides.inv() * (S.Rational(data["k"]) * (m-a))
    if mode == "median_basis":
        m, n, p = (b+c)/2, (c+a)/2, (a+b)/2
        basis = S.Matrix.hstack(n-b, p-c)
        assert basis.det() != 0
        target = S.Rational(data["k"]) * (m-a) + S.Rational(data["t"]) * (b-a)
        return basis.inv() * target
    if mode == "equal_components":
        length_b, length_c = map(S.Rational, [data["AB"], data["AC"]])
        alpha, beta = S.symbols("alpha beta")
        solution = S.solve([alpha+beta-1, alpha*length_b-beta*length_c], (alpha, beta))
        assert solution[alpha] > 0 and solution[beta] > 0 and length_b != length_c
        ratio = solution[beta] / solution[alpha]
        assert ratio != 1  # Deliberately guard against the incorrect equal-coefficients shortcut.
        return ratio
    if mode == "cevians":
        a, b, c, d = map(vector, [[0, 0], [7, 0], [7, 7], [0, 7]])
        p, q = map(S.Rational, data["BM_MC"])
        m = (q*b+p*c)/(p+q)
        p, q = map(S.Rational, data["DN_NC"])
        n = (q*d+p*c)/(p+q)
        basis = S.Matrix.hstack(m-a, n-a)
        assert basis.det() != 0
        result = basis.inv()*(b-a)
        assert basis*result == b-a
        return result
    if mode == "division":
        p, q = map(S.Rational, data["BD_DC"])
        d = (q*b+p*c)/(p+q)
        result = sides.inv()*(d-a)
        assert sum(result) == 1 and all(x > 0 for x in result)
        assert (d-b).dot(d-b)/(c-d).dot(c-d) == (p/q)**2
        return result
    if mode == "hexagon":
        h = S.sqrt(3)/2
        vertices = {name: vector(coords) for name, coords in zip("ABCDEF", [
            [1, 0], [S.Rational(1, 2), h], [-S.Rational(1, 2), h],
            [-1, 0], [-S.Rational(1, 2), -h], [S.Rational(1, 2), -h]])}
        basis = S.Matrix.hstack(vertices["C"]-vertices["A"], vertices["E"]-vertices["A"])
        first, second = data["target"]
        target = vertices[second] - vertices[first]
        result = S.simplify(basis.inv()*target)
        assert S.simplify(basis*result-target) == S.zeros(2, 1)
        return result
    raise AssertionError(mode)


def main():
    total = 0
    for path in PATHS:
        questions = json.loads(path.read_text(encoding="utf-8"))["questions"]
        bank = [q for q in questions if q.get("practice_scope", {}).get("bank") == BANK]
        assert len(bank) == 30, path
        assert Counter(q["practice_scope"]["family"] for q in bank) == Counter({i: 5 for i in range(1, 7)})
        assert len({q["text"] for q in bank}) == 30
        assert all(q["type"] == "vector_workbench" for q in questions[:3]), "Interactivele inițiale trebuie păstrate."
        for q in bank:
            options = q["options"]
            assert len(options) == 4 and len({o["text"] for o in options}) == 4
            assert sum(o["is_correct"] is True for o in options) == 1
            assert q["type"] == "multiple_choice" and q["format"] == "grid"
            assert len(q["explanation"]) > 120
            data = q["verification"]
            wanted = expected(data)
            if data["answer_kind"] == "pair":
                values = [pair_option(o["text"]) for o in options]
            elif data["answer_kind"] == "number":
                values = [S.Rational(o["text"]) for o in options]
            else:
                values = [o["text"] for o in options]
            matches = [value == wanted for value in values]
            assert sum(matches) == 1 and matches == [o["is_correct"] for o in options], q["text"]
            total += 1
        print(f"OK: {path.name}: 30 grids, 6x5 families, independent exact calculations.")
    print(f"OK: {total} grids: finite enumeration, medians, oblique bases, ratios and regular hexagon.")


if __name__ == "__main__":
    main()
