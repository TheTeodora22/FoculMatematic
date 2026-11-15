"""Audit independent exact G4 §3 (115 grile), fără importarea generatorului.

Reface medianele din geometrie, inversează datele și validează existența
triunghiurilor. Pentru invarianți verifică polinoame identic nule; pentru
optimizare compară punctul critic cu ambele capete ale segmentului închis.
Locurile geometrice sunt clasificate numai după reducerea ecuației.
"""
import json
import re
from collections import Counter
from pathlib import Path

import sympy as S

PATH=Path(__file__).resolve().parents[1]/"data/quizzes/clasa_9/clasa_9_u08_l02_aplicatii_vectoriale_in_geometria_plana_coliniaritate_si_relatia_lui_l.json"
BANK="g4_vectoriale_leibniz_v1"
X,Y=S.symbols("x y",real=True)


def point(values):
    return S.Point(*(x if isinstance(x,S.Basic) else S.Rational(x) for x in values))


def squared(first,second):
    return S.simplify((first.x-second.x)**2+(first.y-second.y)**2)


def coordinates(P):
    return tuple(S.simplify(x) for x in P)


def triangle(A,B,C):
    determinant=S.Matrix([[B.x-A.x,C.x-A.x],[B.y-A.y,C.y-A.y]]).det()
    assert determinant!=0
    sides=(B.distance(C),C.distance(A),A.distance(B))
    assert all(v>0 for v in sides)
    a,b,c=sides
    assert a+b>c and a+c>b and b+c>a
    return S.Triangle(A,B,C)


def from_squares(values):
    a2,b2,c2=map(S.Rational,values)
    assert min(a2,b2,c2)>0
    a,b,c=[S.sqrt(q) for q in (a2,b2,c2)]
    assert a+b>c and a+c>b and b+c>a
    cx=S.simplify((b2+c2-a2)/(2*c))
    cy2=S.simplify(b2-cx*cx)
    assert cy2>0
    A,B,C=point([0,0]),point([c,0]),point([cx,S.sqrt(cy2)])
    tri=triangle(A,B,C)
    assert squared(B,C)==a2 and squared(C,A)==b2 and squared(A,B)==c2
    return tri


def actual_medians(tri):
    A,B,C=tri.vertices
    return [squared(A,B.midpoint(C)),squared(B,C.midpoint(A)),squared(C,A.midpoint(B))]


def reconstruct_medians(values):
    ma2,mb2,mc2=map(S.Rational,values)
    assert min(ma2,mb2,mc2)>0
    a2,b2,c2=S.symbols("a2 b2 c2",real=True)
    solution=S.solve([2*b2+2*c2-a2-4*ma2,2*a2+2*c2-b2-4*mb2,
                      2*a2+2*b2-c2-4*mc2],(a2,b2,c2))
    squares=[solution[q] for q in (a2,b2,c2)]
    tri=from_squares(squares)
    assert actual_medians(tri)==[ma2,mb2,mc2]
    return squares,tri


def dist_poly(P):
    return (X-P.x)**2+(Y-P.y)**2


def circle_descriptor(center,radius2):
    if radius2<0:
        return ("empty",)
    if radius2==0:
        return ("point",coordinates(center))
    return ("circle",coordinates(center),radius2)


def derive_locus(points,constant):
    expression=S.expand(sum(dist_poly(P) for P in points)-constant)
    solution=S.solve([S.diff(expression,X),S.diff(expression,Y)],(X,Y))
    center=point([solution[X],solution[Y]])
    radius2=S.simplify(-expression.subs({X:center.x,Y:center.y})/len(points))
    assert S.expand(expression-len(points)*(dist_poly(center)-radius2))==0
    return circle_descriptor(center,radius2)


def parse_locus(text):
    if text=="Mulțimea vidă":
        return ("empty",)
    if text=="Întregul plan":
        return ("plane",)
    match=re.fullmatch(r"Punctul \(([^;]+); ([^)]+)\)",text)
    if match:
        return ("point",tuple(S.Rational(x) for x in match.groups()))
    match=re.fullmatch(r"Cercul cu centrul \(([^;]+); ([^)]+)\) și raza la pătrat (.+)",text)
    assert match,text
    a,b,r=map(S.Rational,match.groups())
    assert r>0, "A circle option must have strictly positive radius squared."
    return ("circle",(a,b),r)


def expected(data):
    family=data["family"]
    if family==2:
        c,a,m=map(S.Rational,[data["AB"],data["BC"],data["median_A"]])
        assert 2*m==a and c>0 and a>c
        tri=from_squares([a*a,(4*m*m+a*a-2*c*c)/2,c*c])
        A,B,C=tri.vertices
        assert actual_medians(tri)[0]==m*m
        assert S.Line(A,B).is_perpendicular(S.Line(A,C))
        return squared(A,C)
    if family in (4,23):
        w,h=map(S.Rational,[data["width"],data["height"]])
        assert w>0 and h>0
        t=S.Integer(0) if family==4 else S.Symbol("t",real=True)
        A,B,C,D=point([0,0]),point([w,0]),point([w+t,h]),point([t,h])
        expression=S.expand(dist_poly(A)+dist_poly(C)-dist_poly(B)-dist_poly(D))
        if family==4:
            assert expression==0
            return S.Integer(0)
        solution=S.solve(expression,t)
        assert len(solution)==1
        assert S.expand(expression-2*w*t)==0
        t0=solution[0]
        assert t0==0 and S.Line(A,B).is_perpendicular(S.Line(A,point([t0,h])))
        return t0
    if family==6:
        tri=from_squares(data["sides_squared"])
        ma2,mb2,mc2=actual_medians(tri)
        a2,b2,c2=map(S.Rational,data["sides_squared"])
        assert b2-a2==c2-b2
        assert S.simplify(mb2-ma2)==S.simplify(mc2-mb2)
        return S.simplify(mb2-ma2)
    if family==7:
        mb2,mc2=map(S.Rational,[data["median_b_squared"],data["median_c_squared"]])
        b2,c2=S.symbols("b2 c2",real=True)
        # In a right triangle with A at the origin, the midpoint coordinates
        # give these equations directly, independently of inverse formulas.
        solution=S.solve([c2+b2/4-mb2,b2+c2/4-mc2],(b2,c2))
        b2,c2=solution[b2],solution[c2]
        tri=from_squares([b2+c2,b2,c2])
        assert actual_medians(tri)[1:]==[mb2,mc2]
        A,B,C=tri.vertices
        assert S.Line(A,B).is_perpendicular(S.Line(A,C))
        return b2,c2
    if family==8:
        c,a,mb2=map(S.Rational,[data["AB"],data["BC"],data["median_b_squared"]])
        tri=from_squares([a*a,2*a*a+2*c*c-4*mb2,c*c])
        A,B,C=tri.vertices; M=A.midpoint(C)
        assert squared(B,M)==mb2
        foot=S.Line(B,C).projection(M)
        return squared(M,foot)
    if family==9:
        a2,c2=map(S.Rational,[data["BC_squared"],data["AB_squared"]])
        a=S.sqrt(a2)
        # B=(0,0), C=(a,0), |AB|²=c². Orthogonality of actual median
        # vectors determines A.x through c²-a*A.x-2a²=0.
        ax=S.simplify((c2-2*a2)/a)
        ay2=S.simplify(c2-ax*ax)
        assert ay2>0
        A,B,C=point([ax,S.sqrt(ay2)]),point([0,0]),point([a,0])
        triangle(A,B,C)
        BN=point(coordinates(A.midpoint(C)-B)); CP=point(coordinates(A.midpoint(B)-C))
        assert S.simplify(BN.dot(CP))==0
        return squared(A,C)
    if family==10:
        squares,_=reconstruct_medians(data["medians_squared"])
        return squares[0]
    if family==12:
        R,t=map(S.Rational,[data["radius"],data["offset"]])
        assert 0<t<R
        direction_x,direction_y,z=S.symbols("u v z",real=True)
        polynomial=S.Poly((t+z*direction_x)**2+(z*direction_y)**2-R*R,z)
        leading,_,constant=polynomial.all_coeffs()
        # Viete: the oriented parameters have negative product because A is
        # interior. Converting to positive lengths multiplies by -|direction|².
        product=S.simplify(-constant/leading*(direction_x**2+direction_y**2))
        assert product>0
        mirrored=S.Poly((-t+z*direction_x)**2+(z*direction_y)**2-R*R,z)
        assert S.simplify(mirrored.all_coeffs()[-1]-constant)==0
        return S.simplify(2/product)
    if family==15:
        side=S.Rational(data["side"])
        assert side>0
        points=[point([sx*side/2,sy*side/2]) for sx,sy in [(1,1),(-1,1),(-1,-1),(1,-1)]]
        expression=S.expand(sum(dist_poly(P) for P in points))
        assert S.expand(expression-4*(X*X+Y*Y)-2*side*side)==0
        # On the circumcircle X²+Y²=side²/2.
        return S.simplify(4*(side*side/2)+2*side*side)
    if family==16:
        u=S.Rational(data["scale"])
        assert u>0
        A,B,C=point([-u,0]),point([u,0]),point([0,2*u])
        center=point([0,-2*u]); radius2=6*u*u
        relation=S.expand(dist_poly(A)+dist_poly(B)-dist_poly(C))
        assert S.expand(relation-(dist_poly(center)-radius2))==0
        assert all(squared(P,center)!=radius2 for P in (A,B,C)), "Distance zero would make a degenerate triangle."
        # Positive legs x,y and hypotenuse sqrt(x²+y²) satisfy strict triangle inequalities.
        return S.Integer(1)
    if family==19:
        median=S.Rational(data["median"])
        assert median>0
        squares,tri=reconstruct_medians([median*median]*3)
        assert len(set(squares))==1 and tri.is_equilateral()
        return squares[0]
    if family==20:
        A,B=point(data["A"]),point(data["B"])
        assert A!=B
        return derive_locus([A,B],S.Rational(data["constant"]))

    A,B,C=[point(data[name]) for name in "ABC"]
    tri=triangle(A,B,C)
    a2,b2,c2=squared(B,C),squared(C,A),squared(A,B)
    G=tri.centroid
    if family==1:
        return squared(A,B.midpoint(C))
    if family==3:
        return sum(actual_medians(tri))
    if family==5:
        p,q=map(S.Rational,data["BD_DC"])
        assert p>0 and q>0
        D=B+(C-B)*p/(p+q)
        assert B.distance(D)+D.distance(C)==B.distance(C)
        assert S.simplify(B.distance(D)/D.distance(C)-p/q)==0
        # Validate Stewart with actual Euclidean lengths.
        value=squared(A,D)
        bd,dc=B.distance(D),D.distance(C)
        assert S.simplify(b2*bd+c2*dc-B.distance(C)*(value+bd*dc))==0
        return value
    if family==11:
        D,E,F=B.midpoint(C),C.midpoint(A),A.midpoint(B)
        expression=S.expand(dist_poly(A)+dist_poly(B)+dist_poly(C)-dist_poly(D)-dist_poly(E)-dist_poly(F))
        assert S.diff(expression,X)==S.diff(expression,Y)==0
        return expression
    if family==13:
        D=point(data["D"])
        polygon=S.Polygon(A,B,C,D)
        assert polygon.is_convex()
        M,N=A.midpoint(C),B.midpoint(D)
        gap=squared(M,N)
        assert S.simplify(squared(A,B)+squared(B,C)+squared(C,D)+squared(D,A)-squared(A,C)-squared(B,D)-4*gap)==0
        return gap
    if family==14:
        D=point([X,Y])
        expression=S.expand(squared(A,B)+squared(B,C)+squared(C,D)+squared(D,A)-squared(A,C)-squared(B,D))
        solution=S.solve([S.diff(expression,X),S.diff(expression,Y)],(X,Y))
        result=point([solution[X],solution[Y]])
        assert S.expand(expression-dist_poly(result))==0
        assert S.Polygon(A,B,C,result).is_convex()
        return coordinates(result)
    if family in (17,21):
        leibniz=S.expand(dist_poly(A)+dist_poly(B)+dist_poly(C)-3*dist_poly(G))
        assert S.diff(leibniz,X)==S.diff(leibniz,Y)==0
        if family==21:
            return derive_locus([A,B,C],S.Rational(data["constant"]))
        M=point(data["M"])
        assert squared(M,G)==S.Rational(data["MG_squared"])
        assert S.Rational(data["MG_squared"])>=0
        return squared(M,A)+squared(M,B)+squared(M,C)
    if family==18:
        O=tri.circumcircle.center
        H=S.Line(B,C).perpendicular_line(A).intersection(S.Line(C,A).perpendicular_line(B))[0]
        R2=squared(O,A)
        assert S.simplify(9*squared(O,G)-9*R2+a2+b2+c2)==0
        assert S.Line(O,H).contains(G)
        mapping={"OG²":(O,G),"GH²":(G,H),"OH²":(O,H)}
        first,second=mapping[data["target"]]
        return squared(first,second)
    if family==22:
        t=S.Symbol("t",real=True)
        M=A+t*(C-A)
        objective=S.expand(squared(M,B)+squared(M,C))
        assert S.diff(objective,t,2)>0
        critical=S.solve(S.diff(objective,t),t)
        assert len(critical)==1
        candidates=[S.Integer(0),S.Integer(1)]
        if 0<=critical[0]<=1:
            candidates.append(critical[0])
        best=min(candidates,key=lambda x:objective.subs(t,x))
        result=A+best*(C-A)
        assert 0<=best<=1
        assert all(objective.subs(t,best)<=objective.subs(t,candidate) for candidate in candidates)
        return coordinates(result)
    raise AssertionError(family)


def main():
    source=json.loads(PATH.read_text(encoding="utf-8"))
    questions=[q for q in source["questions"] if q.get("practice_scope",{}).get("bank")==BANK]
    assert len(questions)==115 and len({q["text"] for q in questions})==115
    assert Counter(q["practice_scope"]["family"] for q in questions)==Counter({i:5 for i in range(1,24)})
    locus_cases={20:set(),21:set()}; minima=set()
    for q in questions:
        family=q["practice_scope"]["family"]
        assert q["practice_scope"]["coverage"]==("partial_explicit_case" if family in (12,16) else "original_grid_adaptation")
        assert q["type"]=="multiple_choice" and q["format"]=="grid"
        assert len(q["options"])==4 and len(q["explanation"])>150
        assert len({o["text"] for o in q["options"]})==4
        assert sum(o["is_correct"] is True for o in q["options"])==1
        data=q["verification"]
        wanted=expected(data)
        if data["answer_kind"]=="pair":
            values=[tuple(S.Rational(x.strip()) for x in o["text"].strip("()").split(";")) for o in q["options"]]
        elif data["answer_kind"]=="locus":
            values=[parse_locus(o["text"]) for o in q["options"]]
        else:
            values=[S.Rational(o["text"]) for o in q["options"]]
        assert len(set(values))==4, "Mathematically duplicate options"
        matches=[value==wanted for value in values]
        assert sum(matches)==1 and matches==[o["is_correct"] for o in q["options"]],q["text"]
        if family in locus_cases:
            locus_cases[family].add(wanted[0])
        if family==22:
            assert "închis" in q["text"]
            minima.add("A" if wanted==coordinates(point(data["A"])) else "C" if wanted==coordinates(point(data["C"])) else "interior")
    assert all(cases=={"empty","point","circle"} for cases in locus_cases.values())
    assert minima=={"A","C","interior"}
    print("OK: 115 grids, 23x5 families, independent exact geometry/algebra checks.")
    print("OK: positive valid median reconstruction; strict triangle inequalities; polynomial invariants; Leibniz and center distances.")
    print("OK: each locus family covers empty/point/circle; segment minima cover both endpoints and interior.")
    print("Scope: families12/16 are explicitly partial original configurations, not full catalog-proof coverage.")


if __name__=="__main__":
    main()
