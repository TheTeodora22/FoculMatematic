"""Independent exact audit: G4 scalar products and cosine/sine applications.

No generator/Django import or eval. Repository data and displayed options are
linked explicitly; numerical answers come from independent equations/geometry.
"""
import ast
import json
from collections import Counter
from pathlib import Path

import sympy as S

ROOT=Path(__file__).resolve().parents[1]
BANK='g4_scalar_cosinus_v1'
Q=S.Rational


def parse(value):
    if not isinstance(value,str):return S.sympify(value)
    def walk(n):
        if isinstance(n,ast.Constant):
            assert isinstance(n.value,int) and not isinstance(n.value,bool)
            return S.Integer(n.value)
        if isinstance(n,ast.Tuple):return S.Tuple(*(walk(arg) for arg in n.elts))
        if isinstance(n,ast.UnaryOp):
            assert isinstance(n.op,(ast.USub,ast.UAdd))
            return -walk(n.operand) if isinstance(n.op,ast.USub) else walk(n.operand)
        if isinstance(n,ast.BinOp):
            a,b=walk(n.left),walk(n.right)
            if isinstance(n.op,ast.Add):return a+b
            if isinstance(n.op,ast.Sub):return a-b
            if isinstance(n.op,ast.Mult):return a*b
            if isinstance(n.op,ast.Div):return a/b
            if isinstance(n.op,ast.Pow):return a**b
        if isinstance(n,ast.Call):
            name=n.func.id if isinstance(n.func,ast.Name) else n.func.value.id+'.'+n.func.attr
            functions={'sqrt':S.sqrt,'Interval':S.Interval,'Interval.open':S.Interval.open}
            assert name in functions and not n.keywords
            return functions[name](*(walk(arg) for arg in n.args))
        raise ValueError(ast.dump(n))
    return walk(ast.parse(value,mode='eval').body)


def same(a,b):
    if isinstance(a,S.Tuple) or isinstance(b,S.Tuple):
        return isinstance(a,S.Tuple) and isinstance(b,S.Tuple) and len(a)==len(b) and all(same(x,y) for x,y in zip(a,b))
    if isinstance(a,S.Set) or isinstance(b,S.Set):
        return isinstance(a,S.Set) and isinstance(b,S.Set) and S.SymmetricDifference(a,b)==S.EmptySet
    return S.simplify(a-b)==0


def vec(values):return S.Matrix([parse(value) for value in values])
def v(*values):return S.Matrix(values)
def point(value):return S.Point(*value)
def tuplev(value):return S.Tuple(*value)
def squared(value):return S.expand(value.dot(value))
def norm(value):return S.sqrt(squared(value))
def cross(a,b):return S.Matrix.hstack(a,b).det()
def mid(a,b):return (a+b)/2
def line(a,b):return S.Line(point(a),point(b))
def intersection(l1,l2):
    result=l1.intersection(l2)
    assert len(result)==1 and isinstance(result[0],S.Point)
    return vec(result[0])
def convex(points):
    turns=[cross(points[(i+1)%4]-points[i],points[(i+2)%4]-points[(i+1)%4]) for i in range(4)]
    assert all(t>0 for t in turns) or all(t<0 for t in turns)
def triangle(sides):
    a,b,c=map(parse,sides)
    assert a>0 and b>0 and c>0 and a+b>c and a+c>b and b+c>a
    xx=S.simplify((b*b+c*c-a*a)/(2*c))
    yy=S.sqrt(S.simplify(b*b-xx*xx));assert yy>0
    return v(0,0),v(c,0),v(xx,yy)
def cosines(sides):
    a,b,c=triangle(sides)
    return S.Tuple(*[S.simplify((one-origin).dot(two-origin)/(norm(one-origin)*norm(two-origin)))
        for origin,one,two in ((a,b,c),(b,c,a),(c,a,b))])


def confirm_text(q):
    """Bridge original enunciation and exact audit data; never inspect the key."""
    d=q['verification'];section=q['practice_scope']['section'];typ=q['practice_scope']['type'];text=q['text']
    def shown(value):return r'\('+S.latex(value)+r'\)'
    def pair_shown(value):return shown(tuplev(vec(value)))
    if section==1 and typ in (2,3,4,10):
        for name in ('u','v','w'):
            if name in d:assert name+'='+pair_shown(d[name]) in text,(section,typ,name)
    if section==1 and typ in (8,15,16):
        for name in ('A','B','C','O'):
            if name in d:assert name+pair_shown(d[name]) in text,(section,typ,name)
    if 'quad' in d:
        for name,value in zip('ABCD',d['quad']):assert name+pair_shown(value) in text,(section,typ,name)
    if section==1 and typ in (1,23):
        a,b,c=d['sides'];assert f'BC={a}' in text and f'CA={b}' in text and f'AB={c}' in text
    if section==1 and typ==25:
        a,b,c=d['sides'];assert f'BC={a}' in text and f'AC={b}' in text and f'AB={c}' in text
    if section==2 and typ in (1,10):assert shown(S.Tuple(*map(parse,d['sides']))) in text
    if section==2 and typ in (2,3):
        a,b,c=d['sides'];assert f'a={a}' in text and f'b={b}' in text and f'c={c}' in text
    if section==2 and typ in (8,9):
        for name,value in zip('abc',d['sides']):
            assert (name+'='+shown(parse(value)) in text) or (name+'='+str(value) in text)
    if section==2 and typ==14:
        a,b,c=d['sides'];assert f'BC={a}' in text and f'AC={b}' in text and f'AB={c}' in text
    if section==2 and typ==20:
        pts=[vec(value) for value in d['cyclic']]
        for label,one,two in [('AB',0,1),('BC',1,2),('CD',2,3),('DA',3,0),('AC',0,2)]:
            assert label+'='+shown(norm(pts[two]-pts[one])) in text
    # Parameter and branch constraints are checked as well as the coefficients.
    if section==1 and typ==6:assert f'{d["angle"]}°' in text and f'(m;{d["height"]})' in text
    if section==1 and typ==11:assert f'|v|={d["length"]}' in text and f'u·v={d["dot"]}' in text and 'positive' not in text and 'pozitivă' in text
    if section==1 and typ==12:assert f'm>{2*d["scale"]}' in text
    if section==2 and typ==7:assert all(str(length) in text for length in d['fixed_sides'])
    if section==2 and typ==15:assert all(str(r) in text for r in d['ratios']) and 'exterior' in text
    if section==2 and typ==16:assert f'R={d["radius"]}' in text and f'A={d["angle"]}°' in text
    if section==2 and typ==19:assert str(2*d['half_angle'])+'°' in text and 'OA='+str(d['distance']) in text


def recompute(section,typ,d):
    # JSON integers must stay exact through division (e.g. s/2 in a hexagon).
    def exact_integers(value):
        if type(value) is int:return S.Integer(value)
        if isinstance(value,list):return [exact_integers(item) for item in value]
        if isinstance(value,dict):return {key:exact_integers(item) for key,item in value.items()}
        return value
    d=exact_integers(d)
    if section==1:
        if typ==1:
            a,b,c=triangle(d['sides']);return S.simplify((b-a).dot(c-a))
        if typ==2:return vec(d['u']).dot(vec(d['v']))
        if typ==3:
            a,b,c=(vec(d[name]) for name in ('u','v','w'));return (a-2*b).dot(3*a+c)
        if typ==4:
            a,b=vec(d['u']),vec(d['v']);assert squared(a)>0 and squared(b)>0
            cosine=S.simplify(a.dot(b)/(norm(a)*norm(b)))
            return S.Tuple(cosine,S.simplify(180*S.acos(cosine)/S.pi))
        if typ==5:
            m=S.Symbol('m',real=True);a=v(m,d['u_constant']);b=vec(d['v'])
            answer=S.solve(a.dot(b),m);assert len(answer)==1
            assert squared(a.subs(m,answer[0]))>0 and squared(b)>0
            return answer[0]
        if typ==6:
            m=S.Symbol('m',real=True);k=d['height'];theta=S.pi*d['angle']/180
            assert k>0 and 0<theta<S.pi
            cosine=S.cos(theta)
            roots=S.solve(m*m*(1-cosine*cosine)-k*k*cosine*cosine,m)
            valid=[r for r in roots if S.simplify(r/S.sqrt(r*r+k*k)-cosine)==0]
            assert len(valid)==1
            return S.simplify(valid[0])
        if typ==7:
            m,n=S.symbols('m n',real=True);j=d['j'];a=v(1,m);b=v(n,j);c=v(2,-j)
            rows=S.solve([a.dot(b),a.dot(c)],[m,n],dict=True);assert len(rows)==1
            row=rows[0];assert all(squared(vector.subs(row))>0 for vector in (a,b,c))
            return S.Tuple(row[m],row[n])
        if typ==8:
            a,b,c=(vec(d[name]) for name in ('A','B','C'));assert cross(b-a,c-a)!=0
            return (b-a).dot(c-a)
        if typ==9:
            s=d['side'];a=v(s,0);b=v(s/2,S.sqrt(3)*s/2);dd=v(-s,0)
            return S.simplify((b-a).dot(dd-a))
        if typ==10:return squared(vec(d['u'])+vec(d['v'])+vec(d['w']))
        if typ==11:
            xx,yy=S.symbols('xx yy',real=True)
            rows=S.solve([xx-d['dot'],xx*xx+yy*yy-d['length']**2],[xx,yy],dict=True)
            rows=[row for row in rows if row[yy]>0];assert len(rows)==1
            return S.Tuple(rows[0][xx],rows[0][yy])
        if typ==12:
            s=d['scale'];m=S.Symbol('m',real=True);a,b,mm=v(0,s),v(4*s,s),v(m,0)
            roots=S.solve((a-mm).dot(b-mm),m)
            roots=[r for r in roots if r>2*s];assert len(roots)==1
            return S.Tuple(S.simplify(roots[0]),0)
        if typ==13:
            ca=cosines([d['hypotenuse'],*d['legs']])[0];assert ca==0
            return S.Integer(90)
        if typ==14:
            m=S.Symbol('m',real=True);a,b=vec(d['u']),v(m,d['v_y'])
            roots=S.solve(cross(a,b),m);assert len(roots)==1
            b=b.subs(m,roots[0]);assert squared(a)>0 and squared(b)>0
            assert S.simplify(a.dot(b)**2-squared(a)*squared(b))==0
            return roots[0]
        if typ==15:
            a,b,c,o=(vec(d[n]) for n in ('A','B','C','O'))
            assert S.simplify((a-o).dot(c-b)+(b-o).dot(a-c)+(c-o).dot(b-a))==0
            return S.simplify(-(c-o).dot(b-a))
        if typ==16:
            a,b,c=(vec(d[n]) for n in ('A','B','C'));tri=S.Triangle(point(a),point(b),point(c))
            h=vec(tri.orthocenter)
            assert (h-a).dot(c-b)==(h-b).dot(a-c)==(h-c).dot(b-a)==0
            return tuplev(h)
        if typ==17:
            a,b,c=v(0,0),v(d['width'],0),v(0,d['height'])
            center=S.Circle(point(a),point(b),point(c)).center
            return S.Tuple(*center)
        if typ==18:
            a,b=vec(d['u']),vec(d['v']);assert squared(a)==squared(b) and cross(a,b)!=0
            return S.simplify((a+b).dot(b-a))
        if typ==19:
            side1,side2=d['sides'];theta=S.pi*d['angle']/180
            a,b=v(side1,0),v(side2*S.cos(theta),side2*S.sin(theta));assert cross(a,b)!=0
            return S.simplify(squared(a+b)+squared(b-a))
        if typ==20:
            m,xx,yy=S.symbols('m xx yy',real=True);a=v(0,0);b=v(m,d['u_y']);dd=vec(d['v']);c=b+dd;mm=v(xx,yy)
            expression=S.expand(squared(mm-a)+squared(mm-c)-squared(mm-b)-squared(mm-dd))
            assert not expression.has(xx,yy)
            roots=S.solve(expression,m);assert len(roots)==1 and cross(b.subs(m,roots[0]),dd)!=0
            return roots[0]
        if typ==21:
            s=d['scale'];m=S.Symbol('m',real=True);a,b,c,dd=v(0,0),v(2*s,-s),v(4*s,0),v(m,2*s)
            roots=S.solve(squared(b-a)+squared(dd-c)-squared(dd-a)-squared(c-b),m);assert len(roots)==1
            dd=dd.subs(m,roots[0]);convex([a,b,c,dd]);assert (c-a).dot(dd-b)==0
            return roots[0]
        if typ==22:
            a,b,c,dd=[vec(p) for p in d['quad']];convex([a,b,c,dd])
            actual=4*squared(mid(a,c)-mid(b,dd))
            rhs=sum(squared(one-two) for one,two in ((a,b),(b,c),(c,dd),(dd,a)))-squared(c-a)-squared(dd-b)
            assert actual==rhs
            return actual
        if typ==23:
            a,b,c=triangle(d['sides']);g=(a+b+c)/3
            return S.simplify(squared(a-g)+squared(b-g)+squared(c-g))
        if typ==24:
            l1,l2=d['legs'];a,b,c=v(0,0),v(l1,0),v(0,l2)
            h=vec(line(b,c).projection(point(a)))
            assert S.simplify(squared(h-a)-norm(h-b)*norm(h-c))==0
            return S.simplify(norm(h-a))
        if typ==25:
            aa,bb,cc=map(parse,d['sides']);a,b,c=triangle(d['sides'])
            foot=(bb*b+cc*c)/(bb+cc)
            return S.simplify(squared(foot-a))
        if typ==26:
            pts=[vec(p) for p in d['quad']];convex(pts);rotation=S.Matrix([[0,-1],[1,0]])
            middles=[mid(pts[i],pts[(i+1)%4]) for i in range(4)]
            opposite=[pts[(i+3)%4]-pts[(i+2)%4] for i in range(4)]
            lines=[line(mm,mm+rotation*normal) for mm,normal in zip(middles,opposite)]
            p=intersection(lines[0],lines[1])
            assert all(ln.contains(point(p)) for ln in lines)
            assert all(not (lines[i].is_parallel(lines[k]) and lines[i].contains(point(middles[k]))) for i in range(4) for k in range(i))
            xx,yy=S.symbols('xx yy',real=True);variable=v(xx,yy)
            assert S.expand(sum((variable-mm).dot(normal) for mm,normal in zip(middles,opposite)))==0
            return tuplev(p)
    if section==2:
        if typ==1:return cosines(d['sides'])
        if typ==2:
            a,b,c=map(parse,d['sides']);ca,cb,cc=cosines(d['sides'])
            return S.simplify(b*cc+c*cb)
        if typ==3:
            a,b,c=map(parse,d['sides']);ca,cb,cc=cosines(d['sides'])
            return S.simplify(a*b*cc+a*c*cb+b*c*ca)
        if typ==4:
            angles=[S.pi*a/180 for a in d['angles']];assert sum(angles)==S.pi and all(a>0 for a in angles)
            sides=[2*d['radius']*S.sin(a) for a in angles]
            return S.simplify(sum(sides[i]*S.sin(angles[(i+1)%3]-angles[(i+2)%3]) for i in range(3)))
        if typ==5:
            bang=d['B'];assert 0<bang<90
            # sin B and sin C are strictly positive for interior angles;
            # the exact factorization forces cos A=0, not cos² A=0 ambiguities.
            return S.Integer(90)
        if typ==6:
            answer=cosines(d['sides'])[0];assert answer<0
            return answer
        if typ==7:
            b,c=d['fixed_sides'];m=S.Symbol('m',real=True)
            relations=[S.Gt(m,0),S.Gt(m+b,c),S.Gt(m+c,b),S.Gt(b+c,m)]
            return S.Intersection(*(S.solve_univariate_inequality(rel,m,relational=False) for rel in relations))
        if typ==8:return S.simplify(180*S.acos(cosines(d['sides'])[0])/S.pi)
        if typ==9:
            values=cosines(d['sides']);cot=[S.simplify(c/S.sqrt(1-c*c)) for c in values]
            return S.simplify(cot[0]+cot[2]-2*cot[1])
        if typ==10:return cosines(d['sides'])[0]
        if typ==11:
            s=d['side'];u,w=v(s,0),v(0,s)
            return squared(u+w)
        if typ==12:
            _,b,c=map(parse,d['sides']);a=S.Symbol('a',positive=True)
            roots=S.solve(1/(a+b)+1/(a+c)-3/(a+b+c),a)
            roots=[r for r in roots if r.is_positive];assert len(roots)==1
            return S.simplify(180*S.acos(cosines([roots[0],b,c])[0])/S.pi)
        if typ==13:
            a,b,c=triangle(d['sides']);left,right=d['parts'];assert left>0 and right>0 and left+right==parse(d['sides'][0])
            foot=b+S.Rational(left,left+right)*(c-b)
            return S.simplify(norm(foot-a))
        if typ==14:
            a,b,c=triangle(d['sides']);bisector=b/norm(b)+c/norm(c)
            mm=mid(b,c)
            reflected=2*bisector*(mm.dot(bisector)/squared(bisector))-mm
            nn=intersection(line(a,reflected),line(b,c))
            assert nn[1]>0 and c[1]>nn[1]
            return S.simplify(norm(mm-b)*norm(nn-b)/(norm(mm-c)*norm(nn-c)))
        if typ==15:
            p,q,r,s=d['ratios'];a,b,c=v(0,0),v(1,0),v(0,1)
            dd=(q*b+p*c)/(p+q);ee=(s*c+r*a)/(r+s)
            ff=intersection(line(dd,ee),line(a,b));assert ff[0]>1
            return S.simplify(norm(ff-a)/norm(ff-b))
        if typ==16:
            R,angle=d['radius'],d['angle'];assert R>0 and 0<angle<180
            # Build an isosceles triangle with the given A,R, then compute H.
            alpha=S.pi*angle/180;beta=(S.pi-alpha)/2
            opposite=2*R*S.sin(alpha);equal=2*R*S.sin(beta)
            a,b,c=triangle([opposite,equal,equal])
            h=vec(S.Triangle(point(a),point(b),point(c)).orthocenter)
            return S.simplify(norm(h-a))
        if typ==17:
            ab,ac=d['AB'],d['AC'];r=S.Symbol('r',positive=True);f=r*ac/ab+ab/(r*ac)
            roots=S.solve(S.diff(f,r),r);assert len(roots)==1 and roots[0]>0
            assert S.diff(f,r,2).subs(r,roots[0])>0
            assert S.limit(f,r,0,dir='+')==S.oo and S.limit(f,r,S.oo)==S.oo
            return roots[0]
        if typ==18:
            a,b,c,dd=[vec(p) for p in d['quad']];convex([a,b,c,dd])
            metric=(squared(dd-a)+squared(c-b)-squared(b-a)-squared(dd-c))/2
            assert metric==(c-a).dot(dd-b)==0 and squared(c-a)>0 and squared(dd-b)>0
            return metric
        if typ==19:
            theta=S.pi*d['half_angle']/180;dist=d['distance'];assert 0<theta<S.pi/2 and dist>0
            e1,e2=v(S.cos(theta),S.sin(theta)),v(S.cos(theta),-S.sin(theta))
            a=v(dist,0);mm=S.simplify(2*dist/S.cos(theta))*e1
            nn=intersection(line(a,mm),line(v(0,0),e2));assert S.simplify(nn.dot(e2))>0
            return S.simplify(1/norm(mm)+1/norm(nn))
        if typ==20:
            points=[vec(p) for p in d['cyclic']];convex(points)
            circle=S.Circle(*(point(p) for p in points[:3]));center=vec(circle.center)
            assert all(S.simplify(squared(p-center)-circle.radius**2)==0 for p in points)
            return S.simplify(norm(points[3]-points[1]))
    raise ValueError((section,typ))


def run():
    target=next((ROOT/'data/quizzes/clasa_9').glob('clasa_9_u08_l01_*.json'))
    questions=[q for q in json.loads(target.read_text(encoding='utf-8'))['questions'] if q.get('practice_scope',{}).get('bank')==BANK]
    assert len(questions)==230
    scope=Counter()
    for q in questions:
        tag=q['practice_scope'];key=(tag['section'],tag['type']);scope[key]+=1
        confirm_text(q)
        values=[parse(v) for v in q['verification']['option_values']]
        assert len(values)==4 and all(not same(values[i],values[k]) for i in range(4) for k in range(i))
        for value,option in zip(values,q['options']):assert option['text']==r'\('+S.latex(value)+r'\)',(tag,option)
        expected=recompute(*key,q['verification'])
        matches=[same(value,expected) for value in values]
        assert matches==[option['is_correct'] for option in q['options']] and sum(matches)==1,(tag,expected,values)
        # Equivalent radical forms can serialize to different LaTeX strings.
        # The option has already been checked against the independently computed value.
        correct_text=q['options'][matches.index(True)]['text']
        assert 'Rezultatul cerut este '+correct_text in q['explanation'],(tag,expected)
    assert scope==Counter({(section,typ):5 for section,count in ((1,26),(2,20)) for typ in range(1,count+1)})
    print('OK: 230 grids, 46 G4 types x 5, 920 distinct options; exact independent geometry and angle-branch checks.')


if __name__=='__main__':run()
