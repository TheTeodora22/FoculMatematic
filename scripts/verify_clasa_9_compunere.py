"""Audit prin compuneri directe, enumerare și verificarea pragurilor."""
import json
import re
from collections import Counter
from fractions import Fraction as F
from itertools import product
from math import floor, sqrt, isclose
from pathlib import Path

path=Path(__file__).resolve().parents[1]/'data/quizzes/clasa_9/clasa_9_u02_l07_compunerea_functiilor.json'
data=json.loads(path.read_text(encoding='utf-8'))
qs=data['questions']
assert data['difficulty']=='hard'
assert len(qs)==len({q['text'] for q in qs})==115
assert Counter(z['catalog']['type'] for z in qs)==Counter({i:5 for i in range(1,24)})
for z in qs:
    assert len(z['options'])==len({o['text'] for o in z['options']})==4
    assert sum(o['is_correct'] for o in z['options'])==1
    assert all(len(o['text'])<=255 for o in z['options'])
    assert z['explanation']
def answer(t,j):
    item=next(z for z in qs if z['catalog']['type']==t and z['catalog']['variant']==j)
    return next(o['text'] for o in item['options'] if o['is_correct'])
def check(t,j,value):
    assert F(answer(t,j))==value,(t,j,value)
xs=[F(k,3) for k in range(-20,21)]
for j in range(1,6):
    q=j+1;n=j+2
    f=lambda x:2*(x-j)/(1+(x-j)**2)
    g=lambda y:j+(sqrt(1+y)-sqrt(1-y))/(sqrt(1+y)+sqrt(1-y))
    for u in [-.99,-.75,-.1,0,.1,.75,.99]:
        assert isclose(g(f(j+u)),j+u,rel_tol=1e-10,abs_tol=1e-10)
        assert isclose(f(g(u)),u,rel_tol=1e-10,abs_tol=1e-10)
    check(1,j,F(j)+F(1,n))
    f=lambda x:abs(x)
    g=lambda x:x-j
    check(3,j,f(g(-2))-g(f(-2)))
    # Calculul puterilor întregi, fără reducerea modulară din generator.
    gg=2**(j+3)%10
    check(4,j,3**gg%10)
    outer=lambda t:t*t if t<0 else t+1
    for x in xs+[F(j),F(j)-F(1,100),F(j)+F(1,100)]:
        actual=outer(x-j)
        expected=(x-j)**2 if x<j else x-j+1
        assert actual==expected
    for a in range(-3,5):
        equal=all(q*(2*x+a)+j==2*(q*x+j)+a for x in xs)
        assert equal==(a==F(answer(6,j)))
    result=1
    for _ in range(n):result=q*result+j
    check(7,j,result)
    # Involuția discontinuă păstrează cele două clase de argumente.
    for x in [sqrt(2),sqrt(3)+j]:
        assert isclose(2*j-(2*j-x),x)
    a,b=map(F,re.findall(r'-?\d+(?:/\d+)?',answer(12,j)))
    assert all(q*(a*x+b)+j==x for x in xs)
    for x in xs:
        recovered=F(2*q*x+q+j-j,q)
        assert recovered==2*x+1
    check(13,j,2*(j+2)+1)
    solutions=[x for x in xs if (x*x+j)**2+j==q*q+j]
    assert solutions==[F(-1),F(1)]
    check(15,j,j+2)
    assert all((q*k)//q==k for k in range(40))
    assert q*(1//q)!=1
    assert q**3!=(q+1)**2
    admissible=[a for a in range(-4,5) if all(a*(a*x+j)+j==x for x in xs)]
    assert admissible==[int(answer(18,j))]
    check(19,j,1)
    # Exemplu cu exact un punct fix pentru limita minimă.
    mapping={0:0}
    for k in range(1,2*j+1,2):mapping[k]=k+1;mapping[k+1]=k
    assert all(mapping[mapping[k]]==k for k in mapping)
    assert sum(mapping[k]==k for k in mapping)==1
    x=F(-3*j-1,3)
    for _ in range(n):x=x+j*floor(x)
    check(20,j,x)
    subsets=list(product([False,True],repeat=j))
    check(21,j,sum(any(s) for s in subsets))
    count=sum(sum(t)==3*j+3 for t in product([j,j+1,j+3],repeat=3))
    check(22,j,count)
    f=lambda x:F(4*j,3)-x
    assert all(f(x)+2*f(2*j-x)==x and f(f(x))==x for x in xs)
    check(23,j,f(j+1))
print('115 questions verified: exact iterations, finite enumeration, inverse compositions and branch thresholds.')
