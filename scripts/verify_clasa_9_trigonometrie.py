"""Independent read-only G3 audit; no generator import or eval/parse_expr.

Repository arithmetic has a deliberately small AST grammar. Original requested
expressions are linked to displayed LaTeX and evaluated with domain checks before
cancellation. Special geometric, range and period questions use separate checks.
"""
import argparse
import ast
import json
from collections import Counter
from pathlib import Path

import sympy as S

ROOT=Path(__file__).resolve().parents[1]
BANK='g3_trigo_v1'
COUNTS={1:35,2:40,3:80,4:25,5:40,6:45,7:75,8:105,9:140}
MAPPING={'1':1,'2':2,'3.1':3,'3.2':4,'3.3':5,'3.4':6,'4':7,'5':8,'6':9,'7':9}
TYPES={'1':7,'2':8,'3.1':16,'3.2':5,'3.3':8,'3.4':9,'4':15,'5':21,'6':17,'7':11}
SYMBOLS={name:S.Symbol(name,real=True) for name in ('x','y','z','a','b','c','t','u','v','m','n','k')}


def same(a,b):
    if isinstance(a,str) or isinstance(b,str):return type(a) is str and type(b) is str and a==b
    if isinstance(a,S.Tuple) or isinstance(b,S.Tuple):
        return isinstance(a,S.Tuple) and isinstance(b,S.Tuple) and len(a)==len(b) and all(same(x,y) for x,y in zip(a,b))
    if isinstance(a,S.Set) or isinstance(b,S.Set):
        return isinstance(a,S.Set) and isinstance(b,S.Set) and S.SymmetricDifference(a,b)==S.EmptySet
    return S.simplify(S.trigsimp(a-b))==0


def parse(raw,bindings=None,display=False):
    """Parse only exact repository arithmetic, optionally substituting givens.

    The numeric path checks original denominator/tangent/cotangent domains at
    every AST node, before a SymPy cancellation could erase a restriction.
    """
    if isinstance(raw,S.Basic):return raw
    if type(raw) is int:return S.Integer(raw)
    assert isinstance(raw,str) and len(raw)<30000
    binding_values={name:parse(value) for name,value in (bindings or {}).items()}
    constants={'pi':S.pi,'oo':S.oo,'EmptySet':S.EmptySet,'Reals':S.S.Reals}
    constructors={'Tuple':S.Tuple,'FiniteSet':S.FiniteSet,'Interval':S.Interval,
                  'Interval.open':S.Interval.open,'Interval.Lopen':S.Interval.Lopen,
                  'Interval.Ropen':S.Interval.Ropen}
    trig={'sin':S.sin,'cos':S.cos,'tan':S.tan,'cot':S.cot}
    def flat(operation,*values):
        args=[]
        def collect(value):
            if value.func==operation:
                for child in value.args:collect(child)
            else:args.append(value)
        for value in values:collect(value)
        return operation(*args,evaluate=not display)
    def walk(node):
        if isinstance(node,ast.Constant):
            assert type(node.value) is int
            return S.Integer(node.value)
        if isinstance(node,ast.Name):
            if node.id in binding_values:return binding_values[node.id]
            if node.id in constants:return constants[node.id]
            assert node.id in SYMBOLS,node.id
            return SYMBOLS[node.id]
        if isinstance(node,ast.Tuple):return S.Tuple(*(walk(value) for value in node.elts))
        if isinstance(node,ast.UnaryOp):
            assert isinstance(node.op,(ast.USub,ast.UAdd))
            value=walk(node.operand)
            if isinstance(node.op,ast.UAdd):return value
            return -value
        if isinstance(node,ast.BinOp):
            a,b=walk(node.left),walk(node.right)
            if isinstance(node.op,ast.Add):return flat(S.Add,a,b)
            if isinstance(node.op,ast.Sub):return flat(S.Add,a,-b)
            if isinstance(node.op,ast.Mult):return flat(S.Mul,a,b)
            if isinstance(node.op,ast.Div):
                if not display and not b.free_symbols:assert S.simplify(b)!=0,'Zero denominator in original expression.'
                return S.Mul(a,S.Pow(b,-1,evaluate=not display),evaluate=not display)
            if isinstance(node.op,ast.Pow):
                assert (display and b.free_symbols) or (b.is_Rational and abs(b)<=128)
                if not display and not a.free_symbols and b<0:assert S.simplify(a)!=0
                return S.Pow(a,b,evaluate=not display)
            raise AssertionError(ast.dump(node))
        if isinstance(node,ast.Call):
            if isinstance(node.func,ast.Name):name=node.func.id
            else:
                assert isinstance(node.func,ast.Attribute) and isinstance(node.func.value,ast.Name)
                name=node.func.value.id+'.'+node.func.attr
            assert not node.keywords
            args=[walk(value) for value in node.args]
            if name in constructors:return constructors[name](*args)
            assert len(args)==1
            value=args[0]
            if name in trig:
                if display:return S.Function(name)(value)
                if not value.free_symbols:
                    if name=='tan':assert S.simplify(S.cos(value))!=0,'Undefined tangent.'
                    if name=='cot':assert S.simplify(S.sin(value))!=0,'Undefined cotangent.'
                return trig[name](value)
            if name=='sqrt':
                if not display and not value.free_symbols:assert value>=0
                return S.Pow(value,S.Rational(1,2),evaluate=not display)
            if name=='Abs':return S.Abs(value,evaluate=not display)
            if name=='floor':return S.floor(value)
            if name=='ceiling':return S.ceiling(value)
            if name=='sign':return S.sign(value)
            raise AssertionError(name)
        raise AssertionError(ast.dump(node))
    value=walk(ast.parse(raw,mode='eval').body)
    return value if display or isinstance(value,S.Set) else S.simplify(value)


def expression_bridge(question,source):
    """Ensure the independently evaluated source actually appears in the task."""
    rendered=S.latex(parse(source,display=True))
    assert rendered in question['text'],('Original expression missing from displayed question.',question['practice_scope'],rendered)


def binding_bridge(question,bindings):
    for name,raw in bindings.items():
        assert name in SYMBOLS
        value=parse(raw)
        assert not value.free_symbols
        expected=name+'='+r'\('+S.latex(value)+r'\)'
        assert expected in question['text'],('Binding missing or different in displayed task',name,value,question['practice_scope'])


def option_value(raw):
    if isinstance(raw,str):
        node=ast.parse(raw,mode='eval').body
        if isinstance(node,ast.Constant) and type(node.value) is str:return node.value
    return parse(raw)


def finite_real(value):
    if isinstance(value,S.Tuple):return all(finite_real(item) for item in value)
    return bool(value.is_real and value.is_finite)


def quarter_index(angle):
    """Determine the open quarter exactly, including rational radian inputs."""
    coefficient=S.simplify(angle/S.pi)
    if coefficient.is_Rational:
        twice=2*coefficient
        if twice.is_Integer:return ('axis',int(twice)%4)
        return ('quadrant',int(S.floor(twice))%4+1)
    assert angle.is_Rational
    # Classical rational bounds 333/106 < pi < 355/113 suffice for these inputs.
    lower,upper=S.Rational(333,106),S.Rational(355,113)
    endpoints=sorted((2*angle/lower,2*angle/upper))
    quarters=[S.floor(value) for value in endpoints]
    assert quarters[0]==quarters[1],('Radian angle too close to a boundary for the rational bounds',angle)
    return ('quadrant',int(quarters[0])%4+1)


def trig_sign(function,angle):
    kind,index=quarter_index(angle)
    if kind=='axis':
        sine=[0,1,0,-1][index];cosine=[1,0,-1,0][index]
        if function=='sin':return sine
        if function=='cos':return cosine
        if function=='tan':return 2 if cosine==0 else sine*cosine
        if function=='cot':return 2 if sine==0 else sine*cosine
    else:
        sine=1 if index in (1,2) else -1
        cosine=1 if index in (1,4) else -1
        return sine if function=='sin' else cosine if function=='cos' else sine*cosine
    raise AssertionError(function)


def fourier_frequencies(expression,variable):
    """Nonzero frequencies of an exact finite exponential polynomial.

    Independence of distinct exponentials forces each frequency to have an
    integer phase turn under a period. This establishes minimality, rather than
    merely testing a candidate shift on a few points.
    """
    expanded=S.expand(expression.rewrite(S.exp))
    coefficients={}
    for term in S.Add.make_args(expanded):
        exponents=[factor for factor in S.Mul.make_args(term) if factor.func==S.exp and factor.has(variable)]
        if not exponents:
            assert not term.has(variable),('Not a finite Fourier polynomial',term)
            continue
        assert len(exponents)==1
        exponential=exponents[0]
        phase=exponential.args[0]
        frequency=S.simplify(S.diff(phase,variable)/S.I)
        assert not frequency.has(variable) and frequency.is_real
        remainder=S.simplify(phase-S.I*frequency*variable)
        assert not remainder.has(variable)
        coefficient=S.simplify((term/exponential)*S.exp(remainder))
        assert not coefficient.has(variable)
        coefficients[frequency]=S.simplify(coefficients.get(frequency,0)+coefficient)
    return sorted([frequency for frequency,coefficient in coefficients.items() if coefficient!=0 and frequency!=0],key=S.default_sort_key)


def principal_fourier_period(expression,variable):
    frequencies=fourier_frequencies(expression,variable)
    assert frequencies,'A constant function has no least positive period.'
    assert all(frequency.is_Rational for frequency in frequencies)
    common=S.Rational(0)
    for frequency in frequencies:common=S.gcd(common,abs(frequency))
    assert common>0
    period=S.simplify(2*S.pi/common)
    assert all((frequency*period/(2*S.pi)).is_Integer for frequency in frequencies)
    return period


def foundation_value(question,operation,data):
    text=question['text']
    def number(key):return parse(data[key])
    def shown(value):return r'\('+S.latex(value)+r'\)'
    if operation=='degrees_to_rad':
        d=number('degrees');assert str(d)+'°' in text
        return S.pi*d/180
    if operation=='rad_to_degrees':
        r=number('radians');assert shown(r)+' radiani' in text
        return S.simplify(180*r/S.pi)
    if operation=='angle_system':
        total,difference=number('sum_radians'),number('difference_degrees')
        assert shown(total)+' radiani' in text and f'α−β={difference}°' in text
        aa,bb=S.symbols('alpha beta',real=True)
        result=S.solve([S.pi*(aa+bb)/180-total,aa-bb-difference],[aa,bb],dict=True)
        assert len(result)==1 and result[0][aa]>0 and result[0][bb]>0
        return S.Tuple(result[0][aa],result[0][bb])
    if operation=='arc_length':
        radius,angle=number('radius'),number('angle_radians')
        assert radius>0 and 0<angle<=2*S.pi
        assert f'R={radius} cm' in text and str(S.simplify(180*angle/S.pi))+'°' in text
        return radius*angle
    if operation=='inscribed_arc':
        radius,angle=number('radius'),number('inscribed_degrees')
        assert radius>0 and 0<angle<180 and 'NU conține A' in text
        assert f'rază {radius} cm' in text and f'A={angle}°' in text
        # The opposite arc can be major when the inscribed angle is obtuse.
        return S.simplify(2*S.pi*radius*(2*angle)/360)
    if operation=='regular_polygon':
        n=number('sides');assert n.is_Integer and n>=3 and f'{n} laturi' in text and 'convex' in text
        total=S.pi*(n-2)
        return S.Tuple(180*total/(n*S.pi),total/n)
    if operation=='isosceles_angle_count':
        d=number('angle_degrees');assert 0<d<180 and f'{d}°' in text
        assert 'echilateral este admis' in text
        aa,bb,cc=S.symbols('aa bb cc',real=True);variables=(aa,bb,cc);configurations=set()
        for fixed in range(3):
            for one,two in ((0,1),(1,2),(2,0)):
                rows=S.solve([aa+bb+cc-180,variables[fixed]-d,variables[one]-variables[two]],variables,dict=True)
                for row in rows:
                    if all(v in row and row[v]>0 for v in variables):
                        configurations.add(tuple(sorted(row[v] for v in variables)))
        return S.Integer(len(configurations))
    if operation=='rotation':
        turns=number('turns');assert turns>0 and shown(turns)+' ture' in text
        return 2*S.pi*turns
    if operation=='rotation_time':
        rpm,seconds=number('rpm'),number('seconds');assert rpm>0 and seconds>0
        assert f'{rpm} rotații/minut' in text and shown(seconds)+' secunde' in text
        return S.simplify(rpm*seconds*2*S.pi/60)
    if operation=='reduce_degrees':
        angle=number('angle_degrees');assert f'{angle}°' in text and '[0°;360°)' in text
        result=angle-360*S.floor(angle/360);assert 0<=result<360
        return result
    if operation=='unit_circle':
        angle=number('radians');assert shown(angle) in text
        result=S.Tuple(S.cos(angle),S.sin(angle));assert same(result[0]**2+result[1]**2,1)
        return result
    if operation=='proportional_angles':
        weights=[parse(v) for v in data['weights']];total=number('total_degrees')
        assert len(weights)==3 and total==180 and all(v>0 for v in weights)
        assert ', '.join(map(str,weights)) in text
        result=S.Tuple(*(total*v/sum(weights) for v in weights));assert all(0<v<180 for v in result)
        return result
    if operation=='quadrilateral_equal':
        total=number('three_sum');assert f'B+C+D={total}°' in text and 'convex' in text
        a,d=S.symbols('a d',real=True);row=S.solve([3*a+d-360,2*a+d-total],[a,d],dict=True)[0]
        assert 0<row[a]<180 and 0<row[d]<180
        return row[d]
    if operation=='arc_angle':
        length,radius=number('length'),number('radius');assert length>0 and radius>0
        assert shown(length)+' cm' in text and f'rază {radius} cm' in text
        return length/radius
    if operation=='quadrant':
        angle=number('radians');assert shown(angle)+' radiani' in text
        kind,index=quarter_index(angle);assert kind=='quadrant','An axis point is not in any quadrant.'
        expected={str(i):'Cadranul '+roman for i,roman in enumerate(('I','II','III','IV'),1)}
        assert data['option_labels']==expected
        return S.Integer(index)
    if operation=='right_isosceles_equality':
        hyp=number('hypotenuse');assert hyp>0 and f'ipotenuza {hyp}' in text and 'sin B+sin C=√2' in text
        # Equality in (sin B + cos B)^2<=2 forces positive sin B=cos B.
        y=S.Symbol('y',positive=True);roots=S.solve(2*y*y-1,y);assert roots==[S.sqrt(2)/2]
        return S.simplify(180*S.asin(roots[0])/S.pi)
    return None


def geometric_evaluation(question,bindings):
    """Check the geometry behind the expression, independently of its formula."""
    scope=question['practice_scope']
    if scope['section']!='3.1':return None
    typ=scope['type'];g={name:parse(value) for name,value in bindings.items()}
    a,b,c=(g.get(key) for key in ('a','b','c'));x,y=g.get('x'),g.get('y')
    def norm(value):return S.sqrt(value.dot(value))
    def vec(*values):return S.Matrix(values)
    def acute(value):assert 0<value<S.pi/2
    if typ==1:
        assert a>0 and b>0 and c>0 and same(a*a+b*b,c*c)
        ab,ac=vec(b,0),vec(b,a)
        return S.simplify(abs(S.det(S.Matrix.hstack(ab,ac)))/(norm(ab)*norm(ac)))
    if typ==2:
        assert a>b>0
        height=S.sqrt(a*a-b*b)
        first,second=vec(2*b,0),vec(b,height)
        return S.simplify(abs(S.det(S.Matrix.hstack(first,second)))/(norm(first)*norm(second)))
    if typ==3:
        assert a>0 and 0<b<1
        opposite=a*b
        return S.sqrt(a*a-opposite*opposite)
    if typ==4:
        assert a>0 and b>0 and 0<x<S.pi
        return S.simplify(abs(S.det(S.Matrix.hstack(vec(a,0),vec(b*S.cos(x),b*S.sin(x))))))
    if typ==5:
        assert a>0 and 0<x<S.pi
        apex=vec(0,a*S.cos(x/2));base_midpoint=vec(0,0)
        return norm(apex-base_midpoint)
    if typ in (6,7,8):
        acute(x)
        assert S.cos(x)!=0 and S.sin(x)!=0 and 1+S.cos(x)!=0
        if typ==6:assert S.trigsimp(1+S.tan(SYMBOLS['x'])**2-1/S.cos(SYMBOLS['x'])**2)==0
        return None
    if typ==9:
        assert a>b>0
        ma,mc=vec(-b,0),vec(a-b,a)
        return S.simplify(ma.dot(mc)/(norm(ma)*norm(mc)))
    if typ==10:
        assert a>0 and b>0 and c>0 and same(a*a,b*b+c*c)
        assert same(x,(a*a+c*c-b*b)/(2*a*c)) and same(y,(a*a+b*b-c*c)/(2*a*b))
        return a
    if typ==11:
        assert a>0 and 0<x<S.pi
        return S.simplify(norm(vec(a,0)+vec(a*S.cos(x),a*S.sin(x))))
    if typ==12:
        assert a>0;acute(x);acute(y)
        left,right=vec(-a/S.tan(x),0),vec(a/S.tan(y),0)
        return S.simplify(norm(right-left))
    if typ==13:
        assert a>b>0 and c>0
        vertices=[S.Point(0,0),S.Point(a,0),S.Point(b,c),S.Point(0,c)]
        assert S.Polygon(*vertices).is_convex()
        return vertices[1].distance(vertices[2])
    if typ==14:
        assert a>0 and b>0
        return S.Point(0,0).distance(S.Point(a,b))
    if typ==15:
        acute(x);acute(y)
        xx,yy=SYMBOLS['x'],SYMBOLS['y']
        assert S.trigsimp((S.tan(xx)+S.tan(yy))*S.cos(xx)*S.cos(yy)-S.sin(xx+yy))==0
        return S.sin(x+y)
    raise AssertionError(typ)


def special_value(question,operation,data):
    text=question['text'];x=SYMBOLS['x']
    def number(key):return parse(data[key])
    def shown(value):return r'\('+S.latex(value)+r'\)'
    if operation=='sign':
        source=data['expression'];bindings=data['givens']
        expression_bridge(question,source);binding_bridge(question,bindings)
        g={key:parse(value) for key,value in bindings.items()}
        assert data['option_labels']=={'-1':'Negativ','0':'Zero','1':'Pozitiv','2':'Nedefinit'}
        if source in ('sin(x)','cos(x)','tan(x)','cot(x)'):
            return S.Integer(trig_sign(source.split('(')[0],g['x']))
        if source=='sin(x)*cos(y)*tan(z)':
            signs=[trig_sign('sin',g['x']),trig_sign('cos',g['y']),trig_sign('tan',g['z'])]
            return S.Integer(2 if 2 in signs else S.prod(signs))
        if source=='cos(x)-cos(y)':
            assert 0<=g['x']<=S.pi and 0<=g['y']<=S.pi
            return S.Integer(1 if g['x']<g['y'] else -1 if g['x']>g['y'] else 0)
        raise AssertionError(('Unreviewed sign expression',source))
    if operation=='finite_extrema':
        expression_bridge(question,data['expression']);binding_bridge(question,data['givens'])
        angles=[parse(value) for value in data['angles']]
        assert shown(S.FiniteSet(*angles)) in text and len(angles)>0
        results=[parse(data['expression'],{**data['givens'],'x':value}) for value in angles]
        assert all(finite_real(value) for value in results)
        return S.Tuple(S.Min(*results),S.Max(*results))
    if operation=='range_abs_sine':
        coefficient=number('coefficient');assert coefficient>0
        expression_bridge(question,data['expression']);binding_bridge(question,{'a':coefficient})
        t=SYMBOLS['t'];expression=coefficient*(S.Abs(t)-t)
        # Piecewise linear on [-1,0] and [0,1], all intermediate values attained.
        values=[expression.subs(t,endpoint) for endpoint in (-1,0,1)]
        return S.Interval(S.Min(*values),S.Max(*values))
    if operation=='linear_trig_min':
        constant,a,b=number('constant'),number('sin_coefficient'),number('cos_coefficient')
        assert f'{constant}−{abs(a)}sin x+cos y' in text and a<0 and b==1
        # The two independent arguments attain their extrema simultaneously.
        return constant-abs(a)-abs(b)
    if operation=='parity':
        expression_bridge(question,data['expression'])
        assert data['option_labels']=={'0':'Nici pară, nici impară','1':'Pară, dar nu impară',
            '2':'Impară, dar nu pară','3':'Atât pară, cât și impară'}
        if data['domain']=='positive_interval':
            upper=number('upper');assert upper>0 and f'NUMAI pe (0;{upper})' in text
            return S.Integer(0)  # The domain is not invariant under x -> -x.
        assert data['domain']=='Reals' and 'domeniul ℝ' in text
        expression=parse(data['expression'])
        # All current parity expressions are entire sin/cos/polynomial expressions.
        assert not expression.has(S.tan,S.cot)
        reflected=expression.subs(x,-x)
        even=same(reflected,expression);odd=same(reflected,-expression)
        return S.Integer(3 if even and odd else 1 if even else 2 if odd else 0)
    if operation=='parity_parameter':
        coefficient=number('cos_coefficient');assert coefficient!=0 and data['target']=='even'
        assert f'a sin x+{coefficient}cos x pară pe ℝ' in text
        aa=SYMBOLS['a'];expression=aa*S.sin(x)+coefficient*S.cos(x)
        odd_part=S.expand_trig(expression-expression.subs(x,-x))
        candidate=S.solve(odd_part.subs(x,S.pi/2),aa)
        assert len(candidate)==1 and same(odd_part.subs(aa,candidate[0]),0)
        return candidate[0]
    if operation=='candidate_period':
        source=data['expression'];candidate=number('period')
        assert candidate>0 and 'T='+shown(candidate) in text and 'f(x)='+source in text
        expression=parse(source);principal=principal_fourier_period(expression,x)
        assert not expression.has(S.tan,S.cot)
        multiple=S.simplify(candidate/principal)
        return S.Integer(1 if multiple.is_Integer else 0)
    if operation=='period':
        function,frequency,mode=data['function'],number('frequency'),data['mode']
        assert function in ('sin','cos','tan','cot') and frequency!=0
        trig={'sin':S.sin,'cos':S.cos,'tan':S.tan,'cot':S.cot}[function]
        if mode=='plain':
            expression_bridge(question,function+'(a*x)');binding_bridge(question,{'a':frequency})
            if function in ('tan','cot'):
                assert 'domeniul său natural' in text
                # Zero/pole lattices have consecutive spacing pi/|frequency|.
                period=S.pi/abs(frequency)
                assert same(trig(frequency*(x+period)),trig(frequency*x))
                return period
            return principal_fourier_period(trig(frequency*x),x)
        if mode=='absolute':
            assert function=='sin'
            source=f'Abs(sin({frequency}*x))';expression_bridge(question,source)
            candidate=S.pi/abs(frequency)
            assert same(S.Abs(S.sin(frequency*(x+candidate))),S.Abs(S.sin(frequency*x)))
            # Zeros form precisely the lattice k*pi/f; a smaller shift cannot preserve it.
            return candidate
        assert mode=='square' and function in ('sin','cos')
        expression_bridge(question,f'{function}({frequency}*x)**2')
        return principal_fourier_period(trig(frequency*x)**2,x)
    if operation in ('period_sum','nonperiodic_sum'):
        frequencies=[parse(value) for value in data['frequencies']];functions=data['functions']
        assert len(frequencies)==len(functions)==2 and all(frequency>0 for frequency in frequencies)
        assert functions==['sin','cos']
        expression=S.sin(frequencies[0]*x)+S.cos(frequencies[1]*x)
        if operation=='period_sum':
            scale=2*frequencies[0]
            assert same(frequencies[1],scale/3) and f'sin({scale}x/2)+cos({scale}x/3)' in text
            return principal_fourier_period(expression,x)
        scale=frequencies[0]
        assert same(frequencies[1],scale*S.sqrt(2)) and f'sin({scale}x)+cos({scale}√2·x)' in text
        actual=fourier_frequencies(expression,x)
        assert len(actual)==4
        positive=[value for value in actual if value>0]
        assert len(positive)==2 and S.simplify(positive[0]/positive[1]).is_irrational
        reflected=expression.subs(x,-x)
        assert same((expression-reflected)/2,S.sin(frequencies[0]*x))
        assert same((expression+reflected)/2,S.cos(frequencies[1]*x))
        proof=question['explanation']
        assert ('Independența' in proof and 'incomensurabile' in proof) or ('partea impară' in proof and 'partea pară' in proof and 'k≠0' in proof)
        assert data['option_labels']=={'0':'Funcția nu este periodică','1':'Perioada principală este 2π',
                                     '2':'Perioada principală este π','3':'Funcția este constantă'}
        return S.Integer(0)
    if operation=='functional_period':
        amplitude,frequency,reflection=number('amplitude'),number('frequency'),number('reflection_coefficient')
        assert amplitude!=0 and frequency>0 and reflection==2
        assert f'f(x)+{reflection}f(−x)={amplitude}cos({frequency}x)' in text
        f,g=S.symbols('f g',real=True)
        rhs=amplitude*S.cos(frequency*x)
        rows=S.solve([f+reflection*g-rhs,g+reflection*f-rhs],[f,g],dict=True)
        assert len(rows)==1 and same(rows[0][f].subs(x,-x),rows[0][g])
        return principal_fourier_period(rows[0][f],x)
    if operation=='recover_functions':
        sine=number('sine');quadrant=int(data['quadrant'])
        assert 0<abs(sine)<1 and quadrant in (1,2,3,4)
        assert (sine>0)==(quadrant in (1,2))
        assert 'sin x='+shown(sine) in text and f'cadranul {quadrant}' in text
        cosine=S.sqrt(1-sine*sine)*(-1 if quadrant in (2,3) else 1)
        assert sine!=0 and cosine!=0 and same(sine*sine+cosine*cosine,1)
        return S.Tuple(cosine,sine/cosine,cosine/sine)
    if operation=='recover_sum':
        total=number('sum');assert data['sine_less_cosine'] is True
        assert 'x este în (0;π/4)' in text and 'sin x+cos x='+shown(total) in text
        ss,cc=S.symbols('ss cc',real=True)
        rows=S.solve([ss+cc-total,ss*ss+cc*cc-1],[ss,cc],dict=True)
        valid=[row for row in rows if 0<row[ss]<row[cc]<1]
        assert len(valid)==1
        return S.Tuple(valid[0][ss],valid[0][cc])
    if operation=='recover_parameter':
        aa,bb=number('a'),number('b');assert 0<aa<bb
        assert f'a={aa}, b={bb}' in text and 'x∈(0;π/2)' in text
        assert data['expression']=='cos(x)+tan(x)+cot(x)' and 'cos x+tan x+cot x' in text
        sine=(bb-aa)/(aa+bb);cosine=S.sqrt(1-sine*sine)
        assert 0<sine<1 and cosine>0
        return S.simplify(cosine+sine/cosine+cosine/sine)
    if operation=='trig_quadratic_min':
        angle=number('angle');assert 0<angle<S.pi/2 and 'α='+shown(angle) in text
        t=SYMBOLS['t'];expression=(1-S.sin(angle))*t*t-2*t*S.cos(angle)+1+S.sin(angle)
        assert S.diff(expression,t,2)>0
        critical=S.solve(S.diff(expression,t),t);assert len(critical)==1
        return S.simplify(expression.subs(t,critical[0]))
    if operation=='minimum_even_power':
        coefficient=number('coefficient');power=number('power')
        assert coefficient>0 and power==4 and f'{coefficient}(sin⁴x+cos⁴x)' in text
        t=SYMBOLS['t'];polynomial=coefficient*(t*t+(1-t)**2)
        roots=S.solve(S.diff(polynomial,t),t)
        values=[polynomial.subs(t,value) for value in [0,1,*roots] if 0<=value<=1]
        return S.Min(*values)
    if operation=='range_polynomial_sine':
        offset=number('offset');assert f'f(x)={offset}−2sin x+(1+sin x)²' in text
        t=SYMBOLS['t'];polynomial=S.expand(offset-2*t+(1+t)**2)
        assert same(polynomial,parse(data['polynomial'],{'a':offset}))
        roots=S.solve(S.diff(polynomial,t),t)
        values=[polynomial.subs(t,value) for value in [-1,1,*roots] if -1<=value<=1]
        return S.Interval(S.Min(*values),S.Max(*values))
    if operation=='linear_trig_bound':
        a,b=number('sin_coefficient'),number('cos_coefficient')
        assert a>0 and b>0 and f'|{a}sin x+{b}cos x|≤C' in text
        norm=S.sqrt(a*a+b*b)
        sine,cosine=a/norm,b/norm
        assert same(sine*sine+cosine*cosine,1) and same(a*sine+b*cosine,norm)
        return norm
    if operation=='power_from_sum':
        total=number('sum');power=number('power')
        assert power.is_Integer and 1<=power<=10 and total*total<=2
        assert 'sin x+cos x='+shown(total) in text and 'sin⁵x+cos⁵x' in text and power==5
        product=(total*total-1)/2
        previous,current=S.Integer(2),total
        for exponent in range(2,int(power)+1):previous,current=current,S.expand(total*current-product*previous)
        return S.simplify(current)
    if operation=='angle_sum_from_values':
        sine,cosine=number('sine_x'),number('cosine_y')
        assert data['quadrant_x']==1 and data['quadrant_y']==2 and data['requested']=='sin_sum'
        assert 0<sine<1 and -1<cosine<0
        assert 'sin x='+shown(sine) in text and 'cos y='+shown(cosine) in text
        assert 'x în cadranul I și y în cadranul II' in text
        unit_x=S.sqrt(1-sine*sine)+S.I*sine
        unit_y=cosine+S.I*S.sqrt(1-cosine*cosine)
        return S.simplify(S.im(unit_x*unit_y))
    if operation in ('difference_from_sums','half_sum_from_sums'):
        sine,cosine=number('sine_sum'),number('cosine_sum')
        assert 'sin x+sin y='+shown(sine) in text and 'cos x+cos y='+shown(cosine) in text
        norm2=S.simplify(sine*sine+cosine*cosine);assert 0<=norm2<=4
        if operation=='difference_from_sums':return S.simplify((norm2-2)/2)
        assert 'x,y sunt în (0;π/2)' in text and sine>0 and cosine>0
        cos_delta=S.sqrt(norm2)/2;sin_delta=S.sqrt(1-norm2/4)
        sin_mid,cos_mid=sine/S.sqrt(norm2),cosine/S.sqrt(norm2)
        assert sin_mid*cos_delta>cos_mid*sin_delta and cos_mid*cos_delta>sin_mid*sin_delta
        return S.simplify(sine/cosine)
    if operation=='half_angle_from_cos':
        cosine=number('cosine');quadrant=int(data['quadrant'])
        assert -1<cosine<1 and quadrant in (1,2,3,4) and (cosine>0)==(quadrant in (1,4))
        assert 'cos x='+shown(cosine) in text and f'cadranul {quadrant}' in text and '0<x<2π' in text
        u,v=S.symbols('u v',real=True)
        solutions=S.solve([u*u+v*v-1,v*v-u*u-cosine],[u,v],dict=True)
        valid=[row for row in solutions if row[u]>0 and (row[v]>0)==(quadrant in (1,2))]
        assert len(valid)==1
        return S.Tuple(valid[0][u],valid[0][v])
    if operation=='double_sum_from_tangents':
        a,b=number('tangent_x'),number('tangent_y');assert a>0 and b>0 and a!=1
        assert 'tan x='+shown(a) in text and 'tan y='+shown(b) in text and 'sunt ascuțite' in text
        ux=(1+S.I*a)/S.sqrt(1+a*a);uy=(1+S.I*b)/S.sqrt(1+b*b)
        unit=S.expand(ux*ux*uy)
        denominator=S.simplify(S.re(unit));assert denominator!=0
        return S.simplify(S.im(unit)/denominator)
    if operation=='three_angle_sum':
        sines=[parse(value) for value in data['sines']];quadrants=data['quadrants']
        assert len(sines)==3 and quadrants==[1,2,4] and data['requested']=='sin_sum'
        assert '(sin x;sin y;sin z)='+shown(S.Tuple(*sines)) in text and 'cadranele I,II,IV' in text
        units=[]
        for sine,quadrant in zip(sines,quadrants):
            assert 0<abs(sine)<1 and (sine>0)==(quadrant in (1,2))
            cosine=S.sqrt(1-sine*sine)*(-1 if quadrant in (2,3) else 1)
            units.append(cosine+S.I*sine)
        return S.simplify(S.im(S.prod(units)))
    if operation in ('finite_sum','finite_product'):
        source=data['term'];lower=int(data['lower']);upper=int(data['upper'])
        assert data['index']=='k' and 0<=lower<=upper<=64
        term_tex=S.latex(parse(source,display=True))
        assert data['term_latex']==term_tex
        operator=r'\sum' if operation=='finite_sum' else r'\prod'
        expected_tex=operator+'_{k='+str(lower)+'}^{'+str(upper)+'}'+r'\left('+term_tex+r'\right)'
        assert expected_tex in text,('Wrong displayed aggregate or bounds',question['practice_scope'])
        binding_bridge(question,data['givens'])
        values=[parse(source,{**data['givens'],'k':S.Integer(index)}) for index in range(lower,upper+1)]
        assert all(finite_real(value) for value in values)
        result=S.simplify(S.trigsimp(sum(values) if operation=='finite_sum' else S.prod(values)))
        check_aggregate_formula(question,result,lower,upper)
        return result
    return None


def check_aggregate_formula(question,result,lower,upper):
    """Cross-check explicit aggregates against independent closed-form identities.

    Exceptional denominator cases use the original finite sum; they are not
    discarded merely because a derived quotient would have the form 0/0.
    """
    scope=question['practice_scope'];key=scope['section'],scope['type']
    angle=parse(question['verification']['givens']['x']);n=S.Integer(upper-lower+1)
    if key in (('5',20),('7',3)):
        assert lower==0 and S.sin(angle)!=0
        assert same(result,S.sin(2**n*angle)/(2**n*S.sin(angle)))
    elif key==('5',21):
        reduced=S.prod(S.cos(angle/2**(index+1)) for index in range(lower,upper+1))
        assert same(result,reduced)
    elif key==('7',1):
        assert lower==1 and S.sin(angle)!=0 and S.sin((n+1)*angle)!=0
        assert same(result,(S.cot(angle)-S.cot((n+1)*angle))/S.sin(angle))
    elif key==('7',2):
        assert lower==1 and S.sin(angle/2**n)!=0
        assert same(result,S.sin(angle)/(2**n*S.sin(angle/2**n)))
    elif key==('7',4):
        assert lower==0 and S.sin(angle)!=0 and S.sin(2**n*angle)!=0
        assert same(result,S.cot(angle)-2**n*S.cot(2**n*angle))
    elif key in (('7',5),('7',6)):
        assert lower==1
        if S.sin(angle/2)==0:
            assert S.simplify(angle/(2*S.pi)).is_Integer
            expected=S.Integer(0) if key[1]==5 else n
            assert same(result,expected)
            assert '0/0' in question['explanation'] or 'împărți la zero' in question['explanation']
        else:
            second=S.sin((n+1)*angle/2) if key[1]==5 else S.cos((n+1)*angle/2)
            assert same(result,S.sin(n*angle/2)*second/S.sin(angle/2))
    elif key==('7',7):
        assert lower==1 and S.sin(angle)!=0
        assert same(result,S.sin(n*angle)**2/S.sin(angle))
    elif key==('7',8):
        assert lower==1 and S.sin(angle)!=0
        assert same(result,n/2-S.sin(n*angle)*S.cos((n+1)*angle)/(2*S.sin(angle)))
    elif key==('7',9):
        assert lower==1 and S.sin(angle)!=0
        assert same(result,((n+1)*S.sin(2*n*angle)-n*S.sin(2*(n+1)*angle))/(4*S.sin(angle)**2))
    elif key==('7',10):
        quotients=[]
        for index in range(lower,upper+1):
            u=2**index*angle;assert S.sin(u/2)!=0
            quotients.append(S.sin(3*u/2)/S.sin(u/2))
        assert same(result,S.prod(quotients))
    else:raise AssertionError(('Unreviewed aggregate family',key))


def check_evaluate_context(question,bindings):
    scope=question['practice_scope'];key=scope['section'],scope['type']
    g={name:parse(value) for name,value in bindings.items()}
    if key[0]=='4':assert 0<g['x']<S.pi/2
    if key in (('3.3',4),('3.3',5)):assert 0<g['x']<S.pi/2
    if key==('3.3',6):assert g['n'].is_Integer
    if key==('5',16):assert S.sin(g['x'])!=0 and S.sin(4*g['x'])!=0
    if key==('6',13):assert S.cos(g['x'])!=0
    if key==('6',14):assert all(g[name]>0 for name in ('x','y','z')) and same(sum(g[name] for name in ('x','y','z')),S.pi)
    if key==('6',16):assert same(g['x']+g['y'],g['z'])
    if key==('7',11):assert same(sum(g[name] for name in ('x','y','z','t')),2*S.pi)


def recompute(question):
    verification=question['verification']
    operation=verification['operation']
    foundation=foundation_value(question,operation,verification)
    if foundation is not None:return foundation
    special=special_value(question,operation,verification)
    if special is not None:return special
    if operation=='evaluate':
        source=verification['expression']
        expression_bridge(question,source)
        bindings=verification.get('givens',{})
        binding_bridge(question,bindings)
        check_evaluate_context(question,bindings)
        result=parse(source,bindings=bindings)
        assert not result.free_symbols,('Unbound symbolic expression',source,bindings)
        assert finite_real(result),('Non-real or undefined expression',source)
        geometric=geometric_evaluation(question,bindings)
        if geometric is not None:assert same(geometric,result),('Formula does not match geometric givens',question['practice_scope'])
        return result
    raise AssertionError(('Unknown audit operation',operation,question['practice_scope']))


def verify(question):
    scope=question['practice_scope']
    assert scope['catalog']=='G3' and scope['section'] in TYPES
    assert 1<=scope['type']<=TYPES[scope['section']] and 1<=scope['variant']<=5
    assert question['type']=='multiple_choice' and question['format']=='grid'
    assert question['text'] and question['explanation'] and scope['adaptation']
    options=question['options'];assert len(options)==4
    raw_values=question['verification']['option_values'];assert len(raw_values)==4
    values=[option_value(raw) for raw in raw_values]
    for raw,value,option in zip(raw_values,values,options):
        if question['verification'].get('answer_kind')=='label':
            assert option['text']==question['verification']['option_labels'][raw],('Label/source mismatch',scope)
        else:assert option['text']==r'\('+S.latex(value)+r'\)',('Option/source mismatch',scope)
        assert type(option['is_correct']) is bool
    assert all(not same(values[i],values[k]) for i in range(4) for k in range(i)),('Equivalent options',scope)
    expected=recompute(question)
    truth=[same(value,expected) for value in values]
    assert sum(truth)==1 and truth==[option['is_correct'] for option in options],('Incorrect key',scope,expected,values)
    correct_text=options[truth.index(True)]['text']
    assert correct_text in question['explanation'],('Explanation misses verified result',scope)


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--partial',action='store_true',help='Audit finished questions without requiring the final full bank.')
    parser.add_argument('--lesson',type=int,choices=range(1,10))
    args=parser.parse_args()
    total=0;coverage=Counter();counts={};all_texts=[]
    for lesson in range(1,10):
        if args.lesson and lesson!=args.lesson:continue
        path=next((ROOT/'data/quizzes/clasa_9').glob(f'clasa_9_u07_l{lesson:02d}_*.json'))
        data=json.loads(path.read_text(encoding='utf-8'))
        questions=[q for q in data['questions'] if q.get('practice_scope',{}).get('bank')==BANK]
        if not args.partial:assert len(questions)==COUNTS[lesson],(lesson,len(questions))
        assert len({q['text'] for q in questions})==len(questions)
        all_texts.extend(q['text'] for q in questions)
        for question in questions:
            scope=question['practice_scope'];assert MAPPING[scope['section']]==lesson
            try:verify(question)
            except Exception as exc:
                raise AssertionError(f"L{lesson} {scope['section']}.{scope['type']} variant {scope['variant']}: {exc}") from exc
            coverage[(scope['section'],scope['type'])]+=1;total+=1
        counts[lesson]=len(questions)
    expected={(section,typ):5 for section,count in TYPES.items() for typ in range(1,count+1)
              if not args.lesson or MAPPING[section]==args.lesson}
    if not args.partial:assert coverage==Counter(expected)
    assert len(set(all_texts))==len(all_texts),'Duplicate enunciations across lessons.'
    assert total>0,'No finished questions to audit.'
    print(f'OK: {total} trigonometrie grids, {total*4} options; lesson counts {counts}.')


if __name__=='__main__':main()
