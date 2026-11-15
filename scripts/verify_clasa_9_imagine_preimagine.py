"""Verificări exacte ale imaginilor finite și ale capetelor intervalelor."""
import json
import re
from collections import Counter
from fractions import Fraction as F
from pathlib import Path

path=Path(__file__).resolve().parents[1]/'data/quizzes/clasa_9/clasa_9_u02_l04_notiunea_imaginea_si_preimaginea_unei_functii.json'
data=json.loads(path.read_text(encoding='utf-8'))
qs=data['questions']
assert data['title']=='Imaginea și preimaginea unei funcții'
assert len(qs)==len({q['text'] for q in qs})==30
assert Counter(q['catalog']['type'] for q in qs)==Counter({i:5 for i in range(1,7)})
for item in qs:
    assert len(item['options'])==len({o['text'] for o in item['options']})==4
    assert sum(o['is_correct'] for o in item['options'])==1
    assert item['explanation']

def item(t,j):
    return next(z for z in qs if z['catalog']['type']==t and z['catalog']['variant']==j)
def answer(t,j):
    return next(o['text'] for o in item(t,j)['options'] if o['is_correct'])
def numbers(s):
    return list(map(int,re.findall(r'-?\d+',s)))
for j in range(1,6):
    f=dict(zip(range(1,5),[j,j+1,j,j+2]))
    assert set(numbers(answer(1,j)))=={f[x] for x in [1,2,3]}
    assert set(numbers(answer(2,j)))=={x for x in f if f[x] in {j,j+2}}
    q=j+1;offset=j-2
    lo,hi=numbers(answer(3,j))
    assert lo==-q*(j+2)+j and hi==q+j
    assert answer(3,j)[0]=='(' and answer(3,j)[-1]==']'
    assert numbers(answer(4,j))==[2*j+1]
    assert answer(4,j)[0]=='['
    for o in item(5,j)['options']:
        a,b=numbers(o['text'])
        valid=a>0 and a*j+b==q*j+offset and a*(j+2)+b==q*(j+2)+offset
        assert valid==o['is_correct']
    low=offset-q*(j+2);high=offset-q*j
    for o in item(6,j)['options']:
        a,b=numbers(o['text'])
        valid=a<0 and a*j+b==high and a*(j+2)+b==low
        assert valid==o['is_correct']
    for x in [F(k,2) for k in range(-20,41)]+[F(j)+F(1,100),F(j+2)+F(1,100)]:
        assert (low<=-q*x+offset<high)==(j<x<=j+2)
        assert (-q*x+j<=j-q*(2*j+1))==(x>=2*j+1)
print('30 questions verified: finite sets, coefficients, endpoint inclusion and exact inequalities.')
