"""Secțiunile A1.3.1–3.3: 185 de grile originale după catalogul Burtea IX.

Verifică prin enumerare completă formulele logice și identitățile de mulțimi.
Modifică numai lecția Operații logice elementare și legi de calcul.
"""
import json
from collections import Counter
from itertools import product
from pathlib import Path


NAMES = {
    "3.1": ["Evaluarea negației", "Evaluarea disjuncției și conjuncției", "Evaluarea implicației",
            "Evaluarea echivalenței", "Formule cu trei propoziții", "Tautologii fundamentale",
            "Reguli de inferență", "Reconstrucția valorilor de adevăr", "Legile de calcul propozițional",
            "Legile lui De Morgan", "Logică și geometrie analitică", "Cuantificatori în formule compuse"],
    "3.2": ["Negația ca mulțime complementară", "Disjuncția ca reuniune", "Conjuncția ca intersecție",
            "Implicația și incluziunea", "Echivalență și egalitate de mulțimi", "Operații pe predicate binare finite",
            "Consecință aritmetică într-un singur sens", "Traducerea reuniunii în predicate",
            "Traducerea intersecției în predicate", "Complementul relativ și predicatele",
            "Cardinalul unei mulțimi de adevăr", "Incluziuni cu parametri", "Egalități de mulțimi prin logică",
            "Recuperarea unei mulțimi din operațiile ei", "Identități cu diferențe succesive"],
    "3.3": ["Negarea universalului", "Negarea existențialului", "Formalizarea enunțurilor despre numărul soluțiilor",
            "Negarea cuantificatorilor alternați", "Valoarea de adevăr pe mulțimi finite", "Condiție suficientă",
            "Condiție necesară", "Condiție necesară și suficientă", "Suficiență fără necesitate", "Negarea unei incluziuni"],
}
EVALUATIONS = list(product([False, True], repeat=3))
P, Q, R = "p", "q", "r"


def neg(a): return ("¬", a)
def conj(a, b): return ("∧", a, b)
def disj(a, b): return ("∨", a, b)
def imp(a, b): return ("⇒", a, b)
def iff(a, b): return ("⇔", a, b)


def evaluate(f, p, q, r):
    if isinstance(f, str):
        return dict(p=p, q=q, r=r)[f]
    a = evaluate(f[1], p, q, r)
    if f[0] == "¬": return not a
    b = evaluate(f[2], p, q, r)
    return {"∧": a and b, "∨": a or b, "⇒": (not a) or b, "⇔": a == b}[f[0]]


def display(f):
    if isinstance(f, str): return f
    if f[0] == "¬": return f"¬({display(f[1])})"
    return f"({display(f[1])} {f[0]} {display(f[2])})"


def signature(f): return tuple(evaluate(f, *v) for v in EVALUATIONS)
def truth(v): return "Adevărat" if v else "Fals"
def truth_pair(p, q): return f"{truth(p)}; {truth(q)}"
PAIRS = [truth_pair(a, b) for a, b in product([False, True], repeat=2)]


def set_text(s):
    return "{" + "; ".join(map(str, sorted(s))) + "}" if s else "∅"


def build_questions():
    result = []

    def add(section, kind, text, correct, wrong, explanation):
        values = list(map(str, [correct, *wrong]))
        assert len(values) == len(set(values)) == 4, (section, kind, text, values)
        position = len(result) % 4
        values.insert(position, values.pop(0))
        result.append({
            "text": text, "type": "multiple_choice", "format": "grid", "points": 10,
            "explanation": explanation,
            "options": [{"text": v, "is_correct": i == position} for i, v in enumerate(values)],
            "catalog": {"section": f"A1.{section}", "type": kind,
                        "type_name": NAMES[section][kind-1],
                        "origin": "Exercițiu nou după tipologia catalogului Burtea IX"},
        })

    def pair(section, kind, text, a, b, explanation):
        correct = truth_pair(a, b)
        add(section, kind, text + " Alegeți valorile în ordinea indicată.", correct,
            [v for v in PAIRS if v != correct], explanation)

    def set_question(kind, text, answer, universe, explanation):
        candidates = [set(), set(universe), set(universe)-set(answer), set(answer)|{max(universe)+1}]
        candidates += [{x} for x in sorted(universe)]
        correct = set_text(answer)
        wrong = list(dict.fromkeys(set_text(s) for s in candidates if set_text(s) != correct))[:3]
        add("3.2", kind, text, correct, wrong, explanation)

    pool = [P, Q, R, neg(P), neg(Q), neg(R), conj(P,Q), disj(P,Q), imp(P,Q), iff(P,Q),
            conj(P,neg(Q)), disj(neg(P),Q), conj(neg(P),neg(Q)), disj(P,neg(Q)),
            conj(P,R), disj(Q,R), imp(Q,P), iff(P,neg(Q)), conj(P,neg(P))]

    def equivalent(section, kind, text, target, correct, explanation):
        assert signature(target) == signature(correct)
        wrong = []
        for candidate in pool:
            if signature(candidate) != signature(target) and display(candidate) not in wrong:
                wrong.append(display(candidate))
            if len(wrong) == 3: break
        add(section, kind, text, display(correct), wrong, explanation)

    # 3.1: operatori, evaluări, tabele complete, inferențe.
    assignments = [(True,False,True), (False,True,False), (True,True,False), (False,False,True), (True,False,False)]
    formula_pairs = {
        1: [(neg(P),neg(Q)), (neg(neg(P)),neg(Q)), (neg(P),neg(neg(Q))),
            (neg(neg(neg(P))),neg(Q)), (neg(P),neg(neg(neg(Q))))],
        2: [(conj(P,Q),disj(P,Q)), (disj(P,Q),conj(P,neg(Q))),
            (conj(neg(P),Q),disj(neg(P),Q)), (conj(P,neg(Q)),disj(P,neg(Q))),
            (conj(neg(P),neg(Q)),disj(neg(P),neg(Q)))],
        3: [(imp(P,Q),imp(Q,P)), (imp(neg(P),Q),imp(P,neg(Q))),
            (imp(P,neg(Q)),imp(neg(Q),P)), (imp(neg(P),neg(Q)),imp(Q,P)),
            (imp(Q,neg(P)),imp(P,Q))],
        4: [(iff(P,Q),iff(P,neg(Q))), (iff(neg(P),Q),iff(neg(P),neg(Q))),
            (iff(P,neg(Q)),iff(Q,neg(P))), (iff(neg(P),neg(Q)),iff(P,Q)),
            (iff(neg(neg(P)),Q),iff(P,neg(Q)))],
        5: [(conj(disj(P,Q),disj(P,R)),disj(conj(P,Q),R)),
            (imp(conj(P,Q),R),iff(P,disj(Q,R))),
            (neg(disj(P,conj(Q,R))),conj(neg(P),disj(Q,R))),
            (iff(imp(P,Q),R),imp(P,conj(Q,R))),
            (disj(conj(P,neg(Q)),R),conj(imp(P,Q),neg(R)))],
    }
    for kind, forms in formula_pairs.items():
        for (f,g), values in zip(forms,assignments):
            p,q,r = values
            text = f"Se dau p = {truth(p)}, q = {truth(q)}"
            if kind == 5: text += f", r = {truth(r)}"
            text += f". Evaluați {display(f)} și {display(g)}."
            pair("3.1",kind,text,evaluate(f,*values),evaluate(g,*values),
                 f"Aplicând tabelele operatorilor din interior spre exterior, obținem "
                 f"{display(f)} = {truth(evaluate(f,*values))} și {display(g)} = {truth(evaluate(g,*values))}. "
                 "¬ inversează valoarea; ∧ cere ambele valori adevărate; ∨ cere cel puțin una; "
                 "⇒ este falsă numai pentru A⇒F; ⇔ este adevărată când valorile coincid.")

    tautologies = [disj(P,neg(P)),neg(conj(P,neg(P))),imp(P,P),
                   iff(neg(neg(P)),P),imp(conj(P,Q),P)]
    for i,f in enumerate(tautologies,1):
        assert all(signature(f))
        wrong = [g for g in [P,neg(P),conj(P,Q),iff(P,Q)] if not all(signature(g))][:3]
        add("3.1",6,f"Care formulă este o tautologie? Setul {i}.",display(f),[display(g) for g in wrong],
            f"{display(f)} este adevărată în toate cele opt evaluări ale lui p, q, r. "
            "Celelalte formule admit evaluări false; o tautologie este adevărată indiferent de valorile propozițiilor.")

    inference = [(conj(imp(P,Q),P),Q,"Modus ponens"),
                 (conj(imp(P,Q),neg(Q)),neg(P),"Modus tollens"),
                 (conj(imp(P,Q),imp(Q,R)),imp(P,R),"Tranzitivitatea implicației"),
                 (conj(disj(P,Q),neg(P)),Q,"Silogism disjunctiv"),
                 (conj(P,Q),P,"Eliminarea conjuncției")]
    for premise, conclusion, name in inference:
        allowed = [v for v in EVALUATIONS if evaluate(premise,*v)]
        assert allowed and all(evaluate(conclusion,*v) for v in allowed)
        wrong = [f for f in pool if any(not evaluate(f,*v) for v in allowed)][:3]
        add("3.1",7,f"Știind că {display(premise)} este adevărată, care concluzie este obligatoriu adevărată?",
            display(conclusion),[display(f) for f in wrong],
            f"{name}: din ipoteza {display(premise)} rezultă {display(conclusion)}. "
            "Verificarea tuturor evaluărilor în care ipoteza este adevărată confirmă concluzia; fiecare altă variantă are un contraexemplu.")

    reconstructions = [(disj(P,Q),False),(conj(P,Q),True),(imp(P,Q),False),
                       (conj(neg(P),Q),True),(conj(P,neg(Q)),True)]
    for f, desired in reconstructions:
        solutions = [(p,q) for p,q in product([False,True],repeat=2) if evaluate(f,p,q,False)==desired]
        assert len(solutions)==1
        p,q = solutions[0]
        pair("3.1",8,f"Dacă {display(f)} este {truth(desired).lower()}, ce valori au p și q?",p,q,
             f"Singura pereche compatibilă cu tabelul de adevăr este p = {truth(p)}, q = {truth(q)}.")

    laws = [(disj(P,conj(Q,R)),conj(disj(P,Q),disj(P,R))),
            (conj(P,disj(Q,R)),disj(conj(P,Q),conj(P,R))),
            (imp(P,Q),disj(neg(P),Q)),(iff(P,Q),conj(imp(P,Q),imp(Q,P))),
            (disj(P,conj(P,Q)),P)]
    for f,g in laws:
        equivalent("3.1",9,f"Care formulă este echivalentă logic cu {display(f)}?",f,g,
                   f"Legea de calcul dă {display(f)} ⇔ {display(g)}. Cele două coloane coincid în toate evaluările.")

    demorgan = [(neg(conj(P,Q)),disj(neg(P),neg(Q))),
                (neg(disj(P,Q)),conj(neg(P),neg(Q))),
                (neg(disj(disj(P,Q),R)),conj(conj(neg(P),neg(Q)),neg(R))),
                (neg(conj(conj(P,Q),R)),disj(disj(neg(P),neg(Q)),neg(R))),
                (neg(conj(P,disj(Q,R))),disj(neg(P),conj(neg(Q),neg(R))))]
    for f,g in demorgan:
        equivalent("3.1",10,f"Aplicând legile lui De Morgan, cu ce este echivalentă {display(f)}?",f,g,
                   "Negația schimbă ∧ în ∨ și ∨ în ∧ și neagă fiecare operand. "
                   f"Rezultatul este {display(g)}; echivalența este verificată pe toate evaluările.")

    for m,n,b,c,x0 in [(2,2,1,3,0),(1,-1,0,2,1),(3,1,-2,0,0),(-2,-2,4,1,2),(0,2,1,-1,1)]:
        parallel = m==n and b!=c
        intersects = m!=n and m*x0+b==n*x0+c
        pair("3.1",11,f"Dreptele d₁: y = {m}x + ({b}) și d₂: y = {n}x + ({c}). "
             f"Fie p: «dreptele sunt paralele distincte» și q: «se intersectează într-un singur punct cu abscisa {x0}». "
             "Evaluați p ∨ q și p ⇒ q.",parallel or intersects,(not parallel) or intersects,
             f"Pantele sunt {m} și {n}; termenii liberi sunt {b} și {c}. "
             f"La x = {x0}, ordonatele sunt {m*x0+b} și {n*x0+c}. "
             f"Rezultă p = {truth(parallel)}, q = {truth(intersects)}, apoi aplicăm tabelele pentru ∨ și ⇒.")

    for a,b,c in [(1,2,3),(2,0,4),(0,3,6),(0,0,0),(0,0,1)]:
        p = b!=0 or (a==0 and c==0)
        q = b==0 and (a!=0 or c==0)
        pair("3.1",12,f"În ℝ, fie P: ∀x ∃y, {a}x + {b}y = {c}, și "
             f"Q: ∃x ∀y, {a}x + {b}y = {c}. Evaluați P și Q.",p,q,
             "În P, dacă coeficientul lui y este nenul, putem alege y în funcție de x; dacă este zero, "
             "egalitatea trebuie să fie identică în x. În Q, egalitatea pentru orice y impune coeficientul lui y zero, "
             f"apoi trebuie să existe x. Rezultă P = {truth(p)} și Q = {truth(q)}.")

    # 3.2: mulțimi finite pentru calcule, tabele de apartenență pentru identități.
    for shift in range(5):
        u=set(range(shift,shift+7)); a={shift,shift+2,shift+4}; b={shift+2,shift+3,shift+5}
        defs=f"În universul U = {set_text(u)}, mulțimile de adevăr ale lui p și q sunt A = {set_text(a)}, B = {set_text(b)}. "
        for kind, label, answer in [(1,"¬p(x)",u-a),(2,"p(x) ∨ q(x)",a|b),(3,"p(x) ∧ q(x)",a&b)]:
            operation={1:"complementul U ∖ A",2:"reuniunea A ∪ B",3:"intersecția A ∩ B"}[kind]
            set_question(kind,defs+f"Care este mulțimea de adevăr a lui {label}?",answer,u,
                         f"Formula corespunde operației {operation}; rezultă {set_text(answer)}.")
        small={shift,shift+2}; large=small|{shift+4}
        pair("3.2",4,f"În U = {set_text(u)}, p are mulțimea de adevăr {set_text(small)}, iar q are "
             f"mulțimea de adevăr {set_text(large)}. Evaluați ∀x∈U (p(x)⇒q(x)) și ∀x∈U (q(x)⇒p(x)).",
             True,False,f"Prima mulțime este inclusă în a doua. Reciproca este falsă pentru x = {shift+4}, care verifică q, dar nu p.")

    for a in range(1,6):
        add("3.2",5,f"În ℝ, p(x): x² = {a*a}. Care predicat q(x) are exact aceeași mulțime de adevăr?",
            f"x = {a} sau x = {-a}",[f"x = {a}",f"x > {a}",f"x² = {-a*a}"],
            f"x² = {a*a} ⇔ (x − {a})(x + {a}) = 0 ⇔ x = {a} sau x = {-a}. "
            "Egalitatea mulțimilor de adevăr exprimă echivalența predicatelor.")

    for m in range(2,7):
        e=set(range(m+1)); pairs={(x,y) for x in e for y in e if x+y==m and x<y}
        fmt=lambda s: "{"+"; ".join(f"({x}; {y})" for x,y in sorted(s))+"}" if s else "∅"
        candidates=[{(y,x) for x,y in pairs},{(x,y) for x in e for y in e if x+y==m},set(),{(0,0)}]
        wrong=list(dict.fromkeys(fmt(s) for s in candidates if s!=pairs))[:3]
        add("3.2",6,f"Pe E = {set_text(e)}, fie p(x,y): x + y = {m}, q(x,y): x < y. "
            "Care este mulțimea de adevăr a lui p ∧ q în E×E?",fmt(pairs),wrong,
            f"Enumerăm perechile cu sumă {m} și păstrăm numai perechile cu prima componentă mai mică: {fmt(pairs)}.")

    for d in range(2,7):
        pair("3.2",7,f"Pentru n ∈ ℤ, fie p(n): {d*d} divide n, q(n): {d} divide n. "
             "Evaluați ∀n (p(n)⇒q(n)) și ∀n (q(n)⇒p(n)).",True,False,
             f"Dacă n = {d*d}k, atunci n = {d}·({d}k). Reciproca este infirmată de n = {d}, "
             f"divizibil cu {d}, dar nu cu {d*d}.")

    for d,e in [(2,3),(3,5),(4,7),(5,6),(6,7)]:
        for kind,symbol,correct,wrong in [
            (8,"∪","p(x) ∨ q(x)",["p(x) ∧ q(x)","¬p(x) ∧ ¬q(x)","p(x) ∧ ¬q(x)"]),
            (9,"∩","p(x) ∧ q(x)",["p(x) ∨ q(x)","¬p(x) ∧ ¬q(x)","p(x) ∧ ¬q(x)"])]:
            add("3.2",kind,f"În ℤ, A este mulțimea multiplilor lui {d}, B a multiplilor lui {e}; "
                f"p(x): x∈A, q(x): x∈B. Ce condiție descrie apartenența la A {symbol} B?",correct,wrong,
                f"Apartenența la {symbol} se traduce prin {'«sau» inclusiv' if kind==8 else '«și»'}. "
                f"Condiția este {correct}. Valorile divizibile cu unul singur dintre {d}, {e} disting operațiile.")

    for shift in range(5):
        u=set(range(shift,shift+8)); a={shift,shift+1,shift+3}; b={shift+1,shift+2,shift+3,shift+5}
        set_question(10,f"În U = {set_text(u)}, p are mulțimea de adevăr A = {set_text(a)}, iar q are B = {set_text(b)}. "
                     "Ce mulțime de adevăr are q(x) ∧ ¬p(x)?",b-a,u,
                     f"q ∧ ¬p înseamnă apartenență la B și neapartenență la A, deci B ∖ A = {set_text(b-a)}.")

    for m in range(3,8):
        e=set(range(-m,m+1)); sol={x for x in e if x*x<=m*m and x%2==0}
        count=len(sol)
        add("3.2",11,f"Fie E = {set_text(e)} și p(x): «x² ≤ {m*m} și x este par». "
            "Care este cardinalul mulțimii de adevăr a lui p pe E?",count,[count-1,count+1,count+2],
            f"Elementele care verifică ambele condiții sunt {set_text(sol)}; sunt {count} elemente.")

    for k,b in [(0,3),(1,5),(-2,2),(2,7),(-3,1)]:
        add("3.2",12,f"Fie t ∈ ℝ, t ≥ {k}, A = [{k}; t] și B = [{k-1}; {b}]. "
            "Pentru care t este adevărată implicația ∀x∈ℝ (x∈A ⇒ x∈B)?",
            f"t ∈ [{k}; {b}]",[f"t ∈ ({k}; {b})",f"t ∈ [{k}; {b+1}]",f"t ∈ [{b}; +∞)"],
            f"Implicația este adevărată exact când A ⊆ B. Capătul stâng {k} aparține deja lui B; "
            f"capătul drept trebuie să satisfacă t ≤ {b}. Împreună cu t ≥ {k}, rezultă intervalul închis indicat.")

    # Identități de mulțimi: funcția booleană indică apartenența elementului arbitrar.
    def identity(kind, left, correct, wrong_candidates, explanation):
        left_text,lf=left; ct,cf=correct
        sig=lambda f: tuple(f(*v) for v in EVALUATIONS)
        assert sig(lf)==sig(cf)
        wrong=[]
        for text,f in wrong_candidates:
            if sig(f)!=sig(lf) and text not in wrong: wrong.append(text)
            if len(wrong)==3: break
        assert len(wrong)==3
        add("3.2",kind,f"Pentru mulțimi arbitrare A, B, C, care expresie este întotdeauna egală cu {left_text}?",
            ct,wrong,explanation+" Identitatea este verificată pentru toate cele opt cazuri de apartenență la A, B, C.")

    set_pool=[("A",lambda a,b,c:a),("B",lambda a,b,c:b),("C",lambda a,b,c:c),
              ("A ∩ B",lambda a,b,c:a and b),("A ∪ B",lambda a,b,c:a or b),
              ("A ∖ B",lambda a,b,c:a and not b),("B ∖ A",lambda a,b,c:b and not a),
              ("A ∩ B ∩ C",lambda a,b,c:a and b and c),("∅",lambda a,b,c:False)]
    identities=[
        (("A ∪ (B ∖ A)",lambda a,b,c:a or (b and not a)),("A ∪ B",lambda a,b,c:a or b),"Elementele deja în A și cele din B care nu sunt în A alcătuiesc A ∪ B."),
        (("A ∩ (B ∪ C)",lambda a,b,c:a and (b or c)),("(A ∩ B) ∪ (A ∩ C)",lambda a,b,c:(a and b) or (a and c)),"Aplicăm distributivitatea intersecției față de reuniune."),
        (("A ∪ (B ∩ C)",lambda a,b,c:a or (b and c)),("(A ∪ B) ∩ (A ∪ C)",lambda a,b,c:(a or b) and (a or c)),"Aplicăm distributivitatea reuniunii față de intersecție."),
        (("(A ∖ B) ∪ (A ∩ B)",lambda a,b,c:(a and not b) or (a and b)),("A",lambda a,b,c:a),"Separăm elementele lui A după apartenența sau neapartenența la B."),
        (("A ∩ (A ∪ B)",lambda a,b,c:a and (a or b)),("A",lambda a,b,c:a),"Legea absorbției păstrează exact elementele lui A."),
    ]
    for left,correct,exp in identities: identity(13,left,correct,set_pool,exp)

    for shift in range(5):
        a={shift,shift+1,shift+2}; b={shift+1,shift+3,shift+4}; union=a|b; inter=a&b
        set_question(14,f"Se cunosc A = {set_text(a)}, A∪B = {set_text(union)} și A∩B = {set_text(inter)}. "
                     "Care este mulțimea B?",b,union,
                     f"B = (A∩B) ∪ ((A∪B) ∖ A) = {set_text(b)}. Datele fixează atât elementele din A, cât și pe cele din afara lui A.")

    differences=[
        (("(A ∖ B) ∖ C",lambda a,b,c:a and not b and not c),("A ∖ (B ∪ C)",lambda a,b,c:a and not (b or c)),"Excludem atât elementele din B, cât și pe cele din C."),
        (("A ∖ (B ∖ C)",lambda a,b,c:a and not (b and not c)),("(A ∖ B) ∪ (A ∩ C)",lambda a,b,c:(a and not b) or (a and c)),"Negăm condiția «în B și nu în C», apoi aplicăm distributivitatea."),
        (("(A ∖ C) ∖ (B ∖ C)",lambda a,b,c:(a and not c) and not (b and not c)),("A ∖ (B ∪ C)",lambda a,b,c:a and not (b or c)),"După excluderea lui C, eliminarea lui B∖C elimină exact elementele rămase din B."),
        (("(A ∪ B) ∖ C",lambda a,b,c:(a or b) and not c),("(A ∖ C) ∪ (B ∖ C)",lambda a,b,c:(a and not c) or (b and not c)),"Diferența față de C se distribuie peste reuniune."),
        (("A ∖ (B ∩ C)",lambda a,b,c:a and not (b and c)),("(A ∖ B) ∪ (A ∖ C)",lambda a,b,c:(a and not b) or (a and not c)),"Legea lui De Morgan transformă neapartenența la B∩C în neapartenență la cel puțin una dintre mulțimi."),
    ]
    for left,correct,exp in differences: identity(15,left,correct,set_pool,exp)

    # 3.3: negarea cuantificatorilor, necesitate, suficiență.
    for a in range(1,6):
        add("3.3",1,f"Fie f: ℝ→ℝ o funcție arbitrară. Care este negarea propoziției ∀x∈ℝ, f(x) > {a}?",
            f"∃x∈ℝ, f(x) ≤ {a}",[f"∀x∈ℝ, f(x) ≤ {a}",f"∃x∈ℝ, f(x) < {a}",f"∀x∈ℝ, f(x) > {a}"],
            "Negarea lui «pentru orice» este «există», iar negarea inegalității stricte > este ≤. "
            "Funcția constantă egală cu pragul arată de ce nu putem înlocui ≤ cu <.")
        add("3.3",2,f"Fie f: ℝ→ℝ o funcție arbitrară. Care este negarea propoziției ∃x∈ℝ, f(x) = {a}?",
            f"∀x∈ℝ, f(x) ≠ {a}",[f"∃x∈ℝ, f(x) ≠ {a}",f"∀x∈ℝ, f(x) = {a}",f"∃x∈ℝ, f(x) < {a}"],
            "Negarea unei existențe afirmă că niciun argument nu verifică egalitatea: pentru orice x, f(x) este diferit de valoarea indicată.")

    for n in range(2,7):
        add("3.3",3,f"Care este negarea afirmației «Ecuația f(x) = 0 are cel puțin {n} soluții întregi distincte»?",
            f"Ecuația are cel mult {n-1} soluții întregi distincte.",
            [f"Ecuația are exact {n-1} soluții întregi distincte.",f"Ecuația are cel puțin {n+1} soluții întregi distincte.",
             f"Ecuația are cel mult {n-2} soluții întregi distincte."],
            f"Afirmația inițială cere existența a {n} întregi distincți care sunt soluții. Negarea exclude un asemenea grup: "
            f"numărul soluțiilor este mai mic decât {n}, adică cel mult {n-1}; poate fi și zero.")

    quantifiers=[
        ("∀x∈E ∃y∈E, P(x,y)","∃x∈E ∀y∈E, ¬P(x,y)",
         ["∀x∈E ∃y∈E, ¬P(x,y)","∀x∈E ∀y∈E, ¬P(x,y)","∃x∈E ∀y∈E, P(x,y)"]),
        ("∃x∈E ∀y∈E, P(x,y)","∀x∈E ∃y∈E, ¬P(x,y)",
         ["∃x∈E ∀y∈E, ¬P(x,y)","∀x∈E ∀y∈E, ¬P(x,y)","∀x∈E ∃y∈E, P(x,y)"]),
        ("∀x∈E ∀y∈E, P(x,y)","∃x∈E ∃y∈E, ¬P(x,y)",
         ["∀x∈E ∀y∈E, ¬P(x,y)","∃x∈E ∀y∈E, ¬P(x,y)","∃x∈E ∃y∈E, P(x,y)"]),
        ("∃x∈E ∃y∈E, P(x,y)","∀x∈E ∀y∈E, ¬P(x,y)",
         ["∃x∈E ∃y∈E, ¬P(x,y)","∀x∈E ∃y∈E, ¬P(x,y)","∀x∈E ∀y∈E, P(x,y)"]),
        ("∀x∈E ∃y∈E ∀z∈E, P(x,y,z)","∃x∈E ∀y∈E ∃z∈E, ¬P(x,y,z)",
         ["∀x∈E ∃y∈E ∀z∈E, ¬P(x,y,z)","∃x∈E ∃y∈E ∃z∈E, ¬P(x,y,z)","∃x∈E ∀y∈E ∃z∈E, P(x,y,z)"]),
    ]
    for text,correct,wrong in quantifiers:
        add("3.3",4,f"Pentru un predicat arbitrar P pe o mulțime nevidă E, care este negarea lui {text}?",correct,wrong,
            "Păstrăm ordinea variabilelor, schimbăm fiecare ∀ în ∃ și fiecare ∃ în ∀, apoi negăm predicatul. "
            "Schimbarea ordinii cuantificatorilor nu este permisă în general.")

    for e,c in [({0,1,2},2),({0,1,2},1),({-2,-1,0,1,2},0),({1,2,3},0),({2},4)]:
        p=all(any(x+y==c for y in e) for x in e)
        q=any(all(x+y==c for x in e) for y in e)
        missing=[x for x in sorted(e) if c-x not in e]
        exp=f"Pentru P, martorul necesar este y = {c} − x. "
        exp+=f"Pentru x = {missing[0]}, acest martor nu aparține lui E. " if missing else "El aparține lui E pentru fiecare x din E. "
        exp+="Pentru Q, un singur y trebuie să funcționeze pentru toate valorile lui x; într-o mulțime cu cel puțin două valori distincte ale lui x, acest lucru este imposibil. " if len(e)>1 else f"Mulțimea are un singur element; alegerea x = y = 2 verifică suma {c}. "
        pair("3.3",5,f"Fie E = {set_text(e)}. Evaluați P: ∀x∈E ∃y∈E, x+y={c}, și "
             f"Q: ∃y∈E ∀x∈E, x+y={c}.",p,q,exp)

    for d in range(3,8):
        add("3.3",6,f"Pentru n ∈ ℤ, care condiție este suficientă pentru ca n să fie divizibil cu {d}?",
            f"n este divizibil cu {d*d}.",[f"n = {d+1}.",f"n = {d-1}.","n = 1."],
            f"Dacă n = {d*d}k, atunci n = {d}·({d}k), deci {d} divide n. Celelalte valori propuse nu sunt divizibile cu {d}.")
        add("3.3",7,f"Pentru n ∈ ℤ, care condiție este necesară pentru ca n să fie divizibil cu {d*d}?",
            f"n este divizibil cu {d}.",[f"n este divizibil cu {d**3}.","n este impar.","n > 0."],
            f"Orice multiplu al lui {d*d} este multiplu al lui {d}. Divizibilitatea cu {d**3} nu este necesară "
            f"(n = {d*d}); nici imparitatea (n = {2*d*d}), nici pozitivitatea (n = 0).")

    for a,b in [(0,2),(1,3),(-2,4),(3,1),(-1,5)]:
        add("3.3",8,f"Pentru x ∈ ℝ, care condiție este necesară și suficientă pentru |x − ({a})| = {b}?",
            f"x ∈ {set_text({a-b,a+b})}",[f"x = {a+b}",f"x ∈ ({a-b}; {a+b})",f"x < {a-b}"],
            f"|x − ({a})| = {b} ⇔ x − ({a}) = {b} sau x − ({a}) = {-b}. "
            f"Rezultă exact x ∈ {set_text({a-b,a+b})}; ambele implicații sunt valabile.")

    labels=["Suficientă, dar nu necesară.","Necesară, dar nu suficientă.","Necesară și suficientă.","Nici necesară, nici suficientă."]
    for d in range(2,7):
        add("3.3",9,f"Pentru n ∈ ℤ, ce relație are condiția «{d*d} divide n» cu proprietatea «{d} divide n»?",
            labels[0],labels[1:],f"Prima condiție implică proprietatea, deci este suficientă. "
            f"Nu este necesară: n = {d} verifică proprietatea, dar nu este divizibil cu {d*d}.")

    inclusions=[
        ("A ⊆ B ∖ C","x∈A și (x∉B sau x∈C)",lambda a,b,c:a and (not b or c)),
        ("A ⊆ B","x∈A și x∉B",lambda a,b,c:a and not b),
        ("A∩B ⊆ C","x∈A și x∈B și x∉C",lambda a,b,c:a and b and not c),
        ("A ⊆ B∪C","x∈A și x∉B și x∉C",lambda a,b,c:a and not b and not c),
        ("A∖B ⊆ C","x∈A și x∉B și x∉C",lambda a,b,c:a and not b and not c),
    ]
    witness_pool=[("x∈A și x∈B",lambda a,b,c:a and b),
                  ("x∉A și x∈B",lambda a,b,c:not a and b),
                  ("x∈C",lambda a,b,c:c),
                  ("x∈A și x∉B",lambda a,b,c:a and not b)]
    for statement,condition,fn in inclusions:
        sig=lambda f: tuple(f(*v) for v in EVALUATIONS)
        wrong=["Există x pentru care "+t+"." for t,f in witness_pool if sig(f)!=sig(fn)][:3]
        add("3.3",10,f"Pentru mulțimi arbitrare A, B, C din același univers, care este negarea incluziunii {statement}?",
            "Există x pentru care "+condition+".",wrong,
            "O incluziune este falsă exact dacă există un element al mulțimii din stânga care nu aparține celei din dreapta. "
            f"Aplicând regulile pentru reuniune, intersecție și diferență, condiția martorului este: {condition}.")

    expected={(f"A1.{s}",k):5 for s,names in NAMES.items() for k in range(1,len(names)+1)}
    assert Counter((q["catalog"]["section"],q["catalog"]["type"]) for q in result)==expected
    assert len({q["text"] for q in result})==len(result)==185
    return result


def main():
    path=Path(__file__).resolve().parents[1]/"clasa_9"/"clasa_9_u01_l04_operatii_logice_elementare_si_legi_de_calcul.json"
    payload={"title":"Operații logice elementare și legi de calcul",
             "description":"Clasa a 9-a · Mulțimi și logică matematică",
             "difficulty":"medium","questions":build_questions()}
    path.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(f"Scrise {len(payload['questions'])} grile: {path.name}")


if __name__=="__main__": main()
