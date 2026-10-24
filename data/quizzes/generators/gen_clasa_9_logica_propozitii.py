"""95 de grile originale după A1 §2 din catalogul Burtea IX (p. 34–40).

Rulează independent; modifică numai lecția despre propoziții și predicate.
Nu transcrie enunțurile scanate. Metadatele catalogului rămân în JSON.
"""
import json
from collections import Counter
from pathlib import Path


TYPE_NAMES = {
    1: "Recunoașterea propozițiilor",
    2: "Adevărul unor afirmații numerice",
    3: "Adevărul unor afirmații geometrice",
    4: "Propoziții despre zecimale periodice",
    5: "Mulțimea de adevăr a unei ecuații",
    6: "Universul unui predicat rațional",
    7: "Predicate cu modul",
    8: "Predicate cu parte întreagă",
    9: "Predicate aritmetice de integritate",
    10: "Predicate binare diofantice",
    11: "Predicate binare prin pătrate",
    12: "Predicate cu iraționali independenți",
    13: "Particularizarea unui predicat",
    14: "Cuantificatorul universal",
    15: "Cuantificatorul existențial",
    16: "Ordinea cuantificatorilor",
    17: "Cuantificare pe intervale",
    18: "Propoziții aritmetice universale",
    19: "Predicate cu trei variabile geometrice",
}


def finite_set(values):
    values = sorted(set(values))
    return "{" + "; ".join(map(str, values)) + "}" if values else "∅"


def build_questions():
    questions = []

    def add(kind, text, correct, wrong, explanation, difficulty="medium"):
        values = [str(correct), *map(str, wrong)]
        assert len(values) == len(set(values)) == 4, (kind, text, values)
        position = len(questions) % 4
        values.insert(position, values.pop(0))
        questions.append({
            "text": text, "type": "multiple_choice", "format": "grid", "points": 10,
            "explanation": explanation,
            "options": [{"text": value, "is_correct": i == position}
                        for i, value in enumerate(values)],
            "catalog": {"section": "A1.2", "type": kind, "type_name": TYPE_NAMES[kind],
                        "difficulty": difficulty,
                        "origin": "Exercițiu nou după tipologia catalogului Burtea IX, §2"},
        })

    # 1. Inclusiv propoziții false: adevărul nu este criteriul de recunoaștere.
    for statement, value in [("7 este număr prim.",True), ("9 este număr par.",False),
                             ("√2 este număr irațional.",True), ("3 + 4 = 8.",False),
                             ("Orice pătrat este dreptunghi.",True)]:
        correct = "Propoziție adevărată." if value else "Propoziție falsă."
        labels = ["Propoziție adevărată.","Propoziție falsă.","Predicat cu o variabilă liberă.","Ordin de efectuare a unui calcul."]
        add(1, f"Cum se clasifică enunțul «{statement}»?", correct,
            [label for label in labels if label!=correct],
            "Enunțul este declarativ și are o valoare de adevăr determinată, deci este o propoziție. "
            f"În acest caz este {'adevărat' if value else 'fals'}. O propoziție falsă rămâne propoziție; "
            "nu are variabile libere și nu este un ordin.", "easy")

    # 2. Un produs constant caracterizează proporționalitatea inversă.
    for a, b in [(2, 12), (3, 15), (4, 10), (5, 18), (6, 14)]:
        add(2, f"Mărimile pozitive x și y sunt invers proporționale. Pentru x = {a}, y = {b}. "
            f"Care afirmație este adevărată pentru x = {2*a}?", f"y = {b//2}" if b % 2 == 0 else f"y = {b}/2",
            [f"y = {2*b}", f"y = {b}", "y = 0"],
            f"Produsul xy este constant, egal cu {a*b}. Dublarea lui x înjumătățește valoarea lui y.")

    # 3. Afirmații universale geometrice, cu contraexemple explicite.
    geometry = [
        ("Care afirmație despre dreptunghiuri este adevărată?", "Diagonalele oricărui dreptunghi sunt egale.",
         ["Diagonalele oricărui dreptunghi sunt perpendiculare.", "Orice dreptunghi are toate laturile egale.", "Orice dreptunghi are un unghi de 60°."],
         "Diagonalele unui dreptunghi sunt egale. Un dreptunghi cu laturi 2 și 3 infirmă primele două proprietăți suplimentare; unghiurile sale sunt de 90°."),
        ("Care afirmație despre romburi este adevărată?", "Diagonalele oricărui romb sunt perpendiculare.",
         ["Diagonalele oricărui romb sunt egale.", "Orice romb este pătrat.", "Orice romb are un unghi drept."],
         "Diagonalele rombului sunt perpendiculare. Un romb cu un unghi de 60° infirmă celelalte trei afirmații."),
        ("Care afirmație despre triunghiurile euclidiene este adevărată?", "Suma unghiurilor interioare este 180°.",
         ["Orice triunghi are un unghi drept.", "Orice triunghi isoscel este echilateral.", "Un triunghi poate avea două unghiuri obtuze."],
         "Suma unghiurilor este 180°. Triunghiurile echilaterale nu au unghi drept; un triunghi cu unghiuri 40°, 70°, 70° este isoscel și nu este echilateral."),
        ("Care afirmație despre paralelograme este adevărată?", "Diagonalele se înjumătățesc reciproc.",
         ["Diagonalele sunt întotdeauna egale.", "Diagonalele sunt întotdeauna perpendiculare.", "Toate unghiurile sunt întotdeauna drepte."],
         "În orice paralelogram, diagonalele au același mijloc. Egalitatea diagonalelor sau perpendicularitatea lor impun condiții suplimentare."),
        ("Care afirmație despre pătrate este adevărată?", "Diagonalele sunt egale și perpendiculare.",
         ["Diagonala are aceeași lungime ca latura.", "Suma unghiurilor interioare este 180°.", "Diagonalele nu se înjumătățesc reciproc."],
         "Pătratul are diagonale egale, perpendiculare și cu același mijloc. Diagonala este latura înmulțită cu √2, iar suma unghiurilor este 360°."),
    ]
    for text, correct, wrong, explanation in geometry:
        add(3, text, correct, wrong, explanation)

    # 4. Rangurile încep cu prima cifră de după virgulă.
    for period, rank in [("142857", 500), ("27", 101), ("123", 2026), ("081", 100), ("36", 2024)]:
        digit = period[(rank - 1) % len(period)]
        wrong = [str(d) for d in range(10) if str(d) != digit][:3]
        add(4, f"În scrierea zecimală 0,({period}), care este a {rank}-a cifră după virgulă? "
            "Cifrele din paranteze formează perioada.", digit, wrong,
            f"Perioada are {len(period)} cifre. Poziția în perioadă este (({rank} − 1) mod {len(period)}) + 1 "
            f"= {(rank-1)%len(period)+1}; cifra este {digit}.")

    for a, b, domain in [(2, 3, "ℝ"), (-3, 4, "ℤ"), (0, 5, "ℚ"), (-2, 6, "ℕ"), (-4, -1, "ℕ")]:
        roots = [x for x in (a, b) if domain != "ℕ" or x >= 0]
        correct = finite_set(roots)
        candidates = [finite_set([a, b]), finite_set([a]), finite_set([b]), "ℝ", "∅", finite_set([-a, -b])]
        wrong = list(dict.fromkeys(v for v in candidates if v != correct))[:3]
        add(5, f"Determinați mulțimea de adevăr a predicatului (x − ({a}))(x − ({b})) = 0, "
            f"cu x ∈ {domain}. Folosim ℕ = {{0, 1, 2, …}}.", correct, wrong,
            f"Produsul este zero dacă x = {a} sau x = {b}. Păstrăm numai rădăcinile din {domain}: {correct}.", "easy")

    for a, b in [(2, 5), (-1, 3), (4, -2), (0, 7), (-3, -1)]:
        domain = f"ℝ ∖ {{{a}}}"
        add(6, f"Pentru predicatul (x² − ({a+b})x + ({a*b}))/(x − ({a})) = 0, "
            "care sunt domeniul real maxim D și mulțimea de adevăr A?",
            f"D = {domain}; A = {{{b}}}",
            [f"D = ℝ; A = {finite_set([a,b])}", f"D = {domain}; A = {finite_set([a,b])}", f"D = {domain}; A = ∅"],
            f"Numitorul impune x ≠ {a}. Numărătorul este (x − ({a}))(x − ({b})); "
            f"după excluderea valorii {a}, rămâne x = {b}.")

    for a, r in [(2, 3), (-1, 4), (5, 2), (0, 6), (-4, 1)]:
        add(7, f"Care este mulțimea de adevăr în ℝ a predicatului |x − ({a})| ≤ {r}?",
            f"[{a-r}; {a+r}]", [f"({a-r}; {a+r})", finite_set([a-r,a+r]), f"[{a}; {a+r}]"],
            f"Inegalitatea este echivalentă cu −{r} ≤ x − ({a}) ≤ {r}, deci {a-r} ≤ x ≤ {a+r}.")

    for k, m in [(2, 3), (3, -2), (4, 1), (5, 0), (2, -3)]:
        from fractions import Fraction
        left, right = str(Fraction(m, k)), str(Fraction(m+1, k))
        add(8, f"Determinați mulțimea de adevăr în ℝ a predicatului ⌊{k}x⌋ = {m}. "
            "⌊t⌋ este cel mai mare întreg mai mic sau egal cu t.", f"[{left}; {right})",
            [f"({left}; {right}]", f"[{left}; {right}]", f"({left}; {right})"],
            f"Definiția părții întregi dă {m} ≤ {k}x < {m+1}. Împărțim prin {k} > 0; "
            f"capătul {left} este inclus, iar {right} este exclus.", "hard")

    for d, c in [(3, 1), (4, 1), (5, 2), (6, 1), (7, 3)]:
        residue = (-c) % d
        add(9, f"Pentru care n ∈ ℕ este (n + {c})/{d} număr întreg? Folosim ℕ = {{0, 1, 2, …}}.",
            f"n = {d}k + {residue}, k ∈ ℕ",
            [f"n = {d}k + {(residue+1)%d}, k ∈ ℕ", f"n = {d}k, k ∈ ℕ", "Pentru orice n ∈ ℕ"],
            f"Este necesar și suficient ca {d} să dividă n + {c}, adică n ≡ {residue} (mod {d}). "
            f"Cum 0 ≤ {residue} < {d}, toate soluțiile naturale sunt n = {d}k + {residue}.", "hard")

    for a, b, n in [(1, 2, 6), (3, -1, 8), (-2, 4, 10), (0, 3, 12), (2, 5, 9)]:
        count = 2 * sum(n % d == 0 for d in range(1, n+1))
        add(10, f"Câte perechi ordonate (x, y) ∈ ℤ² verifică (x − ({a}))(y − ({b})) = {n}?",
            count, [count//2, count+2, count-2],
            f"Punem u = x − ({a}), v = y − ({b}). Fiecare divizor întreg nenul u al lui {n} "
            f"determină exact un v = {n}/u. Numărul divizorilor cu ambele semne este {count}; "
            "schimbarea variabilelor este bijectivă.", "hard")

    for a, b in [(2, 3), (-1, 4), (0, -2), (5, 1), (-3, -4)]:
        add(11, f"Care este mulțimea perechilor reale (x, y) pentru care "
            f"(x − ({a}))² + (y − ({b}))² ≤ 0?", f"{{({a}; {b})}}",
            [f"{{({a+1}; {b})}}", "ℝ²", "∅"],
            "Ambele pătrate sunt nenegative. Suma lor poate fi ≤ 0 numai dacă ambele sunt zero, "
            f"deci x = {a} și y = {b}.")

    for a, b in [(1, 3), (-2, 4), (3, -1), (0, 5), (-4, -2)]:
        add(12, f"Determinați (x, y) ∈ ℚ² dacă (x − ({a}))√2 + y − ({b}) = 0.",
            f"({a}; {b})", [f"({a+1}; {b})", f"({a}; {b+1})", "Nu există soluții raționale."],
            f"Dacă x ≠ {a}, egalitatea ar exprima √2 ca raport de numere raționale, imposibil. "
            f"Așadar x = {a}, apoi y = {b}.", "hard")

    for a in [1, 2, 3, 4, 5]:
        add(13, f"Fie p(x): x² ≤ {a*a}, cu x ∈ ℝ. Care sunt, în ordine, valorile de adevăr "
            f"ale lui p({a}), p({-a}), p({a+1})?", "Adevărat, adevărat, fals",
            ["Adevărat, fals, fals", "Fals, adevărat, adevărat", "Adevărat, adevărat, adevărat"],
            f"Primele două pătrate sunt {a*a}, deci satisfac inegalitatea. Ultimul este {(a+1)**2} > {a*a}.", "easy")

    for a in [1, 2, 3, 4, 5]:
        add(14, f"Care propoziție universală este adevărată? În acest set, a = {a}.",
            "Pentru orice x ∈ ℝ, (x − a)² ≥ 0.",
            ["Pentru orice x ∈ ℝ, (x − a)² > 0.", "Pentru orice x ∈ ℝ, x > a.", "Pentru orice x ∈ ℝ, x² = a²."],
            "Pătratul unui număr real este nenegativ. Prima afirmație falsă are contraexemplul x = a; "
            "a doua, x = a − 1; a treia, x = 0, deoarece a > 0.")

    for a in [2, 3, 4, 5, 6]:
        add(15, f"Care valoare este un martor pentru propoziția ∃x ∈ ℤ: x² = {a*a}?", a,
            [a-1, a+1, 0],
            f"Un martor este o valoare din univers care verifică predicatul. Pentru x = {a}, x² = {a*a}; "
            f"celelalte valori propuse au pătrate diferite. Și −{a} este martor, dar nu apare între variante.")

    truth_choices = ["P adevărată; Q falsă", "P falsă; Q adevărată", "P și Q adevărate", "P și Q false"]
    for a in [1, 2, 3, 4, 5]:
        add(16, f"În ℝ, fie P: ∀x ∃y, y = x + {a}, și Q: ∃y ∀x, y = x + {a}. "
            "Care este evaluarea corectă?", truth_choices[0], truth_choices[1:],
            f"P este adevărată: pentru fiecare x alegem y = x + {a}. Q este falsă: "
            f"x = 0 ar impune y = {a}, iar x = 1 ar impune y = {a+1}. "
            "Nu există un singur y care să funcționeze pentru toate valorile lui x.", "hard")

    for l, r, s, t in [(-2, 5, -3, 4), (0, 2, 1, 3), (-4, -1, 2, 6), (1, 4, -5, -2), (-3, 3, -2, 2)]:
        add(17, f"Pentru a ∈ ({l}; {r}) și b ∈ ({s}; {t}), care este cea mai mică valoare "
            "reală M pentru care propoziția ∀a ∀b, a + b < M este adevărată?",
            r+t, [l+s, r+t-1, r+t+1],
            f"Avem a < {r} și b < {t}, deci a + b < {r+t}. Suma se poate apropia "
            f"oricât de mult de {r+t} din stânga, astfel încât nicio valoare mai mică a lui M nu este suficientă.", "hard")

    arithmetic = [
        ("Care propoziție despre produsele de întregi consecutivi este adevărată pentru orice n ∈ ℤ?", "n(n + 1) este divizibil cu 2.",
         ["n² + 1 este divizibil cu 2.", "n(n + 1) este divizibil cu 3.", "n² este impar."],
         "Dintre doi întregi consecutivi unul este par. Contraexemple pentru celelalte afirmații: n = 0, n = 1, respectiv n = 0."),
        ("Care propoziție despre produsul a trei întregi consecutivi este adevărată pentru orice n ∈ ℤ?", "n(n + 1)(n + 2) este divizibil cu 6.",
         ["n(n + 1)(n + 2) este divizibil cu 12.", "n² + 2 este divizibil cu 3.", "n + 1 este par."],
         "Trei întregi consecutivi conțin un multiplu de 3 și un număr par. Celelalte afirmații sunt infirmate de n = 1, n = 0, respectiv n = 0."),
        ("Care proprietate aritmetică a expresiei n² − n este valabilă pentru orice n ∈ ℤ?", "n² − n este par.",
         ["n² − n este impar.", "n² + n + 1 este par.", "n² − n este divizibil cu 4."],
         "n² − n = n(n − 1) este produsul a doi întregi consecutivi. Contraexemple: n = 0 pentru primele două afirmații false și n = 2 pentru ultima."),
        ("Care proprietate a pătratelor numerelor impare este valabilă pentru orice n ∈ ℤ?", "(2n + 1)² − 1 este divizibil cu 8.",
         ["(2n + 1)² este par.", "(2n + 1)² − 1 este divizibil cu 16.", "2n + 1 este număr prim."],
         "(2n + 1)² − 1 = 4n(n + 1), iar n(n + 1) este par. Contraexemple: n = 0, n = 1, respectiv n = 4."),
        ("Care afirmație despre pătrate perfecte este adevărată pentru orice n ∈ ℕ, cu ℕ = {0, 1, 2, …}?", "n² + 2n + 1 este pătrat perfect.",
         ["n² + 1 este pătrat perfect.", "n² + 2n este pătrat perfect.", "2n + 1 este pătrat perfect."],
         "n² + 2n + 1 = (n + 1)². Pentru n = 1, celelalte expresii sunt 2, 3, respectiv 3, care nu sunt pătrate perfecte."),
    ]
    for text, correct, wrong, explanation in arithmetic:
        add(18, text, correct, wrong, explanation, "hard")

    for ratios in [(1, 2, 3), (2, 3, 4), (2, 5, 5), (1, 3, 5), (3, 4, 5)]:
        scale = 180 // sum(ratios)
        assert scale * sum(ratios) == 180
        angles = tuple(scale*r for r in ratios)
        triple = lambda xs: "(" + "; ".join(f"{x}°" for x in xs) + ")"
        wrong = [triple([angles[0]+10, angles[1]-10, angles[2]]),
                 triple([angles[0], angles[1]+10, angles[2]]), triple(ratios)]
        add(19, f"Unghiurile α, β, γ ale unui triunghi sunt direct proporționale, în această ordine, "
            f"cu {ratios[0]}, {ratios[1]}, {ratios[2]}. Care este tripletul (α; β; γ)?", triple(angles), wrong,
            f"Scriem unghiurile {ratios[0]}k, {ratios[1]}k, {ratios[2]}k. "
            f"Suma lor este 180°, deci k = 180/{sum(ratios)} = {scale}°. Rezultă {triple(angles)}.")

    assert Counter(q["catalog"]["type"] for q in questions) == {i: 5 for i in TYPE_NAMES}
    assert len({q["text"] for q in questions}) == len(questions) == 95
    return questions


def main():
    path = Path(__file__).resolve().parents[1] / "clasa_9" / "clasa_9_u01_l03_propozitii_predicate_si_cuantificatori.json"
    payload = {"title": "Propoziții, predicate și cuantificatori",
               "description": "Clasa a 9-a · Mulțimi și logică matematică",
               "difficulty": "medium", "questions": build_questions()}
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Scrise {len(payload['questions'])} grile: {path.name}")


if __name__ == "__main__":
    main()
