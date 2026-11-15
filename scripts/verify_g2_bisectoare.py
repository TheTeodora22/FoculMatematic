"""Audit independent exact al celor 130 grile G2 §3.

Nu importă generatorul. Reface intersecții/proiecții/centre geometrice cu
SymPy, verifică ipotezele și toate cele nouă puncte ale cercului lui Euler.
"""
import json
from collections import Counter
from pathlib import Path

import sympy as S

PATH = Path(__file__).resolve().parents[1] / "data/quizzes/clasa_9/clasa_9_u06_l04_teorema_bisectoarei_relatia_lui_sylvester.json"
BANK = "g2_bisectoare_sylvester_v1"
PARTIAL = {7,8,9,10,12,13,14,26}


def point(values):
    return S.Point(*(S.Rational(x) for x in values))


def vec(p):
    return S.Matrix(p)


def coordinates(p):
    return tuple(S.simplify(x) for x in p)


def intersection(first,second):
    result=first.intersection(second)
    assert len(result)==1 and isinstance(result[0],S.Point)
    return result[0]


def altitude_centre(a,b,c):
    return intersection(S.Line(b,c).perpendicular_line(a),S.Line(c,a).perpendicular_line(b))


def bisector(vertex,first,second):
    u,v=vec(first-vertex),vec(second-vertex)
    direction=u/S.sqrt(u.dot(u))+v/S.sqrt(v.dot(v))
    assert direction != S.zeros(2,1)
    return S.Line(vertex,vertex+S.Point(*direction))


def coefficient(vector,direction):
    vector,direction=vec(vector),vec(direction)
    assert direction.dot(direction)>0
    k=S.simplify(vector.dot(direction)/direction.dot(direction))
    assert S.simplify(vector-k*direction)==S.zeros(2,1)
    return k


def expected(data):
    family=data["family"]
    if family==7:
        p,q=map(S.Rational,[data["AB"],data["AE"]])
        assert 0<q<2*p
        A,B,E=S.Point(0,0),S.Point(p,0),S.Point(q/2,q*S.sqrt(3)/2)
        D=intersection(S.Line(B,E),S.Line(A,S.Point(S.sqrt(3),1)))
        C=intersection(S.Line(B,E),S.Line(A,S.Point(0,1)))
        assert C.y>0 and 0<D.y<E.y<C.y
        # AD bisects angle BAE, whose two half-angles are 30 degrees.
        assert S.simplify(vec(B-A).dot(vec(E-A))/(A.distance(B)*A.distance(E)))==S.Rational(1,2)
        return S.simplify(B.distance(D)/D.distance(E))
    if family==13:
        h=S.Rational(data["height"])
        A,D=S.Point(0,h),S.Point(0,0)
        B,C=S.Point(-h/S.sqrt(3),0),S.Point(h*S.sqrt(3),0)
        M=B.midpoint(C)
        assert S.Line(A,D).is_perpendicular(S.Line(B,C))
        def angle(P,Q,R):
            u,v=vec(P-Q),vec(R-Q)
            cosine=S.simplify(u.dot(v)/S.sqrt(u.dot(u)*v.dot(v)))
            return S.simplify(180*S.acos(cosine)/S.pi)
        assert angle(B,A,D)==angle(D,A,M)==angle(M,A,C)==30
        angles={"A":angle(B,A,C),"B":angle(A,B,C),"C":angle(A,C,B)}
        angles["B+C"]=angles["B"]+angles["C"]
        angles["B−C"]=angles["B"]-angles["C"]
        return angles[data["target"]]
    if family in (23,24):
        c=S.Rational(data["side"])
        assert c>0
        if family==23:
            a=S.Symbol("a",positive=True)
            possible=S.solveset(a/(a+2*c)-S.Rational(1,3),a,domain=S.Interval.open(0,S.oo))
            assert possible==S.FiniteSet(c)
            return c
        # The zero sum of bisectors has A/B coefficients zero:
        # a²=bc and b²=ac. Elimination gives a³=c³, with a,b,c>0.
        a=S.Symbol("a",positive=True)
        possible=S.solveset(a**3-c**3,a,domain=S.Interval.open(0,S.oo))
        assert possible==S.FiniteSet(c)
        a=c; b=a*a/c
        assert a/(a+c)+a/(a+b)-1==0
        assert b/(b+c)+b/(a+b)-1==0
        assert c/(b+c)+c/(a+c)-1==0
        return a,b

    A,B,C=[point(data[name]) for name in "ABC"]
    triangle=S.Triangle(A,B,C)
    assert isinstance(triangle,S.Triangle)
    a,b,c=B.distance(C),C.distance(A),A.distance(B)
    assert all(x>0 for x in (a,b,c)) and a+b>c and b+c>a and c+a>b
    assert b!=c, "External bisector finite foot and midpoint ratios require AB != AC."
    assert all(x*x<y*y+z*z for x,y,z in ((a,b,c),(b,c,a),(c,a,b))), "Orthic incenter requires acute triangle."
    I=triangle.incenter
    O=triangle.circumcircle.center
    H=altitude_centre(A,B,C)
    G=triangle.centroid
    D=intersection(S.Line(A,I),S.Line(B,C))
    assert B.distance(D)+D.distance(C)==a
    assert S.simplify(B.distance(D)/D.distance(C)-c/b)==0
    assert all(S.simplify(side.distance(I)-triangle.inradius)==0 for side in triangle.sides)
    if family==1:
        return B.distance(D)
    if family==2:
        return S.simplify(B.distance(D)/D.distance(C))
    if family==3:
        basis=S.Matrix.hstack(vec(B-A),vec(C-A))
        result=basis.inv()*vec(D-A)
        assert all(k>0 for k in result) and sum(result)==1
        return coordinates(result)
    if family==4:
        return coordinates(I)
    if family==5:
        return coordinates(I-G)
    if family==6:
        u,v=vec(B-A)/c,vec(C-A)/b
        E=intersection(S.Line(A,A+S.Point(*(u-v))),S.Line(B,C))
        assert S.Line(A,D).is_perpendicular(S.Line(A,E))
        t=coefficient(E-B,C-B)
        assert t<0 or t>1
        assert S.simplify(B.distance(E)/C.distance(E)-c/b)==0
        return coordinates(E)
    if family==8:
        E=intersection(S.Line(A,C),S.Line(A,B).parallel_line(D))
        assert 0<C.distance(E)<b
        return S.simplify(C.distance(E)/b)
    if family==9:
        M=A.midpoint(B)
        N=intersection(S.Line(M,D),S.Line(A,C))
        assert S.Line(M,N).contains(D)
        return coefficient(N-A,C-A)
    if family==10:
        foot=S.Line(B,C).projection(A)
        M=B.midpoint(C)
        assert D!=M and foot!=M
        return S.simplify(foot.distance(M)/D.distance(M))
    if family==11:
        K=B+C-A
        P=intersection(bisector(A,B,C),bisector(B,A,K))
        Q=intersection(bisector(C,A,K),bisector(K,B,C))
        assert P!=Q and S.Line(P,Q).is_parallel(S.Line(A,C))
        return coefficient(Q-P,C-A)
    if family==12:
        M=B.midpoint(C)
        P=intersection(S.Line(A,M),S.Line(B,I))
        assert A.distance(P)+P.distance(M)==A.distance(M)
        return S.simplify(A.distance(P)/P.distance(M))
    if family==14:
        # Variant is encoded by radius? These five triangles are in fixed order;
        # infer AP=AQ from the explicit integer in the question via data.
        r=S.Rational(data["radius"])
        assert 0<r<min(b,c)
        P=A+(B-A)*r/c; Q=A+(C-A)*r/b
        M=P.midpoint(Q)
        return coefficient(M-A,D-A)
    if family==15:
        assert S.Line(A,H).is_perpendicular(S.Line(B,C))
        assert S.Line(B,H).is_perpendicular(S.Line(C,A))
        return coordinates(H)
    if family==16:
        X,Y,Z=B+C-A,C+A-B,A+B-C
        enlarged=S.Triangle(X,Y,Z)
        assert enlarged.circumcircle.center==H
        return coordinates(altitude_centre(X,Y,Z))
    if family==17:
        assert O!=G and G!=H and H!=O
        assert S.Line(O,H).contains(G)
        distances={"OH":O.distance(H),"OG":O.distance(G),"GH":G.distance(H)}
        first,second=data["target"].split("/")
        return S.simplify(distances[first]/distances[second])
    if family==18:
        N=O.midpoint(H)
        result=vec(A-N)+vec(B-N)+vec(C-N)
        assert result==vec(O-N)
        return coordinates(result)
    if family==19:
        midpoints=[A.midpoint(B),B.midpoint(C),C.midpoint(A)]
        circle=S.Circle(*midpoints)
        assert circle.center==O.midpoint(H)
        nine=midpoints+[A.midpoint(H),B.midpoint(H),C.midpoint(H)]+[
            S.Line(B,C).projection(A),S.Line(C,A).projection(B),S.Line(A,B).projection(C)]
        assert len(set(nine))==9
        assert all(S.simplify(circle.center.distance(P)**2-circle.radius**2)==0 for P in nine)
        assert S.simplify(circle.radius*2-triangle.circumcircle.radius)==0
        return S.simplify(circle.radius**2)
    if family==20:
        D=2*O-A
        assert O.distance(D)==O.distance(A)
        assert S.Line(A,B).is_perpendicular(S.Line(B,D))
        assert S.Line(A,C).is_perpendicular(S.Line(C,D))
        assert H-B==C-D and C-H==D-B
        return coordinates(D)
    if family==21:
        feet=[S.Line(B,C).projection(A),S.Line(C,A).projection(B),S.Line(A,B).projection(C)]
        orthic=S.Triangle(*feet)
        incenter=orthic.incenter
        assert incenter==H
        distances=[side.distance(H) for side in orthic.sides]
        assert distances[0]==distances[1]==distances[2] and distances[0]>0
        affine=S.Matrix([[P.x for P in feet],[P.y for P in feet],[1,1,1]]).inv()*S.Matrix([H.x,H.y,1])
        assert all(k>0 for k in affine)
        return coordinates(incenter)
    if family==22:
        reflected=H.reflect(S.Line(B,C))
        assert S.simplify(reflected.distance(O)**2-A.distance(O)**2)==0
        assert S.Line(B,C).contains(H.midpoint(reflected))
        return coordinates(reflected)
    if family==25:
        value=A.distance(D)**2
        assert S.simplify(value-b*c+B.distance(D)*D.distance(C))==0
        return S.simplify(value)
    if family==26:
        M=B.midpoint(C)
        line=S.Line(A,D)
        N=line.projection(M)
        assert line.contains(N) and S.Line(M,N).is_perpendicular(line)
        assert N==line.projection(B).midpoint(line.projection(C))
        return coordinates(N)
    raise AssertionError(family)


def main():
    data=json.loads(PATH.read_text(encoding="utf-8"))
    questions=[q for q in data["questions"] if q.get("practice_scope",{}).get("bank")==BANK]
    assert len(questions)==130
    assert Counter(q["practice_scope"]["family"] for q in questions)==Counter({i:5 for i in range(1,27)})
    assert len({q["text"] for q in questions})==130
    for q in questions:
        family=q["practice_scope"]["family"]
        assert q["practice_scope"]["coverage"]==("partial_explicit_case" if family in PARTIAL else "original_grid_adaptation")
        assert q["format"]=="grid" and q["type"]=="multiple_choice"
        assert len(q["explanation"])>150
        assert len(q["options"])==4 and len({o["text"] for o in q["options"]})==4
        assert sum(o["is_correct"] is True for o in q["options"])==1
        verification=q["verification"]
        wanted=expected(verification)
        if verification["answer_kind"]=="pair":
            values=[tuple(S.Rational(x.strip()) for x in o["text"].strip("()").split(";")) for o in q["options"]]
        else:
            values=[S.Rational(o["text"]) for o in q["options"]]
        matches=[value==wanted for value in values]
        assert sum(matches)==1 and matches==[o["is_correct"] for o in q["options"]], q["text"]
    print("OK: 130 grids, 26x5 catalog families; all exact answers independently verified.")
    print("OK: acute and nondegenerate triangles; internal/external bisectors; side weights; Euler/Sylvester; all nine points; orthic incenter.")
    print("Scope: 8 explicitly partial/preparatory families; no claim of complete original proof coverage.")


if __name__=="__main__":
    main()
