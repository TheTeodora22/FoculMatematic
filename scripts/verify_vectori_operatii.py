"""Independent read-only audit of G1 operations (48 types x 5 adaptations).

No generator import and no stored answer field. Recompute numeric answers from
givens using SymPy matrices/rationals; test geometric defining equations and
nondegeneracy. Theorem choices are reviewed conclusions with symbolic checks
where available, not a claim of machine-proving all Euclidean geometry.
"""
import json
import re
from collections import Counter
from pathlib import Path

import sympy as S

ROOT = Path(__file__).resolve().parents[1]
TARGET = next((ROOT / 'data/quizzes/clasa_9').glob('clasa_9_u05_l03_*.json'))
BANK = 'vectori_operatii_grile_v1'
PAIR = re.compile(r'\((-?\d+(?:/\d+)?);\s*(-?\d+(?:/\d+)?)\)')


def vector(values):
    return S.Matrix([S.Rational(value) for value in values])


def det(first, second):
    return S.Matrix.hstack(first, second).det()


def point_givens_match_text(question):
    """Every displayed named datum represented in audit metadata must match it.

    Some metadata also contains auxiliary/unused points not shown to students.
    Such points are not treated as a claim about the exercise statement.
    """
    given = question['verification']
    pattern = re.compile(r'(?<![A-Za-z])(OA|OB|OC|OD|A|B|C|D|G|u|v|w)\s*=?\s*'
                         r'\((-?\d+(?:/\d+)?);\s*(-?\d+(?:/\d+)?)\)')
    for name, x, y in pattern.findall(question['text']):
        if name in given:
            assert vector([x, y]) == vector(given[name]), (name, question['practice_scope'])
    section, typ = question['practice_scope']['section'], question['practice_scope']['type']
    aliases = {}
    if (section, typ) == ('2.1', 20):
        aliases = {'M': 'D'}
    elif (section, typ) == ('2.2', 12):
        aliases = {'M': 'C'}
    elif (section, typ) == ('2.2', 17):
        aliases = {'A′': 'C', 'B′': 'D'}
    for displayed, stored in aliases.items():
        match = re.search(re.escape(displayed)+r'\s*=?\s*'+PAIR.pattern, question['text'])
        assert match and vector(match.groups()) == vector(given[stored])


def expected(question):
    scope = question['practice_scope']
    section, typ, j = scope['section'], scope['type'], scope['variant']
    g = question['verification']
    pts = {name: vector(g[name]) for name in 'ABCD' if name in g}
    if len(pts) == 4:
        a, b, c, d = [pts[name] for name in 'ABCD']
        assert det(b-a, c-a) != 0, 'Degenerate starting triangle.'
    if section == '2.1':
        if typ == 1: return c-a
        if typ == 2:
            assert det(b-a, d-a) != 0
            return b+d-2*a
        if typ == 3: return b-a+d-c
        if typ == 4: return b+c-a-d
        if typ == 5: return a-b-d+c
        if typ == 6:
            midpoint = (b+c)/2
            assert b-a+c-a == 2*(midpoint-a)
            return 2*(midpoint-a)
        if typ == 7:
            # Explicit symbolic cancellation of the arbitrary moving point.
            mx, my = S.symbols('mx my')
            m = S.Matrix([mx, my])
            result = m-a+c-b-(m-b)
            assert result == c-a
            return result
        if typ == 8:
            lengths = list(map(S.Rational, g['lengths']))
            assert all(value > 0 for value in lengths)
            assert max(lengths) > sum(lengths)-max(lengths)
            for length in lengths:
                assert str(length) in question['text']
            return 'Nu, lungimea maximă depășește suma celorlalte două.'
        if typ == 9:
            first, second = map(S.Rational, g['legs'])
            assert first > 0 and second > 0
            return S.sqrt(first**2+second**2)
        if typ == 10:
            result = a+c-b
            assert result-a == c-b and b-a == c-result
            return result
        if typ == 11:
            result = b+c-a
            assert result-a == b-a+c-a
            return result
        if typ == 12:
            result = (a+b)/2
            assert a-result+b-result == S.zeros(2, 1)
            return result
        if typ == 13: return vector(g['u'])-vector(g['v'])
        if typ == 14:
            radius = S.Rational(g['radius'])
            assert radius > 0
            # |OA+OB|²=R² implies each mutual dot product=-R²/2;
            # the squared chord length is consequently 3R² for every pair.
            dot = S.solve(S.Symbol('dot')*2+2*radius**2-radius**2, S.Symbol('dot'))[0]
            assert 2*radius**2-2*dot == 3*radius**2
            return 'Echilateral.'
        if typ == 15:
            assert g['radius'] > 0
            assert 'distincte' in question['text'] and 'ordine pe cerc' in question['text']
            # Reviewed proof: a nonzero chord sum determines its unordered
            # equal-radius endpoints uniquely. Opposite sums give antipodal
            # pairs; the zero-sum case is already a pair of diameters.
            assert 'diametr' in question['explanation']
            return 'Este dreptunghi, posibil pătrat.'
        if typ == 16: return -a-b-c
        if typ == 17:
            u, v, w = [vector(g[key]) for key in ('u', 'v', 'w')]
            assert det(u, v) != 0
            result = S.Matrix.hstack(u, v).inv()*w
            assert result[0]*u+result[1]*v == w
            return result
        if typ == 18:
            reflected_b, reflected_c = 2*a-b, 2*a-c
            return reflected_b-a+reflected_c-a
        if typ == 19:
            return 2*((c+d)/2-(a+b)/2)
        if typ == 20:
            result = 2*((a+b)/2)-d
            assert (d+result)/2 == (a+b)/2
            return result
        if typ == 21:
            assert g['length'] > 0 and 'strict între 0° și 180°' in question['text']
            assert 'romb' in question['explanation']
            return 'Sensul bisectoarei interioare a unghiului dintre u și v.'
        if typ in (22, 25):
            result = (a+b+c+d)/4
            assert a-result+b-result+c-result+d-result == S.zeros(2, 1)
            if typ == 25:
                assert ((a+b)/2+(c+d)/2)/2 == ((a+d)/2+(b+c)/2)/2
            return result
        if typ == 23:
            lengths = list(map(S.Rational, g['lengths']))
            assert all(value > 0 for value in lengths)
            # Positive multiples of (1,0) attain this upper bound.
            return sum(lengths)
        if typ == 24:
            assert all(value > 0 for value in g['lengths'])
            assert 'strict pozitive' in question['text']
            return 'Când sunt coliniari și au același sens.'
        if typ == 26:
            o = vector(g['O'])
            r = S.Rational(g['radius'])
            assert r*r > o.dot(o)
            # Vieta for circle intersections on y=0 and x=0.
            x = S.Symbol('x')
            horizontal = S.Poly((x-o[0])**2+o[1]**2-r**2, x)
            vertical = S.Poly(o[0]**2+(x-o[1])**2-r**2, x)
            return S.Matrix([-horizontal.nth(1)/horizontal.nth(2), -vertical.nth(1)/vertical.nth(2)])
        if typ == 27:
            vectors = [vector(g[key]) for key in ('u', 'v', 'w')]
            assert all(value.dot(value) == 1 and value[0] > 0 for value in vectors)
            total = sum(vectors, S.zeros(2, 1))
            return S.sqrt(total.dot(total))
        if typ == 28:
            u, v = vector(g['u']), vector(g['v'])
            assert det(u, v) != 0
            return -u-v
    if section == '2.2':
        if typ == 1: return (a+b)/2
        if typ == 2:
            u, v = vector(g['u']), vector(g['v'])
            return 2*(u+v)-(u-v)
        if typ == 3:
            side = S.Rational(g['side'])
            assert side > 0
            # Exact regular hexagon coordinates, independently solving the basis.
            ha = S.Matrix([side, 0])
            hb = S.Matrix([side/2, S.sqrt(3)*side/2])
            hf = S.Matrix([side/2, -S.sqrt(3)*side/2])
            hd = S.Matrix([-side, 0])
            return S.Matrix.hstack(hb-ha, hf-ha).inv()*(hd-ha)
        if typ == 4:
            k = S.Rational(g['k'])
            assert f'AM=({k})AB' in question['text']
            return a+k*(b-a)
        if typ == 5:
            u, v = vector(g['u']), vector(g['v'])
            match = re.search(r'(\d+)\(2u−v\)−(\d+)\(u\+v\)', question['text'])
            assert match
            first, second = map(int, match.groups())
            return first*(2*u-v)-second*(u+v)
        if typ == 6:
            match = re.search(r'MA\+(\d+)AB=0', question['text'])
            assert match
            k = int(match[1])
            result = a+k*(b-a)
            assert a-result+k*(b-a) == S.zeros(2, 1)
            return result
        if typ == 7:
            p, q = S.Rational(g['p']), S.Rational(g['q'])
            assert p > 0 and q > 0 and f'BP:PC={p}:{q}' in question['text']
            result = (q*b+p*c)/(p+q)-a
            point = result+a
            assert q*(point-b) == p*(c-point)
            return result
        if typ == 8:
            k = S.Rational(g['k'])
            assert b != a and f'C=A+({k})AB' in question['text']
            return k
        if typ == 9:
            u, v = vector(g['u']), vector(g['v'])
            assert det(u, v) != 0
            scale = g['scale']
            t = S.Symbol('t')
            result = S.solve(det(t*v-scale*u, v-u), t)
            assert len(result) == 1 and result[0] != 0
            return result[0]
        if typ == 10:
            k = g['k']
            assert k > 0
            assert f'({k+1})OA−{k}OB' in question['text']
            # C=(k+1)A-kB implies C-A=-k(B-A), a symbolic identity.
            ax, bx = S.symbols('ax bx')
            assert S.expand(((k+1)*ax-k*bx)-ax+k*(bx-ax)) == 0
            return 'A, B și C sunt coliniare.'
        if typ == 11:
            p, q = S.Rational(g['p']), S.Rational(g['q'])
            assert p+q != 0
            result = (p*a+q*b)/(p+q)
            assert p*(a-result)+q*(b-result) == S.zeros(2, 1)
            return result
        if typ == 12:
            p, q = S.Rational(g['p']), S.Rational(g['q'])
            barycenter = vector(g['G'])
            assert p*(a-barycenter)+q*(b-barycenter) == S.zeros(2, 1)
            direct = p*(a-c)+q*(b-c)
            assert direct == (p+q)*(barycenter-c)
            return direct
        if typ == 13: return (c-b)/2
        if typ == 14:
            bases = list(map(S.Rational, g['bases']))
            assert all(length > 0 for length in bases)
            return sum(bases)/2
        if typ == 15: return (c-a)/2
        if typ == 16:
            s, k = S.Rational(g['s']), S.Rational(g['k'])
            assert s > 0 and 0 < k < 1
            eb, ec = S.Matrix([2*s, -s]), S.Matrix([-s, 2*s])
            result = eb+k*(ec-eb)
            assert result[0]+result[1] == s  # line BC has equation x+y=s
            return result
        if typ == 17:
            # Coordinates c,d here denote A',B', not vertices C,D.
            midpoint_aa, midpoint_bb = (a+c)/2, (b+d)/2
            assert midpoint_aa != midpoint_bb
            return midpoint_bb-midpoint_aa
        if typ == 18:
            assert all(length > 0 for length in g['lengths'])
            assert 'convex' in question['text']
            return 'AB este paralelă cu CD.'
        if typ == 19:
            assert 'convex' in question['text'] and 'mijlocul ambelor bimediane' in question['text']
            result = a+c-b
            assert (a+c)/2 == (b+result)/2
            assert det(c-a, result-b) != 0
            return result
        if typ == 20:
            lower, upper, height = [S.Rational(g[key]) for key in ('lower', 'upper', 'height')]
            assert lower > 0 and upper > 0 and height > 0
            a, b, c, d = S.Matrix([0, 0]), S.Matrix([lower, 0]), S.Matrix([upper, height]), S.Matrix([0, height])
            t, r = S.symbols('t r')
            solutions = S.solve(a+t*(c-a)-(b+r*(d-b)), (t, r))
            assert 0 < solutions[t] < 1
            intersection = a+solutions[t]*(c-a)
            left = a+solutions[t]*(d-a)
            right = b+solutions[t]*(c-b)
            assert (left+right)/2 == intersection
            return S.sqrt((right-left).dot(right-left))
    raise AssertionError((section, typ))


def verify(question):
    point_givens_match_text(question)
    result = expected(question)
    options = question['options']
    assert len(options) == 4
    assert question['type'] == 'multiple_choice' and question['format'] == 'grid'
    assert question['explanation'].strip() and question['practice_scope']['adaptation']
    if isinstance(result, S.MatrixBase):
        values = []
        for option in options:
            match = PAIR.fullmatch(option['text'])
            assert match, option['text']
            values.append(tuple(vector(match.groups())))
        result = tuple(result)
    elif isinstance(result, str):
        values = [option['text'] for option in options]
    else:
        result = S.simplify(result)
        values = [S.Rational(option['text']) for option in options]
    assert len(set(values)) == 4, 'Mathematically duplicate options.'
    truth = [value == result for value in values]
    flags = [option['is_correct'] for option in options]
    assert all(type(flag) is bool for flag in flags)
    assert sum(truth) == sum(flags) == 1 and truth == flags, (question['practice_scope'], values, result, flags)


def main():
    questions = json.loads(TARGET.read_text(encoding='utf-8'))['questions']
    assert len(questions) == 243
    assert all(question['type'] == 'vector_workbench' for question in questions[:3])
    grids = [question for question in questions if question.get('practice_scope', {}).get('bank') == BANK]
    assert len(grids) == len({question['text'] for question in grids}) == 240
    expected_keys = {(section, typ, j) for section, count in [('2.1', 28), ('2.2', 20)]
                     for typ in range(1, count+1) for j in range(1, 6)}
    actual_keys = {(q['practice_scope']['section'], q['practice_scope']['type'], q['practice_scope']['variant']) for q in grids}
    assert actual_keys == expected_keys
    for question in grids:
        verify(question)
    positions = Counter(next(i for i, option in enumerate(question['options']) if option['is_correct']) for question in grids)
    assert positions == Counter({i: 60 for i in range(4)})
    print('OK: 240 grids, 48 types x 5 variants; 960 options; exact independent calculations and theorem review checks.')


if __name__ == '__main__':
    main()
