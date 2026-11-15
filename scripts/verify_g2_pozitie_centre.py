"""Independent exact audit of G2 §1/§2; no generator or Django import."""
import ast
import json
from collections import Counter
from pathlib import Path

import sympy as S

ROOT=Path(__file__).resolve().parents[1]
BANK='g2_pozitie_centre_v1'
Q=S.Rational


def parse(value):
    """Exact numbers/tuples only, with a small AST allowlist; no eval."""
    if not isinstance(value,str):return S.sympify(value)
    def walk(node):
        if isinstance(node,ast.Constant):
            assert isinstance(node.value,int) and not isinstance(node.value,bool)
            return S.Integer(node.value)
        if isinstance(node,ast.Tuple):return S.Tuple(*(walk(arg) for arg in node.elts))
        if isinstance(node,ast.UnaryOp):
            assert isinstance(node.op,(ast.UAdd,ast.USub))
            value=walk(node.operand)
            return -value if isinstance(node.op,ast.USub) else value
        if isinstance(node,ast.BinOp):
            left,right=walk(node.left),walk(node.right)
            if isinstance(node.op,ast.Add):return left+right
            if isinstance(node.op,ast.Sub):return left-right
            if isinstance(node.op,ast.Mult):return left*right
            if isinstance(node.op,ast.Div):return left/right
            if isinstance(node.op,ast.Pow):return left**right
        if isinstance(node,ast.Call):
            assert isinstance(node.func,ast.Name) and node.func.id=='sqrt' and len(node.args)==1 and not node.keywords
            return S.sqrt(walk(node.args[0]))
        raise ValueError(ast.dump(node))
    return walk(ast.parse(value,mode='eval').body)


def same(left,right):
    if isinstance(left,S.Tuple) or isinstance(right,S.Tuple):
        return isinstance(left,S.Tuple) and isinstance(right,S.Tuple) and len(left)==len(right) and all(same(a,b) for a,b in zip(left,right))
    return S.simplify(left-right)==0


def vec(value):return S.Matrix([parse(v) for v in value])
def v(*values):return S.Matrix(values)
def pt(value):return S.Point(*value)
def pair(value):return S.Tuple(*value)
def midpoint(a,b):return vec(S.Segment(pt(a),pt(b)).midpoint)
def centroid(*points):
    # Independent geometric centroid for triangles; mean for other cardinalities.
    if len(points)==3:return vec(S.Triangle(*(pt(p) for p in points)).centroid)
    return sum(points,S.zeros(2,1))/len(points)
def determinant(a,b):return S.Matrix.hstack(a,b).det()
def intersection(a,b,c,d):
    result=S.Line(pt(a),pt(b)).intersection(S.Line(pt(c),pt(d)))
    assert len(result)==1 and isinstance(result[0],S.Point)
    return vec(result[0])
def length(value):return S.sqrt(value.dot(value))


def recompute(section,typ,d):
    points={name:vec(d[name]) for name in ('A','B','C','D','M','N','P','A2','B2','D2') if name in d}
    a,b,c,e=(points.get(name) for name in ('A','B','C','D'))
    if section==1:
        if typ==1:return pair(a)
        if typ==2:return pair(midpoint(b,c)+midpoint(c,a)+midpoint(a,b))
        if typ==3:
            p,q=d['p'],d['q'];t=S.Symbol('t',real=True)
            value=S.solve(q*t-p*(1-t),t)[0]
            assert 0<value<1
            return pair(b+value*(c-b))
        if typ==4:return pair(midpoint(b,e)-midpoint(a,c))
        if typ==5:
            a,b,c=v(0,0),v(1,0),v(0,1)
            div=(d['q']*b+d['p']*c)/(d['p']+d['q'])
            p=intersection(a,div,c,midpoint(a,b))
            return S.simplify(pt(a).distance(pt(p))/pt(p).distance(pt(div)))
        if typ==6:
            a2,b2,e2=(points[name] for name in ('A2','B2','D2'));lam=parse(d['lambda'])
            c=b+e-a;c2=b2+e2-a2
            p,q,r,s=[(1-lam)*p+lam*p2 for p,p2 in zip((a,b,c,e),(a2,b2,c2,e2))]
            assert determinant(q-p,s-p)!=0 and q-p==r-s and r-q==s-p
            return pair(q-p)
        if typ==7:
            alpha=S.Symbol('alpha',real=True);p,q=d['p'],d['q']
            mm,nn,pp=v(p,0),v(0,q),v(alpha,parse(d['beta']))
            alpha=S.solve(determinant(pp-mm,nn-mm),alpha)[0]
            return alpha
        if typ==8:
            mm,nn=midpoint(a,e),midpoint(b,c)
            result=midpoint(mm,nn);left,right=midpoint(a,b),midpoint(c,e)
            assert left!=right and result==midpoint(left,right)
            return pair(result)
        if typ==9:
            lam=parse(d['lambda']);p=intersection(v(0,0),v(1,1),v(1,0),v(lam,1))
            assert 0<p[0]<1 and p[0]==p[1]
            return p[0]
        if typ==10:
            m,n=S.symbols('m n',real=True);left,right=d['denominators']
            result=S.solve([right*m-left*n,m+n-d['sum']],[m,n],dict=True)
            assert len(result)==1
            mm,nn=result[0][m],result[0][n]
            assert mm.is_Integer and nn.is_Integer and 0<mm<left and 0<nn<right
            return S.Tuple(mm,nn)
        if typ==11:
            a,b,c=v(0,0),v(1,0),v(0,1)
            mm=(d['q']*b+d['p']*c)/(d['p']+d['q'])
            p=intersection(a,c,mm,mm+(b-a))
            return S.simplify(pt(a).distance(pt(p))/pt(a).distance(pt(c)))
        if typ==12:
            a,b,c=v(0,0),v(6,0),v(0,6);weights=d['weights']
            mm=(weights[0]*a+weights[1]*b+weights[2]*c)/sum(weights)
            result=[]
            for vertex,left,right in ((a,b,c),(b,c,a),(c,a,b)):
                base=intersection(vertex,mm,left,right)
                result.append(S.simplify(pt(mm).distance(pt(vertex))/pt(mm).distance(pt(base))))
            assert S.simplify(sum(1/(1+ratio) for ratio in result))==1
            return S.Tuple(*result)
        if typ==13:
            e=a+c-b;lam,mu=parse(d['lambda']),parse(d['mu'])
            ee=a+lam*(b-a);ff=b+mu*(c-b);gg=c+lam*(e-c);hh=e+mu*(a-e)
            assert ee+gg==ff+hh and determinant(ff-ee,hh-ee)!=0
            return pair(ff-ee)
        if typ==14:
            a,b,c=v(0,0),v(4,0),v(0,3);lam,mu=parse(d['lambda']),parse(d['mu'])
            dd=a+lam*(b-a);ee=a+lam*(c-a);ff=a+mu*(dd-a);gg=a+mu*(ee-a)
            assert determinant(gg-ff,c-b)==0
            return S.simplify(length(gg-ff)/length(c-b))
        if typ==15:
            direction=vec(d['direction']);assert direction[0]!=0
            line=S.Line(pt(a),pt(a+direction));xx,yy=S.symbols('xx yy',real=True)
            expression=S.solve(line.equation(xx,yy),yy)[0]
            return S.Tuple(S.diff(expression,xx),expression.subs(xx,0))
        if typ==16:
            x,y=S.symbols('x y',real=True);mm=v(x,y)
            expr=(a-mm)+(b-mm)-(c-mm)
            centre=S.solve(list(expr),[x,y],dict=True)[0]
            assert d['radius']>=0
            return S.Tuple(centre[x],centre[y],d['radius'])
        if typ==17:
            a,b,c,e=v(0,0),v(d['width'],0),v(d['width'],d['height']),v(0,d['height'])
            p=intersection(a,midpoint(b,c),b,midpoint(c,e))
            return S.simplify(length(p-a))
    if section==2:
        if typ==1:
            nn=S.Matrix(S.symbols('nx ny',real=True));middle=midpoint(b,c)
            value=S.solve(list((nn-a)+2*(nn-middle)),list(nn),dict=True)[0]
            return S.Tuple(*(value[component] for component in nn))
        if typ==2:
            g=centroid(a,b,c);mirror=2*midpoint(b,c)-g
            return pair(mirror-g)
        if typ==3:
            e=a+c-b
            result=centroid(a,midpoint(b,c),midpoint(e,c))
            assert result==midpoint(a,c)
            return pair(result)
        if typ==4:return pair(centroid(a,b,e)-centroid(a,b,c))
        if typ==5:
            o=intersection(a,c,b,e)
            centers=[centroid(o,one,two) for one,two in ((a,b),(b,c),(c,e),(e,a))]
            assert centers[0]+centers[2]==centers[1]+centers[3]
            assert determinant(centers[1]-centers[0],centers[3]-centers[0])!=0
            return pair(centers[1]-centers[0])
        if typ==6:
            side=d['side'];a,b,c=v(0,0),v(side,0),v(0,side)
            g=centroid(a,b,c);mirror=2*midpoint(b,c)-g
            ee=intersection(a,c,mirror,mirror+(b-a))
            ff=intersection(a,b,mirror,mirror+(c-a))
            assert g==midpoint(ee,ff)
            return pair(ee)
        if typ==7:return pair(centroid(midpoint(b,c),midpoint(c,a),midpoint(a,b)))
        if typ==8:
            vertices=[vec(value) for value in d['hexagon']]
            mids=[midpoint(vertices[i],vertices[(i+1)%6]) for i in range(6)]
            g1,g2=centroid(*mids[::2]),centroid(*mids[1::2])
            assert g1==g2
            return pair(g1)
        if typ==9:return pair(centroid(points['M'],points['N'],points['P'])-centroid(a,b,c))
        if typ==10:return pair((a-e)+(b-e)+(c-e))
        if typ==11:
            px,py=S.symbols('px py',real=True);p=v(px,py)
            mm,nn=points['M'],points['N']
            equations=list((mm+nn+p)-(a+b+c))
            row=S.solve(equations,[px,py],dict=True)[0]
            result=v(row[px],row[py]);assert determinant(nn-mm,result-mm)!=0
            return pair(result)
        if typ==12:
            lam=parse(d['lambda']);q=S.Symbol('q',real=True)
            g=v(Q(1,3),Q(1,3));mm,nn=v(lam,0),v(0,q)
            result=S.solve(determinant(g-mm,nn-mm),q)
            assert len(result)==1 and 0<result[0]<1
            return result[0]
        if typ==13:
            assert determinant(b-a,c-a)>0
            rotation=S.Matrix([[0,-1],[1,0]])
            apexes=[(one+two)/2-S.sqrt(3)/2*rotation*(two-one) for one,two in ((a,b),(b,c),(c,a))]
            # Exact rotations cancel; calculate the derived centroid explicitly.
            result=centroid(*apexes)
            assert all(S.simplify(z)==0 for z in result-centroid(a,b,c))
            return S.Tuple(*(S.simplify(z) for z in result))
        if typ==14:
            mids=[midpoint(one,two) for one,two in ((a,b),(b,c),(c,e),(e,a))]
            return pair(centroid(*mids))
        if typ==15:
            left,right=d['lengths'];assert left>0 and right>0
            u,vv=v(left,0),v(right,0);w=-u-vv
            assert u+vv+w==v(0,0)
            # Witness with nondegenerate source and image triangles attains bound.
            source=[v(0,0),v(100,0),v(0,100)]
            image=[p+delta for p,delta in zip(source,[u,vv,w])]
            assert determinant(image[1]-image[0],image[2]-image[0])!=0
            return length(w)
        if typ==16:
            lam,nu=parse(d['lambda']),parse(d['nu']);mu=S.Symbol('mu',real=True)
            mm,nn,pp=lam*v(3,4),mu*v(3,-4),nu*v(6,0)
            row=S.solve((mm+nn+pp)[1],mu);assert len(row)==1 and 0<row[0]<1
            nn=nn.subs(mu,row[0]);assert determinant(nn-mm,pp-mm)!=0
            return row[0]
        if typ==17:return pair(centroid(a,b,c))
        if typ==18:
            alpha=parse(d['alpha']);beta,gamma=S.symbols('beta gamma',real=True)
            a,b,c=v(0,0),v(6,0),v(0,6)
            mm=(1-alpha)*a+alpha*b;nn=(1-beta)*b+beta*c;pp=(1-gamma)*c+gamma*a
            rows=S.solve(list(mm+nn+pp-a-b-c),[beta,gamma],dict=True)
            assert len(rows)==1
            return S.Tuple(rows[0][beta],rows[0][gamma])
        if typ==19:
            fixed=[a,b,c,e]
            centers=[centroid(*(p for ii,p in enumerate(fixed) if ii!=i)) for i in range(4)]
            point=intersection(fixed[0],centers[0],fixed[1],centers[1])
            assert all(S.Line(pt(vertex),pt(center)).contains(pt(point)) for vertex,center in zip(fixed,centers))
            return pair(point)
        if typ==20:
            ox,oy=S.symbols('ox oy',real=True);o=v(ox,oy)
            mirrored=[2*midpoint(one,two)-o for one,two in ((b,c),(c,a),(a,b))]
            row=S.solve(list(sum(mirrored,S.zeros(2,1))-(a+b+c)),[ox,oy],dict=True)[0]
            return S.Tuple(row[ox],row[oy])
    raise ValueError((section,typ))


def run():
    scope=Counter();total=0
    for lesson,expected_count in ((1,85),(3,100)):
        path=next((ROOT/'data/quizzes/clasa_9').glob(f'clasa_9_u06_l{lesson:02d}_*.json'))
        questions=[q for q in json.loads(path.read_text(encoding='utf-8'))['questions'] if q.get('practice_scope',{}).get('bank')==BANK]
        assert len(questions)==expected_count
        for q in questions:
            tag=q['practice_scope'];key=(tag['section'],tag['type']);scope[key]+=1
            values=[parse(value) for value in q['verification']['option_values']]
            assert len(values)==4 and all(not same(values[i],values[j]) for i in range(4) for j in range(i))
            for value,option in zip(values,q['options']):assert option['text']==r'\('+S.latex(value)+r'\)'
            expected=recompute(*key,q['verification'])
            matches=[same(value,expected) for value in values]
            assert sum(matches)==1 and matches==[option['is_correct'] for option in q['options']],(tag,expected,values)
            assert 'Rezultatul cerut este '+r'\('+S.latex(expected)+r'\)' in q['explanation'],tag
            total+=1
    assert scope==Counter({(section,typ):5 for section,count in ((1,17),(2,20)) for typ in range(1,count+1)})
    print(f'OK: {total} G2 grids, 37 catalog labels x 5, 740 distinct options; exact independent geometry.')


if __name__=='__main__':run()
