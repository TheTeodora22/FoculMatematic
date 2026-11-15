"""Read-only mathematical audit, independent of the question generator.

Input is repository-owned audit data, parsed by a small AST allowlist (no eval,
sympify strings, or generator import). Numerical keys, sets and polynomials are
recomputed from original equations/conditions with exact symbolic arithmetic.
"""
import ast
import json
from collections import Counter
from pathlib import Path

import sympy as S

ROOT=Path(__file__).resolve().parents[1]
BANK='gradul_ii_a4_v1'
SYMBOLS={name:S.Symbol(name,real=True) for name in 'x y z m a b c t p q n'.split()}
x=SYMBOLS['x']; m=SYMBOLS['m']; t=SYMBOLS['t']


def parse(value):
    if not isinstance(value,str): return S.sympify(value)
    env={**SYMBOLS,'oo':S.oo,'pi':S.pi,'Reals':S.S.Reals,'EmptySet':S.EmptySet,'True':True,'False':False}
    funcs={'sqrt':S.sqrt,'Abs':S.Abs,'cos':S.cos,'sin':S.sin,'Rational':S.Rational,
           'FiniteSet':S.FiniteSet,'Interval':S.Interval,'Union':S.Union,
           'Complement':S.Complement,'Tuple':S.Tuple,'Interval.open':S.Interval.open,
           'Interval.Lopen':S.Interval.Lopen,'Interval.Ropen':S.Interval.Ropen}
    def node(n):
        if isinstance(n,ast.Constant):
            if isinstance(n.value,bool): return n.value
            assert isinstance(n.value,(int,float))
            return S.Rational(str(n.value))
        if isinstance(n,ast.Name): return env[n.id]
        if isinstance(n,ast.Tuple): return S.Tuple(*(node(v) for v in n.elts))
        if isinstance(n,ast.Set): return S.FiniteSet(*(node(v) for v in n.elts))
        if isinstance(n,ast.UnaryOp): return -node(n.operand) if isinstance(n.op,ast.USub) else node(n.operand)
        if isinstance(n,ast.BinOp):
            left,right=node(n.left),node(n.right)
            if isinstance(n.op,ast.Add): return left+right
            if isinstance(n.op,ast.Sub): return left-right
            if isinstance(n.op,ast.Mult): return left*right
            if isinstance(n.op,ast.Div): return left/right
            if isinstance(n.op,ast.Pow): return left**right
        if isinstance(n,ast.Call):
            name=n.func.id if isinstance(n.func,ast.Name) else n.func.value.id+'.'+n.func.attr
            assert name in funcs and not n.keywords
            return funcs[name](*(node(arg) for arg in n.args))
        raise ValueError(ast.dump(n))
    return node(ast.parse(value,mode='eval').body)


def same(first,second):
    if isinstance(first,S.Tuple) and isinstance(second,S.Tuple):
        return len(first)==len(second) and all(same(a,b) for a,b in zip(first,second))
    if isinstance(first,S.Set) or isinstance(second,S.Set):
        return isinstance(first,S.Set) and isinstance(second,S.Set) and S.SymmetricDifference(first,second)==S.EmptySet
    return S.simplify(first-second)==0


def solve_one(equations,variable):
    equations=[parse(v) for v in equations]
    values=S.solve(equations,[variable],dict=True)
    assert len(values)==1, values
    return S.simplify(values[0][variable])


def vertex(f):
    p=S.Poly(f,x)
    assert p.degree()==2 and p.LC()!=0
    center=S.solve(S.diff(f,x),x)
    assert len(center)==1
    return S.Tuple(center[0],S.simplify(f.subs(x,center[0])))


def increasing(f):
    assert S.Poly(f,x).degree()>=1
    return S.solve_univariate_inequality(S.Ge(S.diff(f,x),0),x,relational=False)


def numeric_set(f,domain=S.S.Reals): return S.solveset(f,x,domain=domain)


def recompute(d):
    task=d['task']
    f=parse(d['f']) if 'f' in d else None
    if task=='linear_tuple':
        variables=[SYMBOLS[v] for v in d['variables']]
        rows=S.solve([parse(v) for v in d['equations']],variables,dict=True)
        assert len(rows)==1
        return S.Tuple(*(S.simplify(rows[0][v]) for v in variables))
    if task in ('vertex','vertex_x','vertex_value'):
        result=vertex(f)
        return result if task=='vertex' else result[0 if task=='vertex_x' else 1]
    if task in ('range','range_min'):
        domain=parse(d['domain'])
        result=S.calculus.util.function_range(f,x,domain)
        return result.inf if task=='range_min' else result
    if task=='vertex_point':
        aa=S.Symbol('aa',real=True)
        eq=aa*(d['px']-d['h'])**2+d['k']-parse(d['py'])
        value=S.solve(eq,aa)
        assert len(value)==1 and value[0]!=0
        return S.expand(value[0]*(x-d['h'])**2+d['k'])
    if task in ('distance_extreme','distance_argmin'):
        f=sum(weight*((x-px)**2+py**2) for (px,py),weight in zip(d['points'],d['weights']))
        result=vertex(f)
        return result[1] if task=='distance_extreme' else result[0]
    if task=='piecewise_values':
        return sum(parse(d['left'] if at<=d['threshold'] else d['right']).subs(x,at) for at in d['arguments'])
    if task=='parameter_root': return solve_one([d['equation']],SYMBOLS[d['variable']])
    if task=='image_sets':
        aa,bb=parse(d['A']),parse(d['B'])
        def image(domain): return S.FiniteSet(*(f.subs(x,at) for at in domain))
        return (image(aa)&image(bb))-image(aa&bb)
    if task=='root_count':
        result=numeric_set(f,parse(d['domain']))
        assert isinstance(result,S.FiniteSet)
        return S.Integer(len(result))
    if task=='vertex_locus':
        v=vertex(f); parameter=SYMBOLS[d['parameter']]
        param=S.solve(v[0]-x,parameter)
        assert len(param)==1
        return S.expand(v[1].subs(parameter,param[0]))
    if task=='fixed_point':
        parameter=SYMBOLS[d['parameter']]
        p=S.Poly(f,parameter)
        assert p.degree()==1
        at=S.solve(p.coeff_monomial(parameter),x)
        assert len(at)==1
        return S.Tuple(at[0],S.simplify(f.subs({x:at[0],parameter:0})))
    if task=='vertex_quadrant':
        assert d['quadrant']==1
        v=vertex(f); parameter=SYMBOLS[d['parameter']]
        return S.Intersection(*(S.solve_univariate_inequality(S.Gt(c,0),parameter,relational=False) for c in v))
    if task=='known_root':
        constant=S.Symbol('constant',real=True)
        val=S.solve(d['known']**2-d['sum']*d['known']+constant,constant)[0]
        return val if d.get('output')=='product' else S.Tuple(val,d['sum']-d['known'])
    if task=='root_expression':
        result=numeric_set(f)
        assert len(result)==2
        terms=[parse(d['expression']).subs(t,r) for r in result]
        assert all(v.is_finite for v in terms)
        return S.simplify(sum(terms))
    if task=='viete_square_parameter':
        p=S.Symbol('p',real=True)
        val=S.solve(d['sum']**2-2*p-d['squares'],p)[0]
        assert d['sum']**2-4*val>=0
        return val
    if task=='viete_eliminate':
        pp=S.Poly(f,x); aa,bb,cc=pp.all_coeffs(); parameter=SYMBOLS[d['parameter']]
        param=S.solve(-bb/aa-t,parameter)
        assert len(param)==1
        return S.expand((cc/aa).subs(parameter,param[0]))
    if task=='coeff_from_roots':
        rr=list(map(parse,d['roots'])); p=S.Poly(S.prod(x-r for r in rr),x)
        return S.Tuple(*p.all_coeffs()[1:])
    if task=='common_root':
        common=S.gcd(parse(d['first']),parse(d['second']))
        result=numeric_set(common)
        assert len(result)==1
        return next(iter(result))
    if task=='polynomial_roots': return S.expand(S.prod(x-parse(r) for r in d['roots']))
    if task=='root_product_sign':
        pp=S.Poly(f,x); aa,bb,cc=pp.all_coeffs()
        assert S.discriminant(pp,x)>=0
        return S.sign(cc/aa)
    if task=='transformed_roots':
        rr=numeric_set(f)
        mapped=[parse(d['transform']).subs(t,r) for r in rr]
        assert all(v.is_finite for v in mapped)
        return S.expand(S.prod(x-v for v in mapped))
    if task=='between_parameter':
        at=d['threshold']; expression=x*x-d['sum']*x+m
        return S.solve_univariate_inequality(S.Lt(expression.subs(x,at),0),m,relational=False)
    if task=='system':
        variables=[SYMBOLS[v] for v in d['variables']]
        rows=S.solve([parse(e) for e in d['equations']],variables,dict=True)
        assert all(all(row[v].is_real for v in variables) for row in rows)
        return S.FiniteSet(*(S.Tuple(*(row[v] for v in variables)) for row in rows))
    if task=='sqrt_system':
        rr=S.solveset(t*t-d['sum']*t+d['product'],t,domain=S.Interval(0,S.oo))
        assert len(rr)==2
        first,second=rr
        return S.FiniteSet(S.Tuple(first**2,second**2),S.Tuple(second**2,first**2))
    if task=='increasing': return increasing(f)
    if task=='monotone_parameter':
        # For the convex quadratics used here, the derivative is increasing;
        # its value at the left endpoint controls the whole segment.
        assert S.diff(f,x,2)>0 and d['direction']=='increasing' and d['left']<d['right']
        return S.solve_univariate_inequality(S.Ge(S.diff(f,x).subs(x,d['left']),0),m,relational=False)
    if task=='functional_increasing':
        argument=parse(d['argument'])
        inverse=S.solve(argument-t,x)
        assert len(inverse)==1
        recovered=S.expand(parse(d['rhs']).subs(x,inverse[0]).subs(t,x))
        return increasing(recovered)
    if task=='two_monotone_intervals':
        # Vertex m must be to the right of the first closed segment and to
        # the left of the second one; equality still gives strict monotonicity.
        return S.Intersection(S.Interval(d['first'][1],S.oo),S.Interval(-S.oo,d['second'][0]))
    if task=='inequality':
        expression=parse(d['expression']); op={'>':S.Gt,'>=':S.Ge,'<':S.Lt,'<=':S.Le}[d['operator']]
        result=S.solve_univariate_inequality(op(expression,0),x,relational=False)
        # Explicitly retain all poles, even if later cancellation is possible.
        poles=numeric_set(S.denom(expression))
        return result-poles
    if task=='evaluate': return S.simplify(f.subs(x,d['at']))
    if task=='global_sign_parameter':
        f=x*x-2*d['offset']*x+m
        val=vertex(f)[1]
        return S.solve_univariate_inequality(S.Gt(val,0) if d['strict'] else S.Ge(val,0),m,relational=False)
    if task=='minimum_values': return S.Min(*(parse(v).subs(x,d['at']) for v in d['functions']))
    if task=='coeff_from_interval':
        polynomial=S.Poly(d['a']*(x-d['left'])*(x-d['right']),x)
        return S.Tuple(*polynomial.all_coeffs()[1:])
    if task=='halfline_sign':
        assert d['linear']>0
        return S.Interval(0,S.oo)
    if task=='root_distance':
        rr=sorted(numeric_set(f)); assert len(rr)==2
        return S.simplify(rr[1]-rr[0])
    if task in ('intersection','contact'):
        first=parse(d.get('first',d.get('f'))); second=parse(d.get('second',d.get('line')))
        rr=numeric_set(first-second)
        points=S.FiniteSet(*(S.Tuple(r,S.simplify(first.subs(x,r))) for r in rr))
        if task=='intersection': return points
        assert len(points)==1
        return next(iter(points))
    if task=='tangent_parameter':
        expression=parse(d['first'])-parse(d['line']); variable=SYMBOLS[d['variable']]
        answer=solve_one([str(S.discriminant(expression,x))],variable)
        result=numeric_set(expression.subs(variable,answer))
        assert len(result)==1
        if 'contact_domain' in d: assert next(iter(result)) in parse(d['contact_domain'])
        return answer
    if task=='uniform_horizontal_tangent':
        n=SYMBOLS['n']; parameter=SYMBOLS[d['parameter']]
        coefficients=S.Poly(S.discriminant(f-n,x),parameter).all_coeffs()
        return solve_one(list(map(str,coefficients)),n)
    if task=='uniform_root_count':
        discriminant=S.simplify(S.discriminant(f,x))
        assert discriminant.is_negative
        return S.Integer(0)
    if task in ('common_tangent','common_contact_tangent'):
        first=parse(d['first']); second=parse(d['second'])
        if task=='common_contact_tangent':
            rr=numeric_set(first-second); assert len(rr)==1
            at=next(iter(rr)); slope=S.diff(first,x).subs(x,at)
            assert same(slope,S.diff(second,x).subs(x,at))
            return S.expand(slope*(x-at)+first.subs(x,at))
        p,q=SYMBOLS['p'],SYMBOLS['q']; line=p*x+q
        rows=S.solve([S.discriminant(first-line,x),S.discriminant(second-line,x)],[p,q],dict=True)
        realrows=[row for row in rows if row[p].is_real and row[q].is_real]
        assert len(realrows)==1
        result=S.expand(line.subs(realrows[0]))
        assert len(numeric_set(first-result))==len(numeric_set(second-result))==1
        return result
    if task=='tangent_at':
        at=d['at']; slope=S.diff(f,x).subs(x,at)
        return S.expand(slope*(x-at)+f.subs(x,at))
    if task=='bisector_parameter':
        cc=SYMBOLS['c']; f=d['a']*x*x+cc
        return solve_one([str(S.discriminant(f-x,x)),str(S.discriminant(f+x,x))],cc)
    if task=='two_lines_parabola':
        bb,cc=SYMBOLS['b'],SYMBOLS['c']; f=d['a']*x*x+bb*x+cc
        rows=S.solve([S.discriminant(f-parse(line),x) for line in d['lines']],[bb,cc],dict=True)
        assert len(rows)==1
        return S.Tuple(rows[0][bb],rows[0][cc])
    if task=='point_tangent_positive':
        bb=SYMBOLS['b']; f=x*x+bb*x+d['intercept']
        possible=S.solve(S.discriminant(f-d['line'],x),bb)
        valid=[v for v in possible if -v/2>0]
        assert len(valid)==1
        return S.Tuple(valid[0],d['intercept'])
    if task=='above_two_lines': return S.Interval(max(S.Rational(p)**2/4 for p in d['slopes']),S.oo)
    if task=='double_parabola_parameter':
        candidate=parse(d['candidate']); variable=SYMBOLS[d['variable']]
        return solve_one([str(S.discriminant(parse(d[key])-candidate,x)) for key in ('first','second')],variable)
    if task=='mixed_system':
        rr=S.solveset(t*t+t-d['constant'],t,domain=S.Interval(0,S.oo))
        assert len(rr)==1
        yy=next(iter(rr)); xx=S.sqrt(yy)
        return S.FiniteSet(S.Tuple(-xx,yy),S.Tuple(xx,yy))
    if task=='proportional_coefficients':
        pp=S.Poly(S.expand(d['a']*f/S.Poly(f,x).LC()),x)
        assert len(numeric_set(f))==2
        return S.Tuple(*pp.all_coeffs()[1:])
    if task=='three_equal':
        assert S.Rational(d['sum'])**2==3*d['pairs']
        value=S.Rational(d['sum'],3)
        return S.Tuple(value,value,value)
    raise ValueError(task)


def run():
    counts=[]; scope=Counter(); tasks=Counter(); checked=0
    for path in sorted((ROOT/'data/quizzes/clasa_9').glob('clasa_9_u04_l*.json')):
        data=json.loads(path.read_text(encoding='utf-8'))
        questions=[q for q in data['questions'] if q.get('practice_scope',{}).get('bank')==BANK]
        counts.append(len(questions))
        for q in questions:
            tag=q['practice_scope']; scope[(tag['section'],tag['type'])]+=1
            d=q['verification']; tasks[d['task']]+=1
            assert len(q['options'])==4 and len({v['text'] for v in q['options']})==4
            values=list(map(parse,d['option_values']))
            assert len(values)==4 and all(not same(values[i],values[j]) for i in range(4) for j in range(i))
            for value,option in zip(values,q['options']):
                assert option['text']==r'\('+S.latex(value)+r'\)',(tag,option['text'])
            expected=recompute(d)
            matches=[same(value,expected) for value in values]
            assert matches==[v['is_correct'] for v in q['options']],(tag,d['task'],expected,values,matches)
            assert sum(matches)==1
            assert 'Rezultatul cerut este '+r'\('+S.latex(expected)+r'\)' in q['explanation'],tag
            checked+=1
    assert counts==[60,30,30,75,155,75,55],counts
    assert scope==Counter({(section,typ):5 for section,total in [(1,24),(2,17),(3,9),(4,22),(5,15),(6,9)] for typ in range(1,total+1)})
    print(f'OK: {checked} grids; 96 types x 5; 1920 mathematically distinct options; {len(tasks)} independent audit tasks.')


if __name__=='__main__':run()
