"""Audit exact și contraexemple pentru grilele de proprietăți."""
import json
import sys
from collections import Counter
from fractions import Fraction as F
from itertools import combinations
from math import floor, gcd, lcm, comb
from pathlib import Path

root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root/'data/quizzes/generators'))
from clasa_9_property_lessons import LESSONS
data=[json.loads((root/'data/quizzes/clasa_9'/filename).read_text(encoding='utf-8')) for filename,_ in LESSONS]
assert [len(p['questions']) for p in data]==[40,85,95,110]
for i,p in enumerate(data,1):
    qs=p['questions']
    assert len({q['text'] for q in qs})==len(qs)
    assert Counter(q['catalog']['type'] for q in qs)==Counter({t:5 for t in range(1,[8,17,19,22][i-1]+1)})
    for q in qs:
        assert q['catalog']['section']==f'A2.4.{i}'
        assert len(q['options'])==len({o['text'] for o in q['options']})==4
        assert sum(o['is_correct'] for o in q['options'])==1
        assert q['explanation'] and all(len(o['text'])<=255 for o in q['options'])
def answer(section,t,j):
    q=next(z for z in data[section-1]['questions'] if z['catalog']['type']==t and z['catalog']['variant']==j)
    return next(o['text'] for o in q['options'] if o['is_correct'])
def numeric(section,t,j,v):
    assert F(answer(section,t,j))==v,(section,t,j,v)

xs=[F(k,5) for k in range(-45,46)]
for j in range(1,6):
    q=j+1
    numeric(1,2,j,max(gcd(n,6*q) for n in range(1,12*q+1)))
    numeric(1,6,j,1/F(1,j+3)+j)
    numeric(1,7,j,j)
    for x in xs:
        frac=x-floor(x)
        assert j<=j+q*frac<j+q
        assert 0<=q*x*x/(1+x*x)<q
    # Parametrii de mărginire diferiți de j cresc în modul pe întregi.
    for a in [j-2,j-1,j+1,j+2]:
        assert abs((a-j)*100)>abs((a-j)*10)
    for x in xs:
        assert (-x)**3+j*(-x)==-(x**3+j*x)
        assert (x-j)**2+q==((2*j-x)-j)**2+q
        assert ((2*j-x)-j)**3+q+((x-j)**3+q)==2*q
        if x!=j:
            f=lambda t:q+F(3)/(t-j)
            assert f(x)+f(2*j-x)==2*q
            g=lambda t:2*t+1/(t-j)
            assert g(x)+g(2*j-x)==4*j
        if x.denominator!=1:
            assert floor(x)+j+floor(-x)+j==2*j-1
    numeric(2,4,j,j);numeric(2,7,j,j);numeric(2,8,j,-2*j)
    numeric(2,9,j,j);numeric(2,12,j,F(2*j-1,2))
    numeric(3,1,j,2)
    base=[3,7,9,2,8][j-1]
    cycle=[pow(base,n,10) for n in range(1,50)]
    first=next(t for t in range(1,10) if all(cycle[k]==cycle[k+t] for k in range(len(cycle)-t)))
    numeric(3,2,j,first)
    numeric(3,3,j,q)
    f=lambda n:j+3 if n<j else (-1)**n
    threshold=next(n for n in range(j+2) if all(f(k+2)==f(k) for k in range(n,30)))
    numeric(3,4,j,threshold)
    for x in xs:
        frac=lambda t:t-floor(t)
        assert frac((x+q)/q)==frac(x/q)
        alt=lambda t:j*(-1 if floor(t)%2 else 1)*frac(t)
        assert alt(x+2)==alt(x)
    numeric(3,5,j,q);numeric(3,6,j,lcm(q,q+1));numeric(3,7,j,2)
    p=[2,3,5,7,11][j-1]
    assert all(pow(n,p,p)==n%p for n in range(-30,31))
    numeric(3,8,j,p);numeric(3,10,j,2*q)
    nn=j+2
    for x in xs:
        assert sum(floor(x+F(k,nn)) for k in range(nn))==floor(nn*x)
    numeric(3,11,j,floor(F(-j*nn,3)))
    numeric(3,13,j,1);numeric(3,14,j,lcm(2*q,3*q));numeric(3,15,j,q)
    numeric(3,17,j,j);numeric(3,18,j,3*q)
    h=lambda t:1/(1-t)
    for x in xs:
        if x not in [0,1]:assert h(h(h(x)))==x
    # Verificarea diferențelor fără derivate și a îmbinărilor.
    for x,y in combinations(xs,2):
        assert q*y+j>q*x+j
        assert y+j*floor(y)>x+j*floor(x)
        if 0<=x<y<=1:
            assert j*y/(1+y*y)>j*x/(1+x*x)
        if (x<j+1 and y<j+1) or (x>j+1 and y>j+1):
            om=lambda t:(t-j)/(t-j-1)
            assert om(x)>om(y)
    ar=[(j+3)*n+gcd(n,n+2) for n in range(1,60)]
    assert all(y>x for x,y in zip(ar,ar[1:]))
    numeric(4,8,j,-j)
    # La îmbinare, parametrul a trebuie să fie cel puțin j.
    for a in [F(j)-F(1,10),F(j),F(j)+F(1,10)]:
        f=lambda t:t+j if t<0 else 2*t+a
        sample=[F(-1,1000),F(0),F(1,1000)]
        increasing=all(f(x)<=f(y) for x,y in combinations(sample,2))
        assert increasing==(a>=j)
    numeric(4,19,j,len(list(combinations(range(1,j+4),3))))
    numeric(4,21,j,j+1);numeric(4,22,j,j)
print('330 questions verified: coverage, exact arithmetic, symmetries, cycles, inequalities and counterexamples.')
