"""Audit independent al celor 315 grile, citind enunțurile și toate opțiunile.

Nu importă formulele sau răspunsurile din generator. Verifică răspunsuri
prin enumerare, aritmetică exactă și identități polinomiale. Verificările
finite susțin exemplele concrete; nu înlocuiesc demonstrațiile universale.
"""
import ast
import json
import re
from collections import Counter
from fractions import Fraction as F
from itertools import combinations, permutations, product
from math import comb, factorial, gcd, isqrt
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data/quizzes/clasa_9/clasa_9_u01_l05_rationamente_logice_inductia_matematica_si_probleme_de_numarare.json"


def groups(pattern, text):
    match = re.search(pattern, text)
    assert match, ("Enunț nerecunoscut", pattern, text)
    return tuple(map(int, match.groups()))


def scalar(value): return F(value.replace("−", "-"))
def pair(value): return tuple(map(int, re.findall(r"-?\d+", value.replace("−", "-"))))


# Aritmetică polinomială exactă pentru certificarea pasului inductiv, nu doar
# pentru verificarea formulei în câteva puncte.
def trim(p):
    p = list(map(F, p))
    while len(p)>1 and p[-1]==0: p.pop()
    return p


def plus(a,b):
    return trim([(a[i] if i<len(a) else 0)+(b[i] if i<len(b) else 0) for i in range(max(len(a),len(b)))])


def times(a,b):
    p=[F(0)]*(len(a)+len(b)-1)
    for i,x in enumerate(a):
        for j,y in enumerate(b): p[i+j]+=x*y
    return trim(p)


def power(a,n):
    assert n>=0
    p=[F(1)]
    for _ in range(n): p=times(p,a)
    return p


def shift(p):
    result=[F(0)]
    for k,c in enumerate(p):
        result=plus(result,[c*comb(k,j) for j in range(k+1)])
    return result


def expression(text):
    text=text.split("=",1)[-1].replace("−","-").replace(" ","")
    for symbol,exponent in [("²",2),("³",3),("⁴",4),("⁵",5)]: text=text.replace(symbol,"**"+str(exponent))
    text=text.replace("ⁿ","**n").replace("^","**")
    tokens=re.findall(r"\d+|n|\*\*|[()+*/-]",text)
    result=[]
    for token in tokens:
        if result and (result[-1].isdigit() or result[-1] in {"n",")"}) and (token.isdigit() or token in {"n","("}):
            result.append("*")
        result.append(token)
    return ast.parse("".join(result),mode="eval").body


def polynomial(text):
    def visit(node):
        if isinstance(node,ast.Constant): return [F(node.value)]
        if isinstance(node,ast.Name) and node.id=="n": return [F(0),F(1)]
        if isinstance(node,ast.UnaryOp) and isinstance(node.op,ast.USub): return [-v for v in visit(node.operand)]
        assert isinstance(node,ast.BinOp),ast.dump(node)
        a,b=visit(node.left),visit(node.right)
        if isinstance(node.op,ast.Add): return plus(a,b)
        if isinstance(node.op,ast.Sub): return plus(a,[-x for x in b])
        if isinstance(node.op,ast.Mult): return times(a,b)
        if isinstance(node.op,ast.Div):
            assert len(b)==1 and b[0]!=0
            return trim([x/b[0] for x in a])
        if isinstance(node.op,ast.Pow):
            assert len(b)==1 and b[0].denominator==1
            return power(a,int(b[0]))
        raise AssertionError(ast.dump(node))
    return trim(visit(expression(text)))


def at(p,n): return sum(c*n**k for k,c in enumerate(p))


def numeric_expression(text,n):
    def visit(node):
        if isinstance(node,ast.Constant): return F(node.value)
        if isinstance(node,ast.Name) and node.id=="n": return F(n)
        if isinstance(node,ast.UnaryOp) and isinstance(node.op,ast.USub): return -visit(node.operand)
        assert isinstance(node,ast.BinOp)
        a,b=visit(node.left),visit(node.right)
        if isinstance(node.op,ast.Add): return a+b
        if isinstance(node.op,ast.Sub): return a-b
        if isinstance(node.op,ast.Mult): return a*b
        if isinstance(node.op,ast.Div): return a/b
        if isinstance(node.op,ast.Pow):
            assert b.denominator==1
            return a**int(b)
        raise AssertionError(ast.dump(node))
    return visit(expression(text))


def prime_exponent(value,p):
    exponent=0
    while value%p==0:
        exponent+=1
        value//=p
    return exponent


def assert_tiling(pieces,side):
    assert all(0<=x and 0<=y and x+s<=side and y+s<=side for x,y,s in pieces)
    assert sum(s*s for x,y,s in pieces)==side*side
    for (x,y,s),(xx,yy,ss) in combinations(pieces,2):
        assert min(x+s,xx+ss)<=max(x,xx) or min(y+s,yy+ss)<=max(y,yy)


def square_base(n):
    if n in {6,8}:
        side=3 if n==6 else 4
        big=side-1
        pieces=[(F(0),F(0),F(big))]+[(F(x),F(y),F(1)) for x in range(side) for y in range(side) if x>=big or y>=big]
    else:
        assert n==7
        side=F(1)
        pieces=[(F(x,2),F(y,2),F(1,2)) for x,y in [(0,1),(1,0),(1,1)]]
        pieces += [(F(x,4),F(y,4),F(1,4)) for x,y in product(range(2),repeat=2)]
    assert len(pieces)==n
    assert_tiling(pieces,side)
    return pieces,side


def zigzag(r,corner):
    # Exemplu concret, monoton în x, al tăieturii simetrice presupuse de enunț.
    ys=[F(0)]+[F((-1)**i,100) for i in range(1,r+1)]+[-F((-1)**i,100) for i in range(r,0,-1)]+[F(0)]
    points=[]
    for i,delta in enumerate(ys):
        x=-1+F(2*i,2*r+1)
        points.append((x,x+delta if corner else delta))
    assert all(points[-1-i]==(-x,-y) for i,(x,y) in enumerate(points))
    assert all(-1<x<1 and -1<y<1 for x,y in points[1:-1])
    for a,b,c in zip(points,points[1:],points[2:]):
        assert (b[0]-a[0])*(c[1]-b[1])!=(b[1]-a[1])*(c[0]-b[0])
    return points


def option_truths(q):
    """Returnează adevărul fiecărei opțiuni, dedus din enunț, fără cheia JSON."""
    s=q["catalog"]["section"]; k=q["catalog"]["type"]; t=q["text"]
    options=[o["text"] for o in q["options"]]
    if s=="A1.4.1":
        if k==1:
            out=[]
            for value in map(scalar,options):
                square=value>=0 and value.denominator==1 and isqrt(int(value))**2==value
                if not square:
                    assert any(isqrt((n*n*value).__floor__())**2!=(n*n*value).__floor__() for n in range(1,101))
                out.append(square)
            return out
        if k==2:
            p,=groups(r"k\^(\d+)",t)
            out=[]
            for option in options:
                poly=polynomial(option)
                delta=plus(shift(poly),[-x for x in poly])
                out.append(at(poly,1)==1 and delta==power([F(1),F(1)],p))
            return out
        if k in {3,5,6,7,8,22}:
            n,=groups(r"\^(\d+)",t)
            if k==3: expected=sum((-1)**(i+1)*i*i for i in range(1,n+1))
            if k==5:
                c,=groups(r"k\((\d+)k",t)
                expected=sum(i*(c*i+1) for i in range(1,n+1))
            if k==6: expected=sum((F(1,i*(i+1)) for i in range(1,n+1)),F(0))
            if k==7: expected=sum((F(1,i*(i+1)*(i+2)) for i in range(1,n+1)),F(0))
            if k==8:
                expected=F(1)
                for i in range(2,n+1): expected*=1-F(1,i*i)
            if k==22:
                value=1
                for i in range(1,n+1): value*=i*(i+1)
                expected=prime_exponent(value,2)
        elif k==4:
            n,=groups(r"⋯\+(\d+)\)",t)
            expected=sum(j for i in range(1,n+1) for j in range(1,i+1))
        elif k==9:
            factors=re.findall(r"\(1\+(\d+)\^(\d+)\)",t)
            expected=1
            for a,b in factors: expected*=1+int(a)**int(b)
            assert len(factors)>=2
        elif k==10:
            a,p=groups(r"(\d+)ⁿ > n\^(\d+)",t)
            expected=max(n for n in range(1,250) if a**n<=n**p)+1
            assert a**expected>expected**p
            # Raportul (1+1/n)^p descrește: certifică pasul pentru toți indicii următori.
            assert F(expected+1,expected)**p<=a
        elif k==11:
            c,=groups(r"ⁿ (\d+)/k²",t); n,=groups(r"∑ₖ₌₂\^(\d+)",t)
            expected=c*(1+sum((F(1,i*(i-1)) for i in range(2,n+1)),F(0)))
            assert sum((F(c,i*i) for i in range(1,n+1)),F(0))<expected
        elif k==12:
            n,=groups(r"la 1 la (\d+)",t)
            assert isqrt(n+1)**2==n+1
            expected=2*(isqrt(n+1)-1)
        elif k==13:
            n,=groups(r"x_(\d+)",t)
            expected=sum(2*i-1 for i in range(1,n+1))
        elif k==14:
            n,=groups(r"\(1\+1/100\)\^(\d+)",t)
            expected=1+F(n,100)
            assert F(101,100)**n>=expected
        elif k==15:
            c,=groups(r"f\(n\)=(\d+)\(n³−n\)",t)
            target=plus(shift([0,-c,0,c]),[0,c,0,-c])
            return [polynomial(o)==target for o in options]
        elif k==16:
            a,=groups(r"a=(\d+)",t)
            expected=a-1
        elif k==17:
            a,b,c=groups(r"dintre (\d+), (\d+), (\d+)",t)
            expected=next(n for n in range(1,a*b*c+1) if n%a==n%b==n%c==0)
        elif k==18:
            a,=groups(r"u₁=√(\d+)",t)
            expected=isqrt(a)+1
            assert (expected-1)**2<a<expected**2 and a+expected<=expected**2
        elif k==19:
            a,=groups(r"x\+1/x=(\d+)",t)
            expected=(a*a-2)**2-2
        elif k==20:
            a,=groups(r"aₙ₊₁=(\d+)aₙ",t)
            actual=[0]
            for _ in range(10): actual.append(a*actual[-1]+a-1)
            return [all(numeric_expression(o,n)==actual[n] for n in range(11)) for o in options]
        elif k==21:
            a,=groups(r"uₙ₊₁=\(uₙ\+(\d+)\)/2",t)
            expected=a
            assert a>=2
        elif k==23:
            a,=groups(r"produsului \((\d+)²\+1²\)",t)
            u,v=a,1
            for c,d in [(2,1),(1,2)]: u,v=u*c-v*d,u*d+v*c
            assert u*u+v*v==(a*a+1)*25
            return [pair(o)==(u,v) for o in options]
        elif k==24:
            if "lui k+4" in t:
                target=4
                n,=groups(r"1²,…,(\d+)²",t)
                required=list(range(n+1,n+5))
                # Certificăm simbolic identitatea blocului, pentru orice n.
                delta=plus(plus(power([1,1],2),[-x for x in power([2,1],2)]),
                           plus([-x for x in power([3,1],2)],power([4,1],2)))
                assert delta==[F(4)]
                bases=[([1,2,3,4,5,6,7],[1,1,-1,1,-1,-1,1]),([1],[1]),
                       ([1,2,3,4],[-1,-1,-1,1]),([1,2,3,4,5],[-1,1,-1,-1,1])]
                assert [sum(s*i*i for i,s in zip(indices,signs)) for indices,signs in bases]==[0,1,2,3]
            else:
                target,=groups(r"întregul (-?\d+)",t)
                n,=groups(r"1²,…,(\d+)²",t)
                required=list(range(1,n+1))
            out=[]
            for o in options:
                terms=re.findall(r"([+−])(\d+)²",o)
                assert sorted(int(value) for sign,value in terms)==required
                out.append(sum((1 if sign=="+" else -1)*int(value)**2 for sign,value in terms)==target)
            return out
        elif k==25:
            target,=groups(r"exact (\d+) pătrate",t)
            out=[]
            for o in options:
                base,steps=pair(o)
                valid=base in {6,7,8} and steps>=0 and base+3*steps==target
                if valid:
                    pieces,side=square_base(base)
                    for _ in range(steps):
                        x,y,size=pieces.pop(); half=size/2
                        pieces.extend((x+i*half,y+j*half,half) for i,j in product(range(2),repeat=2))
                    assert len(pieces)==target
                    assert_tiling(pieces,side)
                out.append(valid)
            return out
        elif k==26:
            vertices,=groups(r"are (\d+) vârfuri intermediare",t)
            corner="unește două vârfuri opuse" in t
            points=zigzag(vertices//2,corner)
            expected=len(points)-1+(2 if corner else 3)
        elif k==27:
            c,=groups(r"aₙ=(\d+)n²",t); n,=groups(r"a_(\d+)",t)
            expected=(c*n*n-c*(n-1)**2)**2
        elif k==28:
            d,=groups(r"și de (\d+) lei",t)
            reachable={2*i+d*j for i in range(151) for j in range(151)}
            expected=max(n for n in range(151) if n not in reachable)+1
            assert expected in reachable and expected+1 in reachable
        elif k==29:
            n,=groups(r"în (\d+) segmente",t)
            upward={(i,j) for i in range(n) for j in range(n) if i+j<=n-1}
            downward={(i,j) for i in range(n) for j in range(n) if i+j<=n-2}
            expected=len(upward)+len(downward)
        elif k==30:
            r,=groups(r"cu (\d+) vârfuri intermediare",t)
            outer=1 if "trei triunghiuri congruente" in t else 2
            expected=outer+2*(r+1)
        else: raise AssertionError((s,k))
    else:
        assert s=="A1.4.2"
        if k==1:
            a,both,union=groups(r"\|A\|=(\d+), \|A∩B\|=(\d+), \|A∪B\|=(\d+)",t)
            expected=union-a+both
        elif k==2:
            total,=groups(r"are (\d+) submulțimi",t)
            expected=next(n for n in range(20) if 2**n==total)
        elif k==3:
            total,a,b,both=map(int,re.findall(r"\d+",t))
            expected=total-a-b+both
        elif k==4:
            a,b,c,ab,ac,bc,abc=map(int,re.findall(r"\d+",t))
            atoms=[a-ab-ac+abc,b-ab-bc+abc,c-ac-bc+abc,ab-abc,ac-abc,bc-abc,abc]
            assert min(atoms)>=0
            expected=sum(atoms)
        elif k==5:
            left,right,d=groups(r"\[(\d+); (\d+)\].*cu (\d+)",t)
            expected=len([x for x in range(left,right+1) if x%d==0])
        elif k in {6,7}:
            n,=groups(r"\{1,…,(\d+)\}",t)
            a,b=groups(r"cu (\d+) (?:și|sau cu) (\d+)",t)
            expected=sum((x%a==0 and x%b==0) if k==6 else (x%a==0 or x%b==0) for x in range(1,n+1))
        elif k==8:
            n,=groups(r"1≤x≤(\d+)",t)
            expected=sum(gcd(x,n)==1 for x in range(1,n+1))
        elif k==9:
            n,=groups(r"cu (\d+) persoane",t)
            unordered=len(list(combinations(range(n),2))); ordered=len(list(permutations(range(n),2)))
            return [pair(o)==(unordered,ordered) for o in options]
        elif k==10:
            c,limit=groups(r"\{(\d+)\+k².*≤(\d+)\}",t)
            expected=len({c+k*k for k in range(limit+1) if c+k*k<=limit})
        elif k==11:
            length,=groups(r"exact (\d+) cifre",t)
            expected=sum(1 for _ in product(range(10),repeat=length-2))
        elif k==12:
            m,=groups(r"1,…,(\d+) formăm",t)
            triples=list(product(range(1,m+1),repeat=3))
            correct=len(triples),sum(len(set(v))==3 for v in triples)
            return [pair(o)==correct for o in options]
        elif k==13:
            a,b,c=groups(r"(\d+) bile albe, (\d+) negre și (\d+) roșii",t)
            colors=["a"]*a+["n"]*b+["r"]*c
            expected=sum([colors[i] for i in triple]==["a","n","r"] for triple in permutations(range(a+b+c),3))
        elif k==14:
            n,=groups(r"cu (\d+) bile",t)
            expected=sum(1 for _ in permutations(range(n),3))
        elif k==15:
            n,=groups(r"Distribuim (\d+) calculatoare",t)
            expected=sum(1 for _ in product(range(2),repeat=n))
        elif k==16:
            n,=groups(r"Distribuim (\d+) obiecte",t)
            expected=sum(set(v)=={0,1,2} for v in product(range(3),repeat=n))
        elif k==17:
            positions,colors=groups(r"Avem (\d+) panouri distincte și (\d+) culori",t)
            expected=sum(1 for _ in product(range(colors),repeat=positions))
        elif k==18:
            rank,=groups(r"poziția (\d+)",t)
            stream="".join(map(str,range(1,rank+1)))
            expected=int(stream[rank-1])
            assert all(scalar(o).denominator==1 and 0<=scalar(o)<=9 for o in options)
        elif k==19:
            digits,=groups(r"folosim (\d+) cifre",t)
            return [sum(len(str(k)) for k in range(1,int(o)+1))==digits for o in options]
        elif k==20:
            p,n=groups(r"prim (\d+).*lui (\d+)!",t)
            expected=prime_exponent(factorial(n),p)
        elif k==21:
            n,=groups(r"lui (\d+)!",t)
            value=str(factorial(n))
            expected=len(value)-len(value.rstrip("0"))
        elif k==22:
            n,=groups(r"ab=(\d+)",t)
            expected=sum(n%a==0 and gcd(a,n//a)==1 for a in range(1,n+1))
        elif k==23:
            n,=groups(r"cu (\d+) vârfuri",t)
            expected=sum((j-i)%n not in {1,n-1} for i,j in combinations(range(n),2))
        elif k==24:
            n,=groups(r"cu (\d+) laturi",t)
            expected=sum(j not in {i,(i-1)%n,(i+1)%n} for i,j in product(range(n),repeat=2))
        elif k==25:
            n,=groups(r"de (\d+) drepte",t)
            expected=len(set(range(n))|{i+n for i in range(n)})
        elif k==26:
            n,=groups(r"determină (\d+) puncte",t)
            points=[(x,x*x) for x in range(n)]
            lines=set()
            for (x,y),(xx,yy) in combinations(points,2):
                slope=F(yy-y,xx-x)
                lines.add((slope,y-slope*x))
            expected=len(lines)
        elif k==27:
            steps,=groups(r"după (\d+) etape",t)
            pieces=[1]
            for _ in range(steps): pieces=[size/2 for size in pieces for _ in range(4)]
            expected=len(pieces)
        elif k==28:
            n,=groups(r"√1,√2,…,√(\d+)",t)
            expected=sum(isqrt(k)**2==k for k in range(1,n+1))
        elif k==29:
            n,k=groups(r"are (\d+) elemente.*cu (\d+) elemente",t)
            first={frozenset(x) for x in combinations(range(n),k)}
            second={frozenset(x) for x in combinations(range(n),n-k)}
            assert {frozenset(range(n))-x for x in first}==second
            return [o=="Numerele sunt egale; complementarea B↦A∖B este o bijecție." for o in options]
        elif k==30:
            a,b=groups(r"2\^(\d+)·3\^(\d+)",t)
            n=2**a*3**b
            expected=sum(n%d==0 and d%2==0 for d in range(1,n+1))
        elif k==31:
            limit,=groups(r"\[1; (\d+)\]",t)
            expected=sum(sum(n%d==0 for d in range(1,n+1))==4 for n in range(1,limit+1))
        elif k==32:
            aa,bb=re.search(r"A=\{([^}]+)\} și B=\{([^}]+)\}",t).groups()
            a=set(map(int,aa.split("; "))); b=set(map(int,bb.split("; ")))
            expected=sum(a|set(c)==b for k in range(len(b)+1) for c in combinations(b,k))
        elif k==33:
            total,=groups(r"3x\+5y=(\d+)",t)
            expected=sum(3*x+5*y==total for x,y in product(range(total+1),repeat=2))
        else: raise AssertionError((s,k))
    return [scalar(o)==expected for o in options]


def main():
    data=json.loads(SOURCE.read_text(encoding="utf-8"))
    questions=data["questions"]
    assert len(questions)==315
    assert len({q["text"] for q in questions})==315
    counts=Counter((q["catalog"]["section"],q["catalog"]["type"]) for q in questions)
    assert counts=={(f"A1.4.{s}",k):5 for s,n in [(1,30),(2,33)] for k in range(1,n+1)}
    for index,q in enumerate(questions,1):
        try:
            assert q["format"]=="grid" and q["explanation"] and len(q["options"])==4
            assert len({o["text"] for o in q["options"]})==4
            values=option_truths(q)
            assert values.count(True)==1,values
            assert values==[o["is_correct"] for o in q["options"]],values
        except Exception as error:
            raise AssertionError(f"Grila {index}, {q['catalog']['section']}, tip {q['catalog']['type']}: {q['text']}") from error
    print("Audit independent: 315/315 grile; 63/63 tipuri; toate cele 1260 de variante verificate.")


if __name__=="__main__": main()
