"""Original A4 grids; no runtime expression parsing or database writes.

Each catalog proof/drawing is explicitly adapted to a computable question.
The audit data describes the original mathematical givens, not an answer key.
"""
import json
import re
from collections import Counter
from pathlib import Path

import sympy as S

ROOT = Path(__file__).resolve().parents[1]
BANK = 'gradul_ii_a4_v1'
NAMES=json.loads(Path(__file__).with_name('quadratic_type_names.json').read_text(encoding='utf-8'))
PAGES={1:'129–133',2:'134–137',3:'138–139',4:'139–144',5:'144–146',6:'146–149'}
PARTIAL={(1,11),(1,15),(1,19),(2,9),(2,10),(2,14),(3,2),(3,8),
         (4,8),(4,13),(4,17),(4,19),(5,10),(5,12),(5,13),(6,6)}
x, y, z, m, a, b, c, t = S.symbols('x y z m a b c t', real=True)
Q = S.Rational
LESSON1 = {1,2,4,5,6,7,8,9,12,13,14,24}
LESSON2 = {10,19,20,21,22,23}


def tex(value): return S.latex(S.sympify(value))
def math(value): return r'\(' + tex(value) + r'\)'
def poly(value): return S.expand(value)
def vertex(f):
    p = S.Poly(f,x); aa,bb,cc = p.all_coeffs()
    h = -bb/(2*aa)
    return S.Tuple(h,S.simplify(f.subs(x,h)))
def roots(f): return S.solveset(f,x,domain=S.S.Reals)
def realrange(f,domain=S.S.Reals):
    return S.calculus.util.function_range(f,x,domain)
def inequality(f,op):
    rel = {'>':S.Gt,'>=':S.Ge,'<':S.Lt,'<=':S.Le}[op](f,0)
    return S.solve_univariate_inequality(rel,x,relational=False)
def solutions(equations,variables):
    solved = S.solve(equations,variables,dict=True)
    return S.FiniteSet(*(S.Tuple(*(S.simplify(row[v]) for v in variables)) for row in solved))


def mutate(value,k):
    if isinstance(value,S.Set):
        if isinstance(value,S.FiniteSet):
            return S.FiniteSet(*(mutate(v,k) for v in value)) if value else S.FiniteSet(k)
        return S.S.Reals if k==1 else S.EmptySet if k==2 else S.FiniteSet(0)
    if isinstance(value,S.Tuple): return S.Tuple(value[0]+k,*value[1:])
    return S.simplify(value+k)


def build_questions():
    banks={i:[] for i in range(1,8)}

    def emit(section,typ,j,text,answer,reason,audit,lesson=None,adaptation='Exercițiu original de calcul sau concluzie; justificarea este în explicație.'):
        if lesson is None:
            lesson = (1 if typ in LESSON1 else 2 if typ in LESSON2 else 3) if section==1 else 4 if section==2 and typ<16 else 7 if section in (2,6) else 5 if section in (3,4) else 6
        answer=S.sympify(answer)
        values=[answer]
        for k in [1,-1,2,-2,3,4]:
            candidate=mutate(answer,k)
            if candidate not in values: values.append(candidate)
            if len(values)==4: break
        if len(values)<4:
            for candidate in [S.EmptySet,S.S.Reals,S.FiniteSet(j),S.Interval(j,j+1)]:
                if candidate not in values:values.append(candidate)
                if len(values)==4:break
        assert len(values)==4,(section,typ,j,values)
        correct=len(banks[lesson])%4
        values.insert(correct,values.pop(0))
        reason=reason.replace(' (cu numărul j din enunț)','')
        reason=re.sub(r'(?<![A-Za-zăâîșțĂÂÎȘȚ])j',f'({j})',reason)
        banks[lesson].append({
            'text':text,'type':'multiple_choice','format':'grid','points':10,
            'explanation':reason+' Rezultatul cerut este '+math(answer)+'.',
            'options':[{'text':math(v),'is_correct':i==correct} for i,v in enumerate(values)],
            'practice_scope':{'bank':BANK,'catalog':'A4','section':section,'type':typ,'type_name':NAMES[str(section)][str(typ)],'pages':PAGES[section],'variant':j,'coverage':'partial_case' if (section,typ) in PARTIAL else 'adapted_grid','adaptation':adaptation},
            'verification':{**audit,'option_values':[str(v) for v in values]},
        })

    for j in range(1,6):
        aa=(-1 if j%2==0 else 1)*(j+1); h=j-3; k=2-j
        f=poly(aa*(x-h)**2+k)
        coeff=S.Tuple(aa,-2*aa*h,aa*h*h+k)
        sample=[(i,f.subs(x,i)) for i in (-1,0,2)]
        eqs=[a*i*i+b*i+c-value for i,value in sample]
        emit(1,1,j,'Determinați coeficienții (a;b;c) ai funcției '+math(a*x*x+b*x+c)+' dacă '+', '.join('f('+str(i)+')='+str(value) for i,value in sample)+'. Verificați a≠0.',coeff,
             'Înlocuirea celor trei abscise distincte produce un sistem liniar în a,b,c. Soluția sa este unică; primul coeficient este nenul, deci funcția are gradul al doilea.',{'task':'linear_tuple','equations':list(map(str,eqs)),'variables':['a','b','c']})
        emit(1,2,j,'Pentru '+math(S.Eq(y,f))+', determinați perechea (h;k) din forma canonică a(x−h)²+k.',S.Tuple(h,k),
             'Completăm pătratul: h=−b/(2a), iar k=f(h)=−Δ/(4a). Coeficientul principal este nenul.',{'task':'vertex','f':str(f)})
        emit(1,3,j,'Determinați imaginea pe ℝ a funcției '+math(S.Eq(y,f))+'.',realrange(f),
             'Forma canonică este '+math(aa*(x-h)**2+k)+'. Pătratul poate lua orice valoare nenegativă. Pentru a>0 imaginea începe la minim; pentru a<0 se termină la maxim, iar extremul este atins.',{'task':'range','f':str(f),'domain':'Reals'})
        family=poly((j+1)*(x-m)**2+j)
        emit(1,4,j,'Pentru familia '+math(S.Eq(y,family))+', m∈ℝ, determinați coordonatele vârfului în funcție de m.',S.Tuple(m,j),
             'Gruparea după pătratul x−m dă un coeficient principal pozitiv. Abscisa vârfului este m și ordonata este termenul independent al pătratului.',{'task':'vertex','f':str(family)})
        value=f.subs(x,h+2)
        emit(1,5,j,f'Parabola are vârful V({h};{k}) și trece prin punctul ({h+2};{value}). Determinați polinomul f(x).',f,
             'Scriem f(x)=a(x−h)²+k. Punctul suplimentar are abscisa diferită de h, deci a=(y−k)/(x−h)² este determinat unic și nenul.',{'task':'vertex_point','h':h,'k':k,'px':h+2,'py':str(value)})
        tang=poly((j+1)*(x-h)**2)
        emit(1,6,j,f'Parabola este tangentă axei Ox în ({h};0) și trece prin ({h+1};{j+1}). Determinați f(x).',tang,
             'Tangența la Ox înseamnă rădăcină dublă h: f(x)=a(x−h)². Înlocuirea punctului suplimentar dă a nenul.',{'task':'vertex_point','h':h,'k':0,'px':h+1,'py':j+1})
        eqs=[-b/(2*(j+1))-h,(j+1)*h*h+b*h+c-k]
        emit(1,7,j,f'Funcția f(x)={j+1}x²+bx+c are vârful V({h};{k}). Determinați (b;c).',S.Tuple(-2*(j+1)*h,(j+1)*h*h+k),
             'Condiția pentru abscisă este −b/(2a)=h. După aflarea lui b, condiția f(h)=k determină c.',{'task':'linear_tuple','equations':list(map(str,eqs)),'variables':['b','c']})
        # M=(x,0), A=(j,1), B=(-j,2): difference of squared distances.
        distance=poly((x-j)**2+1-2*((x+j)**2+4))
        emit(1,8,j,f'M(x;0), A({j};1), B({-j};2). Determinați maximul funcției MA²−2MB².',vertex(distance)[1],
             'Formula distanței dă '+math(distance)+'. Coeficientul lui x² este negativ, deci valoarea din vârf este maximul pe ℝ.',{'task':'distance_extreme','points':[[j,1],[-j,2]],'weights':[1,-2]})
        invariant=(x-m-j)**2+(x-m+j)**2+j
        emit(1,9,j,'Pentru m∈ℝ, aflați minimul pe ℝ al funcției '+math(S.Eq(y,invariant))+'.',2*j*j+j,
             'La dezvoltare, funcția devine 2(x−m)²+2j²+j (cu numărul j din enunț). Pătratul este minim zero pentru x=m; valoarea minimă nu depinde de m.',{'task':'vertex_value','f':str(invariant)})
        emit(1,10,j,'Care este abscisa axei de simetrie a parabolei '+math(S.Eq(y,f))+'?',S.Integer(h),
             'În forma canonică, valorile la h−t și h+t sunt egale. Axa este x=h=−b/(2a).',{'task':'vertex_x','f':str(f)})
        emit(1,11,j,'Pentru trasarea parabolei '+math(S.Eq(y,f))+', care este perechea (xV;yV)?',S.Tuple(h,k),
             'Determinăm vârful prin h=−b/(2a), k=f(h). Pentru desen se adaugă axa x=h, sensul ramurilor din semnul lui a și intersecțiile cu axele.',{'task':'vertex','f':str(f)},adaptation='Trasarea este adaptată în identificarea vârfului; nu se cere desen interactiv.')
        positive=poly((j+1)*(x-h)**2+k)
        emit(1,12,j,f'O funcție pătratică are minimul {k}, axa x={h} și f({h+1})={k+j+1}. Determinați f(x).',positive,
             'Minimul și axa fixează vârful (h,k). Din f(h+1)=a+k obținem a>0 și forma canonică, apoi dezvoltăm.',{'task':'vertex_point','h':h,'k':k,'px':h+1,'py':k+j+1})
        pa=S.Tuple(j,2*j,3*j)
        emit(1,13,j,f'Coeficienții a,b,c sunt în progresie aritmetică, a={j}, iar axa parabolei este x=−1. Determinați (a;b;c).',pa,
             'Axa impune b=2a. Din progresia aritmetică avem a+c=2b, deci c=3a. Valoarea a dată este pozitivă.',{'task':'linear_tuple','equations':[str(a-j),str(b-2*a),str(a+c-2*b)],'variables':['a','b','c']})
        emit(1,14,j,f'M(t;0), A({j};2), B({j+4};−1). Pentru ce t suma MA²+MB² este minimă?',j+2,
             'Suma este (t−j)²+(t−j−4)²+5. La completarea pătratului rezultă 2(t−j−2)²+13. Minimul se atinge unic la mijlocul absciselor punctelor fixe.',{'task':'distance_argmin','points':[[j,2],[j+4,-1]],'weights':[1,1]})
        xx=[-j,j]
        emit(1,15,j,f'f(x)=x² pentru x≤0 și f(x)=2x+{j} pentru x>0. Calculați f({-j})+f({j}).',j*j+3*j,
             'Argumentul negativ folosește ramura pătratică; cel pozitiv folosește ramura afină. Pragul 0 aparține primei ramuri, conform enunțului.',{'task':'piecewise_values','threshold':0,'left':'x**2','right':str(2*x+j),'arguments':xx},adaptation='Graficul pe ramuri este adaptat într-o evaluare cu validarea ramurilor.')
        emit(1,16,j,f'f(x)=x²+m pentru x≤0 și f(x)=2x−m pentru x>0. Punctul ({j};{3*j}) aparține graficului. Aflați m.',-j,
             'Abscisa dată este pozitivă, deci se impune 2x−m=y pe ramura din dreapta. Soluția este validă pe această ramură; folosirea celeilalte formule ar fi incorectă.',{'task':'parameter_root','equation':str(2*j-m-3*j),'variable':'m'})
        domain=S.Interval.open(h,h+2)
        restricted=poly((x-h)**2+k)
        emit(1,17,j,'Aflați imaginea lui '+math(S.Eq(y,restricted))+' pe intervalul '+math(domain)+'.',realrange(restricted,domain),
             'Pe intervalul de la dreapta vârfului funcția este strict crescătoare. Nici vârful, nici celălalt capăt nu aparțin domeniului, deci nici valorile lor limită nu sunt atinse.',{'task':'range','f':str(restricted),'domain':str(domain)})
        aset=S.FiniteSet(-j,0); bset=S.FiniteSet(0,j)
        emit(1,18,j,f'Pentru f(x)=x², A={{−{j};0}} și B={{0;{j}}}, determinați mulțimea (f(A)∩f(B))∖f(A∩B).',S.FiniteSet(j*j),
             'A∩B={0}, deci f(A∩B)={0}. Totuși f(A)=f(B)={0,j²}, deoarece −j și j au aceeași imagine. Diferența cerută conține numai j²; imaginea nu păstrează în general intersecția.',{'task':'image_sets','f':'x**2','A':str(aset),'B':str(bset)})
        crossing=poly((x-j)*(x-j-2)-1)
        emit(1,19,j,'Câte rădăcini reale distincte are ecuația '+math(S.Eq(crossing,0))+'?',S.Integer(2),
             'La x=j valoarea este −1, iar coeficientul principal este pozitiv. Forma canonică are minim strict negativ și tinde la +∞ pe ambele ramuri, deci sunt două rădăcini reale distincte; echivalent Δ>0.',{'task':'root_count','f':str(crossing),'domain':'Reals'},adaptation='Existența unei rădăcini este adaptată în numărul de rădăcini pentru o familie explicită.')
        family=poly((x-m)**2+j*m+1)
        emit(1,20,j,'Vârfurile familiei '+math(S.Eq(y,family))+' (m∈ℝ) aparțin unei drepte y=g(x). Determinați g(x).',j*x+1,
             'Forma canonică dă V=(m,jm+1). Eliminarea lui m=xV produce yV=jxV+1. Deoarece m parcurge ℝ, se obține întreaga dreaptă.',{'task':'vertex_locus','f':str(family),'parameter':'m'})
        family=poly((x-m)**2+m*m+j)
        emit(1,21,j,'Determinați g(x) pentru locul vârfurilor familiei '+math(S.Eq(y,family))+' (m∈ℝ), scris y=g(x).',x*x+j,
             'Vârful este (m,m²+j). Eliminarea parametrului dă y=x²+j. Toate abscisele reale sunt parcurse deoarece m este arbitrar.',{'task':'vertex_locus','f':str(family),'parameter':'m'})
        family=x*x+m*(x-j)+j
        emit(1,22,j,'Aflați punctul fix comun tuturor graficelor familiei '+math(S.Eq(y,family))+' (m∈ℝ). Răspundeți (x;y).',S.Tuple(j,j*j+j),
             'Pentru ca valoarea să nu depindă de m, coeficientul lui m trebuie să fie zero: x−j=0. Înlocuirea în termenul fără m dă ordonata fixă.',{'task':'fixed_point','f':str(family),'parameter':'m'})
        family=(x-m)**2+m+j
        emit(1,23,j,'Pentru ce m vârful parabolei '+math(S.Eq(y,family))+' se află strict în cadranul I?',S.Interval.open(0,S.oo),
             'Vârful este (m,m+j). Condițiile sunt m>0 și m+j>0. Cum j este pozitiv, a doua condiție este automată când prima este adevărată; axele sunt excluse.',{'task':'vertex_quadrant','f':str(family),'parameter':'m','quadrant':1})
        eqs=[-a/2-j,b/2-(j+1)]
        emit(1,24,j,f'f(x)=x²+ax și g(x)=−x²+bx au, respectiv, minimul atins la x={j} și maximul atins la x={j+1}. Determinați (a;b).',S.Tuple(-2*j,2*j+2),
             'Coeficienții principali +1 și −1 asigură existența minimului, respectiv maximului. Formula abscisei vârfului dă −a/2=j și b/2=j+1.',{'task':'linear_tuple','equations':list(map(str,eqs)),'variables':['a','b']})

        r,s=j,j+2; p=poly((x-r)*(x-s)); total=r+s; product=r*s
        emit(2,1,j,f'Numărul {r} este rădăcină a ecuației x²−{total}x+m=0. Determinați perechea (m; cealaltă rădăcină).',S.Tuple(product,s),
             'Înlocuirea rădăcinii cunoscute determină m. Prin Viète, suma rădăcinilor este coeficientul opus al lui x, deci cealaltă rădăcină se obține prin scădere.',{'task':'known_root','sum':total,'known':r})
        emit(2,2,j,'Rădăcinile ecuației '+math(S.Eq(p,0))+' sunt x₁,x₂. Calculați x₁²+x₂² fără a folosi formula radicalilor.',r*r+s*s,
             'Din Viète avem S=−b/a și P=c/a. Identitatea x₁²+x₂²=S²−2P dă rezultatul, după verificarea Δ≥0.',{'task':'root_expression','f':str(p),'expression':'t**2','combine':'sum'})
        emit(2,3,j,'Rădăcinile ecuației '+math(S.Eq(p,0))+' sunt x₁,x₂. Calculați 1/(x₁+1)+1/(x₂+1).',Q(1,r+1)+Q(1,s+1),
             'Numitorii sunt nenuli: rădăcinile sunt pozitive. După aducerea la numitor comun, expresia este (S+2)/(P+S+1), cu S și P date de Viète.',{'task':'root_expression','f':str(p),'expression':'1/(t+1)','combine':'sum'})
        emit(2,4,j,f'Ecuația x²−{total}x+m=0 are rădăcini reale x₁,x₂ cu x₁²+x₂²={r*r+s*s}. Aflați m.',product,
             'Viète și S²−2P dau S²−2m egal cu valoarea prescrisă. Soluția trebuie validată prin Δ=S²−4m≥0; aici Δ=4>0.',{'task':'viete_square_parameter','sum':total,'squares':r*r+s*s})
        param=poly(x*x-m*x+j*m)
        emit(2,5,j,'Pentru valorile lui m cu rădăcini reale, S și P sunt suma și produsul rădăcinilor ecuației '+math(S.Eq(param,0))+'. Determinați expresia P în funcție de S, fără m. În opțiuni, t reprezintă suma S.',j*t,
             'Viète dă S=m și P=jm. Eliminăm m, obținând P=jS. În opțiuni variabila t reprezintă suma S.',{'task':'viete_eliminate','f':str(param),'parameter':'m'},adaptation='Relația independentă este redată ca polinom în t, unde t=S.')
        emit(2,6,j,f'Ecuația monică x²+bx+c=0 are rădăcinile {r} și {s}. Determinați (b;c).',S.Tuple(-total,product),
             'Pentru o ecuație monică, b este opusul sumei rădăcinilor și c este produsul lor. Nu există ambiguitate de factor de scalare.',{'task':'coeff_from_roots','roots':[r,s]})
        p2=poly((x-r)*(x+s+1))
        emit(2,7,j,'Determinați rădăcina reală comună ecuațiilor '+math(S.Eq(p,0))+' și '+math(S.Eq(p2,0))+'.',S.Integer(r),
             'Scădem ecuațiile pentru a obține o ecuație liniară, apoi înlocuim candidatul în ambele ecuații. Celălalt factor al fiecărei ecuații are rădăcini diferite.',{'task':'common_root','first':str(p),'second':str(p2)})
        emit(2,8,j,f'Construiți polinomul monic cu rădăcinile {j}−√2 și {j}+√2.',poly((x-j)**2-2),
             'Suma rădăcinilor conjugate este 2j, iar produsul este j²−2. Polinomul monic este x²−Sx+P, cu coeficientul principal 1.',{'task':'polynomial_roots','roots':[str(j-S.sqrt(2)),str(j+S.sqrt(2))]})
        deg=(m-j)*x*x+x+1
        emit(2,9,j,'Pentru '+math(S.Eq(deg,0))+f', câte rădăcini reale distincte există la m={j}?',S.Integer(1),
             'La parametrul dat coeficientul lui x² se anulează. Ecuația devine x+1=0, deci are o soluție reală, însă nu mai este de gradul al doilea. Formula discriminantului nu poate înlocui această separare de caz.',{'task':'root_count','f':str(deg.subs(m,j)),'domain':'Reals'},adaptation='Discuția după parametru este adaptată în cazul degenerat explicit.')
        emit(2,10,j,f'Rădăcinile ecuației x²−{2*j+2}x+m=0 sunt termenii extremi ai progresiei aritmetice cu termenul central {j+1} și rația 1. Aflați m.',j*(j+2),
             'Cei trei termeni sunt j, j+1, j+2, deci rădăcinile sunt j și j+2. Viète fixează produsul m. Aceasta este o adaptare la progresia rădăcinilor, fără condiția suplimentară asupra tuturor coeficienților.',{'task':'known_root','sum':2*j+2,'known':j,'output':'product'},adaptation='Caz simplificat de rădăcini în PA; nu reproduce condiția a,x₁,b,x₂,c în PA.')
        opposite=poly(x*x+j*x-(j+1))
        emit(2,11,j,'Fără a rezolva '+math(S.Eq(opposite,0))+', care este semnul produsului x₁x₂? Răspundeți −1,0 sau 1.',S.Integer(-1),
             'Produsul c/a este strict negativ, iar Δ=b²−4ac>0. Rădăcinile sunt reale, nenule și de semne opuse, deci produsul are semnul −1.',{'task':'root_product_sign','f':str(opposite)})
        transformed=poly((x-Q(1,r))*(x-Q(1,s)))
        emit(2,12,j,'Dacă x₁,x₂ sunt rădăcinile lui '+math(S.Eq(p,0))+', determinați polinomul monic cu rădăcinile 1/x₁ și 1/x₂.',transformed,
             'Produsul P este nenul. Noile rădăcini au suma S/P și produsul 1/P, deci polinomul monic este x²−(S/P)x+1/P.',{'task':'transformed_roots','f':str(p),'transform':'1/t'})
        threshold=j+1
        emit(2,13,j,f'Pentru ce m ecuația x²−{2*threshold}x+m=0 are rădăcini reale x₁<{threshold}<x₂?',S.Interval.open(-S.oo,threshold**2),
             'O parabolă cu coeficient principal pozitiv are un prag strict între rădăcini exact când valoarea în prag este negativă. Aici f(prag)=m−prag², deci m<prag²; această condiție asigură și Δ>0.',{'task':'between_parameter','sum':2*threshold,'threshold':threshold})
        domain=S.Interval.open(j,j+3)
        emit(2,14,j,'Câte rădăcini distincte ale ecuației '+math(S.Eq(p,0))+' aparțin intervalului '+math(domain)+'?',S.Integer(1),
             'Factorizarea dă rădăcinile j și j+2. Capătul j este exclus, iar j+2 este interior; rezultă exact o rădăcină admisă.',{'task':'root_count','f':str(p),'domain':str(domain)},adaptation='Cardinal într-un interval pentru un caz explicit, cu capete validate.')
        power=j+2
        emit(2,15,j,'Rădăcinile ecuației '+math(S.Eq(p,0))+f' sunt x₁,x₂. Calculați S{power}=x₁^{power}+x₂^{power}.',r**power+s**power,
             'Fiecare rădăcină verifică xᵢ²=Sxᵢ−P. Înmulțind și însumând obținem Sₙ₊₂=S·Sₙ₊₁−P·Sₙ, cu S₀=2, S₁=S. Recurența produce exact valoarea cerută.',{'task':'root_expression','f':str(p),'expression':str(t**power),'combine':'sum'})
        eqs=[x+y-total,x*y-product]
        emit(2,16,j,f'Rezolvați în ℝ² sistemul x+y={total}, xy={product}. Răspundeți prin mulțimea perechilor (x;y).',solutions(eqs,[x,y]),
             'x și y sunt rădăcinile aceleiași ecuații t²−St+P=0. După aflarea celor două valori, ambele ordini sunt admise și sunt verificate în sistem.',{'task':'system','equations':list(map(str,eqs)),'variables':['x','y']})
        emit(2,17,j,f'Pentru x,y≥0, rezolvați √x+√y={total}, √(xy)={product}. Răspundeți prin mulțimea perechilor (x;y).',S.FiniteSet(S.Tuple(r*r,s*s),S.Tuple(s*s,r*r)),
             'Punem u=√x≥0 și v=√y≥0. Atunci u+v=S, uv=P; cele două rădăcini pozitive sunt admise. Ridicarea la pătrat dă x=u²,y=v², fără soluții străine, deoarece u,v sunt nenegative.',{'task':'sqrt_system','sum':total,'product':product})

        # Monotonicity: endpoints of maximal intervals are included.
        increasing=S.Interval(h,S.oo) if aa>0 else S.Interval(-S.oo,h)
        emit(3,1,j,'Determinați intervalul maximal pe care '+math(S.Eq(y,f))+' este strict crescătoare.',increasing,
             'Abscisa vârfului este h=−b/(2a). Pentru a>0 funcția crește la dreapta vârfului; pentru a<0 crește la stânga lui. Includerea vârfului nu împiedică strictețea pe acest interval.',{'task':'increasing','f':str(f)})
        deg=(m-j)*x*x+x+j
        emit(3,2,j,'Pentru familia '+math(S.Eq(y,deg))+f', la m={j}, care este intervalul maximal de creștere strictă?',S.S.Reals,
             'Coeficientul principal se anulează la parametrul indicat. Rămâne o funcție afină de pantă +1, strict crescătoare pe toată ℝ; nu se aplică formula vârfului unei parabole.',{'task':'increasing','f':str(deg.subs(m,j))},adaptation='Discuția parametrului este adaptată în cazul degenerat explicit.')
        emit(3,3,j,f'Pentru ce m funcția f(x)=(x−m)² este strict crescătoare pe [{j};{j+2}]?',S.Interval(-S.oo,j),
             'Vârful este la x=m. Segmentul este integral pe ramura crescătoare exact când m≤capătul stâng. Egalitatea este permisă, deoarece funcția rămâne strict crescătoare la dreapta vârfului.',{'task':'monotone_parameter','f':'(x-m)**2','left':j,'right':j+2,'direction':'increasing'})
        emit(3,4,j,f'f(x)={j+1}x²+bx+c descrește până la x={h}, apoi crește; minimul este {k}. Determinați f(x).',positive,
             'Schimbarea variației fixează abscisa vârfului, iar marginea inferioară a imaginii fixează ordonata. Cu a dat, forma canonică este unică.',{'task':'vertex_point','h':h,'k':k,'px':h+1,'py':k+j+1})
        composite=(x-j)**4
        emit(3,5,j,f'f(t)=t² și g(x)=(x−{j})². Care este intervalul maximal pe care f(g(x)) este strict crescătoare?',S.Interval(j,S.oo),
             'Compunerea este (x−j)⁴. Distanța |x−j| crește strict pe [j,+∞), iar ridicarea la puterea a patra păstrează această ordine pentru valori nenegative. La stânga vârfului compunerea descrește.',{'task':'increasing','f':str(composite)})
        emit(3,6,j,f'Pentru ce m funcția f(x)=x²+mx este strict crescătoare pe [0;{j}]?',S.Interval(0,S.oo),
             'Abscisa vârfului este −m/2. Segmentul începe la 0 și trebuie să fie la dreapta vârfului: −m/2≤0, adică m≥0. La m=0, x² este strict crescătoare pe segmentul nenegativ, deci capătul se include.',{'task':'monotone_parameter','f':'x**2+m*x','left':0,'right':j,'direction':'increasing'})
        base=poly((x-j)**2+j); functional=poly(base.subs(x,2*x+1))
        emit(3,7,j,'Funcția pătratică f verifică pentru orice x∈ℝ relația '+math(S.Eq(S.Function('f')(2*x+1),functional))+'. Care este intervalul maximal de creștere strictă al lui f?',S.Interval(j,S.oo),
             'Substituția t=2x+1 este bijectivă pe ℝ și permite recuperarea lui f(t). După completarea pătratului, vârful este la t=j, coeficientul principal fiind pozitiv.',{'task':'functional_increasing','rhs':str(functional),'argument':'2*x+1'})
        moving=(x-(j+1))**2+j
        emit(3,8,j,f'F(s)=min{{(t−{j+1})²+{j}:t∈[s;s+2]}}. Calculați F({j}).',S.Integer(j),
             'Intervalul dat conține abscisa j+1 a vârfului. Pătratul poate fi zero în interior, deci minimul coincide cu valoarea funcției în vârf. În general se proiectează abscisa vârfului pe interval.',{'task':'range_min','f':str(moving),'domain':str(S.Interval(j,j+2))},adaptation='Extremul pe interval mobil este adaptat într-o evaluare concretă; nu se cere formula pe toate ramurile.')
        emit(3,9,j,f'Pentru ce m funcția f(x)=(x−m)² este strict descrescătoare pe [−{j};0] și strict crescătoare pe [{j};{2*j}]?',S.Interval(0,j),
             'Primul segment trebuie să fie la stânga vârfului, deci m≥0. Al doilea trebuie să fie la dreapta lui, deci m≤j. Intersecția condițiilor este închisă la ambele capete; fiecare segment are lungime pozitivă.',{'task':'two_monotone_intervals','first':[-j,0],'second':[j,2*j]})

        qpoly=poly((x-j)*(x-j-2))
        def ineq(typ,expression,op,question,reason,**extra):
            emit(4,typ,j,question,inequality(expression,op),reason,
                 {'task':'inequality','expression':str(expression),'operator':op,**extra})

        ineq(1,qpoly,'>', 'Unde este strict pozitiv polinomul '+math(qpoly)+'?',
             'Rădăcinile simple separă axa în trei intervale. Cu a>0, semnul este pozitiv în exteriorul rădăcinilor și negativ între ele. Stricta pozitivitate exclude rădăcinile.')
        prod=poly((x-j)*(x-j-2)*(x+j)*(x+j+1))
        ineq(2,prod,'<=','Rezolvați '+math(S.Le((x-j)*(x-j-2)*(x+j)*(x+j+1),0))+'.',
             'Ordonăm cele patru rădăcini distincte și urmărim alternarea semnului la rădăcinile simple. Coeficientul principal este pozitiv, iar egalitatea permite toate rădăcinile.')
        ratio=((x-j-2)*(x+j))/(x-j)
        ineq(3,ratio,'>=','Rezolvați '+math(S.Ge(ratio,0))+' pe domeniul său natural.',
             'Numitorul nu poate fi zero. În tabelul de semn includem atât zerourile numărătorului, cât și polul; zerourile admise se includ, polul este întotdeauna exclus.')
        ineq(4,qpoly,'<=','Rezolvați inecuația '+math(S.Le(qpoly,0))+'.',
             'Cu a>0 și două rădăcini simple, polinomul este nepozitiv exact între rădăcini, inclusiv capetele.')
        reduced=poly((x+j)**2-(2*j+2)*x-j*j-1)
        ineq(5,reduced,'<','Rezolvați '+math(S.Lt((x+j)**2-(2*j+2)*x-j*j-1,0))+'.',
             'Dezvoltăm pătratul și reducem termenii asemenea înainte de a construi tabelul de semn. Inegalitatea strictă exclude rădăcinile expresiei reduse.')
        biquad=(x*x-j*j)*(x*x-(j+1)**2)
        ineq(6,biquad,'<=','Rezolvați în ℝ '+math(S.Le(biquad,0))+'.',
             'Punem t=x²≥0. Inecuația în t este nepozitivă între j² și (j+1)². Revenim la x prin j≤|x|≤j+1, cu ambele intervale simetrice și capete incluse.')
        block=(x*x-j)*(x*x-j-2)
        ineq(7,block,'>=','Rezolvați '+math(S.Ge(block,0))+'.',
             'Substituția t=x²−j reduce problema la t(t−2)≥0. Intersectăm condițiile cu t≥−j și revenim prin x²; nu păstrăm valori imposibile ale blocului.')
        at=j+1
        absval=abs(qpoly.subs(x,at))
        emit(4,8,j,'Pentru '+math(S.Eq(y,S.Abs(qpoly)))+f', calculați f({at}).',absval,
             'La argumentul dat polinomul interior este negativ, deci modulul îi schimbă semnul. La rădăcini ambele formule pe ramuri ar avea valoarea zero.',{'task':'evaluate','f':str(S.Abs(qpoly)),'at':at},adaptation='Explicitarea modulului este adaptată într-o evaluare pe ramura cu semn negativ.')
        emit(4,9,j,f'Pentru ce m este x²−{2*j}x+m≥0 pentru orice x∈ℝ?',S.Interval(j*j,S.oo),
             'Coeficientul principal este pozitiv. Forma canonică este (x−j)²+m−j², deci semnul global nenegativ este echivalent cu minimul m−j²≥0. Egalitatea dă rădăcină dublă admisă.',{'task':'global_sign_parameter','offset':j,'strict':False})
        emit(4,10,j,f'Pentru ce m fracția (x²−{2*j}x+m)/(x²+1) este strict pozitivă pentru orice x∈ℝ?',S.Interval.open(j*j,S.oo),
             'Numitorul x²+1 este strict pozitiv peste tot, deci condiția se transferă numărătorului. Minimul acestuia este m−j² și trebuie să fie strict pozitiv; cazul egalității este exclus.',{'task':'global_sign_parameter','offset':j,'strict':True})
        rational=(x*x+j)/(x*x+1)
        emit(4,11,j,'Determinați imaginea pe ℝ a funcției '+math(S.Eq(y,rational))+'.',realrange(rational),
             'Punem t=x²≥0. Raportul devine (t+j)/(t+1)=1+(j−1)/(t+1). Valoarea de la t=0 se atinge; limita 1 se atinge numai în cazul constant j=1, altfel nu se include.',{'task':'range','f':str(rational),'domain':'Reals'})
        emit(4,12,j,f'Pentru ce m inecuația x²−{2*j}x+m<0 nu are nicio soluție reală?',S.Interval(j*j,S.oo),
             'O expresie de forma (x−j)²+m−j² nu poate fi negativă exact când minimul este nenegativ. Egalitatea este inclusă: un pătrat perfect nu este strict negativ nicăieri.',{'task':'global_sign_parameter','offset':j,'strict':False})
        point=j-1
        emit(4,13,j,f'f(x)=min{{(x−{j})²;{j+1}}}. Calculați f({point}).',S.Integer(1),
             'Calculăm cele două valori la argumentul cerut, apoi alegem minimul. Ridicarea la pătrat și operația min se fac în această ordine.',{'task':'minimum_values','functions':[str((x-j)**2),str(j+1)],'at':point},adaptation='Graficul unui minim este adaptat într-o evaluare concretă.')
        emit(4,14,j,f'Pentru a>0, mulțimea soluțiilor lui ax²+bx+c≤0 este exact [{j};{j+2}], iar a={j+1}. Determinați (b;c).',S.Tuple(-(j+1)*(2*j+2),(j+1)*j*(j+2)),
             'Capetele distincte sunt rădăcinile polinomului. Coeficientul principal dat fixează f(x)=a(x−j)(x−j−2). Deoarece a>0, semnul din interior este negativ și în exterior pozitiv.',{'task':'coeff_from_interval','left':j,'right':j+2,'a':j+1})
        emit(4,15,j,f'Pentru ce m expresia x²+{2*j}x+m este nenegativă pentru orice x≥0?',S.Interval(0,S.oo),
             'Pe semiaxa nenegativă, termenii x² și 2jx sunt nenegativi. Valoarea minimă este la x=0 și este m. Necesitatea și suficiența sunt deci m≥0; nu cerem semn global pe toată ℝ.',{'task':'halfline_sign','linear':2*j,'strict':False})
        distance=poly((x-j)*(x-j-4))
        emit(4,16,j,'Calculați distanța dintre rădăcinile reale ale ecuației '+math(S.Eq(distance,0))+'.',S.Integer(4),
             'Formula |x₂−x₁|=√Δ/|a| se obține din formula rădăcinilor. Aici Δ>0 și distanța este strict pozitivă; aceeași valoare rezultă din factorizare.',{'task':'root_distance','f':str(distance)})
        interior=(x-j-1)*(x-j-2)
        emit(4,17,j,'Câte rădăcini reale distincte ale lui '+math(S.Eq(interior,0))+f' sunt strict în intervalul ({j};{j+3})?',S.Integer(2),
             'Factorizarea dă două rădăcini distincte, ambele strict între capetele intervalului. Validarea capetelor este separată de simpla condiție Δ>0.',{'task':'root_count','f':str(interior),'domain':str(S.Interval.open(j,j+3))},adaptation='Poziționarea parametrizată este adaptată într-un caz explicit cu două rădăcini interioare.')
        emit(4,18,j,f'Pentru ce m ecuația x²−{2*j}x+m=0 are două rădăcini separate strict de pragul {j}?',S.Interval.open(-S.oo,j*j),
             'Pentru a>0, pragul se află strict între rădăcini exact când f(prag)<0. Condiția m−j²<0 garantează simultan două rădăcini reale distincte.',{'task':'between_parameter','sum':2*j,'threshold':j})
        outer=(x+j)*(x-j-3)
        domain=S.Union(S.Interval.open(-S.oo,0),S.Interval.open(j,S.oo))
        emit(4,19,j,'Câte rădăcini ale ecuației '+math(S.Eq(outer,0))+f' se află în exteriorul segmentului [0;{j}]?',S.Integer(2),
             'Rădăcinile sunt −j<0 și j+3>j. Ambele sunt exterioare, fără egalitate cu vreun capăt. Suma sau produsul singure nu ar stabili această poziționare.',{'task':'root_count','f':str(outer),'domain':str(domain)},adaptation='Caz explicit de rădăcini în exterior; nu o discuție completă după parametru.')
        emit(4,20,j,f'f(x)=(x−m)²+{j}, x∈ℝ. Care este cea mai mare valoare L pentru care Im f⊆[L;+∞) pentru orice m∈ℝ?',S.Integer(j),
             'Minimul este j și se atinge pentru x=m, oricare ar fi m. Prin urmare orice L≤j este o bornă inferioară, iar cea mai mare este chiar j.',{'task':'vertex_value','f':str((x-m)**2+j)})
        emit(4,21,j,f'Pentru ce m imaginea pe ℝ a lui f(x)=(x−{j})²+m este exact [{j+1};+∞)?',S.Integer(j+1),
             'Coeficientul principal este pozitiv, iar valoarea minimă este m, atinsă în vârf. Egalitatea imaginilor impune egalitatea capetelor inferioare, m=j+1.',{'task':'parameter_root','equation':str(m-j-1),'variable':'m'})
        excluded=S.Complement(S.S.Reals,S.FiniteSet(j))
        square=(x-j)**2
        emit(4,22,j,'Aflați imaginea funcției '+math(S.Eq(y,square))+' pe domeniul '+math(excluded)+'.',S.Interval.open(0,S.oo),
             'Zero este atins numai la x=j, punct exclus. Fiecare valoare pozitivă are două preimagini j±√y, ambele admise. Imaginea este semiaxa strict pozitivă, nu cea închisă.',{'task':'range','f':str(square),'domain':str(excluded)})

        # Relative positions of lines and parabolas. All answers are exact.
        line=j*x+1
        parab=poly(line+(x-j)*(x-j-2))
        intersections=S.FiniteSet(S.Tuple(j,line.subs(x,j)),S.Tuple(j+2,line.subs(x,j+2)))
        emit(5,1,j,'Determinați punctele comune parabolei '+math(S.Eq(y,parab))+' și dreptei '+math(S.Eq(y,line))+'.',intersections,
             'Egalăm cele două expresii ale lui y. Diferența este o ecuație de gradul al doilea cu două rădăcini reale distincte; pentru fiecare abscisă revenim în ecuația dreptei.',{'task':'intersection','first':str(parab),'second':str(line)})
        parab=(x-j)**2+j
        emit(5,2,j,'Pentru ce m dreapta y=m este tangentă parabolei '+math(S.Eq(y,parab))+'?',S.Integer(j),
             'O dreaptă orizontală este tangentă acestei parabole în vârf. Echivalent, ecuația (x−j)²+j−m=0 are o rădăcină dublă exact când m=j.',{'task':'tangent_parameter','first':str(parab),'line':'m','variable':'m'})
        family=(x-m)**2+j
        emit(5,3,j,'Familia '+math(S.Eq(y,family))+' are, pentru fiecare m∈ℝ, o tangentă orizontală comună y=n. Aflați n.',S.Integer(j),
             'Completarea pătratului arată că toate vârfurile au aceeași ordonată j. Diferența f_m(x)−n are discriminant nul pentru orice m exact când n=j.',{'task':'uniform_horizontal_tangent','f':str(family),'parameter':'m'})
        family=x*x-2*j*x+m
        emit(5,4,j,'Pentru ce m axa Ox este tangentă parabolei '+math(S.Eq(y,family))+'?',S.Integer(j*j),
             'Coeficientul principal este 1, deci nu apare degenerarea. Tangența la Ox este echivalentă cu Δ=0; la această valoare polinomul devine pătrat perfect.',{'task':'tangent_parameter','first':str(family),'line':'0','variable':'m'})
        d=j+1; g=(x-d)**2+2*d*j
        common=2*j*x-j*j
        emit(5,5,j,'Determinați expresia dreptei y=ℓ(x) tangentă ambelor parabole '+math(S.Eq(y,x*x))+' și '+math(S.Eq(y,g))+'.',common,
             'Scriem dreapta y=px+q. Pentru prima parabolă condiția Δ=0 dă q=−p²/4. Pentru cea translatată, aceeași condiție determină unic p. Substituția în ambele diferențe produce pătrate perfecte, cu rădăcini duble reale.',{'task':'common_tangent','first':'x**2','second':str(g)})
        parab=(j+1)*x*x-2*x+j
        contact=j
        slope=2*(j+1)*contact-2
        tangent=poly(slope*(x-contact)+parab.subs(x,contact))
        emit(5,6,j,'Aflați expresia ℓ(x) a tangentei y=ℓ(x) la '+math(S.Eq(y,parab))+f' în punctul de abscisă {contact}.',tangent,
             'Pentru ca diferența dintre parabolă și dreaptă să fie a(x−r)², coeficientul liniar impune p=2ar+b. Ordonata punctului fixează interceptul. Această metodă este algebrică, fără derivate.',{'task':'tangent_at','f':str(parab),'at':contact})
        family=(x-m)**2+j
        emit(5,7,j,'Pentru familia '+math(S.Eq(y,family))+' și orice m∈ℝ, câte puncte comune are graficul cu axa Ox?',S.Integer(0),
             'Minimul familiei este j>0, independent de m, deci fiecare parabolă este strict deasupra lui Ox. Ecuația de intersecție nu are soluții reale.',{'task':'uniform_root_count','f':str(family),'parameter':'m'})
        # Symmetric parabola tangent to y=x and y=-x.
        emit(5,8,j,f'Parabola y={j}x²+c este tangentă ambelor bisectoare y=x și y=−x. Aflați c.',Q(1,4*j),
             'Pentru jx²−x+c=0 și jx²+x+c=0 discriminantul este în ambele cazuri 1−4jc. Tangența la ambele drepte este echivalentă cu anularea acestui discriminant, deci c=1/(4j). Coeficientul principal j este pozitiv.',{'task':'bisector_parameter','a':j})
        target=poly(x*x+j)
        tan1=2*x+j-1; tan2=-2*x+j-1
        emit(5,9,j,'O parabolă monică y=x²+bx+c este tangentă dreptelor '+math(S.Eq(y,tan1))+' și '+math(S.Eq(y,tan2))+'. Determinați (b;c).',S.Tuple(0,j),
             'Anulăm discriminantul celor două ecuații de intersecție. Scăderea condițiilor dă b=0; apoi prima condiție determină c. Verificarea produce rădăcini duble pentru ambele drepte.',{'task':'two_lines_parabola','a':1,'lines':[str(tan1),str(tan2)]})
        # Restricted contact with |x| uses the nonnegative half-line.
        emit(5,10,j,f'Pentru x≥0, graficul y=x²+c este tangent ramurii y={2*j}|x|. Aflați c, validând abscisa de contact.',S.Integer(j*j),
             'Pe x≥0, |x|=x. Diferența x²−2jx+c are rădăcină dublă la x=j≥0 exact când c=j². Contactul aparține ramurii cerute; pentru modul trebuie verificată această restricție.',{'task':'tangent_parameter','first':str(x*x+c),'line':str(2*j*x),'variable':'c','contact_domain':'Interval(0, oo)'},adaptation='Tangență pe semidreapta pozitivă a unei curbe cu modul; nu se afirmă unicitate pe întregul grafic.')
        chosen=poly((x-j)**2+j)
        emit(5,11,j,f'Parabola monică y=x²+bx+c trece prin (0;{j*j+j}) și este tangentă dreptei y={j}. Determinați (b;c), știind că abscisa contactului este pozitivă.',S.Tuple(-2*j,j*j+j),
             'Punctul dat fixează c. Tangența la dreapta orizontală impune Δ=0 pentru f(x)−j, deci b²=4j². Condiția abscisei −b/2>0 selectează b=−2j, fără ambiguitatea celor două semne.',{'task':'point_tangent_positive','intercept':j*j+j,'line':j})
        angle=Q(j,6)*S.pi
        slope=2*S.cos(angle)
        triline=slope*x-S.cos(angle)**2
        emit(5,12,j,'Pentru unghiul '+math(S.Eq(S.Symbol('alpha'),angle))+', exprimat în radiani, dreapta este y=2cos(α)x−cos²(α). Câte puncte comune are cu parabola y=x²?',S.Integer(1),
             'Diferența este (x−cos α)². Identitatea Δ=4cos²α−4cos²α=0 este valabilă inclusiv când cos α=0, deci există un singur punct comun, de tangență.',{'task':'root_count','f':str(x*x-triline),'domain':'Reals'},adaptation='Parametrul trigonometric este fixat la un unghi explicit; se verifică identitatea discriminantului.')
        emit(5,13,j,f'Punctul de contact al tangentei y=2tx−t² la y=x² are abscisa t. Dacă t={j}, determinați perechea (x;y) a contactului.',S.Tuple(j,j*j),
             'Ecuația de intersecție este (x−t)²=0, deci contactul este (t,t²). Eliminarea parametrului produce locul y=x², parcurs pe toate abscisele reale.',{'task':'contact','f':'x**2','line':str(2*j*x-j*j)},adaptation='Locul de tangență este explicat; grila cere un punct explicit al acestuia.')
        emit(5,14,j,f'Pentru ce m parabola y=x²+m este strict deasupra dreptei y={2*j}x pentru orice x∈ℝ?',S.Interval.open(j*j,S.oo),
             'Diferența este (x−j)²+m−j². Stricta pozitivitate globală cere ca minimul să fie strict pozitiv; egalitatea ar produce tangență și nu satisface enunțul.',{'task':'global_sign_parameter','offset':j,'strict':True})
        emit(5,15,j,f'Pentru ce m parabola y=x²+m este deasupra sau pe ambele drepte y={2*j}x și y=−{2*j+2}x pentru orice x∈ℝ?',S.Interval((j+1)**2,S.oo),
             'Pentru o dreaptă y=px, diferența are minimul m−p²/4. Ambele minime trebuie să fie nenegative, deci intersectăm m≥j² cu m≥(j+1)². Condiția mai puternică este a doua.',{'task':'above_two_lines','slopes':[2*j,-2*j-2]})

        f1=x*x+j
        f2=poly(2*x*x-(2*j+2)*x+j*(j+2)+j)
        eq=f2-f1
        ints=S.FiniteSet(*(S.Tuple(rr,f1.subs(x,rr)) for rr in roots(eq)))
        emit(6,1,j,'Rezolvați sistemul '+math(S.Eq(y,f1))+' și '+math(S.Eq(y,f2))+'.',ints,
             'Scădem ecuațiile și rezolvăm ecuația pătratică pentru x. Pentru fiecare abscisă revenim în prima parabolă, apoi verificăm și a doua ecuație.',{'task':'intersection','first':str(f1),'second':str(f2)})
        emit(6,2,j,f'Pentru ce m parabolele y=x² și y=2x²−{2*j}x+m sunt tangente?',S.Integer(j*j),
             'Diferența este x²−2jx+m. Coeficienții principali sunt diferiți, deci diferența are gradul al doilea; tangența este echivalentă cu Δ=0, de unde m=j².',{'task':'tangent_parameter','first':'x**2','line':str(2*x*x-2*j*x+m),'variable':'m'})
        first=(x-j)**2+j
        second=2*(x-j)**2+j
        emit(6,3,j,'Parabolele '+math(S.Eq(y,first))+' și '+math(S.Eq(y,second))+' au același vârf. Determinați punctul lor comun.',S.Tuple(j,j),
             'Diferența este (x−j)², deci unica abscisă comună este j. Ambele valori sunt j, iar tangenta comună este orizontală în vârful comun.',{'task':'contact','f':str(first),'line':str(second)})
        l=poly(2*j*(x-j)+j)
        first=poly((x-j)**2+l)
        second=poly(2*(x-j)**2+l)
        emit(6,4,j,'Determinați expresia dreptei tangente comune în punctul de contact al parabolelor '+math(S.Eq(y,first))+' și '+math(S.Eq(y,second))+'.',l,
             'Diferența parabolelor este un pătrat, deci contactul are abscisa j. Scăzând dreapta indicată de partea afină, ambele expresii devin multipli nenuli ai lui (x−j)²: contact dublu cu aceeași dreaptă.',{'task':'common_contact_tangent','first':str(first),'second':str(second)})
        shift=j+1; second=poly((x-shift)**2+2*shift*j)
        emit(6,5,j,'Găsiți expresia ℓ(x) a dreptei tangente simultan la y=x² și '+math(S.Eq(y,second))+'.',common,
             'Pentru dreapta y=px+q, condițiile de discriminant nul impun q=−p²/4 și p=2j. Interceptul rezultă apoi unic. Fiecare ecuație de intersecție are o rădăcină dublă reală.',{'task':'common_tangent','first':'x**2','second':str(second)})
        candidate=poly(x*x+j)
        first=poly(candidate+(x-j)**2)
        second=poly(candidate+(x+j)**2)
        emit(6,6,j,'Parabola y=x²+c este tangentă ambelor parabole '+math(S.Eq(y,first))+' și '+math(S.Eq(y,second))+'. Aflați c.',S.Integer(j),
             'Diferențele sunt (x−j)²+j−c și (x+j)²+j−c. Fiecare are rădăcină dublă exact când c=j. Contactele sunt la abscise opuse, ambele reale.',{'task':'double_parabola_parameter','first':str(first),'second':str(second),'candidate':'x**2+c','variable':'c'},adaptation='O secțiune cu un parametru a problemei de construire a familiilor; nu se pretinde întreaga familie infinită.')
        eqs=[y-x*x,x*x+y*y-(j*j+j**4)]
        sol=S.FiniteSet(S.Tuple(-j,j*j),S.Tuple(j,j*j))
        emit(6,7,j,f'Rezolvați în ℝ² sistemul y=x², x²+y²={j*j+j**4}.',sol,
             'Substituind y=x² și punând t=x²≥0, ecuația devine t²+t=j⁴+j². Rădăcina t=j² este admisă, iar cealaltă este negativă și se respinge. Revenirea dă x=±j, y=j², ambele perechi verificând sistemul.',{'task':'mixed_system','constant':j*j+j**4})
        mono=poly((x-j)*(x-j-2))
        other=poly((j+1)*x*x+b*x+c)
        emit(6,8,j,'Ecuațiile '+math(S.Eq(mono,0))+' și '+math(S.Eq(other,0))+' au aceeași mulțime de rădăcini reale. Determinați (b;c).',S.Tuple(-(j+1)*(2*j+2),(j+1)*j*(j+2)),
             'Prima ecuație are două rădăcini reale distincte. Cum gradul celei de-a doua este tot doi și coeficientul principal este fixat nenul, polinoamele sunt proporționale. Înmulțim primul polinom cu j+1 și identificăm coeficienții.',{'task':'proportional_coefficients','f':str(mono),'a':j+1})
        eqs=[x+y+z-3*j,x*y+y*z+z*x-3*j*j]
        emit(6,9,j,f'Pentru x,y,z∈ℝ cu x+y+z={3*j} și xy+yz+zx={3*j*j}, determinați (x;y;z).',S.Tuple(j,j,j),
             'Din pătratul sumei rezultă x²+y²+z²=3j². Atunci (x−j)²+(y−j)²+(z−j)²=0. Fiecare termen este nenegativ, deci toate trei variabilele sunt j. Perechea de condiții se verifică direct.',{'task':'three_equal','sum':3*j,'pairs':3*j*j},adaptation='Sistem de sinteză ales astfel încât identitatea sumei de pătrate asigură unicitatea.')

    assert [len(banks[i]) for i in banks]==[60,30,30,75,155,75,55]
    assert len({q['text'] for qs in banks.values() for q in qs})==480
    return banks


def update_files():
    banks=build_questions()
    for lesson,items in banks.items():
        path=next((ROOT/'clasa_9').glob(f'clasa_9_u04_l{lesson:02d}_*.json'))
        data=json.loads(path.read_text(encoding='utf-8'))
        retained=[q for q in data['questions'] if q.get('practice_scope',{}).get('bank')!=BANK]
        data['questions']=retained+items
        data['difficulty']='hard'
        path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        print(f'Lesson {lesson}: {len(items)} new grids; {len(retained)} preserved.')


if __name__=='__main__': update_files()
