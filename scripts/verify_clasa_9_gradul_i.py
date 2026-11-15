"""Audit independent pentru 315 grile A3; fără importarea generatorului.

Calcule exacte cu Fraction. Mulțimile de soluții sunt comparate pe fiecare
celulă determinată de pragurile lor, inclusiv capete și poli. Formulele afine
sunt verificate prin substituție, sistemele prin ecuațiile inițiale.
"""
import ast
import json
import operator
import re
from collections import Counter
from fractions import Fraction as F
from itertools import product
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
FILES=sorted((ROOT/'data/quizzes/clasa_9').glob('clasa_9_u03_l*.json'))
assert len(FILES)==5
COUNTS=[21,10,14,8,10]

def normalize(s):
    return str(s).replace('−','-').replace('²','**2').replace('ℝ','R').replace('∅','EMPTY')

def expr(s,**env):
    s=normalize(s).strip().rstrip('.')
    s=re.sub(r'\|([^|]+)\|',r'abs(\1)',s)
    s=re.sub(r'(\d)([xamt])',r'\1*\2',s)
    s=re.sub(r'(\))([xamt])',r'\1*\2',s)
    ops={ast.Add:operator.add,ast.Sub:operator.sub,ast.Mult:operator.mul,ast.Div:operator.truediv,ast.Pow:operator.pow}
    def walk(node):
        if isinstance(node,ast.Constant):return F(node.value)
        if isinstance(node,ast.Name):return env[node.id]
        if isinstance(node,ast.UnaryOp):return -walk(node.operand) if isinstance(node.op,ast.USub) else walk(node.operand)
        if isinstance(node,ast.BinOp):return ops[type(node.op)](walk(node.left),walk(node.right))
        if isinstance(node,ast.Call) and isinstance(node.func,ast.Name) and node.func.id in ['abs','min','max']:
            return {'abs':abs,'min':min,'max':max}[node.func.id](*[walk(arg) for arg in node.args])
        raise ValueError(ast.dump(node))
    return walk(ast.parse(s,mode='eval').body)

def inequality(s,**env):
    s=normalize(s).strip().rstrip('.').replace('≤','<=').replace('≥','>=').replace('≠','!=')
    if s=='R':return True
    if s=='EMPTY':return False
    parts=re.split(r'(<=|>=|!=|<|>|=)',s)
    result=True
    for i in range(1,len(parts),2):
        a,b=expr(parts[i-1],**env),expr(parts[i+1],**env)
        result &= {'<':operator.lt,'>':operator.gt,'<=':operator.le,'>=':operator.ge,'=':operator.eq,'!=':operator.ne}[parts[i]](a,b)
    return result

def parse_intervals(s):
    result=[]
    for part in s.split(' ∪ '):
        low,high=part[1:-1].split('; ')
        result.append((None if '∞' in low else F(normalize(low)),
                       None if '∞' in high else F(normalize(high)),
                       part[0]=='[',part[-1]==']'))
    return result

def contains(intervals,x):
    return any((a is None or x>a or (lc and x==a)) and
               (b is None or x<b or (rc and x==b)) for a,b,lc,rc in intervals)

def witnesses(boundaries):
    values=sorted(set(map(F,boundaries)))
    assert values
    return values+[values[0]-1,values[-1]+1]+[(a+b)/2 for a,b in zip(values,values[1:])]

def set_matches(candidate,truth,boundaries):
    ints=parse_intervals(candidate)
    thresholds=list(boundaries)+[v for row in ints for v in row[:2] if v is not None]
    return all(contains(ints,x)==bool(truth(x)) for x in witnesses(thresholds))

def condition_matches(candidate,truth,boundaries):
    return all(inequality(candidate,m=m)==bool(truth(m)) for m in witnesses(boundaries))

def piece_value(s,x,var='x'):
    env={var:x}
    s=normalize(s)
    if '; ' not in s:
        return expr(s.split(' pentru ')[0].split('h(x)=')[-1],**env)
    for clause in s.split('; '):
        clause=clause.strip().rstrip('.')
        if ' pentru ' in clause:
            value,condition=clause.split(' pentru ',1)
        elif ' dacă ' in clause:
            value,condition=clause.split(' dacă ',1)
        else:
            value,condition=clause.split(' la ',1)
        value=value.split('h(x)=')[-1].strip()
        if inequality(condition,**env):return expr(value,**env)
    raise ValueError('Nicio ramură: '+s)

def cases_value(s,parameter,x,name='m'):
    for clause in s.rstrip('.').split('; '):
        condition,result=clause.split(': ')
        if inequality(condition,**{name:parameter}):return inequality(result,**{name:parameter,'x':x})
    raise ValueError('Caz lipsă')

def pair_values(c):return tuple(F(v) for v in c)

def rank_type(m,j):
    # Gaussian elimination of [[m,1|j],[1,m|j]] over Q.
    rows=[[F(m),F(1),F(j)],[F(1),F(m),F(j)]]
    rank=0
    for col in (0,1):
        pivot=next((i for i in range(rank,2) if rows[i][col]),None)
        if pivot is None:continue
        rows[rank],rows[pivot]=rows[pivot],rows[rank]
        factor=rows[rank][col];rows[rank]=[v/factor for v in rows[rank]]
        for k in range(2):
            if k!=rank:
                factor=rows[k][col];rows[k]=[v-factor*w for v,w in zip(rows[k],rows[rank])]
        rank+=1
    if any(not a and not b and c for a,b,c in rows):return 'none'
    return 'unique' if rank==2 else 'infinite'

def described_rank(s,m):
    if s=='Soluție unică pentru orice m.':return 'unique'
    for clause in s.rstrip('.').split('; '):
        condition,result=clause.split(': ')
        if condition=='m≠±1':yes=m not in [-1,1]
        elif condition=='m=±1':yes=m in [-1,1]
        else:yes=inequality(condition,m=m)
        if yes:
            return 'infinite' if 'infinit' in result else ('none' if 'nicio' in result else 'unique')
    raise ValueError('Caz de sistem lipsă')

def valid(s,t,j,c):
    q=j+1
    # For the numerical and coefficient-valued questions, substitute in the
    # original equations rather than recalculate the generator's closed formula.
    if s==1:
        if t==1:
            x,y=pair_values(c);return 2*x-2*j==0 and y==-2*j
        if t==2:
            z=F(c);return z>0 and z*z==(3*j)**2+(4*j)**2
        if t in [3,4]:
            a,b=pair_values(c)
            if t==3:return a+b==q+j-2 and 3*a+b==3*q+j-2
            return all(a*(2*x-1)+b==2*q*x+(j-2-q) for x in [F(-1),F(0),F(1)])
        if t==5:
            x1,y1,x2,y2=map(F,c);return (x1,y1)!=(x2,y2) and all(y==-q*x+j for x,y in [(x1,y1),(x2,y2)])
        if t==6:
            a,b,lc,rc=c
            return all(contains([(F(a),F(b),lc,rc)],2*x+j)==(-j<=x<j+1)
                       for x in witnesses([-j-1,-j,0,j+1,j+2,F(a-j,2),F(b-j,2)]))
        if t==7:
            match=re.fullmatch(r'Ramura y=(.+) pentru x<1; ramura y=(.+) pentru x≥1; punct comun \(1; (\d+)\)\.',c)
            if not match:return False
            left,right,v=match.groups()
            return all(expr(left,x=x)==x+j for x in [-1,0]) and all(expr(right,x=x)==2*x+j-1 for x in [1,2]) and int(v)==j+1
        if t==8:
            m=F(c);return m>0 and F(4*j,m)**2+(4*j)**2==(5*j)**2
        if t==9:
            m=F(c);return m>0 and abs(F(-2*j,m)*2*j)/2==j
        if t==10:
            a=F(c);return all(a*(a*x+j)+j==x for x in [-1,0,1])
        if t==11:
            if j%2==0:return set_matches(c,lambda x:x>j,[j])
            a,b,lc,rc=c
            return all(contains([(F(a),F(b),lc,rc)],x)==(x.numerator//x.denominator==-j)
                       for x in witnesses([-j-1,-j,1-j,2-j,a,b]))
        if t==12:
            m=F(c);return (j+q-j)*(2-0)==(m-j)*(1-0)
        if t==13:return (F(c)-j)*1==-1
        if t==14:
            m=F(c);f=lambda x:x if x<j else 2*x-j
            return f(m)+f(m-j)==3*j
        if t==15:
            m=F(c);return m+2*j==(m+j if m<0 else 2*m+j)
        if t==16:
            a,b=pair_values(c);return a+b==j+4 and a+2*b==2*j+5
        if t==17:
            left,right,b=map(F,c);return -left+b==-j and right+b==2*j and b==0
        if t==18:
            a,b=pair_values(c)
            return all(a*x+b==(q*(-x)+j if j%2 else -q*(-x)) for x in [-2,-1])
        if t==19:return all(piece_value(c,x,'t')==abs(x+j)+abs(x-j) for x in witnesses([-j,0,j]))
        if t==20:
            b,d=pair_values(c);return j*j+b==q and q*j+d==q and j!=q
        if t==21:
            # All valid affine laws have nonzero rational slope; multiplying
            # a nonzero sqrt(2) coefficient preserves irrationality.
            return '\\sqrt2' in c
    if s==2:
        if t==1:return c=='Strict descrescătoare.' and -j<0
        if t==2:return condition_matches(c,lambda m:(m-j)>0,[-j,0,j])
        if t==3:
            match=re.match(r'm=(\d+); (.+)',c)
            if not match:return False
            m=F(match[1]);slope=m-j
            return slope*2+1==1-2*j and (('strict descrescătoare' in c and slope<0) or ('strict crescătoare' in c and slope>0) or ('constantă' in c and slope==0))
        if t==4:
            m=F(c);return m<0 and m*m+j==j+q*q
        if t==5:
            # (m-j)^2+1 is >=1; assess the alternatives at equality as well.
            return c=='Strict crescătoare pentru orice m∈ℝ.' and all((m-j)**2+1>0 for m in witnesses([j-1,j,j+1]))
        if t==6:return condition_matches(c,lambda m:(m-j)<=0,[0,j])
        if t==7:return F(c)==sum(1 for a,b in product(range(-20,0),range(j+7)) if 2*a+b==j)
        if t==8:
            def monotone(m):
                f=lambda x:j*x+(m-j)*(x.numerator//x.denominator)
                xs=sorted([F(-1,100),F(0),F(1,100),F(99,100),F(1),F(101,100)])
                return all(f(y)>f(x) for x,y in zip(xs,xs[1:]))
            return condition_matches(c,monotone,[j-1,j,j+1])
        if t==9:
            expected=[a*b>0 for a,b in [(-j,-j),(-j,q),(q,-j),(q,q)]]
            if c.startswith('Toate'):claimed=[('crescătoare' in c)]*4
            else:claimed=[not v.strip().startswith('Descrescătoare') and not v.strip().startswith('descrescătoare') for v in c.split(',')[:4]]
            return claimed==expected
        if t==10:
            match=re.match(r'f\(f\(x\)\)=([−\-]?\d+)x; (.+)',c)
            if not match:return False
            k=F(normalize(match[1]))
            # Q maps through +q twice; an irrational argument stays irrational
            # through -q twice. Both branches must agree with k*x.
            return k==q*q and 'strict crescătoare' in match[2]
    if s==3:
        if t==1:return set_matches(c,lambda x:-q*x+q*j>0,[j])
        if t==2:return set_matches(c,lambda x:x!=j+2 and F(x-j,x-j-2)>=0,[j,j+2])
        if t==3:
            sign=lambda z: (z>0)-(z<0)
            return all(piece_value(c,x)==sign(x-j)+2*x*sign(j-x) for x in witnesses([j-1,j,j+1]))
        if t==4:return all(piece_value(c,x)==x+abs(x-j) for x in witnesses([j-1,j,j+1]))
        if t==5:
            m=F(c);return m-j>0 and (m-j)*q-q==0
        if t==6:
            for m in [-2,F(0),F(1,2),F(1),F(2)]:
                a=m*(m-1);cuts=[F(-1),F(0),F(1)]
                if a:cuts.append(F(-j,a))
                for x in witnesses(cuts):
                    if cases_value(c,a,x,'a')!=(a*x+j>0):return False
            return True
        if t==7:return set_matches(c,lambda x:q*x-j>=-x+q*j,[j])
        if t==8:return set_matches(c,lambda x:x not in [j,j+1] and 1/(x-j)>=1/(x-j-1),[j,j+1])
        if t==9:return set_matches(c,lambda m:m!=-j and F(m-j,m+j)>0,[-j,j])
        if t==10:return all(piece_value(c,x)==max(q*x-j,j) for x in witnesses([F(2*j,q)-1,F(2*j,q),F(2*j,q)+1]))
        if t==11:return set_matches(c,lambda x:abs(x-j)+abs(x-j-2)<=4,[j-1,j,j+2,j+3])
        if t==12:
            for m in witnesses([j-1,j,j+1]):
                cuts=[F(-1),F(0),F(1)]
                if m!=j:cuts.append(F(q,m-j))
                for x in witnesses(cuts):
                    if cases_value(c,m,x)!=((m-j)*x<=q):return False
            return True
        if t==13:
            def truth(x):
                if x==j+1:return False
                g=F(x-j,x-j-1);return (g if g<0 else g-1)>0
            return set_matches(c,truth,[j,j+1])
        if t==14:return set_matches(c,lambda m:all(m*x+j>0 for x in [-1,1]),[-j,j])
    if s==4:
        if t==1:
            pts={1:[(1,0),(1,2),(2,-1),(2,3)],2:[(2,0),(2,2),(0,3),(4,3)],
                 3:[(3,0),(4,1),(5,2),(6,3)],4:[(4,0),(5,1),(4,1),(5,3)],
                 5:[(5,0),(6,1),(5,1),(6,2)]}[j]
            a,b,d,e=pts
            u=(b[0]-a[0],b[1]-a[1]);v=(e[0]-d[0],e[1]-d[1])
            determinant=u[0]*v[1]-u[1]*v[0]
            offset=(d[0]-a[0],d[1]-a[1])
            if determinant==0:
                kind='Coincidente.' if u[0]*offset[1]-u[1]*offset[0]==0 else 'Paralele distincte.'
            else:kind='Perpendiculare.' if sum(x*y for x,y in zip(u,v))==0 else 'Secante, dar nu perpendiculare.'
            return c==kind
        if t in [2,3,4,6]:
            x,y=pair_values(c)
            if t==2:return x+y==2*j+1 and 2*x-y==j-1
            if t==3:return 2*(x-1)+y==3*j-1 and x-(y+1)==-2
            if t==4:return x!=0 and y!=0 and 1/x+1/y==F(2*j+1,j*q) and 1/x-1/y==F(1,j*q)
            return x+y!=0 and x-y!=0 and 1/(x+y)+1/(x-y)==F(3,j) and 1/(x+y)-1/(x-y)==F(-1,j)
        if t==5:
            actual={(F(a),F(b)) for a,b in re.findall(r'\(([-\d/]+); ([-\d/]+)\)',c)}
            expected={(F(x),F(y)) for x,y in product(range(-q,q+1),repeat=2) if abs(x)+abs(y)==2*j+1 and abs(x)-abs(y)==-1}
            return actual==expected
        if t==7:return all(described_rank(c,m)==rank_type(m,j) for m in [-2,-1,0,1,2])
        if t==8:return F(c)==F(sum(rank_type(m,1)=='unique' for m in range(-j,j+1)),2*j+1)
    if s==5:
        if t==1:return set_matches(c,lambda x:x>=j and 2*x<=2*j+6,[j,j+3])
        if t==2:return set_matches(c,lambda x:abs(2*x-j)<=x+j,[0,2*j])
        if t==3:return set_matches(c,lambda x:x!=j+1 and F(x-j,x-j-1)>=0 and F(x-j-2,x-j-1)<=0,[j,j+1,j+2])
        if t==4:return set_matches(c,lambda x:abs(x-j)<=2 and abs(x-j-1)<2,[j-2,j-1,j+2,j+3])
        if t==5:
            x=F(c);return max(x+j,2*x-j)==3*j
        if t==6:return all(piece_value(c,x)==min(x+j,-x+j,2*j) for x in witnesses([-j,0,j]))
        if t==7:return set_matches(c,lambda x:x!=j and 0<=1/(x-j)<=x-j,[j,j+1])
        if t==8:
            match=re.fullmatch(r'\[(.+); (.+)\] pentru (.+); ∅ în rest\.',c)
            if not match:return False
            low,high,condition=match.groups()
            for x in witnesses([-j,0,j]):
                a,b=expr(low,x=x),expr(high,x=x)
                for y in witnesses([x,x+j,0,j,a,b]):
                    claimed=inequality(condition,x=x) and a<=y<=b
                    if claimed!=(x<=y<=x+j and 0<=y<=j):return False
            return True
        if t==9:return condition_matches(c,lambda m:all(x+m-j>0 and -x+q>0 for x in [-1,1]),[j-1,j+1])
        if t==10:
            return condition_matches(c,lambda m:(m-j)>=0,[j-1,j,j+1])
    raise AssertionError(('Type sans oracle',s,t))

def display_matches(s,t,c,text):
    # Numerical metadata cannot contradict displayed options.
    if not isinstance(c,list):return str(c)==text
    def pair(x,y):return f'({x}; {y})'
    if s==1 and t==1:return text==f'A({c[0]}; 0), B(0; {c[1]})'
    if s==1 and t in [3,4,18]:return text==rf'\(f(x)={c[0]}x{int(c[1]):+d}\)'
    if s==1 and t==5:
        x,y,z,w=c
        # The generated display uses a true minus in the fixed -1 label.
        return normalize(text)==f'A{pair(x,y)}, B{pair(z,w)}'.replace('A(', 'A(')
    if s==1 and t in [6,11]:
        a,b,l,r=c;return text==('[' if l else '(')+f'{a}; {b}'+(']' if r else ')')
    if s==1 and t==17:
        a,b,d=c
        return normalize(text)==f'f(x)={a}x'+('' if d==0 else '+1')+f' pentru x≤0; f(x)={b}x'+('' if d==0 else '+1')+' pentru x≥0.'
    return text==pair(*c)

total=0
for section,path in enumerate(FILES,1):
    data=json.loads(path.read_text(encoding='utf-8'))
    questions=data['questions']
    assert len(questions)==COUNTS[section-1]*5
    assert len({z['text'] for z in questions})==len(questions)
    assert Counter(z['catalog']['type'] for z in questions)==Counter({t:5 for t in range(1,COUNTS[section-1]+1)})
    for item in questions:
        v=item['verification'];s,t,j=v['section'],v['type'],v['variant']
        assert s==section and item['catalog']['section']==f'A3.{s}'
        assert item['text'] and item['explanation']
        opts=item['options'];assert len(opts)==4==len({o['text'] for o in opts})
        assert all(len(o['text'])<=255 for o in opts)
        assert all(display_matches(s,t,c,o['text']) for c,o in zip(v['candidates'],opts)),(s,t,j,'display')
        truth=[]
        for candidate in v['candidates']:
            try:truth.append(bool(valid(s,t,j,candidate)))
            except (ZeroDivisionError,ValueError,KeyError,IndexError):truth.append(False)
        assert truth==[o['is_correct'] for o in opts],(s,t,j,truth,opts)
        assert sum(truth)==1,(s,t,j,'not unique')
        total+=1
    print(f'A3.{section}: {len(questions)} verified')
print(f'{total} questions, {4*total} option checks: OK')
