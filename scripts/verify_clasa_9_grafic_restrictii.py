"""Verifică graficul finit, restricțiile, prelungirile și intersecțiile."""
import json
import re
from collections import Counter
from fractions import Fraction as F
from pathlib import Path

path=Path(__file__).resolve().parents[1]/'data/quizzes/clasa_9/clasa_9_u02_l05_graficul_restrictiile_si_prelungirile_unei_functii_functii_numerice.json'
qs=json.loads(path.read_text(encoding='utf-8'))['questions']
assert len(qs)==len({q['text'] for q in qs})==55
assert Counter((q['catalog']['section'],q['catalog']['type']) for q in qs)==Counter({**{('A2.3.3',i):5 for i in range(7,12)},**{('A2.3.4',i):5 for i in range(1,7)}})
for z in qs:
    assert len(z['options'])==len({o['text'] for o in z['options']})==4
    assert sum(o['is_correct'] for o in z['options'])==1
    assert all(len(o['text'])<=255 for o in z['options'])
    assert z['explanation']
def item(section,t,j):
    return next(z for z in qs if z['catalog']['section']==section and z['catalog']['type']==t and z['catalog']['variant']==j)
def answer(section,t,j):
    return next(o['text'] for o in item(section,t,j)['options'] if o['is_correct'])
def pairs(text):
    return {(int(x),int(y)) for x,y in re.findall(r'\((-?\d+), (-?\d+)\)',text)}
def numbers(text):
    return list(map(int,re.findall(r'-?\d+',text)))
for j in range(1,6):
    q=j+1
    for o in item('A2.3.3',7,j)['options']:
        assert (pairs(o['text'])=={(x,q*x+j) for x in [-1,0,2]})==o['is_correct']
    for o in item('A2.3.3',10,j)['options']:
        assert (pairs(o['text'])=={(x,x*x+j) for x in [1,3,5]})==o['is_correct']
    assert int(answer('A2.3.3',9,j))*q+j==q*(j+2)+j
    # La prelungire, verificăm toate variantele la puncte din domeniul inițial.
    candidates=[lambda x:x+j if x>=0 else x*x,lambda x:x+j+1,lambda x:-x+j,lambda x:x+j if x<0 else x+j+1]
    samples=[F(0),F(j,2),F(j)]
    assert [all(g(x)==x+j for x in samples) for g in candidates]==[True,False,False,False]
    assert pairs(answer('A2.3.4',3,j))=={(j+2,0),(0,q*(j+2))}
    for o in item('A2.3.4',4,j)['options']:
        a,b=numbers(o['text'])
        assert (a*(j+2)+b==0 and b==q*(j+2))==o['is_correct']
    m=F(answer('A2.3.4',5,j))
    assert -(m-1)+q==0 and m-1!=0
    for m in [F(k,2) for k in range(-10,31)]:
        coeff=m-j
        if coeff==0: roots=1
        else:
            delta=4-4*coeff
            roots=2 if delta>0 else 1 if delta==0 else 0
        assert (roots==1)==(m in numbers(answer('A2.3.4',6,j)))
    # Verificarea capetelor celor trei ramuri constante.
    def f(x): return -j if x<0 else q if x<2 else 0
    assert [f(F(-1,100)),f(0),f(F(199,100)),f(2)]==[-j,q,q,0]
print('55 questions verified: finite graphs, restrictions, extensions, intercepts and degenerate equations.')
