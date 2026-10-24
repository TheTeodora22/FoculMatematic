"""80 de grile originale după catalogul Burtea IX, A1 §1.3, p. 18–22.

Acoperă toate cele 24 de tipuri. Nu transcrie enunțuri din scanare.
"""
from collections import Counter
from fractions import Fraction


TYPE_NAMES = [
    "Calcul numeric al modulelor", "Ecuația elementară cu modul", "Sumă de module nulă",
    "Ecuații cu modul în mulțimi discrete", "Inecuații imposibile sau automate",
    "Inecuația dublă cu modul", "Exteriorul unui interval prin modul",
    "Inecuații cu restricții naturale", "Ecuații liniare în modul",
    "Ecuații pătratice în modul", "Produse de factori cu modul", "Fracții cu modul",
    "Modul și puteri ale lui 2", "Radicali pătrați și ipoteze de semn",
    "Ecuații cu parametru încadrat", "Ecuații sub condiție de semn a necunoscutei",
    "Încadrarea unei combinații liniare", "Extreme dintr-o ecuație de elipsoid",
    "Inegalitatea triunghiulară ponderată", "Produse de module",
    "Inegalități cu inverse și module", "Incompatibilitate prin triunghiulară",
    "Stabilitatea unei fracții în interval", "Module cu interval impus",
]


def build_absolute_value_questions():
    questions = []
    occurrences = Counter()

    def add(kind, text, correct, wrong, explanation):
        values = [str(correct), *map(str, wrong)]
        assert len(values) == len(set(values)) == 4, (kind, text, values)
        position = len(questions) % 4
        values.insert(position, values.pop(0))
        occurrences[kind] += 1
        questions.append({
            "text": text, "type": "multiple_choice", "format": "grid", "points": 10,
            "explanation": explanation,
            "options": [{"text": v, "is_correct": i == position} for i, v in enumerate(values)],
            "catalog": {"section": "A1.1.3", "type": kind, "type_name": TYPE_NAMES[kind-1],
                        "variant": occurrences[kind],
                        "origin": "Exercițiu nou după tipologia catalogului Burtea IX"},
        })

    def numeric(kind, text, correct, wrong, explanation):
        assert len(set(map(Fraction, [correct, *wrong]))) == 4
        add(kind, text, correct, wrong, explanation)

    # Tipurile 1–8: câte patru grile; tipurile 9–24: câte trei.
    numeric(1, "Calculați |−3|+|2−7|.", 8, [2,-8,10], "|−3|=3 și |2−7|=|−5|=5, deci suma este 8.")
    numeric(1, "Calculați ||−5|−8|.", 3, [-3,13,5], "Mai întâi |−5|=5. Apoi |5−8|=|−3|=3.")
    numeric(1, "Calculați |2−√5|+|√5−3|.", 1, [-1,5,0], "2<√5<3. Suma este (√5−2)+(3−√5)=1.")
    add(1, "Calculați |√2−2|−|√2+2|.", "−2√2", ["0","2√2","4"],
        "√2<2, deci primul modul este 2−√2; al doilea este √2+2. Diferența este −2√2.")

    rows = [
        ("|3x−1|=5", "{−4/3; 2}", ["{−2; 2}","{2}","{−4/3}"], "3x−1=5 sau 3x−1=−5, deci x=2 sau x=−4/3."),
        ("|2x+3|=1", "{−2; −1}", ["{−1; 1}","{−2}","{1; 2}"], "2x+3=1 sau 2x+3=−1, deci x=−1 sau x=−2."),
        ("|x−4|=0", "{4}", ["{−4; 4}","∅","R"], "Un modul este zero numai când expresia din interior este zero: x=4."),
        ("|5x−2|=−3", "∅", ["{−1/5; 1}","{−1/5}","R"], "Un modul este nenegativ, deci nu poate fi egal cu −3."),
    ]
    for expr,correct,wrong,proof in rows:
        add(2, f"Care este mulțimea soluțiilor reale ale ecuației {expr}?",correct,wrong,proof)

    rows = [
        ("|x²−1|+|2x−2|=0", "{1}", ["{−1; 1}","{−1}","∅"], "Ambii termeni trebuie să fie zero. Prima condiție dă x=±1, iar a doua x=1. Intersecția este {1}."),
        ("|x−2|+|x+2|=0", "∅", ["{−2; 2}","{0}","R"], "Ar trebui să avem simultan x=2 și x=−2, ceea ce este imposibil."),
        ("|(x−3)(x+1)|+|x+1|=0", "{−1}", ["{−1; 3}","{3}","∅"], "Al doilea modul impune x=−1. Această valoare anulează și primul modul, deci este unica soluție."),
        ("|x²−9|+|x−3|=0", "{3}", ["{−3; 3}","{−3}","∅"], "Prima condiție dă x=±3, iar a doua x=3; rămâne numai x=3."),
    ]
    for expr,correct,wrong,proof in rows:
        add(3,f"Rezolvați în R ecuația {expr}.",correct,wrong,proof)

    rows = [
        ("|2x−1|=3", "{−1; 2}", ["{−2; 1}","{2}","∅"], "În R obținem x=−1 sau x=2. Ambele valori sunt întregi."),
        ("|3x+1|=2", "{−1}", ["{−1; 1/3}","{1/3}","∅"], "Soluțiile reale sunt −1 și 1/3. Intersecția cu Z păstrează numai −1."),
        ("|2x+1|=2", "∅", ["{−3/2; 1/2}","{−1; 1}","{0}"], "Soluțiile reale sunt −3/2 și 1/2. Niciuna nu este întreagă."),
        ("(|x|+1)/(|x|−2)=2", "{−5; 5}", ["{−2; 2}","{5}","∅"], "Domeniul cere |x|≠2. Notăm t=|x|: t+1=2t−4, deci t=5. Rezultă x=±5, ambele admise."),
    ]
    for expr,correct,wrong,proof in rows:
        add(4,f"Determinați mulțimea soluțiilor întregi ale ecuației {expr}.",correct,wrong,proof)

    rows = [
        ("|3x−4|<0", "∅", ["R","{4/3}","(−∞; 4/3)"], "Nicio valoare absolută nu este strict negativă."),
        ("|x+2|≥0", "R", ["∅","{−2}","[−2; +∞)"], "Modulul oricărui număr real este nenegativ, deci toate valorile reale sunt admise."),
        ("|2x−1|>−3", "R", ["∅","{1/2}","(1/2; +∞)"], "Pentru orice x real, |2x−1|≥0>−3."),
        ("|x−3|≤0", "{3}", ["R","∅","(−∞; 3]"], "Un modul este cel mult zero exact când este zero: x−3=0."),
    ]
    for expr,correct,wrong,proof in rows:
        add(5,f"Rezolvați în R inecuația {expr}.",correct,wrong,proof)

    rows = [
        ("|2x+8|<2", "(−5; −3)", ["[−5; −3]","(−3; 5)","(−∞; −5) ∪ (−3; +∞)"], "−2<2x+8<2, deci −10<2x<−6 și −5<x<−3."),
        ("|3x−6|≤9", "[−1; 5]", ["(−1; 5)","[1; 5]","(−∞; −1] ∪ [5; +∞)"], "−9≤3x−6≤9, deci −3≤3x≤15 și −1≤x≤5."),
        ("|x+1|<4", "(−5; 3)", ["[−5; 3]","(−3; 5)","(−∞; −5) ∪ (3; +∞)"], "−4<x+1<4, deci −5<x<3."),
        ("|2x−1|≤3", "[−1; 2]", ["(−1; 2)","[−2; 1]","(−∞; −1] ∪ [2; +∞)"], "−3≤2x−1≤3, deci −2≤2x≤4 și −1≤x≤2."),
    ]
    for expr,correct,wrong,proof in rows:
        add(6,f"Care este mulțimea soluțiilor reale ale inecuației {expr}?",correct,wrong,proof)

    rows = [
        ("|2x−5|>1", "(−∞; 2) ∪ (3; +∞)", ["(2; 3)","(−∞; 2] ∪ [3; +∞)","(−∞; −3) ∪ (−2; +∞)"], "2x−5<−1 sau 2x−5>1; rezultă x<2 sau x>3."),
        ("|3x+3|≥6", "(−∞; −3] ∪ [1; +∞)", ["[−3; 1]","(−∞; −3) ∪ (1; +∞)","(−∞; −1] ∪ [3; +∞)"], "3x+3≤−6 sau 3x+3≥6, deci x≤−3 sau x≥1."),
        ("|x−2|>4", "(−∞; −2) ∪ (6; +∞)", ["(−2; 6)","(−∞; −2] ∪ [6; +∞)","(−∞; −6) ∪ (2; +∞)"], "x−2<−4 sau x−2>4, adică x<−2 sau x>6."),
        ("|2x+4|≥2", "(−∞; −3] ∪ [−1; +∞)", ["[−3; −1]","(−∞; −3) ∪ (−1; +∞)","(−∞; 1] ∪ [3; +∞)"], "2x+4≤−2 sau 2x+4≥2, deci x≤−3 sau x≥−1."),
    ]
    for expr,correct,wrong,proof in rows:
        add(7,f"Rezolvați în R inecuația {expr}.",correct,wrong,proof)

    rows = [
        ("|n−3|<2", "{2; 3; 4}", ["{1; 2; 3; 4; 5}","{0; 1; 2}","{3}"], "1<n<5. Numerele naturale din acest interval sunt 2, 3 și 4."),
        ("|2n−5|≤3", "{1; 2; 3; 4}", ["{2; 3}","{0; 1; 2; 3; 4}","{1; 4}"], "−3≤2n−5≤3 conduce la 1≤n≤4."),
        ("|n+1|<3", "{0; 1}", ["{1; 2}","{0; 1; 2}","{0}"], "−4<n<2. Intersecția cu N={0,1,2,…} este {0; 1}."),
        ("|3n−2|>4", "{3; 4; 5; …}", ["{0; 1; 2}","{2; 3; 4; …}","{0; 3; 4; 5; …}"], "3n−2<−4 sau 3n−2>4, adică n<−2/3 sau n>2. În N rămân toate numerele cel puțin 3."),
    ]
    for expr,correct,wrong,proof in rows:
        add(8,f"În convenția N={{0,1,2,…}}, determinați soluțiile naturale ale inecuației {expr}.",correct,wrong,proof)

    rows = [
        ("3|x+1|−5=7", "{−5; 3}", ["{−3; 5}","{3}","∅"], "3|x+1|=12, deci |x+1|=4 și x=−5 sau x=3."),
        ("2|x−2|+1=9", "{−2; 6}", ["{−6; 2}","{2; 6}","∅"], "2|x−2|=8, deci |x−2|=4 și x=−2 sau x=6."),
        ("5|x+3|+2=−3", "∅", ["{−4; −2}","{−3}","R"], "Ar rezulta |x+3|=−1, imposibil deoarece modulul este nenegativ."),
    ]
    for expr,correct,wrong,proof in rows:
        add(9,f"Rezolvați în R ecuația {expr}.",correct,wrong,proof)

    rows = [
        ("|x−1|²−3|x−1|+2=0", "{−1; 0; 2; 3}", ["{1; 2}","{0; 2}","{−1; 3}"], "Cu t=|x−1|≥0, (t−1)(t−2)=0. Din t=1 obținem x=0,2; din t=2, x=−1,3."),
        ("|x+2|²+|x+2|−2=0", "{−3; −1}", ["{−4; −3; −1; 0}","{−2; 1}","∅"], "Cu t=|x+2|≥0 avem (t+2)(t−1)=0. Respingem t=−2, păstrăm t=1, deci x=−3 sau x=−1."),
        ("2|x|²−5|x|+2=0", "{−2; −1/2; 1/2; 2}", ["{1/2; 2}","{−2; 2}","{−1; 1}"], "Cu t=|x|≥0, (2t−1)(t−2)=0. Ambele rădăcini t=1/2 și t=2 sunt admise, fiecare dând două valori opuse ale lui x."),
    ]
    for expr,correct,wrong,proof in rows:
        add(10,f"Determinați mulțimea soluțiilor reale ale ecuației {expr}.",correct,wrong,proof)

    rows = [
        ("|x|(|x−1|−2)<0", "(−1; 0) ∪ (0; 3)", ["(−1; 3)","[−1; 3]","(−∞; −1) ∪ (3; +∞)"], "Pentru un produs strict negativ, |x| trebuie să fie pozitiv și |x−1|−2<0. Avem −1<x<3 și excludem x=0."),
        ("|x−5|(|x|−3)≤0", "[−3; 3] ∪ {5}", ["[−3; 3]","(−3; 3) ∪ {5}","(−∞; −3] ∪ [3; +∞)"], "Dacă x≠5, primul factor este pozitiv și cerem |x|≤3. La x=5 produsul este zero, deci adăugăm și această soluție izolată."),
        ("|x+1|(|x|−2)>0", "(−∞; −2) ∪ (2; +∞)", ["[−2; 2]","(−∞; −2] ∪ [2; +∞)","(−2; 2)"], "Primul factor este nenegativ. Produsul este pozitiv când |x|>2; pe aceste semidrepte x≠−1 automat."),
    ]
    for expr,correct,wrong,proof in rows:
        add(11,f"Rezolvați în R inecuația {expr}.",correct,wrong,proof)

    rows = [
        ("(|x|−1)/(|x|−3)<0", "(−3; −1) ∪ (1; 3)", ["[−3; −1] ∪ [1; 3]","(−1; 1)","(−∞; −3) ∪ (3; +∞)"], "Domeniul exclude |x|=3. Pentru t=|x|≥0, (t−1)/(t−3)<0 exact când 1<t<3."),
        ("(|x|−2)/(|x|−1)≥0", "(−∞; −2] ∪ (−1; 1) ∪ [2; +∞)", ["(−2; −1) ∪ (1; 2)","(−∞; −2] ∪ [−1; 1] ∪ [2; +∞)","(−∞; −1) ∪ (1; +∞)"], "Domeniul exclude |x|=1. Cu t=|x|≥0, raportul este nenegativ pentru 0≤t<1 sau t≥2; traducem cele două condiții în x."),
        ("1/(2−|x|)>0", "(−2; 2)", ["[−2; 2]","(−∞; −2) ∪ (2; +∞)","R"], "Numărătorul este pozitiv, deci cerem numitor strict pozitiv: 2−|x|>0. Rezultă |x|<2; capetele sunt excluse din domeniu."),
    ]
    for expr,correct,wrong,proof in rows:
        add(12,f"Cu respectarea domeniului de definiție, rezolvați în R inecuația {expr}.",correct,wrong,proof)

    for a,total,expected in [(4,36,9),(2,18,6),(1,9,4)]:
        pairs=[(x,n) for x in range(total+1) for n in range(total.bit_length()+1) if x+abs(x-a)+2**n==total]
        assert len(pairs)==expected
        listing=", ".join(f"({x}; {n})" for x,n in pairs)
        numeric(13,f"Câte perechi (x,n)∈N² verifică x+|x−{a}|+2ⁿ={total}, dacă N={{0,1,2,…}}?",expected,
                [expected-1,expected+1,expected+2],
                f"Pentru 0≤x≤{a}, x+|x−{a}|={a}; pentru x>{a}, expresia este 2x−{a}. În ambele cazuri 2ⁿ≤{total}. Verificarea puterilor admise dă exact perechile {listing}, în total {expected}.")

    for condition,correct,wrong,proof in [
        ("a≥0>b", "a−b", ["a+b","b−a","−a−b"], "|a|=a și |b|=−b, deci suma este a−b."),
        ("a<0≤b", "b−a", ["a+b","a−b","−a−b"], "|a|=−a și |b|=b, deci suma este b−a."),
        ("a≤0 și b≤0", "−a−b", ["a+b","a−b","b−a"], "Ambele numere sunt nepozitive: |a|=−a și |b|=−b."),
    ]:
        add(14,f"Simplificați √(a²)+√(b²), știind că {condition}.",correct,wrong,"√(a²)+√(b²)=|a|+|b|. "+proof)

    add(15,"Pentru −2≤b≤−1, rezolvați în x ecuația x+√((b−3)²)=5.","x=b+2",
        ["x=8−b","x=b−2","x=2−b"],"b−3<0, deci radicalul este 3−b. Ecuația devine x+3−b=5, de unde x=b+2.")
    add(15,"Pentru 1≤a≤2, care este mulțimea soluțiilor reale ale ecuației |x|=√((a−4)²)?","{a−4; 4−a}",
        ["{4−a}","{a−4}","∅"],"a−4<0, deci radicalul este 4−a>0. Ecuația |x|=4−a are soluțiile x=±(4−a).")
    add(15,"Pentru −3≤t≤−2, rezolvați în x ecuația 2x+√((t+1)²)=3.","x=(t+4)/2",
        ["x=(2−t)/2","x=(t+2)/2","x=−t/2"],"t+1<0, deci radicalul este −t−1. Obținem 2x−t−1=3 și x=(t+4)/2.")

    add(16,"Rezolvați √(x²)+2x=−6, sub condiția x<0.","{−6}",
        ["{−2}","{6}","∅"],"Pentru x<0, √(x²)=−x. Ecuația devine x=−6, iar valoarea verifică ipoteza și ecuația inițială.")
    add(16,"Determinați toate soluțiile ecuației |x−1|+x=1 care verifică x<0.","(−∞; 0)",
        ["{0}","{−1}","∅"],"Pentru x<0, x−1<0 și |x−1|=1−x. Ecuația se reduce la identitatea 1=1, deci orice x<0 este soluție.")
    add(16,"Rezolvați √((x+2)²)=−x, sub condiția x<0.","{−1}",
        ["{−2}","(−∞; −2)","∅"],"Ecuația este |x+2|=−x. Pentru −2≤x<0 obținem x+2=−x, deci x=−1. Pentru x<−2 obținem −x−2=−x, imposibil.")

    for a,r,b,s in [(1,2,4,1),(-2,1,3,2),(0,3,-1,2)]:
        lo,hi=b-a-r-s,b-a+r+s
        add(17,f"x,y sunt reale, |x−({a})|≤{r} și |y−({b})|≤{s}. Care este mulțimea tuturor valorilor posibile ale lui y−x?",
            f"[{lo}; {hi}]",[f"({lo}; {hi})",f"[{lo+1}; {hi-1}]",f"[{lo-1}; {hi+1}]"],
            f"x∈[{a-r}; {a+r}], y∈[{b-s}; {b+s}]. Minimul este ({b-s})−({a+r})={lo}, iar maximul ({b+s})−({a-r})={hi}. Intervalele sunt independente; toate valorile intermediare se ating.")

    add(18,"Dacă (2x−1)²+(y−2)²+(3z−1)²=9, care este mulțimea valorilor posibile ale lui x?","[−1; 2]",
        ["(−1; 2)","[−3; 3]","[−2; 1]"],"(2x−1)²≤9 dă −3≤2x−1≤3, adică −1≤x≤2. Pentru orice astfel de x putem lua z=1/3 și (y−2)²=9−(2x−1)²≥0, deci întregul interval se realizează.")
    add(18,"Dacă (x+2)²+4(y−1)²+z²=16, care este mulțimea valorilor posibile ale lui x?","[−6; 2]",
        ["[−4; 4]","(−6; 2)","[−2; 6]"],"(x+2)²≤16, deci −6≤x≤2. Pentru orice astfel de x, alegem y=1 și z²=16−(x+2)²≥0; toate valorile sunt posibile.")
    add(18,"Dacă 9(x−1)²+(y+3)²+4z²=36, care este mulțimea valorilor posibile ale lui y?","[−9; 3]",
        ["[−3; 9]","[−6; 6]","(−9; 3)"],"(y+3)²≤36 dă −9≤y≤3. Pentru orice astfel de y, alegem x=1 și 4z²=36−(y+3)²≥0, deci intervalul este complet.")

    numeric(19,"Dacă |x|≤2 și |y|≤1, care este maximul lui |2x−3y|?",7,[5,1,8],
            "Triunghiulara dă |2x−3y|≤2|x|+3|y|≤7. Egalitatea se atinge la x=2, y=−1.")
    numeric(19,"Dacă |x|≤1 și |y|≤4, care este maximul lui |3x+2y|?",11,[7,8,12],
            "|3x+2y|≤3|x|+2|y|≤11, iar x=1, y=4 realizează valoarea 11.")
    numeric(19,"Dacă |x|≤2, |y|≤1 și |z|≤2, care este maximul lui |x−2y+3z|?",10,[6,8,12],
            "|x−2y+3z|≤|x|+2|y|+3|z|≤10. Valoarea se atinge pentru x=2, y=−1, z=2.")

    numeric(20,"a,b sunt reale și a²+b²=10. Care este maximul lui |a+b|·|a−b|?",10,[5,20,0],
            "Produsul este |a²−b²|≤a²+b²=10. Egalitatea se atinge, de exemplu, pentru a=√10, b=0.")
    numeric(20,"a,b sunt reale, |a+b|≤3 și |a−b|≤2. Care este maximul lui |a+b|·|a−b|?",6,[5,9,4],
            "Produsul este cel mult 3·2=6. Se atinge când a+b=3 și a−b=2, adică a=5/2, b=1/2.")
    add(20,"Care expresie este identică cu |a+b+c|·|a−b+c| pentru orice a,b,c reale?","|(a+c)²−b²|",
        ["(a+c)²−b²","|(a+c)²+b²|","|a+c|−|b|"],"Folosim |u||v|=|uv| și diferența de pătrate pentru u=(a+c)+b, v=(a+c)−b.")

    numeric(21,"a,b sunt reale nenule. Care este minimul lui (|a|+|b|)(1/|a|+1/|b|)?",4,[2,1,8],
            "Cu u=|a|>0 și v=|b|>0, produsul este 2+u/v+v/u≥4. Egalitatea se atinge când |a|=|b|.")
    numeric(21,"Pentru x real nenul, care este minimul lui |x|+9/|x|?",6,[3,9,0],
            "Cu t=|x|>0, t+9/t≥2√9=6. Egalitatea se atinge pentru |x|=3, adică x=±3.")
    numeric(21,"a,b sunt reale nenule și |a|+|b|=4. Care este minimul lui 1/|a|+1/|b|?",1,[Fraction(1,2),2,4],
            "Notăm u=|a|, v=|b|. Avem u+v=4 și uv≤4, deci 1/u+1/v=4/(uv)≥1. Egalitate pentru u=v=2.")

    add(22,"Care este mulțimea soluțiilor reale ale sistemului |x|<1 și |x−3|<1?","∅",
        ["(0; 1)","{3/2}","R"],"Dacă ambele inegalități ar fi adevărate, am avea 3=|x−(x−3)|≤|x|+|x−3|<2, contradicție.")
    add(22,"Rezolvați în R inecuația |x−1|+|x−5|<4.","∅",
        ["(1; 5)","[1; 5]","R"],"Din triunghiulară, |x−1|+|x−5|≥|(x−1)−(x−5)|=4. Inecuația strictă este imposibilă.")
    add(22,"Care afirmație descrie sistemul |a|<1, |b|<2, |a+b|≥3, cu a,b reale?","Sistemul nu are soluții reale.",
        ["Orice a,b cu a+b=3 sunt soluții.","Sistemul are doar soluția (a,b)=(1,2).","Sistemul are soluția (a,b)=(0,0)."],"Primele două condiții implică |a+b|≤|a|+|b|<3, în contradicție cu ultima condiție.")

    add(23,"Dacă |x|<1 și |y|<1, care este mulțimea tuturor valorilor posibile ale fracției (x+y)/(1+xy)?","(−1; 1)",
        ["[−1; 1]","(−∞; −1) ∪ (1; +∞)","R"],"1+xy>0 și 1−[(x+y)/(1+xy)]²=(1−x²)(1−y²)/(1+xy)²>0. Rezultă modul strict sub 1. Orice t∈(−1,1) se obține pentru x=t, y=0.")
    add(23,"Dacă |x|<1 și |y|<1, ce se poate afirma despre numitorul 1+xy?","Este strict pozitiv.",
        ["Este strict negativ.","Este întotdeauna zero.","Poate fi pozitiv, zero sau negativ."],"|xy|<1, deci −1<xy<1 și 0<1+xy<2. În particular, fracția cu acest numitor este definită.")
    add(23,"Dacă |x|<1/2 și |y|<1/2, care este mulțimea tuturor valorilor posibile ale lui (x+y)/(1+4xy)?","(−1/2; 1/2)",
        ["[−1/2; 1/2]","(−1; 1)","R"],"Punem u=2x, v=2y, cu |u|,|v|<1. Fracția este (1/2)(u+v)/(1+uv), deci are modul sub 1/2. Orice t din interval se realizează la x=t, y=0.")

    add(24,"Rezolvați |x−2|+|x−4|=2, sub condiția x∈[2; 4].","[2; 4]",
        ["{2; 4}","{3}","∅"],"Pe intervalul dat, suma este (x−2)+(4−x)=2. Orice punct al segmentului verifică ecuația.")
    add(24,"Rezolvați |x−1|−|x−5|=0, sub condiția x∈[2; 4].","{3}",
        ["[2; 4]","{2; 4}","∅"],"Pe [2,4], modulele sunt x−1 și 5−x. Ecuația devine 2x−6=0, deci x=3, care aparține segmentului.")
    add(24,"Rezolvați |x+1|+|x−2|=4, sub condiția x∈[−1; 2].","∅",
        ["[−1; 2]","{−1; 2}","{1/2}"],"Pe segmentul dat, suma este (x+1)+(2−x)=3, deci nu poate fi 4.")

    assert occurrences == {i:4 if i<=8 else 3 for i in range(1,25)}
    assert len(questions) == len({q['text'] for q in questions}) == 80
    return questions
