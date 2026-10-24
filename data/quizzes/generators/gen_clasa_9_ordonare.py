"""80 de grile după catalogul Burtea IX, A1 §1.2, p. 14–17.

Enunțuri originale după tipologii; nu sunt transcrieri validate din scanare.
Acest modul este folosit de generatorul lecției despre numere reale.
"""
from collections import Counter
from fractions import Fraction


TYPE_NAMES = [
    "Inegalitatea mediilor pentru două numere", "Inegalități cu inverse",
    "Produse de sume", "Inegalități ciclice cubice",
    "Inegalități prin diferențe pătrate", "Inegalități cubice prin factorizare",
    "Inegalități de grad mai mare", "Sume cu număr arbitrar de termeni",
    "Inegalități între laturile triunghiului", "Inegalități universale prin pătrat complet",
    "Sumă fixată și inverse", "Sumă fixată și produs maxim", "Produs fixat",
    "Normalizarea unei condiții neliniare", "Estimarea produselor cu termeni adunați",
    "Încadrare prin comparații telescopice", "Produs de factori cu produsul variabilelor fixat",
    "Excluderea integrității prin încadrare", "Comparare cu parametru",
    "Diofantice prin inegalități", "Rigiditate geometrică din egalitate",
    "Minimul unei forme pătratice cu două variabile",
]


def build_ordering_questions():
    questions = []
    occurrences = Counter()

    def add(kind, text, correct, wrong, explanation):
        values = [str(correct), *map(str, wrong)]
        assert len(values) == len(set(values)) == 4, (kind, values)
        position = len(questions) % 4
        values.insert(position, values.pop(0))
        occurrences[kind] += 1
        questions.append({
            "text": text, "type": "multiple_choice", "format": "grid", "points": 10,
            "explanation": explanation,
            "options": [{"text": v, "is_correct": i == position} for i, v in enumerate(values)],
            "catalog": {"section": "A1.1.2", "type": kind, "type_name": TYPE_NAMES[kind-1],
                        "variant": occurrences[kind],
                        "origin": "Exercițiu nou după tipologia catalogului Burtea IX"},
        })

    def numeric(kind, text, answer, explanation, wrong=None):
        answer = Fraction(answer)
        if wrong is None:
            wrong = []
            for candidate in [answer/2, answer*2, answer+1, answer-1, -answer, Fraction(3)]:
                if candidate != answer and candidate not in wrong:
                    wrong.append(candidate)
                if len(wrong) == 3:
                    break
        wrong = list(map(Fraction, wrong))
        assert len(set(wrong + [answer])) == 4
        add(kind, text, answer, wrong, explanation)

    # Tipurile 1–14: patru variante fiecare.
    numeric(1, "a,b sunt pozitive și a+b=10. Care este valoarea maximă a lui ab?", 25,
            "Din (a−b)²≥0 rezultă 4ab≤(a+b)²=100. Maximul 25 se atinge pentru a=b=5.")
    numeric(1, "a,b sunt reale și a+b=8. Care este valoarea minimă a lui a²+b²?", 32,
            "a²+b²≥(a+b)²/2=32. Egalitatea se atinge pentru a=b=4.")
    numeric(1, "Pentru x>0, care este valoarea minimă a lui x+9/x?", 6,
            "Media aritmetică este cel puțin media geometrică: x+9/x≥2√9=6. Egalitatea se atinge la x=3.")
    add(1, "Pentru a,b>0, când are loc egalitatea (a+b)/2=√(ab)?", "a=b",
        ["a+b=1", "ab=1", "a=2b"], "Egalitatea este echivalentă cu (a−b)²=0, deci cu a=b.")

    for s in [2,4,6,10]:
        numeric(2, f"a,b>0 și a+b={s}. Care este valoarea minimă a lui 1/a+1/b?", Fraction(4,s),
                f"1/a+1/b=(a+b)/(ab). Din ab≤{s}²/4 rezultă minimul 4/{s}={Fraction(4,s)}, atins la a=b={Fraction(s,2)}.")

    numeric(3, "a,b,c>0 și abc=1. Care este minimul lui (a+b)(b+c)(c+a)?", 8,
            "Înmulțim a+b≥2√(ab), b+c≥2√(bc), c+a≥2√(ca): produsul este ≥8abc=8. Egalitate la a=b=c=1.")
    numeric(3, "a,b,c>0 și abc=8. Care este minimul lui (a+b)(b+c)(c+a)?", 64,
            "Produsul este ≥8abc=64. Valoarea se atinge pentru a=b=c=2.")
    add(3, "Pentru a,b,c>0, când are loc egalitatea (a+b)(b+c)(c+a)=8abc?", "a=b=c",
        ["a=b, fără condiție asupra lui c", "abc=1, fără alte condiții", "a+b=c"],
        "Egalitatea în toate cele trei inegalități ale mediilor cere a=b, b=c și c=a.")
    numeric(3, "Pentru a,b,c>0, care este minimul raportului (a+b)(b+c)(c+a)/(abc)?", 8,
            "Produsul de la numărător este ≥8abc. Împărțim la abc>0; egalitatea se atinge la a=b=c.")

    for p in [1,2,4,9]:
        numeric(4, f"a,b,c>0 și abc={p}. Determinați minimul lui a(b²+c²)+b(c²+a²)+c(a²+b²).", 6*p,
                f"Din b²+c²≥2bc rezultă a(b²+c²)≥2abc; analog pentru ceilalți doi termeni. Suma este ≥6abc={6*p}. Egalitatea se atinge când a=b=c=∛{p}.")

    for s in [3,6,9,12]:
        numeric(5, f"a,b,c sunt reale și a+b+c={s}. Care este minimul lui a²+b²+c²?", Fraction(s*s,3),
                f"3(a²+b²+c²)−(a+b+c)²=(a−b)²+(b−c)²+(c−a)²≥0. Minimul este {s}²/3={s*s//3}, la a=b=c={s//3}.")

    for p in [1,2,5,8]:
        numeric(6, f"a,b,c>0 și abc={p}. Care este minimul lui a³+b³+c³?", 3*p,
                f"a³+b³+c³−3abc=(a+b+c)[(a−b)²+(b−c)²+(c−a)²]/2≥0. Rezultă minimul {3*p}, atins la a=b=c=∛{p}.")

    for k,c in [(1,2),(2,3),(3,1),(4,5)]:
        numeric(7, f"Pentru x,y reale, determinați minimul expresiei x⁴+{k*k}y⁴−{2*k}x²y²+{c}.", c,
                f"Expresia este (x²−{k}y²)²+{c}≥{c}. Egalitatea se atinge, de exemplu, la x=y=0.")

    for n in [3,4,5,6]:
        numeric(8, f"a₁,…,a{n} sunt pozitive. Care este minimul lui (a₁+…+a{n})(1/a₁+…+1/a{n})?", n*n,
                f"Din Cauchy, produsul este ≥(√(a₁/a₁)+…+√(a{n}/a{n}))²={n}²={n*n}. Egalitatea se atinge când toate numerele sunt egale.")

    for k in [2,3]:
        add(9, f"Un triunghi are laturile b=c={k}. Care este mulțimea tuturor valorilor posibile ale celei de-a treia laturi a?",
            f"(0; {2*k})", [f"[{k}; {2*k}]", f"(0; {k})", f"[{2*k}; +∞)"],
            f"Inegalitățile triunghiului cer |b−c|<a<b+c, deci 0<a<{2*k}. Capetele nu formează triunghiuri nedegenerate.")
    add(9, "Care relație este adevărată pentru laturile oricărui triunghi nedegenerat?", "a²<2(b²+c²)",
        ["a²≥2(b²+c²)", "a≥b+c", "a²=b²+c² pentru orice triunghi"],
        "a<b+c, deci a²<(b+c)²≤2(b²+c²). Ultima relație rezultă din (b−c)²≥0.")
    numeric(9, "Care este cea mai mică constantă reală C pentru care a²<C(b²+c²) în orice triunghi nedegenerat?", 2,
            "C=2 funcționează deoarece a²<(b+c)²≤2(b²+c²). Pentru b=c=1 și a apropiat de 2, raportul a²/(b²+c²) se apropie de 2; nicio constantă mai mică nu funcționează.")

    for h,c in [(2,3),(-3,2),(4,-1),(-1,5)]:
        numeric(10, f"Determinați minimul pe R al expresiei x²+({-2*h})x+({h*h+c}).", c,
                f"Completăm pătratul: expresia este (x−({h}))²+({c}). Minimul {c} se atinge pentru x={h}.")

    for s in [1,3,6,9]:
        numeric(11, f"a,b,c>0 și a+b+c={s}. Care este minimul lui 1/a+1/b+1/c?", Fraction(9,s),
                f"Cauchy dă (a+b+c)(1/a+1/b+1/c)≥9. Minimul este 9/{s}={Fraction(9,s)}, atins la a=b=c={Fraction(s,3)}.")

    for s in [3,6,9,12]:
        numeric(12, f"a,b,c>0 și a+b+c={s}. Care este valoarea maximă a lui abc?", (s//3)**3,
                f"Media aritmetică–geometrică dă abc≤[({s})/3]³={(s//3)**3}. Egalitate la a=b=c={s//3}.")

    for m in [1,2,3,4]:
        numeric(13, f"a,b,c>0 și abc={m**3}. Care este valoarea minimă a lui a+b+c?", 3*m,
                f"a+b+c≥3∛(abc)=3·{m}={3*m}. Egalitatea se atinge pentru a=b=c={m}.")

    add(14, "x,y,z>0 și x+y+z=xyz. Ce relație obținem prin împărțirea egalității la xyz?",
        "1/(yz)+1/(xz)+1/(xy)=1", ["1/x+1/y+1/z=1", "xy+yz+zx=1", "1/(xyz)=1"],
        "Împărțim fiecare termen la xyz: x/(xyz)=1/(yz), y/(xyz)=1/(xz), z/(xyz)=1/(xy).")
    numeric(14, "x,y,z>0 și x+y+z=xyz. Care este minimul lui xy+yz+zx?", 9,
            "Notăm a=1/(yz), b=1/(xz), c=1/(xy); avem a+b+c=1. Atunci xy+yz+zx=1/a+1/b+1/c≥9. Egalitate la x=y=z=√3.")
    numeric(14, "x,y,z>0 și x+y+z=xyz. Care este minimul lui (x+y+z)²?", 27,
            "Notăm S=x+y+z=xyz>0. Din S³≥27xyz=27S rezultă S²≥27. Egalitatea se atinge la x=y=z=√3.")
    add(14, "x,y,z>0, x+y+z=xyz și (x+y+z)²=27. Care sunt valorile lui x,y,z?",
        "x=y=z=√3", ["x=y=z=1", "x=y=z=3", "x=y=z=1/√3"],
        "Valoarea 27 realizează egalitatea în (x+y+z)³≥27xyz. Deci x=y=z=t>0; condiția 3t=t³ dă t=√3.")

    # Tipurile 15–22: trei variante fiecare; totalul este exact 80.
    for s in [3,6,9]:
        answer=s*s//3+s
        numeric(15, f"x,y,z>0 și x+y+z={s}. Determinați maximul lui x(y+1)+y(z+1)+z(x+1).", answer,
                f"Expresia este xy+yz+zx+{s}. Din xy+yz+zx≤(x+y+z)²/3 rezultă maximul {s*s//3}+{s}={answer}, atins la x=y=z={s//3}.")

    for n in [3,5,10]:
        numeric(16, f"Fie S=Σ[k=2,…,{n}] 1/k² și M=Σ[k=2,…,{n}] 1/[k(k−1)]. Din 1/k²<1/[k(k−1)] rezultă S<M. Calculați suma majorantă M.", Fraction(n-1,n),
                f"1/[k(k−1)]=1/(k−1)−1/k. Prin telescopare M=1−1/{n}={Fraction(n-1,n)}; astfel S<{Fraction(n-1,n)}.")

    for n in [3,4,5]:
        numeric(17, f"a₁,…,a{n}>0 și a₁·…·a{n}=1. Care este minimul produsului (1+a₁)·…·(1+a{n})?", 2**n,
                f"Înmulțim 1+aᵢ≥2√aᵢ. Produsul este ≥2^{n}√(a₁·…·a{n})={2**n}, cu egalitate când toate aᵢ sunt 1.")

    for n in [2,3,4]:
        add(18, f"Între ce doi întregi consecutivi se află S=√{n*n+1}+√{n*n-1}, demonstrând astfel că S nu este întreg?",
            f"{2*n-1}<S<{2*n}", [f"{2*n-2}<S<{2*n-1}", f"{2*n}<S<{2*n+1}", f"{2*n+1}<S<{2*n+2}"],
            f"Avem √{n*n+1}>{n} și √{n*n-1}>{n-1}, deci S>{2*n-1}. Totodată S²={2*n*n}+2√{n**4-1}<{4*n*n}, deci S<{2*n}. Încadrarea strictă exclude integritatea.")

    add(19, "Pentru x<1, ordonați crescător numerele A=2, B=3x−1 și C=x+1.", "B<C<A",
        ["A<C<B", "C<B<A", "B<A<C"], "B−C=2(x−1)<0 și C−A=x−1<0. Prin urmare B<C<A.")
    add(19, "Pentru x>1, ordonați crescător numerele A=2, B=3x−1 și C=x+1.", "A<C<B",
        ["B<C<A", "C<A<B", "A<B<C"], "C−A=x−1>0 și B−C=2(x−1)>0. Rezultă A<C<B.")
    numeric(19, "Pentru ce valoare reală a lui x sunt egale toate cele trei numere 2, 3x−1 și x+1?", 1,
            "Din x+1=2 rezultă x=1. Atunci și 3x−1=2, deci condiția este satisfăcută.")

    add(20, "Determinați toate perechile de numere întregi x,y≥2 pentru care xy≤x+y.", "Doar (2; 2)",
        ["Doar (2; 3) și (3; 2)", "Toate perechile cu x=y≥2", "Nu există perechi"],
        "Inegalitatea este (x−1)(y−1)≤1. Cei doi factori sunt întregi cel puțin 1, deci sunt amândoi 1: x=y=2.")
    add(20, "Determinați toate perechile de numere întregi pozitive x,y pentru care xy<x+y.", "x=1 sau y=1",
        ["Doar x=y=1", "x≥2 și y≥2", "Doar x=y=2"],
        "(x−1)(y−1)<1. Produsul este întreg nenegativ, deci este zero: x=1 sau y=1. Orice astfel de pereche verifică inegalitatea.")
    add(20, "Determinați toate tripletele de numere întregi x,y,z≥3 pentru care xyz≤xy+xz+yz.", "Doar (3; 3; 3)",
        ["Doar (3; 3; 4)", "Toate tripletele cu x=y=z≥3", "Nu există triplete"],
        "Împărțim la xyz>0: 1≤1/x+1/y+1/z≤1. Egalitatea în limita superioară impune x=y=z=3; acest triplet verifică relația.")

    for t in [3,4,6]:
        add(21, f"Laturile unui triunghi au perimetrul {3*t} și verifică a²+b²+c²=ab+bc+ca. Care este tripletul (a; b; c)?",
            f"({t}; {t}; {t})", [f"({t-1}; {t}; {t+1})", f"({t-1}; {t+1}; {t})", f"({t}; {t-1}; {t+1})"],
            f"(a−b)²+(b−c)²+(c−a)²=0, deci a=b=c. Din perimetru rezultă a=b=c={t}; triunghiul este echilateral, cu unghiurile de 60°.")

    for h,k,c in [(1,1,3),(2,-1,0),(-1,2,-2)]:
        Lx,Ly,C=-2*h+4*k,4*h-10*k,h*h-4*h*k+5*k*k+c
        numeric(22, f"Determinați minimul pe R² al expresiei x²−4xy+5y²+({Lx})x+({Ly})y+({C}).", c,
                f"Expresia se scrie [x−({h})−2(y−({k}))]²+[y−({k})]²+({c}). Cei doi pătrați sunt nenegativi și se anulează simultan la (x,y)=({h},{k}). Minimul este {c}.")

    assert occurrences == {i:4 if i<=14 else 3 for i in range(1,23)}
    assert len(questions) == len({q['text'] for q in questions}) == 80
    return questions
