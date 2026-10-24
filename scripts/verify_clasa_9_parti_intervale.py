"""Verificări independente ale grilelor din subcapitolele 1.5 și 1.6.

Compară mulțimi de soluții și operații de mulțimi prin apartenență, cu toate
capetele raționale și puncte din vecinătatea lor. Nu înlocuiește demonstrațiile.
"""
import ast
import json
import math
import re
import sys
from collections import Counter
from decimal import Decimal, localcontext
from fractions import Fraction as F
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def real(text, env=None):
    env=env or {}
    text=text.strip().replace("−","-").replace("²","**2")
    text=re.sub(r"√(\d+)",r"sqrt(\1)",text)
    def evaluate(node):
        if isinstance(node,ast.Constant) and isinstance(node.value,int): return F(node.value)
        if isinstance(node,ast.Name): return env[node.id]
        if isinstance(node,ast.UnaryOp) and isinstance(node.op,ast.USub): return -evaluate(node.operand)
        if isinstance(node,ast.BinOp):
            a,b=evaluate(node.left),evaluate(node.right)
            if isinstance(node.op,ast.Add):return a+b
            if isinstance(node.op,ast.Sub):return a-b
            if isinstance(node.op,ast.Mult):return a*b
            if isinstance(node.op,ast.Div):return a/b
            if isinstance(node.op,ast.Pow):return a**int(b)
        if isinstance(node,ast.Call) and isinstance(node.func,ast.Name) and node.func.id=='sqrt':
            return math.sqrt(evaluate(node.args[0]))
        raise ValueError(text)
    return evaluate(ast.parse(text,mode='eval').body)


def contains(solution,x,env=None):
    if solution=='R':return True
    if solution=='∅':return False
    if solution.startswith('R∖'):return not contains(solution[2:],x,env)
    for part in solution.split(' ∪ '):
        part=part.strip()
        if part.startswith('{'):
            if x in {real(v,env) for v in part[1:-1].split(';')}:return True
        else:
            lo,hi=part[1:-1].split(';')
            left=True if '∞' in lo else x>=real(lo,env) if part[0]=='[' else x>real(lo,env)
            right=True if '∞' in hi else x<=real(hi,env) if part[-1]==']' else x<real(hi,env)
            if left and right:return True
    return False


def correct(q):return next(o['text'] for o in q['options'] if o['is_correct'])


def samples_for(q,extra=()):
    values={F(i,12) for i in range(-144,145)}|{F(-100),F(100)}|set(extra)
    for o in q['options']:
        for token in re.findall(r'[−-]?\d+(?:/\d+)?',o['text']):
            v=real(token)
            values.update([v-F(1,100),v,v+F(1,100)])
    return sorted(values)


def check_set(q,predicate,env=None,extra=()):
    points=samples_for(q,extra)
    expected=[bool(predicate(x)) for x in points]
    assert [contains(correct(q),x,env) for x in points]==expected,q['text']
    for option in q['options']:
        if not option['is_correct']:
            assert any(contains(option['text'],x,env)!=v for x,v in zip(points,expected)),(q['text'],option)


def load(filename,section,counts):
    data=json.loads((ROOT/'data/quizzes/clasa_9'/filename).read_text(encoding='utf-8'))
    qs=data['questions']
    assert len(qs)==80 and len({q['text'] for q in qs})==80
    assert Counter(q['catalog']['type'] for q in qs)==counts
    for q in qs:
        assert q['catalog']['section']==section and q['format']=='grid' and q['explanation']
        assert len(q['options'])==len({o['text'] for o in q['options']})==4
        assert sum(o['is_correct'] for o in q['options'])==1
    return {(q['catalog']['type'],q['catalog']['variant']):q for q in qs}


def verify_floor(by):
    for v,x in enumerate(map(F,['-3.28','2.75','-0.04','5']),1):
        k,r=[real(t) for t in correct(by[1,v])[1:-1].split(';')]
        assert k<=x<k+1 and x==k+r and 0<=r<1
    for v,(k,r,m) in enumerate([(2,F(3,4),5),(-2,F(1,3),4),(0,F(9,10),3),(3,F(1,5),5)],1):
        assert real(correct(by[2,v]))==math.floor(m*(k+r))
    for v,n in enumerate([1,3,5,10],1):assert real(correct(by[3,v]))==math.isqrt(n*n+n)
    for v,n in enumerate([2,4,7,9],1):
        s=sum(F(1,k*(k+1)) for k in range(1,n+1))
        assert real(correct(by[4,v]))==s-math.floor(s)
    with localcontext() as ctx:
        ctx.prec=70
        for v,(a,b) in enumerate([(2,3),(5,7),(8,10),(13,17)],1):
            assert real(correct(by[5,v]))==int(Decimal(a).sqrt()+Decimal(b).sqrt())
        for v,(n,k) in enumerate([(2,2),(5,3),(6,2),(10,3)],1):
            A=1/(Decimal(n+1).sqrt()-Decimal(n).sqrt())-Decimal(n).sqrt()
            assert real(correct(by[7,v]))==int(k*A)
    for v,n in enumerate([8,15,24,35],1):assert real(correct(by[6,v]))==sum(math.isqrt(k) for k in range(1,n+1))
    for v,(s,k,r) in enumerate([(5,2,F(1,4)),(3,-1,F(1,3)),(0,-2,F(2,5)),(8,3,F(3,4))],1):
        x=k+1-r;y=s-x
        assert math.floor(x)==k and y-math.floor(y)==r and real(correct(by[8,v]))==x*y
    for v,(r,s) in enumerate([(F(1,5),F(3,10)),(F(7,10),F(3,5)),(F(2,5),F(3,5)),(F(0),F(9,10))],1):
        assert real(correct(by[9,v]))==math.floor(r+s)
    assert correct(by[10,1])=='[xy]≥[x][y]'
    assert real(correct(by[10,2]))==math.floor(F(18,10)*F(24,10))-math.floor(F(18,10))*math.floor(F(24,10))
    assert math.floor(F(1,4))<math.floor(F(-1,2))**2 and correct(by[10,3])=='[xy]<[x][y]'
    assert real(correct(by[10,4]))==math.floor(F(29,10)*F(39,10))==11
    for kind,ns in [(11,[2,3,4,5]),(12,[3,5,8])]:
        for v,n in enumerate(ns,1):assert real(correct(by[kind,v]))==math.floor(n*(1-F(1,2*n)))==n-1
    assert real(correct(by[13,2]))==1-F(2,7) and real(correct(by[13,3]))==0
    assert correct(by[13,1])=='[−x]=−[x]−1'
    assert [correct(by[14,v]) for v in [1,2,3]]==['x∈Z','x∈R∖Z','x∈Z']
    predicates={
        15:[lambda x:math.floor(3*x-6)==7,lambda x:math.floor(2*x+1)==-2,lambda x:math.floor(-2*x+3)==1],
        16:[lambda x:math.floor(2*x)==x+1,lambda x:math.floor(2*x)==x+F(1,2),lambda x:math.floor(2*x)==x-F(1,3)],
        17:[lambda x:7*math.floor(x)**2-8*math.floor(x)+1==0,lambda x:math.floor(x)**2-math.floor(x)-2==0,lambda x:(math.floor(x)-3)**2==0],
        18:[lambda x:x*x==math.floor(x),lambda x:4*x**4-4*math.floor(x*x)+1==0,lambda x:x*x+math.floor(x*x)==2],
        19:[lambda x:math.floor(x-5)==math.floor(-x-1),lambda x:math.floor(x*x-x-6)==math.floor(-x*x+x-2),lambda x:math.floor((x-1)**2-2)==math.floor(-(x-1)**2-4)],
    }
    for kind,functions in predicates.items():
        for v,predicate in enumerate(functions,1):check_set(by[kind,v],predicate)
    for v,n in enumerate([7,11,19],1):assert real(correct(by[20,v]))==sum(math.floor(F(k+1,2)) for k in range(1,n+1))
    for v,(p,n) in enumerate([(3,8),(4,-3),(5,12)],1):assert real(correct(by[21,v]))==sum(math.floor(F(n+j,p)) for j in range(p))
    assert [correct(by[22,v]) for v in [1,2,3]]==['p∈Z','x=1','p=1']
    for x in [F(i,7) for i in range(-21,22)]:
        for n in range(1,10):assert sum(math.floor(x+F(k,n)) for k in range(n))==math.floor(n*x)
    for v,(n,x) in enumerate([(3,F(7,10)),(4,F(-1,5))],1):assert real(correct(by[23,v]))==sum(math.floor(x+F(k,n)) for k in range(n))
    assert correct(by[23,3])=='Σ[k=0,…,n−1] [x+k/n]=[nx]'


def verify_intervals(by):
    for v,I in enumerate(['(−5; 5)','[−2; 3)','(1; 4]','(−∞; 2)'],1):
        assert [contains(I,real(o['text'])) for o in by[1,v]['options']]==[o['is_correct'] for o in by[1,v]['options']]
    for v,I in enumerate(['[−2;3)','(−1;4]','(−∞;5]','[2;+∞)'],1):
        q=by[2,v];points=samples_for(q)
        def inequality(text,x):
            parts=re.split(r'(<=|>=|<|>)',text.replace('≤','<=').replace('≥','>=').replace('−','-'))
            for i in range(1,len(parts),2):
                a,b=real(parts[i-1],{'x':x}),real(parts[i+1],{'x':x})
                result={'<':a<b,'<=':a<=b,'>':a>b,'>=':a>=b}[parts[i]]
                if not result:return False
            return True
        expected=[contains(I,x) for x in points]
        for o in q['options']:
            matches=[inequality(o['text'],x) for x in points]==expected
            assert matches==o['is_correct']
    # Verificare independentă a reuniunilor, intersecțiilor și diferențelor.
    pairs={3:[('[−2;3]','(1;5)'),('(−2;0)','(0;3)'),('[−1;2)','[2;4]'),('(−∞;−1]','(−1;+∞)')],
           4:[('[−2;3]','(1;5)'),('[−1;2]','[2;4]'),('(−1;2)','[2;4]'),('(−∞;3]','[−2;+∞)')],
           8:[('[−2;5]','(0;3]'),('(0;4)','[1;3]'),('[−1;2]','[−1;2]'),('R','(−1;1)')],
           9:[('[−3;4]','(0;2]'),('(−2;5)','[−1;3)'),('[0;2]','{1}'),('[1;3]','[1;3)')]}
    for kind,items in pairs.items():
        for v,(a,b) in enumerate(items,1):
            def pred(x):
                aa,bb=contains(a,x),contains(b,x)
                return aa or bb if kind==3 else aa and bb if kind==4 else aa and not bb
            check_set(by[kind,v],pred)
    for v,expected in enumerate([6,5,1,3],1):assert real(correct(by[5,v]))==expected
    for kind,ts in [(6,[0,1,2,-1]),(7,[0,1,-2,3]),(16,[0,1,-1,3])]:
        for v,t in enumerate(ts,1):
            result=tuple(real(s) for s in correct(by[kind,v])[1:-1].split(';'))
            expected=(t-3,t+4) if kind==6 else (t+1,t+2) if kind==7 else (t-2,t+5)
            assert result==expected
    for v,(a,b,union) in enumerate([('[−2;2]','[0;4]',True),('[−2;2]','[0;4]',False),('(−∞;1)','(2;+∞)',True),('(−∞;1]','[1;+∞)',False)],1):
        check_set(by[10,v],lambda x:not (contains(a,x) or contains(b,x)) if union else not (contains(a,x) and contains(b,x)))
    for v,alist in [(1,[F(0)]),(2,[F(1,4),F(3,4)]),(3,[F(1)]),(4,[F(3,2),F(3)])]:
        for a in alist:check_set(by[11,v],lambda x:0<=x<=a and a-1<=x<=a+1,{'a':a},[a-1,a,a+1])
    for v in range(1,5):
        a,b=(F(2),F(2)) if v==4 else (F(1),F(4))
        H,G,A=2*a*b/(a+b),math.sqrt(a*b),(a+b)/2
        def pred(x):
            i,j=H<=x<=G,G<=x<=A
            return i and j if v==1 else i or j if v in (2,4) else i and not j
        check_set(by[12,v],pred,{'H':H,'G':G,'A':A},[H,G,A])
    check_set(by[13,1],lambda x:F(2,3)<=x<=F(4,3))
    assert correct(by[13,2])==correct(by[13,3])=='{1}'
    check_set(by[13,4],lambda x:F(1,2)<=x<=F(3,2))
    for v in range(1,5):
        def pred(a):
            if a<0:return False
            return {n for n in range(100) if (a<=n<a+1 if v==1 else a<n<=a+1 if v==2 else a<=n<=a+1 if v==3 else a<n<=a*a)}=={3}
        check_set(by[14,v],pred)
    for v,(a,b) in enumerate([(F(1,4),F(1,2)),(F(2),F(3)),(F(1,2),F(2)),(F(1,2),F(3))],1):
        check_set(by[15,v],lambda x:a<=x<=b and 1/b<=x<=1/a,{'a':a,'b':b},[a,b,1/a,1/b])
    for v,x in [(1,F(1,2)),(2,F(1)),(3,F(2)),(4,F(1,2))]:
        check_set(by[17,v],lambda y:(-x<=y<=x and -x*x<=y<=x*x) if v!=4 else (-x<=y<=x or -x*x<=y<=x*x),{'x':x},[-x,x,-x*x,x*x])
    for v,x in [(1,F(2)),(2,F(-3)),(3,F(1,2))]:
        r=(x+1)/(x-1)
        check_set(by[18,v],lambda y:(0<=y<=r and 0<=y<=1) if v<3 else (r<=y<=0 and -1<=y<=1),{'r':r},[r])
    for v,pred in enumerate([lambda x:abs(x)<=2 and abs(x+1)>=3,lambda x:abs(x-1)<2 and abs(x)>1,lambda x:abs(x)<=3 and not abs(x-1)<1],1):check_set(by[19,v],pred)
    for v,(a,b) in enumerate([(F(1,4),F(3,4)),(F(5,4),F(7,4)),(F(-3,4),F(-1,4))],1):
        text=correct(by[20,v]);interval=text.split('I=',1)[1].split(', I∩Z=')[0]
        assert text.endswith('I∩Z=∅') and not any(a<=k<=b for k in range(-10,11))
        assert real(interval[1:-1].split(';')[0])==a and real(interval[1:-1].split(';')[1])==b
    assert correct(by[21,1])=='a∈{0;1;2;3;4;5;6;7}' and correct(by[21,2])=='a∈[0;7]∖Z'
    for a in [F(k,12) for k in range(85)]:
        closed=sum(a<=n<=a+3 and 0<=n<=10 for n in range(11))
        opened=sum(a<n<a+3 and 0<=n<=10 for n in range(11))
        assert (closed==4)==(a.denominator==1) and (opened==3)==(a.denominator!=1)
    check_set(by[21,3],lambda a:a>=1 and sum(0<=n<=a and 1<=n<=10 for n in range(11))==3)


def main():
    floors=load('clasa_9_numere_reale_1_5_parte_intreaga_fractionara.json','A1.1.5',{i:4 if i<=11 else 3 for i in range(1,24)})
    intervals=load('clasa_9_numere_reale_1_6_intervale.json','A1.1.6',{i:4 if i<=17 else 3 for i in range(1,22)})
    verify_floor(floors);verify_intervals(intervals)
    sys.path.insert(0,str(ROOT/'data/quizzes/generators'))
    from gen_clasa_9_numere_reale_operatii import build_lessons
    for filename,payload in build_lessons().items():
        assert json.loads((ROOT/'data/quizzes/clasa_9'/filename).read_text(encoding='utf-8'))==payload
    print('160 grile verificate; 23/23 tipuri la 1.5 si 21/21 la 1.6; solutii rationale, intervale, capete, cazuri parametrice si generator verificate.')


if __name__=='__main__':main()
