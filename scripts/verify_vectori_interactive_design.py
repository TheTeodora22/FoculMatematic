"""Verify design examples only: no Django imports, seed, database or UI writes."""
import json
from fractions import Fraction as F
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def vec(raw):
    return tuple(F(x) for x in raw)


def add(a, b):
    return tuple(x+y for x, y in zip(a, b))


def sub(a, b):
    return tuple(x-y for x, y in zip(a, b))


def mul(k, a):
    return tuple(F(k)*x for x in a)


def det(a, b):
    return a[0]*b[1]-a[1]*b[0]


def solve(e):
    points = {name:vec(value) for name, value in e.get('points', {}).items()}
    def displacement(pair):
        return sub(points[pair[1]], points[pair[0]])
    mode = e['mode']
    if mode == 'same_displacement':
        ref = displacement(e['reference'])
        return {'selected':[''.join(pair) for pair in e['candidates'] if displacement(pair) == ref]}
    if mode == 'classify_vector':
        u, v = displacement(e['reference']), displacement(e['candidate'])
        assert u != (0,0) and v != (0,0), 'Direction requires nonzero vectors.'
        relation = 'equal' if u == v else 'opposite' if u == mul(-1,v) else 'collinear' if det(u,v)==0 else 'noncollinear'
        return {'relation':relation}
    if mode == 'translate_endpoint':
        return {'endpoint':add(points[e['anchor']], displacement(e['reference']))}
    if mode in {'position_from_origin','change_origin'}:
        origin = e['origin'] if mode == 'position_from_origin' else e['new_origin']
        return {'vector':sub(points[e['target']], points[origin])}
    if mode == 'midpoint':
        return {'midpoint':mul(F(1,2),add(*(points[name] for name in e['segment'])))}
    u, v = vec(e['u']), vec(e.get('v',[0,0]))
    if mode == 'head_to_tail': return {'vector':add(u,v)}
    if mode == 'scale_vector': return {'vector':mul(e['scalar'],u)}
    if mode == 'close_polygon': return {'vector':mul(-1,add(u,v))}
    if mode == 'basis_decomposition':
        w, denominator = vec(e['w']), det(u,v)
        assert denominator != 0, 'A basis must be noncollinear.'
        coefficients = (det(w,v)/denominator, det(u,w)/denominator)
        assert add(mul(coefficients[0],u),mul(coefficients[1],v))==w
        return {'coefficients':coefficients}
    raise AssertionError(f'Unsupported design mode: {mode}')


def normalize(value):
    if isinstance(value, (list,tuple)): return tuple(F(x) for x in value)
    return value


def main():
    payload = json.loads((ROOT/'docs/vectori_in_plan_interactive.examples.json').read_text(encoding='utf-8'))
    assert payload['status']=='design_only_not_importable'
    examples = payload['examples']
    assert len({e['id'] for e in examples})==len(examples)
    for e in examples:
        computed = solve(e)
        for key, value in e['expected'].items():
            if key=='selected': assert computed[key]==value, e['id']
            else: assert normalize(computed[key])==normalize(value), (e['id'],key)
    # Verify generated live exercises independently of their production solver.
    live = []
    for path in (ROOT/'data/quizzes/clasa_9').glob('clasa_9_u05_*.json'):
        data = json.loads(path.read_text(encoding='utf-8'))
        live.extend(q for q in data['questions'] if q.get('type') == 'vector_workbench')
    if live:
        assert len(live) == len(examples)
        reference = {e['id']:e for e in examples}
        assert len({q['workshop']['id'] for q in live}) == len(examples)
        for question in live:
            example = reference[question['workshop']['id']]
            assert question['text'] == example['prompt']
            assert question['explanation']
            assert not {'answers','expected'} & question['interactive'].keys()
            computed = solve(question['interactive'])
            for key, value in example['expected'].items():
                if key == 'selected': assert computed[key] == value
                else: assert normalize(computed[key]) == normalize(value)
    # Boundary cases for the proposed mathematical contract.
    assert mul(0,(3,4))==(0,0)
    assert mul(F(-1,2),(4,6))==(-2,-3)
    assert det((1,2),(2,4))==0
    assert sub((-3,-2),(-3,-2))==(0,0)
    try:
        solve({'mode':'basis_decomposition','u':[1,2],'v':[2,4],'w':[3,6]})
    except AssertionError as exc:
        assert 'noncollinear' in str(exc)
    else:
        raise AssertionError('A collinear pair was incorrectly accepted as a basis.')
    print(f'{len(examples)} approved examples and {len(live)} live vector workshops verified exactly; no application data changed.')


if __name__=='__main__':
    main()
