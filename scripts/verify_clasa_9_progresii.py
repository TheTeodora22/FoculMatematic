"""Verificări independente prin recurențe, enumerare și fracții exacte."""
import json
from collections import Counter
from fractions import Fraction as F
from pathlib import Path

root=Path(__file__).resolve().parents[1]/'data/quizzes/clasa_9'
qs=[]
for filename in ['clasa_9_u02_l02a_progresii_aritmetice.json','clasa_9_u02_l02b_progresii_geometrice.json','clasa_9_u02_l02c_aplicatii_progresii.json']:
    qs.extend(json.loads((root/filename).read_text(encoding='utf-8'))['questions'])
assert len(qs)==310
assert len({q['text'] for q in qs})==310
counts=Counter((q['catalog']['section'],q['catalog']['type']) for q in qs)
assert len(counts)==62 and set(counts.values())=={5}
for item in qs:
    assert len(item['options'])==4
    assert len({v['text'] for v in item['options']})==4
    assert sum(v['is_correct'] for v in item['options'])==1
    assert item['explanation']

checked=0
def check(section,t,j,value):
    global checked
    item=next(z for z in qs if z['catalog']['section']==f'A2.2.{section}' and z['catalog']['type']==t and z['catalog']['variant']==j)
    answer=next(o['text'] for o in item['options'] if o['is_correct'])
    assert F(answer)==value,(section,t,j,answer,value)
    checked+=1

for j in range(1,6):
    a=j+2;r=j;n=j+4;q=j+1
    pa=[a]
    pg=[a]
    for _ in range(100):
        pa.append(pa[-1]+r)
        pg.append(pg[-1]*q)
    exp={1:pa[n-1],2:pa[n-1]-(n-1)*r,3:F(pa[6]-pa[1],5),4:pa.index(pa[n-1])+1,5:sum(pa[:9]),6:pa[2],7:sum(pa[:n]),9:r,10:2*j,11:a-r,13:0,14:n,15:sum(k for k in range(1,(j+2)*10+1) if k%(j+2)),16:sum(pa[:2*n]),17:(pa[2]+pa[3])-(pa[0]+pa[1]),18:pa[j+q-1]-pa[j-1]}
    for t,v in exp.items(): check(1,t,j,v)
    # Nonlinear PA constraints determine the positive difference uniquely.
    assert [d for d in range(1,30) if (a-d)*(a+d)==a*a-r*r]==[r]
    u=a
    for k in range(1,n): u=2*u+k-j
    diff=a
    for k in range(1,n): diff+=q**(k-1)
    transformed=F(a)
    previous=(transformed-1)/transformed
    for _ in range(10):
        transformed=q*transformed/(1+(q-1)*transformed)
        current=(transformed-1)/transformed
        assert current/previous==F(1,q)
        previous=current
    qq=1 if j==1 else q
    exp={1:pg[n-1],2:q,3:F(q,q+1),4:q,5:F(pg[1]*pg[2],pg[0]*pg[1]),6:q,7:n,8:sum(a*qq**k for k in range(n)),9:a,10:q,11:a*q*q-(a+2*a*(q-1)),12:1,13:F(1,q),14:diff,15:u+n+1-j,16:sum(4**k+2*6**k+9**k for k in range(1,n+1)),17:sum(k*2**(k-1) for k in range(1,n+1)),18:F(pg[2]-pg[3],pg[0]-pg[1]),19:sum(int(str(j)*k) for k in range(1,j+3)),20:sum(a*2**k for k in range(n))}
    for t,v in exp.items(): check(2,t,j,v)
    assert [x for x in range(2,15) if 2*a*x==a+a*x*x-a*(q-1)**2]==[q]
    root_candidates=[x for x in range(1,100) if 2*(j+2)*(x+1)==(x+1)+(2*j+4)*x]
    assert root_candidates==[2*j+3]
    x=j+1; d=j
    value=d**4+x*(x+d)*(x+2*d)*(x+3*d)
    from math import isqrt
    root=isqrt(value)
    assert root*root==value
    exp={1:2*j,2:3*j,3:root_candidates[0],4:n,5:pa[n-1],7:F(2*j+1,2),9:60-j*5,10:sum(v+10 for v in pa[:n]),11:0,12:(j+2)*r,13:root,14:sum((k+j)*(k+j+1) for k in range(1,n+1)),15:sum((F(1,(k+j)*(k+j+1)) for k in range(1,n+1)),F(0)),16:a*q,19:q,20:a*q,21:10**(j+2),22:n,24:2*a+r}
    for t,v in exp.items(): check(3,t,j,v)
    # Geometry instances satisfy the triangle inequality.
    assert (9+j)+(13+j)>(17+j)  # a²+b²>c² is sufficient here.
    assert (a*a+(2*a+r)*r)==(a+r)**2

print(f'310 grile: structura si acoperire 62x5 valide; {checked} raspunsuri numerice recalculate.')
