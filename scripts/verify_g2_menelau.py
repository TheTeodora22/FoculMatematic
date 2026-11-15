"""Independent read-only exact SymPy audit for G2 section 4.

Does not import the generator or compare with a stored expected answer. Builds
the actual Euclidean/affine configurations, checks finite intersections,
orientation, point membership and theorem identities, then parses all options.
These checks certify the explicit adaptations, not all original olympiad proofs.
"""
import json
import re
from collections import Counter
from pathlib import Path

import sympy as S

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / 'data/quizzes/clasa_9/clasa_9_u06_l05_teorema_lui_menelau.json'
BANK = 'g2_menelau_v1'
PAIR = re.compile(r'\((-?\d+(?:/\d+)?);\s*(-?\d+(?:/\d+)?)\)')


def point(raw): return S.Point(*[S.Rational(value) for value in raw])


def meet(a, b, c, d):
    assert a != b and c != d, 'Line defined by coincident points.'
    result = S.Line(a, b).intersection(S.Line(c, d))
    assert len(result) == 1 and isinstance(result[0], S.Point2D), 'Nonfinite or nonunique intersection.'
    return result[0]


def oriented(u, x, v):
    assert u != v and x != v
    assert S.Line(u, v).distance(x) == 0
    direction = v-u
    t = S.simplify((x-u).dot(direction)/direction.dot(direction))
    return S.simplify(t/(1-t))


def aligned(a, b, c):
    assert a != b
    return S.simplify(S.det(S.Matrix([[b.x-a.x, b.y-a.y], [c.x-a.x, c.y-a.y]]))) == 0


def squared_distance(a, b): return S.simplify((a-b).dot(a-b))


def inside(p, a, b, c):
    t, u = S.symbols('t u')
    solution = S.solve(S.Matrix(p-a)-t*S.Matrix(b-a)-u*S.Matrix(c-a), (t, u))
    assert set(solution) == {t, u}
    return solution[t] > 0 and solution[u] > 0 and solution[t]+solution[u] < 1


def assert_text_coordinates(question):
    data = question['verification']
    for key, value in data.items():
        if key not in list('ABCDEF')+['P','T','M','A_prime','B_prime','C_prime']:
            continue
        label = key.replace('_prime', '′')
        match = re.search(r'(?<![A-Za-z])'+re.escape(label)+r'\s*=?\s*'+PAIR.pattern, question['text'])
        if match:
            assert point(match.groups()) == point(value), (key, question['practice_scope'])


def recompute(question):
    g = question['verification']
    typ, j = question['practice_scope']['type'], question['practice_scope']['variant']
    pts = {key: point(value) for key, value in g.items() if key in list('ABCDEF')+['P','T','M','X']}
    a, b, c = [pts[key] for key in 'ABC']
    if typ != 12:
        assert not aligned(a, b, c), 'Degenerate starting triangle.'

    if typ == 1:
        ab, ac, bc = a.distance(b), a.distance(c), b.distance(c)
        assert len({ab, ac, bc}) == 3, 'An exterior bisector foot would be infinite.'
        d = (ab*c-ac*b)/(ab-ac)
        e = (bc*a-ab*c)/(bc-ab)
        f = (ac*b-bc*a)/(ac-bc)
        ratios = [oriented(b,d,c), oriented(c,e,a), oriented(a,f,b)]
        assert all(value < 0 for value in ratios)
        assert S.simplify(S.prod(ratios)) == -1
        assert aligned(d,e,f)
        assert ratios[0] == -ab/ac and ratios[1] == -bc/ab and ratios[2] == -ac/bc
        return d
    if typ == 2:
        p, x = pts['P'], pts['X']
        midpoint = S.Segment(b,c).midpoint
        assert oriented(a,p,midpoint) == j+1
        assert oriented(a,x,b) == S.Rational(1,5)
        y, z = meet(x,p,c,a), meet(x,p,b,c)
        result = oriented(c,y,a)
        assert result < 0 and oriented(b,z,c) > 0
        assert oriented(a,x,b)*oriented(b,z,c)*result == -1
        assert 'AP:PM='+str(j+1)+':1' in question['text']
        return result
    if typ == 3:
        ab, ac = a.distance(b), a.distance(c)
        d = (ac*b+ab*c)/(ab+ac)
        e = pts['E']
        assert oriented(a,e,c) == j
        assert oriented(b,d,c) == ab/ac
        p = meet(a,d,b,e)
        result = oriented(a,p,d)
        assert result > 0
        assert oriented(d,b,c)*oriented(c,e,a)*result == -1
        return result
    if typ == 4:
        d,p = pts['D'],pts['P']
        assert S.Line(a,b).is_parallel(S.Line(c,d))
        assert a.distance(d) == b.distance(c)
        m = S.Segment(a,b).midpoint
        assert p.x == m.x and p.y > m.y
        x,y = meet(a,p,c,d),meet(b,p,c,d)
        assert squared_distance(m,x) == squared_distance(m,y) > 0
        return S.simplify(m.distance(x)/m.distance(y))
    if typ == 5:
        d=pts['D']; line1,line2=map(point,g['line'])
        e=meet(line1,line2,a,b); f=meet(line1,line2,b,c)
        h=meet(line1,line2,d,a); gg=meet(line1,line2,c,d)
        t=meet(line1,line2,a,c)
        ratios = [oriented(a,e,b),oriented(b,f,c),oriented(c,gg,d),oriented(d,h,a)]
        assert all(value != 0 for value in ratios)
        assert list(map(S.Rational,g['ratios'])) == ratios[:3]
        for label,value in zip(['AE/EB','BF/FC','CG/GD'],ratios[:3]):
            assert label+'='+str(value) in question['text']
        assert ratios[0]*ratios[1]*oriented(c,t,a) == -1
        assert oriented(a,t,c)*ratios[2]*ratios[3] == -1
        assert S.prod(ratios) == 1 and ratios[3] < 0
        return ratios[3]
    if typ in (6,7):
        p=pts['P']
        assert oriented(b,p,c) == S.Rational(j,j+1) > 0
        m,n=S.Segment(a,b).midpoint,S.Segment(a,c).midpoint
        if typ == 6:
            d,e=2*m-p,2*n-p
            assert aligned(a,d,e) and d != a and e != a
            return S.simplify(a.distance(d)/a.distance(e))
        q=S.Segment(a,p).midpoint
        assert aligned(m,q,n) and oriented(m,q,n) > 0
        return S.simplify(m.distance(q)/q.distance(n))
    if typ == 8:
        d,t,m,p=[pts[key] for key in ['D','T','M','P']]
        assert aligned(a,c,t) and oriented(a,m,b) > 0 and oriented(c,p,d) > 0
        n,q=meet(m,t,b,c),meet(p,t,d,a)
        assert meet(m,n,p,q) == t
        result=meet(n,p,m,q)
        assert aligned(b,d,result)
        return result
    if typ == 9:
        ab,ac,bc=a.distance(b),a.distance(c),b.distance(c)
        e=(ab*c+bc*a)/(ab+bc)
        f=(bc*a+ac*b)/(bc+ac)
        d=(ac*b+ab*c)/(ac+ab)
        p=meet(b,e,c,f)
        assert inside(p,a,b,c) and aligned(a,d,p)
        assert oriented(b,d,c)*oriented(c,e,a)*oriented(a,f,b) == 1
        return p
    if typ == 10:
        d=pts['D']; e,f=meet(a,b,c,d),meet(a,d,b,c)
        m,n,k=[S.Segment(first,second).midpoint for first,second in [(a,c),(b,d),(e,f)]]
        assert aligned(m,n,k)
        return k
    if typ == 11:
        weights = list(map(S.Rational,g['weights']))
        assert all(value > 0 for value in weights)
        p=sum((weight*vertex for weight,vertex in zip(weights,[a,b,c])),S.Point(0,0))/sum(weights)
        assert inside(p,a,b,c)
        d,e,f=meet(a,p,b,c),meet(b,p,c,a),meet(c,p,a,b)
        first,second=oriented(a,e,c),oriented(a,f,b)
        assert f'AE/EC={first}' in question['text'] and f'AF/FB={second}' in question['text']
        result=oriented(a,p,d)
        assert result == first+second
        return result
    if typ == 12:
        aa,bb,cc=[point(g[key]) for key in ['A_prime','B_prime','C_prime']]
        assert aligned(a,b,c) and aligned(aa,bb,cc)
        assert len({a,b,c,aa,bb,cc}) == 6
        assert S.Line(a,b) != S.Line(aa,bb)
        x,y,z=meet(a,bb,aa,b),meet(a,cc,aa,c),meet(b,cc,bb,c)
        assert len({x,y,z}) == 3 and aligned(x,y,z)
        return z
    if typ == 13:
        factors=g['factors']
        assert factors == [2,3,4]
        aa,bb,cc=[factor*vertex for factor,vertex in zip(factors,[a,b,c])]
        o=S.Point(0,0)
        assert not aligned(aa,bb,cc)
        assert meet(a,aa,b,bb) == o and aligned(c,cc,o)
        x,y,z=meet(a,b,aa,bb),meet(b,c,bb,cc),meet(c,a,cc,aa)
        assert len({x,y,z}) == 3 and aligned(x,y,z)
        return z
    if typ == 14:
        line1,line2=map(point,g['line'])
        assert f'y=x−{j+1}' in question['text']
        assert line1.y == line1.x-(j+1) and line2.y == line2.x-(j+1)
        d,e,f=meet(line1,line2,b,c),meet(line1,line2,c,a),meet(line1,line2,a,b)
        dd,ee,ff=b+c-d,c+a-e,a+b-f
        initial=[oriented(b,d,c),oriented(c,e,a),oriented(a,f,b)]
        reflected=[oriented(b,dd,c),oriented(c,ee,a),oriented(a,ff,b)]
        assert S.prod(initial) == S.prod(reflected) == -1
        assert all(first*second == 1 for first,second in zip(initial,reflected))
        assert aligned(dd,ee,ff)
        return reflected[2]
    if typ == 15:
        p=pts['P']; assert inside(p,a,b,c)
        pa,pb,pc=p.distance(a),p.distance(b),p.distance(c)
        d=(pc*b+pb*c)/(pb+pc)
        e=(pa*c+pc*a)/(pc+pa)
        f=(pb*a+pa*b)/(pa+pb)
        # Exact affine weights give a finite interior common point without
        # solving radical-heavy general line equations numerically.
        weights=[pb*pc,pa*pc,pa*pb]
        q=sum((weight*vertex for weight,vertex in zip(weights,[a,b,c])),S.Point(0,0))/sum(weights)
        assert aligned(a,d,q) and aligned(b,e,q) and aligned(c,f,q)
        assert all(value > 0 for value in weights)
        assert S.simplify((pb/pc)*(pc/pa)*(pa/pb)) == 1
        # One distractor says the common point must be P: it is false here.
        original_foot=meet(a,p,b,c)
        assert S.simplify((pb/pc)**2-oriented(b,original_foot,c)**2) != 0
        return 'Sunt concurente într-un punct finit interior triunghiului ABC.'
    if typ == 16:
        x,y=S.symbols('x y')
        distances=[(x-vertex.x)**2+(y-vertex.y)**2 for vertex in [a,b,c]]
        solutions=S.solve([distances[0]-distances[1],distances[1]-distances[2]],(x,y))
        assert set(solutions) == {x,y}
        result=S.Point(solutions[x],solutions[y])
        assert squared_distance(result,a) == squared_distance(result,b) == squared_distance(result,c) > 0
        assert 'adaptare parțială' in question['practice_scope']['adaptation']
        return result
    if typ == 17:
        d,e,f=[pts[key] for key in 'DEF']
        radius=S.Rational(g['radius'])
        assert radius > 0 and len({a,b,c,d,e,f}) == 6
        assert all(vertex.dot(vertex) == radius**2 for vertex in [a,b,c,d,e,f])
        x,y,z=meet(a,b,d,e),meet(b,c,e,f),meet(c,d,f,a)
        assert len({x,y,z}) == 3 and aligned(x,y,z)
        return z
    raise AssertionError(typ)


def verify(question):
    assert_text_coordinates(question)
    result=recompute(question)
    options=question['options']
    assert len(options) == 4
    if isinstance(result,S.Point2D):
        values=[]
        for option in options:
            match=PAIR.fullmatch(option['text'])
            assert match, option['text']
            values.append(point(match.groups()))
    elif isinstance(result,str):
        values=[option['text'] for option in options]
    else:
        result=S.simplify(result)
        assert result.is_Rational
        values=[S.Rational(option['text']) for option in options]
    assert len(set(values)) == 4, 'Mathematically duplicate options.'
    flags=[option['is_correct'] for option in options]
    truth=[value == result for value in values]
    assert all(type(flag) is bool for flag in flags)
    assert sum(truth) == sum(flags) == 1 and truth == flags, (question['practice_scope'], result, values, flags)
    assert question['type'] == 'multiple_choice' and question['format'] == 'grid'
    assert question['explanation'] and question['practice_scope']['adaptation']
    answer_text=options[truth.index(True)]['text']
    assert answer_text in question['explanation'], 'Correct result missing from explanation.'


def main():
    data=json.loads(TARGET.read_text(encoding='utf-8'))
    grids=[question for question in data['questions'] if question.get('practice_scope',{}).get('bank') == BANK]
    assert len(grids) == len({question['text'] for question in grids}) == 85
    assert {(q['practice_scope']['type'],q['practice_scope']['variant']) for q in grids} == {
        (typ,j) for typ in range(1,18) for j in range(1,6)}
    assert data['difficulty'] == 'hard'
    for question in grids:
        verify(question)
    positions=Counter(next(i for i,option in enumerate(question['options']) if option['is_correct']) for question in grids)
    assert max(positions.values())-min(positions.values()) <= 1
    print('OK: 85 Menelaus grids, 17 x 5 variants, 340 distinct options; exact configurations, orientations and incidence checks.')


if __name__ == '__main__':
    main()
