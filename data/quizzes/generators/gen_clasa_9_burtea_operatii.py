"""Grile originale după tipurile 3–27 din catalogul Burtea IX, A1 §1.1.

Nu transcrie enunțuri din scanare. Folosește numai biblioteca standard.
Metadatele catalog rămân în JSON pentru auditul acoperirii tipologiilor.
"""
from collections import Counter
from fractions import Fraction as F


TYPE_NAMES = {
    3: "Verificarea inverselor", 4: "Opuse și inverse ale unor expresii",
    5: "Calcul prin relații liniare cunoscute", 6: "Determinare prin sumă de pătrate nulă",
    7: "Recuperare din sumă și sumă de pătrate", 8: "Puteri simetrice din sumă și produs",
    9: "Raport pătrat sau cub", 10: "Verificarea identităților polinomiale",
    11: "Puteri cu exponent întreg", 12: "Simplificare prin produs remarcabil",
    13: "Valori determinate de paritate", 14: "Potențe mari sub o condiție rigidă",
    15: "Operații cu radicali simpli", 16: "Medii ale numerelor cu radicali",
    17: "Raționalitate ascunsă", 18: "Radicali de pătrate și semn cunoscut",
    19: "Descompunerea radicalilor dubli", 20: "Calcul procentual cu radicali",
    21: "Raționalizarea numitorului", 22: "Fracții cu radicali imbricați",
    23: "Sume telescopice de radicali", 24: "Ecuații construite din sume",
    25: "Valori întregi ale expresiilor raționale", 26: "Pătrat perfect prin substituție",
    27: "Egalitate forțată între trei numere",
}


def number(value):
    value = F(value)
    return str(value.numerator) if value.denominator == 1 else str(value)


def number_set(values):
    return "{" + "; ".join(number(v) for v in sorted(set(values))) + "}"


def build_catalog_extension():
    questions = []

    def add(kind, text, correct, wrong, explanation):
        assert len(wrong) == 3
        values = [correct, *wrong]
        assert len(set(values)) == 4, (kind, text, values)
        # Poziția corectă variază; rezultatul nu este mereu aceeași literă.
        position = len(questions) % 4
        values.insert(position, values.pop(0))
        questions.append({
            "text": text, "type": "multiple_choice", "format": "grid", "points": 10,
            "explanation": explanation,
            "options": [{"text": v, "is_correct": i == position} for i, v in enumerate(values)],
            "catalog": {"section": "A1.1.1", "type": kind, "type_name": TYPE_NAMES[kind],
                        "origin": "Exercițiu nou după tipologia catalogului Burtea IX"},
        })

    def numeric(kind, text, answer, explanation, wrong=None):
        answer = F(answer)
        if wrong is None:
            candidates = [-answer, answer + 1, answer - 1, 2 * answer, F(0), F(2)]
            wrong = []
            for v in candidates:
                if v != answer and v not in wrong:
                    wrong.append(v)
                if len(wrong) == 3:
                    break
        assert len(set(map(F, wrong)) | {answer}) == 4
        add(kind, text, number(answer), [number(v) for v in wrong], explanation)

    # Cinci soluții ale ecuației a² − d b² = 1; conjugatele sunt pozitive.
    pell = [(3, 2, 2), (2, 1, 3), (5, 2, 6), (7, 4, 3), (9, 4, 5)]
    for a, b, d in pell:
        assert a*a - b*b*d == 1
        plus, minus = f"{a}+{b}√{d}", f"{a}−{b}√{d}"
        add(3, f"Care este inversul numărului {plus}?", minus,
            [f"−{a}−{b}√{d}", plus, f"−{a}+{b}√{d}"],
            f"Produsul conjugatelor este {a}²−{b}²·{d}=1, deci inversul este {minus}.")

    for a, b, d in pell:
        numeric(4, f"Fie A={a}+{b}√{d} și B={a}−{b}√{d}. Calculați 1/A + 1/B.", 2*a,
                f"A+B={2*a}, AB=1, deci 1/A+1/B=(A+B)/(AB)={2*a}.", [2*a-1, 2*a+1, -2*a])

    for p, q, k, c in [(3, 8, 2, 5), (2, 5, 3, -1), (4, 3, 2, 2), (5, 7, 1, 3), (3, 5, 4, -2)]:
        numeric(5, f"Numerele reale a,b verifică a/{p}+b/{q}={c}. Calculați {k*q}a+{k*p}b.", k*p*q*c,
                f"Înmulțim relația dată cu {k*p*q}: expresia cerută este {k*p*q}·({c})={k*p*q*c}.")

    for m, n in [(1, 2), (2, 3), (-1, 2), (3, -2), (-2, -3)]:
        numeric(6, f"Pentru a,b reale, (a−({m}))²+(b−({n}))²=0. Calculați a³+b³.", m**3+n**3,
                f"Ambele pătrate sunt nenegative, deci fiecare este zero: a={m}, b={n}. Rezultă a³+b³={m**3+n**3}.")

    for u, v in [(2, 5), (3, 7), (-2, 6), (-3, -5), (1, 8)]:
        total, squares = u+v, u*u+v*v
        numeric(7, f"u,v sunt reale, u+v={total} și u²+v²={squares}. Determinați uv.", u*v,
                f"2uv=(u+v)²−(u²+v²)=({total})²−{squares}={2*u*v}, deci uv={u*v}.")

    for u, v, n in [(1, 2, 3), (2, 3, 4), (1, 3, 5), (1, 2, 6), (1, 2, 7)]:
        s, p = u+v, u*v
        powers = [2, s]
        for j in range(2, n+1):
            powers.append(s*powers[-1]-p*powers[-2])
        assert powers[n] == u**n+v**n
        numeric(8, f"a,b sunt reale, a+b={s} și ab={p}. Calculați a^{n}+b^{n}.", powers[n],
                f"Notăm S₀=2, S₁={s}. Relația Sₖ={s}Sₖ₋₁−{p}Sₖ₋₂ dă succesiv "
                + ", ".join(f"S{j}={powers[j]}" for j in range(2, n+1)) + ".")

    for i, (a, b, d) in enumerate(pell):
        power = 2 if i < 3 else 3
        z = f"({a}+{b}√{d})"
        numerator = z if power == 2 else z+"²"
        add(9, f"Scrieți {numerator}/({a}−{b}√{d}) ca o singură putere.", f"{z}^{power}",
            [f"{z}^{n}" for n in (1, 2, 3, 4) if n != power],
            f"Conjugatele au produsul 1. Împărțirea la {a}−{b}√{d} înseamnă înmulțire cu {z}, deci obținem {z}^{power}.")

    identities = [
        ("(a+b)³−a³−b³", "3ab(a+b)", ["3ab(a−b)", "ab(a+b)", "3a²b²"], "Dezvoltarea cubului sumei lasă 3a²b+3ab²=3ab(a+b)."),
        ("(a−b)(a²+ab+b²)", "a³−b³", ["a³+b³", "a³−3ab−b³", "a²−b²"], "La înmulțire se reduc termenii a²b și ab²: rămâne a³−b³."),
        ("(a+b)(a²−ab+b²)", "a³+b³", ["a³−b³", "a²+b²", "a³+b³+2ab"], "Aplicăm formula sumei cuburilor: a³+b³=(a+b)(a²−ab+b²)."),
        ("(a+b+c)²−a²−b²−c²", "2(ab+bc+ca)", ["ab+bc+ca", "2abc", "2(ab−bc+ca)"], "Pătratul sumei conține de două ori fiecare produs a două variabile distincte."),
        ("a³+b³+c³−3abc", "(a+b+c)(a²+b²+c²−ab−bc−ca)", ["(a+b+c)(a²+b²+c²)", "(a+b+c)³", "(a−b)(b−c)(c−a)"], "Dezvoltăm produsul: termenii a²b, ab² etc. se reduc și rămân cuburile și −3abc."),
    ]
    for expr, correct, wrong, proof in identities:
        add(10, f"Care expresie este identică cu {expr}, pentru orice a,b,c reale?", correct, wrong, proof)

    powers = [
        ("Calculați 2⁻³ + 2⁻².", F(3,8), "2⁻³=1/8 și 2⁻²=1/4, deci suma este 3/8."),
        ("Calculați (−3)⁻² · 9.", 1, "(−3)⁻²=1/9, iar (1/9)·9=1."),
        ("Calculați (2/3)⁻².", F(9,4), "Exponentul negativ inversează fracția: (3/2)²=9/4."),
    ]
    for text, value, proof in powers:
        numeric(11, text, value, proof)
    add(11, "Simplificați a⁻²b/(a⁻¹b²), pentru a,b reale nenule.", "1/(ab)",
        ["a/b", "b/a", "ab"], "Scădem exponenții: a^(−2+1)b^(1−2)=a⁻¹b⁻¹=1/(ab).")
    add(11, "Simplificați (a⁻³)² · a⁵, pentru a real nenul.", "1/a",
        ["a", "a¹¹", "1/a¹¹"], "(a⁻³)²=a⁻⁶, deci produsul este a^(−6+5)=a⁻¹=1/a.")

    for t in [F(2), F(3), F(-2), F(1,2), F(-1,2)]:
        numeric(12, f"Pentru t={number(t)}, calculați (1−t)(1+t)(1+t²)(1+t⁴).", 1-t**8,
                f"Aplicăm repetat diferența de pătrate: produsul este (1−t²)(1+t²)(1+t⁴)=1−t⁸={number(1-t**8)}.")

    for c, d in [(1,2), (1,3), (2,3), (2,5), (3,4)]:
        values = [-c-d, -c+d, c-d, c+d]
        add(13, f"m,n sunt numere naturale. Care este mulțimea tuturor valorilor lui {c}(−1)ᵐ+{d}(−1)ⁿ?",
            number_set(values), [number_set([-c-d,c+d]), number_set([abs(c-d),c+d]), number_set([v+1 for v in values])],
            f"Fiecare putere a lui −1 este 1 sau −1, independent de cealaltă. Cele patru combinații dau {number_set(values)}.")

    for a, b, n in [(2,1,2026), (1,2,2025), (3,3,2026), (-1,0,2026), (0,1,2027)]:
        numeric(14, f"a,b sunt reale și (a−({a}))²+(b−({b}))²=0. Calculați (a−b)^{n}.", (a-b)**n,
                f"Suma pătratelor este zero numai când a={a}, b={b}. Atunci a−b={a-b}, deci puterea cerută este {(a-b)**n}.")

    radicals = [
        ("√50+√8", "7√2", ["√58", "9√2", "3√2"], "√50=5√2 și √8=2√2, deci suma este 7√2."),
        ("√75−√12", "3√3", ["√63", "7√3", "√3"], "√75=5√3 și √12=2√3, deci diferența este 3√3."),
        ("(√5−1)²", "6−2√5", ["4", "6+2√5", "5−2√5"], "Folosim (u−v)²=u²−2uv+v²: 5−2√5+1=6−2√5."),
        ("√18 · √8", "12", ["√26", "6", "24"], "Radicandele sunt nenegative: √18·√8=√144=12."),
        ("(√7+√3)(√7−√3)", "4", ["10", "2√21", "−4"], "Diferența de pătrate este (√7)²−(√3)²=7−3=4."),
    ]
    for expr, correct, wrong, proof in radicals:
        add(15, f"Calculați {expr}.", correct, wrong, proof)

    for a,b,d,mode in [(3,1,5,"aritmetică"), (3,1,5,"geometrică"), (3,1,5,"armonică"), (5,2,6,"geometrică"), (7,4,3,"armonică")]:
        product = a*a-b*b*d
        answer = F(a) if mode == "aritmetică" else F(1 if product == 1 else 2) if mode == "geometrică" else F(product,a)
        numeric(16, f"Calculați media {mode} a numerelor pozitive {a}−{b}√{d} și {a}+{b}√{d}.", answer,
                f"Suma numerelor este {2*a}, iar produsul este {product}. " +
                ({"aritmetică": f"Media aritmetică este {2*a}/2={a}.",
                  "geometrică": f"Media geometrică este √{product}={number(answer)}.",
                  "armonică": f"Media armonică este 2·{product}/{2*a}={number(answer)}."}[mode]))

    for i,(a,b,d) in enumerate(pell):
        A,B = a*a+b*b*d, 2*a*b
        expr = f"√({A}+{B}√{d})+√({A}−{B}√{d})"
        if i % 2:
            expr = f"[√({A}+{B}√{d})−√({A}−{B}√{d})]²"
        result = 4*b*b*d if i%2 else 2*a
        numeric(17, f"Calculați {expr}.", result,
                f"Radicalii sunt {a}+{b}√{d} și {a}−{b}√{d}, ambele pozitive. " +
                (f"Diferența este {2*b}√{d}, al cărei pătrat este {result}." if i%2 else f"Suma este {result}."))

    for h,above in [(4,False), (2,True), (-3,False), (-1,True), (7,False)]:
        condition = f"x≥{h+1}" if above else f"x≤{h-1}"
        correct = f"x−({h})" if above else f"{h}−x"
        wrong = [f"{h}−x" if above else f"x−({h})", f"x²−{h*h}", f"x²+{h*h}"]
        add(18, f"Simplificați √((x−({h}))²), știind că {condition}.", correct, wrong,
            f"√((x−({h}))²)=|x−({h})|. Din condiția dată, x−({h}) este " +
            ("pozitiv" if above else "negativ") + f", deci rezultatul este {correct}.")

    for i,(a,b,d) in enumerate([(2,1,3),(3,1,5),(4,1,7),(3,2,2),(5,2,6)]):
        A,B = a*a+b*b*d, 2*a*b
        sign = "+" if i%2 == 0 else "−"
        correct = f"{a}{sign}{b}√{d}"
        add(19, f"Descompuneți radicalul √({A}{sign}{B}√{d}).", correct,
            [f"{a}{'−' if sign == '+' else '+'}{b}√{d}", f"{b}{sign}{a}√{d}", f"{A}{sign}{B}√{d}"],
            f"Radicandul este ({correct})². Deoarece {a}>{b}√{d}, expresia {correct} este pozitivă; radicalul este {correct}.")

    for a,b,percent in [(5,2,25),(7,3,20),(11,2,50),(13,7,10),(6,2,75)]:
        total=2*(a+b)
        numeric(20, f"Calculați {percent}% din numărul (√{a}+√{b})²+(√{a}−√{b})².", F(percent*total,100),
                f"Termenii cu radicali se reduc în sumă: numărul este 2·({a}+{b})={total}. Procentul cerut este {percent}/100·{total}={number(F(percent*total,100))}.")

    for e in [2,5,6,10,13]:
        d=e+1
        add(21, f"Raționalizați numitorul fracției 1/(√{d}+√{e}).", f"√{d}−√{e}",
            [f"√{d}+√{e}", f"√{e}−√{d}", f"(√{d}−√{e})/{d+e}"],
            f"Amplificăm cu conjugata √{d}−√{e}. Numitorul devine {d}−{e}=1, deci rezultatul este √{d}−√{e}.")

    for a,b,d in pell:
        A,B = a*a+b*b*d,2*a*b
        add(22, f"Simplificați √({A}+{B}√{d})/√({A}−{B}√{d}).", f"{A}+{B}√{d}",
            [f"{A}−{B}√{d}", f"{a}+{b}√{d}", "1"],
            f"Radicalii sunt {a}±{b}√{d}, iar conjugatele au produsul 1. Raportul este ({a}+{b}√{d})²={A}+{B}√{d}.")

    for root in [2,3,4,5,6]:
        N=root*root-1
        numeric(23, f"Calculați suma Σ[k=1,…,{N}] 1/(√(k+1)+√k).", root-1,
                f"Fiecare termen este √(k+1)−√k. Suma se telescopează la √{N+1}−1={root-1}.")

    for root,x in [(2,3),(3,-2),(4,5),(5,-1),(6,2)]:
        N=root*root-1
        numeric(24, f"Rezolvați în R ecuația x · (Σ[k=1,…,{N}] 1/(√(k+1)+√k)) = {x*(root-1)}.", x,
                f"Suma se reduce la √{N+1}−1={root-1}. Ecuația devine {root-1}x={x*(root-1)}, deci x={x}.")

    for h,r in [(1,2),(2,3),(3,5),(-1,7),(-2,11)]:
        b=r-2*h
        values=[h-1,h+1,h-r,h+r]
        add(25, f"Determinați toate numerele întregi n≠{h} pentru care (2n+({b}))/(n−({h})) este întreg.", number_set(values),
            [number_set([h-1,h+1]), number_set([h-r,h+r]), number_set([v+1 for v in values])],
            f"Fracția este 2+{r}/(n−({h})). Numărul {r} este prim, deci n−({h}) trebuie să fie unul dintre −{r}, −1, 1, {r}. Obținem {number_set(values)}.")

    for k,sign in [(1,"+"),(2,"−"),(3,"+"),(4,"−"),(5,"+")]:
        block=f"x²{sign}x"
        opposite=f"x²{'−' if sign == '+' else '+'}x+{k}"
        add(26, f"Simplificați √[({block})²+{2*k}({block})+{k*k}], pentru x real.", f"{block}+{k}",
            [f"{block}−{k}", opposite, f"x²+{k}"],
            f"Notăm t={block}. Radicandul este (t+{k})². Cum t≥−1/4 și {k}≥1, t+{k}>0, deci radicalul este {block}+{k}.")

    for t,n in [(1,2),(2,2),(3,3),(-1,3),(-2,2)]:
        numeric(27, f"x,y,z sunt reale, x²+y²+z²=xy+yz+zx și x+y+z={3*t}. Calculați x^{n}+y^{n}+z^{n}.", 3*t**n,
                f"(x−y)²+(y−z)²+(z−x)²=2(x²+y²+z²−xy−yz−zx)=0. Rezultă x=y=z, iar suma lor dă x=y=z={t}. Valoarea cerută este {3*t**n}.")

    assert Counter(q['catalog']['type'] for q in questions) == {kind:5 for kind in range(3,28)}
    assert len({q['text'] for q in questions}) == len(questions) == 125
    # Trei variante distribuite în fiecare familie, circa 80 în total cu tipurile 1–2.
    selected = [q for i, q in enumerate(questions) if i % 5 in (0, 2, 4)]
    assert Counter(q['catalog']['type'] for q in selected) == {kind:3 for kind in range(3,28)}
    return selected
