"""Verifică independent soluțiile și grilele pentru modulul unui număr real.

Rulează din rădăcina backendului cu Python; nu necesită Django.
Pentru ecuații/inecuații compară mulțimile declarate cu predicatele inițiale,
pe o rețea rațională și pe toate capetele/valorile din variantele propuse.
"""
import json
import random
import re
import sys
from collections import Counter
from fractions import Fraction as F
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "data/quizzes/clasa_9/clasa_9_u01_l01_multimea_numerelor_reale_operatii_ordonare_modul_si_aproximari.json"


def correct(question):
    return next(o["text"] for o in question["options"] if o["is_correct"])


def fraction(text):
    return F(text.strip().replace("−", "-"))


def contains(solution, x):
    if solution == "R":
        return True
    if solution == "∅":
        return False
    for part in solution.split(" ∪ "):
        if part.startswith("{"):
            if "…" in part:
                values = [fraction(v) for v in part[1:-1].split(";") if v.strip() != "…"]
                start = values[-1]
                for v in reversed(values[:-1]):
                    if v == start-1:
                        start = v
                    else:
                        break
                if x in values or (x.denominator == 1 and x >= start):
                    return True
                continue
            if x in {fraction(v) for v in part[1:-1].split(";")}:
                return True
        else:
            lo, hi = part[1:-1].split(";")
            lower = True if "∞" in lo else x >= fraction(lo) if part[0] == "[" else x > fraction(lo)
            upper = True if "∞" in hi else x <= fraction(hi) if part[-1] == "]" else x < fraction(hi)
            if lower and upper:
                return True
    return False


PREDICATES = {
    2: [lambda x: abs(3*x-1)==5, lambda x: abs(2*x+3)==1, lambda x: abs(x-4)==0, lambda x: abs(5*x-2)==-3],
    3: [lambda x: abs(x*x-1)+abs(2*x-2)==0, lambda x: abs(x-2)+abs(x+2)==0,
        lambda x: abs((x-3)*(x+1))+abs(x+1)==0, lambda x: abs(x*x-9)+abs(x-3)==0],
    4: [lambda x: abs(2*x-1)==3, lambda x: abs(3*x+1)==2, lambda x: abs(2*x+1)==2,
        lambda x: abs(x)!=2 and (abs(x)+1)/(abs(x)-2)==2],
    5: [lambda x: abs(3*x-4)<0, lambda x: abs(x+2)>=0, lambda x: abs(2*x-1)>-3, lambda x: abs(x-3)<=0],
    6: [lambda x: abs(2*x+8)<2, lambda x: abs(3*x-6)<=9, lambda x: abs(x+1)<4, lambda x: abs(2*x-1)<=3],
    7: [lambda x: abs(2*x-5)>1, lambda x: abs(3*x+3)>=6, lambda x: abs(x-2)>4, lambda x: abs(2*x+4)>=2],
    8: [lambda x: abs(x-3)<2, lambda x: abs(2*x-5)<=3, lambda x: abs(x+1)<3, lambda x: abs(3*x-2)>4],
    9: [lambda x: 3*abs(x+1)-5==7, lambda x: 2*abs(x-2)+1==9, lambda x: 5*abs(x+3)+2==-3],
    10: [lambda x: abs(x-1)**2-3*abs(x-1)+2==0, lambda x: abs(x+2)**2+abs(x+2)-2==0,
         lambda x: 2*abs(x)**2-5*abs(x)+2==0],
    11: [lambda x: abs(x)*(abs(x-1)-2)<0, lambda x: abs(x-5)*(abs(x)-3)<=0, lambda x: abs(x+1)*(abs(x)-2)>0],
    12: [lambda x: abs(x)!=3 and (abs(x)-1)/(abs(x)-3)<0,
         lambda x: abs(x)!=1 and (abs(x)-2)/(abs(x)-1)>=0,
         lambda x: abs(x)!=2 and 1/(2-abs(x))>0],
    16: [lambda x: x<0 and abs(x)+2*x==-6, lambda x: x<0 and abs(x-1)+x==1, lambda x: x<0 and abs(x+2)==-x],
    24: [lambda x: 2<=x<=4 and abs(x-2)+abs(x-4)==2,
         lambda x: 2<=x<=4 and abs(x-1)-abs(x-5)==0,
         lambda x: -1<=x<=2 and abs(x+1)+abs(x-2)==4],
}


def main():
    payload = json.loads(PATH.read_text(encoding="utf-8"))
    questions = [q for q in payload["questions"] if q.get("catalog", {}).get("section") == "A1.1.3"]
    assert len(questions) == 80
    assert Counter(q["catalog"]["type"] for q in questions) == {i: 4 if i<=8 else 3 for i in range(1,25)}
    by = {(q["catalog"]["type"], q["catalog"]["variant"]): q for q in questions}
    for q in questions:
        assert len(q["options"]) == len({o["text"] for o in q["options"]}) == 4
        assert sum(o["is_correct"] for o in q["options"]) == 1
        assert q["format"] == "grid" and q["explanation"]

    checked = 0
    for kind, functions in PREDICATES.items():
        for variant, predicate in enumerate(functions, 1):
            q = by[kind, variant]
            samples = {F(i,6) for i in range(-120,121)} | {F(-100), F(100)}
            # Incluse explicit toate rădăcinile/capetele propuse, chiar fracționare.
            for option in q["options"]:
                for token in re.findall(r"[−-]?\d+(?:/\d+)?", option["text"]):
                    endpoint = fraction(token)
                    samples.update([endpoint-F(1,100), endpoint, endpoint+F(1,100)])
            samples = sorted(samples)
            expected = []
            for x in samples:
                domain = x.denominator==1 if kind==4 else x.denominator==1 and x>=0 if kind==8 else True
                expected.append(bool(domain and predicate(x)))
            assert [contains(correct(q),x) for x in samples] == expected, (kind,variant,"răspuns")
            for option in q["options"]:
                if not option["is_correct"]:
                    assert any(contains(option["text"],x)!=target for x,target in zip(samples,expected)), (kind,variant,"distractor",option)
            checked += 1

    for v,a,total in [(1,4,36),(2,2,18),(3,1,9)]:
        # x≤total și 2^n≤total sunt consecințe ale nenegativității termenilor.
        pairs = [(x,n) for x in range(total+1) for n in range(total.bit_length()+1) if x+abs(x-a)+2**n==total]
        assert F(correct(by[13,v])) == len(pairs)
    for b in [F(-2),F(-3,2),F(-1)]:
        assert b+2+abs(b-3)==5
    for a in [F(1),F(3,2),F(2)]:
        assert abs(a-4)==4-a
    for t in [F(-3),F(-5,2),F(-2)]:
        assert 2*((t+4)/2)+abs(t+1)==3
    assert [F(correct(by[19,v])) for v in [1,2,3]] == [abs(2*2-3*(-1)),abs(3*1+2*4),abs(2-2*(-1)+3*2)]
    assert [F(correct(by[20,v])) for v in [1,2]] == [10,6]
    assert [F(correct(by[21,v])) for v in [1,2,3]] == [4,6,1]
    rng = random.Random(24)
    for _ in range(300):
        x,y = rng.uniform(-.999,.999),rng.uniform(-.999,.999)
        assert 1+x*y>0 and abs((x+y)/(1+x*y))<1
        u,v = x/2,y/2
        assert 1+4*u*v>0 and abs((u+v)/(1+4*u*v))<.5
    sys.path.insert(0,str(ROOT / "data/quizzes/generators"))
    from gen_clasa_9_numere_reale_operatii import build_questions
    assert build_questions() == payload["questions"]
    print(f"80 grile / 24 tipuri. {checked} ecuații/inecuații verificate pe valori raționale, capete și poli; distractori verificați. Generator sincronizat.")


if __name__ == "__main__":
    main()
