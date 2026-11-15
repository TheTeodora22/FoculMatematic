"""Independent exact audit of 200 G4 triangle/area/radius adaptations.

No generator import, no stored expected answers, no eval/sympify/parse_expr.
Builds valid triangles/polygons, actual centers/projections, counts ambiguous
area cases, and parses every numeric LaTeX answer using a narrow grammar.
"""
import ast
import json
import re
from collections import Counter
from pathlib import Path

import sympy as S

ROOT=Path(__file__).resolve().parents[1]
TARGET=ROOT/'data/quizzes/clasa_9/clasa_9_u08_l03_rezolvarea_triunghiurilor_raza_cercului_circumscris_si_inscris_formule.json'
BANK='g4_triunghiuri_v1'


def exact(raw):
    """Safe arithmetic reader for bounded repository audit data."""
    if isinstance(raw,S.Rational): return raw
    if type(raw) is int: return S.Integer(raw)
    assert isinstance(raw,str) and len(raw)<1000
    def walk(node):
        if isinstance(node,ast.Constant) and type(node.value) is int: return S.Integer(node.value)
        if isinstance(node,ast.UnaryOp) and isinstance(node.op,(ast.UAdd,ast.USub)):
            value=walk(node.operand)
            return value if isinstance(node.op,ast.UAdd) else -value
        if isinstance(node,ast.BinOp):
            a,b=walk(node.left),walk(node.right)
            if isinstance(node.op,ast.Add): return a+b
            if isinstance(node.op,ast.Sub): return a-b
            if isinstance(node.op,ast.Mult): return a*b
            if isinstance(node.op,ast.Div): assert b!=0; return a/b
            if isinstance(node.op,ast.Pow): assert b.is_Rational and abs(b)<=8; return a**b
        if isinstance(node,ast.Call) and isinstance(node.func,ast.Name) and node.func.id=='sqrt' and len(node.args)==1 and not node.keywords:
            value=walk(node.args[0]); assert value>=0; return S.sqrt(value)
        raise AssertionError(ast.dump(node))
    return S.simplify(walk(ast.parse(raw,mode='eval').body))


def latex_number(raw):
    assert raw.startswith(r'\(') and raw.endswith(r'\)')
    body=raw[2:-2].replace(r'\left','').replace(r'\right','')
    token_pattern=r'\\(?:frac|sqrt|cdot)|\d+|[{}()+\-*/^]'
    assert not re.sub(token_pattern,'',body).strip(), body
    tokens=re.findall(token_pattern,body); pos=0
    def atom():
        nonlocal pos
        assert pos<len(tokens)
        token=tokens[pos]; pos+=1
        if token in ('+','-'):
            value=atom(); return value if token=='+' else -value
        if token.isdigit(): value=S.Integer(token)
        elif token in ('{','('):
            value=expression(); close='}' if token=='{' else ')'
            assert tokens[pos]==close; pos+=1
        elif token==r'\sqrt':
            value=atom(); assert value>=0; value=S.sqrt(value)
        elif token==r'\frac':
            first,second=atom(),atom(); assert second!=0; value=first/second
        else: raise AssertionError(token)
        if pos<len(tokens) and tokens[pos]=='^':
            pos+=1; exponent=atom(); assert exponent.is_Rational and abs(exponent)<=8
            value=value**exponent
        return value
    def term():
        nonlocal pos
        value=atom()
        while pos<len(tokens) and tokens[pos] not in ('+','-','}',')'):
            if tokens[pos] in ('*',r'\cdot','/'):
                op=tokens[pos]; pos+=1; next_value=atom()
                if op=='/': assert next_value!=0; value/=next_value
                else: value*=next_value
            else: value*=atom()
        return value
    def expression():
        nonlocal pos
        value=term()
        while pos<len(tokens) and tokens[pos] in ('+','-'):
            op=tokens[pos]; pos+=1; other=term()
            value=value+other if op=='+' else value-other
        return value
    result=expression(); assert pos==len(tokens)
    return S.simplify(result)


def point(raw): return S.Point(*[exact(value) for value in raw])
def degrees(raw):
    value=exact(raw); assert 0<value<180
    return value*S.pi/180
def same(a,b): return S.simplify(a-b)==0
def dot(a,b): return S.simplify(a.dot(b))
def cross(a,b): return S.simplify(a.x*b.y-a.y*b.x)
def area(vertices):
    return S.simplify(abs(sum(vertices[i].x*vertices[(i+1)%len(vertices)].y-vertices[(i+1)%len(vertices)].x*vertices[i].y for i in range(len(vertices))))/2)
def side_lengths(vertices):
    a,b,c=vertices
    values=[b.distance(c),c.distance(a),a.distance(b)]
    assert all(value>0 for value in values)
    assert all(values[i]+values[(i+1)%3]>values[(i+2)%3] for i in range(3))
    return values
def from_sides(a,b,c):
    assert a>0 and b>0 and c>0 and a+b>c and a+c>b and b+c>a
    x=(c*c+a*a-b*b)/(2*a)
    y=S.sqrt(S.simplify(c*c-x*x)); assert y>0
    vertices=[S.Point(x,y),S.Point(0,0),S.Point(a,0)]
    assert all(same(one,two) for one,two in zip(side_lengths(vertices),[a,b,c]))
    return vertices
def sas(b,c,angle):
    assert b>0 and c>0
    vertices=[S.Point(0,0),S.Point(c,0),S.Point(b*S.cos(angle),b*S.sin(angle))]
    side_lengths(vertices); assert area(vertices)>0
    return vertices
def right(b,c): return sas(b,c,S.pi/2)
def trig(vertices,index):
    vertex=vertices[index]; u=vertices[(index+1)%3]-vertex; v=vertices[(index+2)%3]-vertex
    denominator=S.sqrt(dot(u,u)*dot(v,v)); assert denominator>0
    return S.simplify(abs(cross(u,v))/denominator),S.simplify(dot(u,v)/denominator)
def center(vertices):
    a,b,c=vertices
    matrix=S.Matrix([[2*(b.x-a.x),2*(b.y-a.y)],[2*(c.x-a.x),2*(c.y-a.y)]])
    assert matrix.det()!=0
    values=matrix.inv()*S.Matrix([b.dot(b)-a.dot(a),c.dot(c)-a.dot(a)])
    o=S.Point(*[S.simplify(value) for value in values])
    assert same(o.distance(a),o.distance(b)) and same(o.distance(a),o.distance(c))
    return o
def circumradius(vertices): return S.simplify(center(vertices).distance(vertices[0]))
def inradius(vertices):
    sides=side_lengths(vertices)
    weighted=sum((length*vertex for length,vertex in zip(sides,vertices)),S.Point(0,0))/sum(sides)
    radii=[S.Line(vertices[i],vertices[(i+1)%3]).distance(weighted) for i in range(3)]
    assert all(same(value,radii[0]) for value in radii)
    assert radii[0]>0
    return S.simplify(radii[0])
def recover_legs(a,total):
    product=S.simplify((total*total-a*a)/2)
    discriminant=S.simplify(total*total-4*product); assert product>0 and discriminant>=0
    first=S.simplify((total-S.sqrt(discriminant))/2)
    second=S.simplify((total+S.sqrt(discriminant))/2)
    assert first>0 and second>0 and same(first**2+second**2,a*a)
    return first,second


def recompute(question):
    scope=question['practice_scope']; section,typ=scope['section'],scope['type']
    g=question['verification']
    if section=='4.1':
        if typ==1:
            a=exact(g['hyp']); angle=degrees(g['B_deg']); assert angle<S.pi/2
            vertices=right(a*S.sin(angle),a*S.cos(angle))
            return side_lengths(vertices)[1]
        if typ==2:
            a=exact(g['hyp']); sine=exact(g['sin_B']); assert a>0 and 0<sine<1
            b=a*sine; c=S.sqrt(a*a-b*b)
            assert same(trig(right(b,c),1)[0],sine)
            return c
        if typ==3:
            m,n=exact(g['m']),exact(g['n']); assert m>0 and n>0
            vertices=[S.Point(0,S.sqrt(m*n)),S.Point(-m,0),S.Point(n,0)]
            assert trig(vertices,0)[1]==0
            return S.Line(vertices[1],vertices[2]).distance(vertices[0])
        if typ==4:
            a=exact(g['hyp']); ratio=exact(g['angle_ratio']); assert ratio>0
            cc=90/(ratio+1); bb=ratio*cc
            assert same(bb+cc,90)
            return side_lengths(right(a*S.sin(degrees(bb)),a*S.cos(degrees(bb))))[1]
        if typ==5:
            total,tangent=exact(g['sum_legs']),exact(g['tan_B']); assert total>0 and tangent>0
            c=total/(1+tangent); b=tangent*c
            return area(right(b,c))
        if typ==6:
            a=exact(g['hyp']); rhs=exact(g['nonlinear_rhs']); y=S.Symbol('y')
            roots=[value for value in S.solve(y*y+y-rhs,y) if value>0 and value<1]
            assert len(roots)==1 and a>0
            b=a*roots[0]; vertices=right(b,S.sqrt(a*a-b*b))
            assert same(trig(vertices,1)[0]+trig(vertices,2)[1]**2,rhs)
            return b
        if typ==7:
            a=exact(g['hyp']); cc=degrees(g['C_deg']); assert cc<S.pi/2
            vertices=right(a*S.cos(cc),a*S.sin(cc)); va,vb,vc=vertices
            _,b,c=side_lengths(vertices); d=(b*vb+c*vc)/(b+c)
            assert same(vb.distance(d)/d.distance(vc),c/b)
            return dot(d-va,d-va)
        if typ==8:
            aa,bb=degrees(g['A_deg']),degrees(g['B_deg']); cc=S.pi-aa-bb; assert cc>0
            a=exact(g['a']); b=a*S.sin(bb)/S.sin(aa); c=a*S.sin(cc)/S.sin(aa)
            vertices=from_sides(a,b,c); assert same(trig(vertices,0)[1],S.cos(aa))
            return b
        if typ==9:
            vertices=sas(exact(g['b']),exact(g['c']),degrees(g['A_deg']))
            return side_lengths(vertices)[0]
        if typ==10:
            vertices=from_sides(*map(exact,g['sides']))
            return trig(vertices,0)[1]
        if typ==11:
            lower,upper=exact(g['lower']),exact(g['upper']); assert lower>upper>0
            h=S.sqrt(lower*upper)
            vertices=[S.Point(0,0),S.Point(lower,0),S.Point(upper,h),S.Point(0,h)]
            assert S.Polygon(*vertices).is_convex()
            assert dot(vertices[2]-vertices[0],vertices[3]-vertices[1])==0
            return sum(vertices[i].distance(vertices[(i+1)%4]) for i in range(4))
        if typ==12:
            total,h=exact(g['sum_legs']),exact(g['height']); assert total>0 and h>0
            a=S.sqrt(h*h+total*total)-h
            b,c=recover_legs(a,total); vertices=right(b,c)
            assert same(S.Line(vertices[1],vertices[2]).distance(vertices[0]),h)
            return c
        if typ==13:
            a=2*exact(g['median']); total=exact(g['sum_legs'])
            b,c=recover_legs(a,total); vertices=right(b,c)
            midpoint=S.Segment(vertices[1],vertices[2]).midpoint
            assert same(vertices[0].distance(midpoint),exact(g['median']))
            return c
        if typ==14:
            vertices=list(map(point,g['vertices'])); assert S.Polygon(*vertices).is_convex()
            assert dot(vertices[2]-vertices[0],vertices[3]-vertices[1])==0
            intersection=S.Line(vertices[0],vertices[2]).intersection(S.Line(vertices[1],vertices[3]))
            assert intersection==[S.Point(0,0)]
            return sum(vertices[i].distance(vertices[(i+1)%4]) for i in range(4))
        if typ==15:
            value=exact(g['sum_sines']); u=exact(g['parameter_deg']); assert 0<=u<60
            angles=[60-u,S.Integer(60),60+u]
            assert all(angle>0 for angle in angles) and sum(angles)==180
            assert same(S.sin(degrees(angles[0]))+S.sin(degrees(angles[2])),value)
            # cos is strictly decreasing on [0,60), so this checked root is unique.
            return angles[0]
    if section=='4.2':
        if typ==1:
            length=exact(g['side']); vertices=from_sides(length,length,length)
            return circumradius(vertices)+inradius(vertices)
        if typ==2:
            vertices=from_sides(*map(exact,g['sides']))
            return circumradius(vertices)+inradius(vertices)
        if typ==3:
            b,c=map(exact,g['legs']); a=exact(g['hyp']); assert same(b*b+c*c,a*a)
            return inradius(right(b,c))
        if typ==4:
            a,b,c=map(point,g['vertices']); assert dot(b-a,c-a)==0
            m=S.Segment(b,c).midpoint
            return inradius([a,b,m])+inradius([a,c,m])
        if typ==5:
            c,b=exact(g['AB']),exact(g['AC']); a,vb,vc=right(b,c)
            d=(b*vb+c*vc)/(b+c)
            return circumradius([a,vb,d])/circumradius([a,vc,d])
        if typ==6:
            rr,ri=exact(g['R']),exact(g['r']); assert rr>0 and ri>0
            a=2*rr; b,c=recover_legs(a,a+2*ri); vertices=right(b,c)
            assert same(circumradius(vertices),rr) and same(inradius(vertices),ri)
            return c
        if typ==7:
            a,b,c=map(exact,g['witness_sides']); vertices=from_sides(a,b,c); ri=inradius(vertices)
            assert same(ri,exact(g['r'])) and same(b+c,a+2*ri)
            assert trig(vertices,0)[1]==0
            return S.Integer(90)
        if typ==8:
            radius=exact(g['R']); aa,bb=degrees(g['A_deg']),degrees(g['B_deg']); cc=S.pi-aa-bb
            assert radius>0 and cc>0
            sides=[2*radius*S.sin(angle) for angle in [aa,bb,cc]]
            vertices=from_sides(*sides); assert same(circumradius(vertices),radius)
            return sum(sides)
    if section=='4.3':
        if typ==1:
            return area(sas(exact(g['b']),exact(g['c']),degrees(g['A_deg'])))
        if typ==2:
            a=exact(g['a']); aa,cc=degrees(g['A_deg']),degrees(g['C_deg']); bb=S.pi-aa-cc; assert bb>0
            vertices=from_sides(a,a*S.sin(bb)/S.sin(aa),a*S.sin(cc)/S.sin(aa))
            return area(vertices)
        if typ==3:
            a,b,target=exact(g['a']),exact(g['b']),exact(g['area']); assert a>0 and b>0 and target>0
            sine=S.simplify(2*target/(a*b))
            if sine>1: return S.Integer(0)
            if sine==1:
                vertices=sas(a,b,S.pi/2); assert same(area(vertices),target)
                return S.Integer(1)
            assert 0<sine<1
            cosine=S.sqrt(1-sine*sine)
            triangles=[[S.Point(0,0),S.Point(b,0),S.Point(a*sign*cosine,a*sine)] for sign in [1,-1]]
            assert all(same(area(vertices),target) for vertices in triangles)
            sides=[side_lengths(vertices) for vertices in triangles]
            assert not same(sides[0][0],sides[1][0]), 'Supplementary angles must give different third sides.'
            return S.Integer(2)
        if typ==4:
            total,b,angle=exact(g['sum_ac']),exact(g['b']),degrees(g['B_deg'])
            product=S.simplify((total*total-b*b)/(2*(1+S.cos(angle))))
            discriminant=S.simplify(total*total-4*product); assert product>0 and discriminant>=0
            a,c=(total-S.sqrt(discriminant))/2,(total+S.sqrt(discriminant))/2
            vertices=[S.Point(c,0),S.Point(0,0),S.Point(a*S.cos(angle),a*S.sin(angle))]
            assert same(vertices[0].distance(vertices[2]),b); side_lengths(vertices)
            return area(vertices)
        if typ==5:
            a,b,c=map(exact,g['sides']); vertices=from_sides(a,b,c); p=(a+b+c)/2
            result=sum(value/(p-value) for value in [a,b,c]); rr,ri=circumradius(vertices),inradius(vertices)
            assert same(result,4*rr/ri-2)
            return result
        if typ==6:
            vertices=list(map(point,g['vertices'])); assert all(trig(vertices,i)[1]>0 for i in range(3))
            feet=[S.Line(vertices[(i+1)%3],vertices[(i+2)%3]).projection(vertices[i]) for i in range(3)]
            result=area(feet)
            assert same(result,2*area(vertices)*S.prod(trig(vertices,i)[1] for i in range(3)))
            return result
        if typ==7:
            a,b,c=map(exact,g['sides']); vertices=from_sides(a,b,c)
            sb,cb=trig(vertices,1); sc,cc=trig(vertices,2)
            return b*b*2*sc*cc+c*c*2*sb*cb
        if typ==8:
            rr,ri=exact(g['R']),exact(g['r']); assert rr>0 and same(rr,2*ri)
            vertices=from_sides(*[rr*S.sqrt(3)]*3)
            assert same(circumradius(vertices),rr) and same(inradius(vertices),ri)
            return S.Integer(60)  # reviewed equality case of Euler's inequality
        if typ==9:
            vertices=list(map(point,g['vertices'])); m=point(g['M']); o=center(vertices); rr=circumradius(vertices)
            assert same(m.distance(o),rr)
            result=sum(vertex.distance(m)**2*2*trig(vertices,i)[0]*trig(vertices,i)[1] for i,vertex in enumerate(vertices))
            assert same(result,4*area(vertices))
            return result
        if typ==10:
            sides=list(map(exact,g['sides'])); vertices=from_sides(*sides)
            result=0
            for i,length in enumerate(sides):
                sine,cosine=trig(vertices,i); assert sine>0
                result+=length*length*cosine/sine
            assert same(result,4*area(vertices))
            return result
        if typ==11:
            vertices=list(map(point,g['vertices'])); assert all(trig(vertices,i)[1]>0 for i in range(3))
            o=center(vertices)
            result=sum(circumradius([vertices[(i+1)%3],o,vertices[(i+2)%3]]) for i in range(3))
            return result
        if typ==12:
            ac,bd=exact(g['AC']),exact(g['BD']); angle=degrees(g['angle_deg']); assert ac>0 and bd>0
            a,c=S.Point(-ac/2,0),S.Point(ac/2,0)
            b=S.Point(-bd*S.cos(angle)/2,bd*S.sin(angle)/2); d=-b
            vertices=[a,b,c,d]; assert S.Polygon(*vertices).is_convex()
            return area(vertices)
        if typ==13:
            vertices=from_sides(*map(exact,g['witness_sides'])); a,b,c=vertices
            median=a.distance(S.Segment(b,c).midpoint)
            assert same(median,exact(g['median'])) and same(area(vertices),exact(g['area']))
            assert trig(vertices,0)[1]==0
            assert 'adaptare parțială' in question['practice_scope']['adaptation']
            return S.Integer(90)
        if typ==14:
            sides=list(map(exact,g['sides'])); angle=degrees(g['A_deg']); opposite=degrees(g['C_deg'])
            assert sides[0]==sides[2] and sides[1]==sides[3] and angle==opposite
            a,b,d=S.Point(0,0),S.Point(sides[0],0),S.Point(sides[3]*S.cos(angle),sides[3]*S.sin(angle))
            c=b+d; vertices=[a,b,c,d]; assert S.Polygon(*vertices).is_convex()
            assert all(same(vertices[i].distance(vertices[(i+1)%4]),sides[i]) for i in range(4))
            result=area(vertices); p=sum(sides)/2
            correction=S.prod(sides)*S.cos((angle+opposite)/2)**2
            assert same(result**2,S.prod(p-value for value in sides)-correction)
            assert (correction==0)==(angle+opposite==S.pi)
            return result
        if typ==15:
            p,q=exact(g['AM_AB']),exact(g['AN_AC']); assert 0<p<1 and 0<q<1
            a,b,c=S.Point(0,0),S.Point(4,0),S.Point(0,3)
            m,n=a+p*(b-a),a+q*(c-a)
            assert S.Polygon(b,m,n,c).is_convex()
            return area([a,m,n])/area([b,m,n,c])
        if typ==16:
            hb,hc=exact(g['h_b']),exact(g['h_c']); assert hb>0 and hc>0
            assert g['circumradius_relation']=='a=R*cos(A)'
            sine,cosine=1/S.sqrt(5),2/S.sqrt(5)
            b,c=hc/sine,hb/sine
            vertices=[S.Point(0,0),S.Point(c,0),S.Point(b*cosine,b*sine)]
            sides=side_lengths(vertices); radius=circumradius(vertices)
            assert same(sides[0],radius*cosine)
            assert same(S.Line(vertices[0],vertices[2]).distance(vertices[1]),hb)
            assert same(S.Line(vertices[0],vertices[1]).distance(vertices[2]),hc)
            return area(vertices)
        if typ==17:
            perimeter=exact(g['perimeter']); assert perimeter>0
            length=perimeter/4
            square=[S.Point(0,0),S.Point(length,0),S.Point(length,length),S.Point(0,length)]
            assert S.Polygon(*square).is_convex()
            return area(square)  # reviewed Bretschneider + AM-GM upper bound
    raise AssertionError((section,typ))


def verify(question):
    result=S.simplify(recompute(question)); assert result.is_real and result.is_finite
    options=question['options']; assert len(options)==4
    values=[latex_number(option['text']) for option in options]
    assert all(not same(a,b) for i,a in enumerate(values) for b in values[i+1:]), 'Equivalent answer options.'
    truth=[same(value,result) for value in values]
    flags=[option['is_correct'] for option in options]
    assert all(type(flag) is bool for flag in flags)
    assert sum(truth)==sum(flags)==1 and truth==flags, (question['practice_scope'],result,values,flags)
    assert question['type']=='multiple_choice' and question['format']=='grid'
    assert question['explanation'] and question['practice_scope']['adaptation']
    assert options[truth.index(True)]['text'] in question['explanation']


def main():
    data=json.loads(TARGET.read_text(encoding='utf-8'))
    grids=[q for q in data['questions'] if q.get('practice_scope',{}).get('bank')==BANK]
    assert len(grids)==len({q['text'] for q in grids})==200
    assert {(q['practice_scope']['section'],q['practice_scope']['type'],q['practice_scope']['variant']) for q in grids}=={
        (section,typ,j) for section,count in [('4.1',15),('4.2',8),('4.3',17)] for typ in range(1,count+1) for j in range(1,6)}
    assert data['difficulty']=='hard'
    for question in grids:
        verify(question)
    positions=Counter(next(i for i,option in enumerate(q['options']) if option['is_correct']) for q in grids)
    assert positions==Counter({i:50 for i in range(4)})
    print('OK: 200 G4 triangle grids, 40 types x 5 variants, 800 exact options; geometric existence and ambiguity checks passed.')


if __name__=='__main__':
    main()
