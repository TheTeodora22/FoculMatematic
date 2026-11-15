"""Audit prin enumerare independentă a produselor și relațiilor finite."""
import json
import re
from collections import Counter
from fractions import Fraction as F
from itertools import product, combinations
from pathlib import Path

root=Path(__file__).resolve().parents[1]
payload=json.loads((root/'data/quizzes/clasa_9/clasa_9_u02_l03_functii_reper_cartezian_produs_cartezian_si_reprezentare_grafica.json').read_text(encoding='utf-8'))
qs=payload['questions']
assert len(qs)==len({z['text'] for z in qs})==70
assert Counter(z['catalog']['type'] for z in qs)==Counter({i:5 for i in range(1,15)})
for z in qs:
    assert len(z['options'])==len({o['text'] for o in z['options']})==4
    assert sum(o['is_correct'] for o in z['options'])==1
    assert all(len(o['text'])<=255 for o in z['options'])
    assert z['explanation']

def item(t,j):
    return next(z for z in qs if z['catalog']['type']==t and z['catalog']['variant']==j)
def correct(t,j):
    return next(o['text'] for o in item(t,j)['options'] if o['is_correct'])
def pairs(text):
    return {(int(a),int(b)) for a,b in re.findall(r'\((-?\d+), (-?\d+)\)',text)}
for j in range(1,6):
    assert pairs(correct(1,j))==set(product({j,j+1},{-j,0,j}))
    x,y=[(1,1),(2,2),(3,3),(4,4),(8,7)][j-1]
    destinations={(u,v) for u,v in product(range(1,9),repeat=2) if sorted([abs(u-x),abs(v-y)])==[1,2]}
    assert int(correct(2,j))==len(destinations)
    n=2*(j+2);m=3*(j+1)
    favorable=sum(u%2==0 and v%3==0 for u,v in product(range(1,n+1),range(1,m+1)))
    assert F(correct(6,j))==F(favorable,n*m)
    size=j+2
    relation={(x,y) for x,y in product(range(1,size+1),repeat=2) if x<=y}
    assert int(correct(10,j))==len(relation)
    subsets=[{j}|set(c) for k in range(3) for c in combinations([j+1,j+2],k)]
    cprod={(j,j)};dprod=set(product({j,j+1,j+2},repeat=2))
    assert int(correct(11,j))==sum(cprod<=set(product(a,b))<=dprod for a,b in product(subsets,repeat=2))
    for option in item(12,j)['options']:
        ps=pairs(option['text'])
        stable=all(a*d==b*c for (a,b),(c,d) in product(ps,repeat=2))
        assert stable==option['is_correct']
    assert int(correct(14,j))==len({(x,y) for x in range(1,j+3) for y in {2,4,6,8} if y not in {4,8,10}})
print('70 questions verified: 14 types x 5, exact enumeration and unique options.')
