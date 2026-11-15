"""Original G3 trigonometry grids. No Django imports or database writes.

Expressions in verification are original symbolic givens, never reduced keys.
Numeric variants of proof tasks are explicitly marked as partial adaptations.
"""
import argparse
import json
from functools import lru_cache
from pathlib import Path

import sympy as S

ROOT=Path(__file__).resolve().parents[1]
BANK='g3_trigo_v1'
NAMES=json.loads(Path(__file__).with_name('trigonometry_type_names.json').read_text(encoding='utf-8'))
LESSONS={'1':1,'2':2,'3.1':3,'3.2':4,'3.3':5,'3.4':6,'4':7,'5':8,'6':9,'7':9}
COUNTS=[35,40,80,25,40,45,75,105,140]
PAGES={'1':'204','2':'205–206','3.1':'206–209','3.2':'209–210','3.3':'210–211','3.4':'212–214','4':'214–218','5':'219–222','6':'223–226','7':'227–229'}
Q=S.Rational
x,y,z,t,a,b,c,k,n=S.symbols('x y z t a b c k n',real=True)
SYMBOLS={str(v):v for v in (x,y,z,t,a,b,c,k,n)}
ACTUAL={**SYMBOLS,'sin':S.sin,'cos':S.cos,'tan':S.tan,'cot':S.cot,'sqrt':S.sqrt,'Abs':S.Abs,'pi':S.pi}
DISPLAY={**SYMBOLS,**{name:S.Function(name) for name in ('sin','cos','tan','cot')},'sqrt':S.sqrt,'Abs':S.Abs,'pi':S.pi}


def exact(value):return S.sympify(value,locals=ACTUAL)
def tex(value):return r'\('+S.latex(value)+r'\)'
def expression_tex(formula):return S.latex(S.sympify(formula,locals=DISPLAY,evaluate=False))
@lru_cache(maxsize=None)
def reduced_expression(formula):return S.trigsimp(exact(formula))
def serial(value):
    if isinstance(value,dict):return {key:serial(item) for key,item in value.items()}
    if isinstance(value,(list,tuple)):return [serial(item) for item in value]
    if isinstance(value,S.Basic):return str(value)
    return value


class Builder:
    def __init__(self):self.banks={lesson:[] for lesson in range(1,10)}
    def emit(self,section,typ,j,text,answer,reason,data,partial=False,labels=None):
        answer=S.sympify(answer)
        if labels is not None:
            values=[S.sympify(code) for code in labels]
            assert answer in values and len(values)==4
        elif isinstance(answer,S.Tuple):
            values=[answer,*[S.Tuple(answer[0]+offset,*answer[1:]) for offset in (1,-1,2)]]
        elif isinstance(answer,S.Interval):
            values=[answer,*[S.Interval(answer.start+offset,answer.end+offset,left_open=answer.left_open,right_open=answer.right_open) for offset in (1,-1,2)]]
        else:values=[S.simplify(answer+offset) for offset in (0,1,-1,2)]
        assert len(values)==len(set(values))==4,(section,typ,j)
        for i,one in enumerate(values):
            for two in values[:i]:
                if not isinstance(one,(S.Set,S.Tuple)):assert S.simplify(one-two)!=0,(section,typ,j)
        lesson=LESSONS[section];position=len(self.banks[lesson])%4
        original=values.index(answer);values.insert(position,values.pop(original))
        texts=[labels[int(value)] if labels is not None else tex(value) for value in values]
        verification={**serial(data),'option_values':[str(value) for value in values]}
        if labels is not None:
            verification['answer_kind']='label'
            verification['option_labels']={str(code):label for code,label in labels.items()}
        else:verification['answer_kind']='math'
        result_label=labels[int(answer)] if labels is not None else tex(answer)
        self.banks[lesson].append({'text':text,'type':'multiple_choice','format':'grid','points':10,
            'explanation':reason+' Rezultatul cerut este '+result_label+'.',
            'options':[{'text':value,'is_correct':i==position} for i,value in enumerate(texts)],
            'practice_scope':{'bank':BANK,'catalog':'G3','section':section,'type':typ,
                'type_name':NAMES[section][typ-1],'variant':j,'reference_pages':PAGES[section],
                'coverage':'partial_explicit_case' if partial else 'adapted_grid',
                'adaptation':('Caz original explicit de calcul/concluzie; nu înlocuiește demonstrația generală a catalogului.' if partial else 'Grilă originală de calcul sau concluzie; metoda este justificată în explicație.')},
            'verification':verification})

    def calc(self,section,typ,j,context,formula,givens,reason,partial=False):
        given_values={name:exact(value) for name,value in givens.items()}
        expr=exact(formula)
        result=S.simplify(reduced_expression(formula).subs({SYMBOLS[name]:value for name,value in given_values.items()}))
        assert not result.has(S.nan,S.zoo,S.oo,-S.oo) and result.is_real is not False,(section,typ,j,result)
        shown=expression_tex(formula)
        bindings=', '.join(name+'='+tex(value) for name,value in given_values.items())
        text=context+' Date: '+bindings+'. Calculați '+r'\('+shown+r'\).'
        self.emit(section,typ,j,text,result,reason,
            {'operation':'evaluate','expression':formula,'expression_latex':shown,'givens':given_values},partial)


def foundations(B):
    for j in range(1,6):
        d=[75,135,210,315,450][j-1]
        B.emit('1',1,j,f'Convertiți măsura de {d}° în radiani.',Q(d,180)*S.pi,
            'Un unghi de 180° măsoară π radiani. Înmulțim numărul de grade cu π/180; sensul rotației este pozitiv.',{'operation':'degrees_to_rad','degrees':d})
        factor=[Q(7,12),Q(5,6),Q(11,8),Q(13,6),Q(17,4)][j-1]
        B.emit('1',2,j,'Convertiți '+tex(factor*S.pi)+' radiani în grade.',180*factor,
            'Înmulțim măsura în radiani cu 180/π. Factorul π se simplifică; nu se reduce modulo un tur deoarece se cere măsura completă.',{'operation':'rad_to_degrees','radians':factor*S.pi})
        total=90+15*j;diff=10*j
        B.emit('1',3,j,'Două unghiuri pozitive au suma '+tex(Q(total,180)*S.pi)+f' radiani și diferența α−β={diff}°. Aflați perechea (α;β) în grade.',S.Tuple(Q(total+diff,2),Q(total-diff,2)),
            f'Convertim suma în grade: α+β={total}°. Adunarea și scăderea celor două ecuații dau α=(sumă+diferență)/2, β=(sumă−diferență)/2. Ambele valori sunt pozitive.',{'operation':'angle_system','sum_radians':Q(total,180)*S.pi,'difference_degrees':diff})
        radius=j+3;degrees=15*(j+1)
        B.emit('1',4,j,f'Un cerc are raza R={radius} cm. Aflați lungimea arcului de măsură {degrees}°.',radius*Q(degrees,180)*S.pi,
            'Mai întâi convertim unghiul la radiani. Lungimea arcului este l=Rα, cu α în radiani; nu se înmulțește direct raza cu numărul de grade.',{'operation':'arc_length','radius':radius,'angle_radians':Q(degrees,180)*S.pi})
        angle=[35,45,60,75,110][j-1];radius=j+2
        B.emit('1',5,j,f'ABC este înscris într-un cerc de rază {radius} cm, iar A={angle}°. Aflați lungimea arcului BC care NU conține A.',radius*Q(angle,90)*S.pi,
            'Arcul opus lui A are măsura dublă a unghiului înscris A, inclusiv când acest arc este mai mare decât un semicerc. Îl convertim în radiani și folosim l=Rα.',{'operation':'inscribed_arc','radius':radius,'inscribed_degrees':angle})
        sides=[5,6,8,10,12][j-1]
        B.emit('1',6,j,f'Aflați (măsura în grade; măsura în radiani) a unui unghi interior al unui poligon regulat convex cu {sides} laturi.',S.Tuple(Q(180*(sides-2),sides),Q(sides-2,sides)*S.pi),
            'Suma unghiurilor interioare este (n−2)·180°. Regularitatea le face egale, deci împărțim la n; conversia în radiani înlocuiește 180° cu π.',{'operation':'regular_polygon','sides':sides})
        angle=[20,30,45,60,100][j-1]
        configs={tuple(sorted((S.Integer(angle),Q(180-angle,2),Q(180-angle,2))))}
        if angle<90:configs.add(tuple(sorted((S.Integer(angle),S.Integer(angle),S.Integer(180-2*angle)))))
        B.emit('1',7,j,f'Un triunghi isoscel nedegenerat are un unghi de {angle}°. Câte triplete neordonate de unghiuri sunt posibile? Triunghiul echilateral este admis ca isoscel.',len(configs),
            'Separăm cazul în care unghiul dat este la vârf de cazul în care este la bază. În al doilea caz, unghiul de la vârf trebuie să rămână strict pozitiv. Tripletele identice se numără o singură dată; pentru 60° ambele construcții sunt același triunghi echilateral.',{'operation':'isosceles_angle_count','angle_degrees':angle})

        turns=Q(2*j+1,2)
        B.emit('2',1,j,'O roată se rotește în sens trigonometric cu '+tex(turns)+' ture. Aflați unghiul total în radiani.',2*S.pi*turns,
            'O rotație completă are 2π radiani. Numărul de ture poate fi fracționar și se înmulțește cu 2π, fără reducere modulo un tur.',{'operation':'rotation','turns':turns})
        rpm=120*(j+1);seconds=Q(2*j+1,2)
        B.emit('2',2,j,f'O roată are viteza constantă {rpm} rotații/minut și se rotește timp de '+tex(seconds)+' secunde. Care este unghiul parcurs în radiani?',2*S.pi*rpm*seconds/60,
            'Convertim timpul în minute, împărțind secundele la 60. Numărul de ture este viteza în rotații/minut înmulțită cu timpul în minute, apoi fiecare tură înseamnă 2π radiani.',{'operation':'rotation_time','rpm':rpm,'seconds':seconds})
        angle=[-425,765,-810,1470,-1441][j-1]
        B.emit('2',3,j,f'Determinați reprezentantul unghiului {angle}° în intervalul [0°;360°).',S.Integer(angle%360),
            'Scădem sau adunăm multipli întregi de 360° până când măsura aparține intervalului cerut. Capătul 360° este exclus; el este reprezentat de 0°.',{'operation':'reduce_degrees','angle_degrees':angle})
        num=[17,-23,40,51,-58][j-1];angle=Q(num,2)*S.pi
        B.emit('2',4,j,'Aflați coordonatele punctului de pe cercul trigonometric asociat numărului real '+tex(angle)+'.',S.Tuple(S.cos(angle),S.sin(angle)),
            'Reducem argumentul modulo 2π. Coordonatele cercului unitate sunt (cos α;sin α), în această ordine; pe axe una dintre componente este zero.',{'operation':'unit_circle','radians':angle})
        weights=[j+1,j+2,j+3];total=sum(weights)
        B.emit('2',5,j,f'Unghiurile unui triunghi sunt proporționale cu {weights[0]}, {weights[1]}, {weights[2]}, în această ordine. Aflați tripletul unghiurilor în grade.',S.Tuple(*[Q(180*w,total) for w in weights]),
            'Suma celor trei unghiuri este 180°. Dacă unghiurile sunt kp,kq,kr, atunci k=180/(p+q+r). Toate ponderile sunt pozitive și dau unghiuri strict între 0° și 180°.',{'operation':'proportional_angles','weights':weights,'total_degrees':180})
        value=270+5*j;common=360-value
        B.emit('2',6,j,f'Într-un patrulater convex, A=B=C și B+C+D={value}°. Aflați unghiul D în grade.',360-3*common,
            'Din A+B+C+D=360° și B+C+D cunoscut, aflăm A. Cele trei unghiuri egale sunt apoi determinate, iar D=360°−3A. Valorile obținute sunt în (0°,180°), compatibile cu un patrulater convex.',{'operation':'quadrilateral_equal','three_sum':value})
        radius=j+2;length=Q(j+1,3)*S.pi
        B.emit('2',7,j,'Un arc de cerc are lungimea '+tex(length)+f' cm, pe cercul de rază {radius} cm. Aflați măsura arcului în radiani.',length/radius,
            'Din l=Rα rezultă α=l/R. Împărțirea este permisă deoarece raza este strict pozitivă; unitățile de lungime se simplifică.',{'operation':'arc_angle','length':length,'radius':radius})
        angle=[Q(13,6),Q(-5,4),Q(17,3),Q(-19,6),Q(23,4)][j-1]*S.pi
        reduced=S.Mod(angle,2*S.pi);quad=int(S.floor(2*reduced/S.pi))+1
        B.emit('2',8,j,'În ce cadran este punctul asociat unghiului '+tex(angle)+' radiani?',quad,
            'Reducem argumentul în [0,2π), apoi îl comparăm cu π/2,π,3π/2. Punctele acestor variante nu sunt pe axe, astfel cadranul este unic.',{'operation':'quadrant','radians':angle},labels={1:'Cadranul I',2:'Cadranul II',3:'Cadranul III',4:'Cadranul IV'})

        p,q,h=[(3,4,5),(5,12,13),(8,15,17),(7,24,25),(20,21,29)][j-1]
        def calc3(typ,context,formula,givens,reason,partial=False):B.calc('3.1',typ,j,context,formula,givens,reason,partial)
        calc3(1,'Un triunghi dreptunghic are cateta opusă unghiului ascuțit α egală cu a, cateta alăturată b și ipotenuza c. Calculați sinusul lui α.','a/c',{'a':p,'b':q,'c':h},'Prin definiție, sinusul unui unghi ascuțit este cateta opusă împărțită la ipotenuză. Datele satisfac a²+b²=c² și toate lungimile sunt pozitive.')
        calc3(2,'Un triunghi isoscel are laturile egale a și baza 2b. Calculați sinusul unui unghi de la bază.','sqrt(a**2-b**2)/a',{'a':h,'b':p},'Înălțimea din vârf înjumătățește baza și are lungimea √(a²−b²). În triunghiul dreptunghic obținut, sinusul unghiului de la bază este înălțimea împărțită la latura egală.')
        calc3(3,'Într-un triunghi dreptunghic, ipotenuza este a și sinusul unui unghi ascuțit este b. Aflați cateta alăturată acestui unghi.','a*sqrt(1-b**2)',{'a':2*h,'b':Q(p,h)},'Cosinusul este rădăcina pozitivă a lui 1−sin²α deoarece unghiul este ascuțit. Înmulțirea cu ipotenuza dă cateta alăturată.')
        calc3(4,'Un paralelogram are laturile a,b și unghiul cuprins x, în radiani. Calculați aria.','a*b*sin(x)',{'a':j+3,'b':j+4,'x':S.pi/6},'Înălțimea pe latura a este b sin x, deci aria este ab sin x. Acesta este un caz explicit de arie prin date trigonometrice, fără condiția suplimentară de diagonală a exemplului din catalog.',True)
        calc3(5,'Triunghiul isoscel are laturile egale a și unghiul de la vârf x, în radiani. Aflați înălțimea pe bază.','a*cos(x/2)',{'a':2*(j+2),'x':[S.pi/3,S.pi/2,2*S.pi/3,S.pi/6,5*S.pi/6][j-1]},'Înălțimea bisectează unghiul de la vârf. În unul dintre cele două triunghiuri dreptunghice, raportul înălțime/latură egală este cos(x/2); x/2 este ascuțit.')
        calc3(6,'Pentru unghiul ascuțit x, în radiani, verificați numeric expresia fundamentală.','1+tan(x)**2',{'x':[S.pi/6,S.pi/4,S.pi/3,S.pi/12,5*S.pi/12][j-1]},'Pitagora împărțit la pătratul catetei alăturate dă 1+tan²x=1/cos²x. Cosinusul este nenul pe domeniul ascuțit. Varianta cere valoarea numerică a membrului stâng.',True)
        calc3(7,'Unghiul x este ascuțit, în radiani. Calculați raportul dintre tangenta complementului și cotangenta unghiului.','tan(pi/2-x)/cot(x)',{'x':[S.pi/6,S.pi/4,S.pi/3,S.pi/12,5*S.pi/12][j-1]},'Unghiurile complementare inversează rolul catetelor: tan(π/2−x)=cot x. Pentru x ascuțit cot x este definită și strict pozitivă, deci raportul este 1.',True)
        calc3(8,'Pentru unghiul ascuțit x, în radiani, calculați fracția.','(1-cos(x))/sin(x)',{'x':[S.pi/6,S.pi/4,S.pi/3,S.pi/12,5*S.pi/12][j-1]},'Înmulțind cu conjugata 1+cos x, obținem sin x/(1+cos x). Numitorii sunt nenuli pentru unghiurile ascuțite, iar identitatea sin²x=1−cos²x justifică reducerea.',True)
        calc3(9,'În pătratul ABCD de latură a, M este pe AB, cu AM=b. Calculați cosinusul unghiului AMC.','-(a-b)/sqrt((a-b)**2+a**2)',{'a':j+3,'b':j+1},'Alegem A=(0,0), B=(a,0), C=(a,a), M=(b,0). Vectorii MA=(−b,0), MC=(a−b,a). Produsul lor scalar este −b(a−b), iar b>0 se simplifică din normele produsului. Semnul negativ indică unghiul obtuz.',True)
        calc3(10,'Într-un triunghi, a=BC,b=CA,c=AB. Unghiurile B,C satisfac cos B=x și cos C=y. Calculați proiecția totală pe BC.','c*x+b*y',{'a':5*j,'b':4*j,'c':3*j,'x':Q(3,5),'y':Q(4,5)},'Teorema proiecțiilor este BC=AB cos B+AC cos C. În datele alese triunghiul este dreptunghic în A, iar proiecțiile sunt pozitive; suma este latura BC.')
        calc3(11,'Un romb are latura a și unghiul A=x, în radiani. Calculați lungimea diagonalei AC.','2*a*cos(x/2)',{'a':j+2,'x':[S.pi/3,S.pi/2,2*S.pi/3,S.pi/6,5*S.pi/6][j-1]},'Diagonalele se înjumătățesc și bisectează unghiurile rombului. Jumătate din AC este a cos(A/2). Deoarece 0<A<π, cos(A/2)>0.')
        calc3(12,'Un triunghi are înălțimea pe BC egală cu a și unghiurile la bază x,y ascuțite, în radiani. Aflați BC.','a/cot(pi/2-x)+a/cot(pi/2-y)',{'a':j+3,'x':S.pi/3,'y':S.pi/4},'Piciorul înălțimii este interior deoarece ambele unghiuri la bază sunt ascuțite. Cele două proiecții pe BC sunt a cot x și a cot y; deoarece cot(π/2−x)=tan x, expresia cerută le însumează.')
        calc3(13,'Trapezul dreptunghic ABCD are AB=a, CD=b, AD=c, AB∥CD și AD⊥AB. Aflați latura oblică BC.','sqrt((a-b)**2+c**2)',{'a':3*j+5,'b':j+2,'c':j+3},'Proiecția orizontală a lui BC este diferența pozitivă a bazelor, iar cea verticală este înălțimea. Pitagora dă BC²=(a−b)²+c²; luăm rădăcina pozitivă.',True)
        calc3(14,'Un triunghi dreptunghic are catetele a,b. Aflați ipotenuza.','sqrt(a**2+b**2)',{'a':p*(j+1),'b':q*(j+1)},'Pitagora determină pătratul ipotenuzei. Deoarece o lungime este pozitivă, se selectează rădăcina pozitivă; celelalte elemente se pot recupera prin rapoartele catetelor.',True)
        calc3(15,'Unghiurile x,y sunt ascuțite, în radiani. Evaluați identitatea numerică.','(tan(x)+tan(y))*cos(x)*cos(y)',{'x':S.pi/6,'y':[S.pi/12,S.pi/6,S.pi/4,S.pi/3,5*S.pi/12][j-1]},'Înlocuind tangentele prin sin/cos și distribuind, expresia devine sin x cos y+cos x sin y=sin(x+y). Ambii cosinuși sunt nenuli.',True)
        B.emit('3.1',16,j,f'ABC este dreptunghic în A și are ipotenuza {2*(j+1)}. Dacă sin B+sin C=√2, aflați unghiul B în grade.',45,
            'C=90°−B, deci sin B+sin C=sin B+cos B≤√2. Egalitatea impune sin B=cos B>0, astfel B=C=45°. Triunghiul este isoscel dreptunghic, iar ipotenuza pozitivă fixează scara.',{'operation':'right_isosceles_equality','hypotenuse':2*(j+1)})


def signs_reductions_relations(B):
    signs={-1:'Negativ',0:'Zero',1:'Pozitiv',2:'Nedefinit'}
    parity_labels={0:'Nici pară, nici impară',1:'Pară, dar nu impară',2:'Impară, dar nu pară',3:'Atât pară, cât și impară'}
    def sign_case(typ,j,formula,givens,reason):
        expr=exact(formula);bindings={SYMBOLS[name]:exact(value) for name,value in givens.items()}
        value=S.simplify(expr.subs(bindings))
        answer=2 if value.has(S.zoo,S.nan,S.oo,-S.oo) else S.sign(value)
        assert answer in (-1,0,1,2),(formula,givens,value)
        shown=expression_tex(formula)
        text='Argumentele sunt în radiani. Date: '+', '.join(name+'='+tex(exact(value)) for name,value in givens.items())+'. Determinați semnul expresiei '+r'\('+shown+r'\).'
        B.emit('3.2',typ,j,text,answer,reason,{'operation':'sign','expression':formula,'expression_latex':shown,'givens':givens},labels=signs)
    for j in range(1,6):
        sign_case(1,j,'sin(x)',{'x':[Q(17,6)*S.pi,-Q(13,6)*S.pi,Q(19,4)*S.pi,Q(7,3)*S.pi,3*S.pi][j-1]},'Reducem argumentul modulo 2π. Sinusul este pozitiv în cadranele I,II, negativ în III,IV și zero pe axa orizontală.')
        sign_case(2,j,'sin(x)*cos(y)*tan(z)',{'x':S.pi/6,'y':[S.pi/3,2*S.pi/3,S.pi/2,5*S.pi/3,S.pi/3][j-1],'z':[S.pi/4,S.pi/4,S.pi/4,3*S.pi/4,S.pi/2][j-1]},'Verificăm mai întâi existența fiecărui factor: tan z cere cos z≠0. Dacă există toți, înmulțim semnele; un factor zero face produsul zero. Un factor nedefinit nu este înlocuit cu zero.')
        degrees=[765,-510,1080,1110,-765][j-1]
        sign_case(3,j,'tan(x)',{'x':Q(degrees,180)*S.pi},f'Unghiul corespunzător este {degrees}°. Tangenta are perioada 180° și este pozitivă în cadranele I,III, negativă în II,IV; pe axa verticală nu este definită.')
        sign_case(4,j,'sin(x)',{'x':[1,2,4,5,7][j-1]},'Argumentul numeric este în radiani, fără factor π. Îl comparăm cu multipli de π/2, folosind de exemplu 3,14<π<22/7, apoi aplicăm semnul sinusului în cadranul găsit.')
        sign_case(5,j,'cos(x)-cos(y)',{'x':[S.pi/6,S.pi/3,S.pi/4,2*S.pi/3,5*S.pi/6][j-1],'y':[S.pi/3,S.pi/6,S.pi/4,S.pi/2,S.pi][j-1]},'Ambele argumente aparțin intervalului [0,π], pe care cosinusul este strict descrescător. Compararea argumentelor stabilește semnul diferenței; argumentele egale dau zero.')

        angle=[Q(13,6)*S.pi,-Q(7,4)*S.pi,Q(8,3)*S.pi,Q(19,6)*S.pi,-Q(17,3)*S.pi][j-1]
        B.calc('3.3',1,j,'Reduceți argumentul la primul cadran și calculați valoarea; toate argumentele sunt în radiani.','sin(x)',{'x':angle},'Periodicitatea și simetriile cercului transformă sinusul într-un sinus sau cosinus al unui unghi ascuțit, cu semnul cadranului original.')
        B.calc('3.3',2,j,'Calculați exact folosind unghiuri remarcabile, în radiani.','a*sin(x)+b*tan(y)+c*tan(z)',{'a':j+1,'b':j+2,'c':j+3,'x':S.pi/6,'y':S.pi/3,'z':S.pi/4},'Valorile sunt sin(π/6)=1/2, tan(π/3)=√3 și tan(π/4)=1. Toate tangentele există; înlocuim fără aproximări zecimale.')
        formula='a*sin(x)+cos(x)';givens={'a':S.Integer(j)};angles=[0,S.pi/6,S.pi/3,S.pi/2]
        values=[S.simplify(j*S.sin(angle)+S.cos(angle)) for angle in angles]
        answer=S.Tuple(S.Min(*values),S.Max(*values))
        B.emit('3.3',3,j,'Pentru a='+tex(S.Integer(j))+', x parcurge mulțimea '+tex(S.FiniteSet(*angles))+'. Aflați (minim;maxim) pentru '+r'\('+expression_tex(formula)+r'\).',answer,
            'Calculăm expresia la toate cele patru argumente admise. Minimul și maximul se compară în această mulțime finită, nu pe întreg cercul.',{'operation':'finite_extrema','expression':formula,'expression_latex':expression_tex(formula),'givens':givens,'angles':angles})
        B.calc('3.3',4,j,'Pentru unghiul ascuțit x în radiani, calculați raportul.','sin(pi-x)*cos(2*pi-x)/(sin(x)*cos(x))',{'x':[S.pi/6,S.pi/4,S.pi/3,S.pi/12,5*S.pi/12][j-1]},'Simetriile dau sin(π−x)=sin x și cos(2π−x)=cos x. Numitorul este nenul pentru unghiul ascuțit, deci raportul este 1.',True)
        B.calc('3.3',5,j,'Argumentul x este ascuțit, în radiani. Calculați produsul complementar.','tan(x)*tan(pi/2-x)',{'x':[S.pi/6,S.pi/4,S.pi/3,S.pi/12,5*S.pi/12][j-1]},'tan(π/2−x)=cot x=1/tan x; toate valorile sunt definite și nenule pe intervalul ascuțit. Produsul este 1.',True)
        B.calc('3.3',6,j,'x este în radiani, iar n este întreg. Calculați valoarea după translația cu nπ.','sin(x+n*pi)',{'x':S.pi/6,'n':[-3,-2,1,2,5][j-1]},'Un număr par de semicercuri păstrează sinusul, iar un număr impar îl schimbă în opusul său: sin(x+nπ)=(−1)^n sin x, inclusiv pentru n negativ.',True)
        B.emit('3.3',7,j,'Determinați imaginea funcției f(x)='+r'\('+expression_tex('a*(Abs(sin(x))-sin(x))')+r'\)'+' pe ℝ, pentru a='+tex(S.Integer(j))+'. Argumentele sunt în radiani.',S.Interval(0,2*j),
            'Punem t=sin x∈[−1,1]. Dacă t≥0, |t|−t=0; dacă t<0, expresia este −2t și parcurge [0,2]. Coeficientul a>0 multiplică ambele capete; fiecare valoare este atinsă.',{'operation':'range_abs_sine','coefficient':j,'expression':'a*(Abs(sin(x))-sin(x))'})
        B.emit('3.3',8,j,f'Care este minimul pe ℝ² al expresiei {j+1}−{j}sin x+cos y? Argumentele sunt în radiani.',0,
            f'Din −1≤sin x≤1 și −1≤cos y≤1 rezultă expresia≥{j+1}−{j}−1=0. Minimul este atins simultan la x=π/2 și y=π, deoarece variabilele sunt independente.',{'operation':'linear_trig_min','constant':j+1,'sin_coefficient':-j,'cos_coefficient':1})

        expression=['sin(x)','cos(x)','x*sin(x)','x**2*sin(x)','sin(x)-sin(x)'][j-1]
        answer=[2,1,1,2,3][j-1]
        B.emit('3.4',1,j,'Clasificați paritatea funcției f(x)='+r'\('+expression_tex(expression)+r'\)'+' pe domeniul ℝ; argumentele trigonometrice sunt în radiani.',answer,
            'Domeniul este simetric. Folosim sin(−x)=−sin x și cos(−x)=cos x, apoi comparăm f(−x) cu f(x) și −f(x). Funcția identic nulă satisface ambele egalități și trebuie tratată separat.',{'operation':'parity','expression':expression,'expression_latex':expression_tex(expression),'domain':'Reals'},labels=parity_labels)
        expression=f'cos({j}*x)'
        B.emit('3.4',2,j,'Clasificați funcția f(x)='+r'\('+expression_tex(expression)+r'\)'+' definită NUMAI pe (0;'+str(j+1)+'). Argumentele sunt în radiani.',0,
            'Domeniul nu este simetric față de zero: pentru x admis, −x nu este admis. Prin definiția funcțiilor pare/impare este necesar −D=D, deci funcția restrânsă nu este nici pară, nici impară, indiferent de simetria formulei cosinusului.',{'operation':'parity','expression':expression,'expression_latex':expression_tex(expression),'domain':'positive_interval','upper':j+1},labels=parity_labels)
        B.emit('3.4',3,j,f'Pentru ce valoare a lui a este funcția f(x)=a sin x+{j+1}cos x pară pe ℝ? Argumentele sunt în radiani.',0,
            'Componenta a sin x este impară, iar componenta cosinusului este pară. Egalitatea f(−x)=f(x) impune 2a sin x=0 pentru orice x; luând x=π/2 obținem a=0. Coeficientul cosinusului este nenul.',{'operation':'parity_parameter','cos_coefficient':j+1,'target':'even'})
        period=2*j*S.pi;yes=int(j%2==0)
        B.emit('3.4',4,j,'Este T='+tex(period)+' o perioadă a funcției f(x)=sin(x/2) pe ℝ? Argumentele sunt în radiani.',yes,
            'Deplasarea cu T schimbă argumentul sinusului cu T/2. Pentru o perioadă, această deplasare trebuie să fie un multiplu întreg de 2π. Funcția este neconstantă și periodică, dar nu orice multiplu de 2π în x este o perioadă.',{'operation':'candidate_period','expression':'sin(x/2)','period':period},labels={0:'Nu, T nu este o perioadă',1:'Da, T este o perioadă',2:'Funcția nu este periodică',3:'Funcția este constantă'})
        fn=['sin','cos','tan','sin','cot'][j-1];freq=Q(j+1,j+2)
        fundamental=S.pi/freq if fn in ('tan','cot') else 2*S.pi/freq
        domain='pe domeniul său natural' if fn in ('tan','cot') else 'pe ℝ'
        B.emit('3.4',5,j,'Aflați perioada principală pozitivă a funcției f(x)='+r'\('+expression_tex(fn+'(a*x)')+r'\)'+' '+domain+', pentru a='+tex(freq)+'. Argumentele sunt în radiani.',fundamental,
            'Sinusul și cosinusul au perioada principală 2π, tangenta și cotangenta π pe domeniul natural. Împărțim perioada de bază la |a|, iar coeficientul este strict pozitiv; deplasarea păstrează și domeniul de definiție.',{'operation':'period','function':fn,'frequency':freq,'mode':'plain'})
        B.emit('3.4',6,j,f'Determinați perioada principală pozitivă a lui f(x)=sin({j}x/2)+cos({j}x/3), pe ℝ. Argumentele sunt în radiani.',12*S.pi/j,
            'Cele două frecvențe nenule sunt distincte, a/2 și a/3, cu a coeficientul întreg din enunț. Pentru o perioadă comună, (a/2)T și (a/3)T trebuie să fie multipli de 2π. Cea mai mică valoare pozitivă este 12π/a. Minimalitatea urmează din independența componentelor armonice cu frecvențe distincte.',{'operation':'period_sum','frequencies':[Q(j,2),Q(j,3)],'functions':['sin','cos']})
        mode='absolute' if j%2 else 'square';function='sin' if j%2 else 'cos'
        formula=f'Abs(sin({j}*x))' if mode=='absolute' else f'cos({j}*x)**2'
        B.emit('3.4',7,j,'Aflați perioada principală pozitivă a funcției f(x)='+r'\('+expression_tex(formula)+r'\)'+' pe ℝ, cu argumentele în radiani.',S.pi/j,
            'Modulul sinusului și pătratul cosinusului au fiecare perioada principală π în argument, nu 2π. Deplasarea cu π schimbă semnul funcției de bază, eliminat de modul sau pătrat. Zerourile sau formula cos²u=(1+cos2u)/2 exclud o perioadă pozitivă mai mică.',{'operation':'period','function':function,'frequency':j,'mode':mode})
        B.emit('3.4',8,j,f'Funcția f:ℝ→ℝ verifică f(x)+2f(−x)={j}cos({j+1}x) pentru orice x. Determinați perioada sa principală pozitivă. Argumentele sunt în radiani.',2*S.pi/(j+1),
            'Înlocuim x cu −x și folosim paritatea cosinusului. Sistemul pentru f(x),f(−x) are determinant −3≠0 și dă f(x)=(a/3)cos(bx), cu a,b numerele pozitive din enunț. Amplitudinea nenulă nu schimbă perioada principală 2π/b.',{'operation':'functional_period','amplitude':j,'frequency':j+1,'reflection_coefficient':2},True)
        B.emit('3.4',9,j,f'Studiați periodicitatea funcției f(x)=sin({j}x)+cos({j}√2·x), x∈ℝ. Argumentele sunt în radiani.',0,
            f'Notăm a={j}. Dacă T>0 ar fi o perioadă, f(−x) ar avea aceeași perioadă. Atunci partea impară [f(x)−f(−x)]/2=sin(ax) și partea pară [f(x)+f(−x)]/2=cos(a√2·x) ar fi ambele T-periodice. Ar rezulta aT=2kπ și a√2T=2mπ cu k,m întregi și k≠0; împărțirea ar da √2=m/k, imposibil. Acest argument folosește paritatea și perioadele funcțiilor elementare. Exemplul este o sumă proprie, nu produsul nespecificat al catalogului.',{'operation':'nonperiodic_sum','frequencies':[j,j*S.sqrt(2)],'functions':['sin','cos']},True,labels={0:'Funcția nu este periodică',1:'Perioada principală este 2π',2:'Perioada principală este π',3:'Funcția este constantă'})

        angles=[S.pi/6,S.pi/4,S.pi/3,S.pi/12,5*S.pi/12]
        def rel(typ,formula,reason,extra=None,partial=True):
            B.calc('4',typ,j,'Toate argumentele sunt în radiani, iar x este ascuțit.',formula,{'x':angles[j-1],**(extra or {})},reason,partial)
        rel(1,'sin(x)**4+cos(x)**2-cos(x)**4-sin(x)**2','Factorizăm sin⁴x−cos⁴x=(sin²x−cos²x)(sin²x+cos²x); relația fundamentală arată anularea expresiei.')
        rel(2,'tan(x)**2+cot(x)**2+2','Expresia este (tan x+cot x)²=1/(sin²x cos²x), deoarece sin²x+cos²x=1. Numitorii sunt nenuli pentru x ascuțit.')
        p,q,h=[(3,4,5),(5,12,13),(8,15,17),(7,24,25),(20,21,29)][j-1]
        quad=[2,3,4,2,3][j-1];sine=Q(p,h)*(1 if quad==2 else -1);cosine=Q(q,h)*(-1 if quad in (2,3) else 1)
        B.emit('4',3,j,'Se cunoaște sin x='+tex(sine)+f', iar punctul unghiului x este în cadranul {quad}. Aflați (cos x;tan x;cot x).',S.Tuple(cosine,sine/cosine,cosine/sine),
            'Relația fundamentală dă cos²x=1−sin²x. Cadranul fixează semnul cosinusului. Apoi tan x=sin x/cos x și cot x=cos x/sin x; valorile sinusului și cosinusului sunt nenule.',{'operation':'recover_functions','sine':sine,'quadrant':quad})
        summ=Q(p+q,h)
        B.emit('4',4,j,'Unghiul x este în (0;π/4), cu sin x+cos x='+tex(summ)+'. Aflați perechea (sin x;cos x).',S.Tuple(Q(p,h),Q(q,h)),
            'Pătratul sumei dă produsul sin x cos x=(m²−1)/2. Cele două valori sunt rădăcinile ecuației t²−mt+(m²−1)/2=0. Intervalul impune sin x<cos x și fixează ordinea; ambele rădăcini sunt pozitive.',{'operation':'recover_sum','sum':summ,'sine_less_cosine':True})
        rel(5,'sin(x)+cos(x)-sin(pi/2-x)-cos(pi/2-x)','Perechile complementare dau sin(π/2−x)=cos x și cos(π/2−x)=sin x, astfel cele două sume sunt egale.')
        rel(6,'cos(x)**2/(1-sin(x))','Înmulțim cu 1+sin x și folosim cos²x=(1−sin x)(1+sin x). Pe domeniul dat 1−sin x>0, deci reducerea este legitimă; rezultă 1+sin x.')
        rel(7,'sin(x)**6+cos(x)**6','Notăm u=sin²x,v=cos²x, u+v=1. Formula u³+v³=(u+v)³−3uv(u+v) reduce expresia la 1−3sin²x cos²x.')
        rel(8,'sin(x)**8+cos(x)**8+4*sin(x)**2*cos(x)**2-2*sin(x)**4*cos(x)**4','Cu u+v=1, u⁴+v⁴=1−4uv+2u²v². Termenii suplimentari se anulează și rămâne constanta 1.')
        rel(9,'(sin(x)**3+cos(x)**3)/(sin(x)+cos(x))','Numitorul este pozitiv pentru x ascuțit. Factorizarea sumei de cuburi dă sin²x−sin x cos x+cos²x=1−sin x cos x.')
        av,bv=S.Integer(j+1),S.Integer(j+3);si=(bv-av)/(av+bv);co=2*S.sqrt(av*bv)/(av+bv)
        B.emit('4',10,j,f'a={av}, b={bv} și x∈(0;π/2) satisfac sin x=(b−a)/(a+b). Calculați cos x+tan x+cot x.',S.simplify(co+si/co+co/si),
            'Datele au 0<a<b, deci sinusul este în (0,1). Cosinusul pozitiv se recuperează ca 2√(ab)/(a+b). Aplicăm apoi definițiile tangentei și cotangentei; niciun numitor nu este zero.',{'operation':'recover_parameter','a':av,'b':bv,'expression':'cos(x)+tan(x)+cot(x)'},True)
        B.emit('4',11,j,'Pentru α='+tex(angles[j-1])+' radiani, care este minimul pe t∈ℝ al trinomului (1−sin α)t²−2t cos α+1+sin α?',0,
            'Coeficientul principal este strict pozitiv în datele date. Discriminantul este 4cos²α−4(1−sin α)(1+sin α)=0. Trinomul este un pătrat cu minimul 0, atins la t=cos α/(1−sin α).',{'operation':'trig_quadratic_min','angle':angles[j-1]},True)
        B.emit('4',12,j,f'Care este minimul pe ℝ al lui {j}(sin⁴x+cos⁴x)? Argumentul este în radiani.',Q(j,2),
            'Cu u=sin²x,v=cos²x avem u+v=1. Din (u−v)²≥0 rezultă u²+v²≥1/2; egalitatea este atinsă la x=π/4. Coeficientul pozitiv multiplică minimul.',{'operation':'minimum_even_power','coefficient':j,'power':4},True)
        B.emit('4',13,j,f'Aflați imaginea funcției f(x)={j}−2sin x+(1+sin x)², x∈ℝ. Argumentul este în radiani.',S.Interval(j+1,j+2),
            'Dezvoltarea pătratului simplifică funcția la a+1+sin²x, cu a constanta din enunț. Deoarece sin²x parcurge [0,1] pe ℝ, imaginea este intervalul închis [a+1,a+2]; ambele capete se ating.',{'operation':'range_polynomial_sine','offset':j,'polynomial':'a+1+t**2'})
        B.emit('4',14,j,f'Aflați cea mai mică bornă C pentru care |{p}sin x+{q}cos x|≤C pentru orice x∈ℝ, în radiani.',h,
            'Cauchy–Schwarz dă |a sin x+b cos x|≤√(a²+b²). Borna este atinsă când (sin x,cos x) este vectorul unitate proporțional cu (a,b), deci nu poate fi micșorată.',{'operation':'linear_trig_bound','sin_coefficient':p,'cos_coefficient':q},True)
        m=[S.Integer(1),(1+S.sqrt(3))/2,S.sqrt(2),-S.Integer(1),-S.sqrt(2)][j-1];product=(m*m-1)/2
        answer=S.simplify(m**5-5*product*m**3+5*product**2*m)
        B.emit('4',15,j,'Se știe sin x+cos x='+tex(m)+'. Calculați sin⁵x+cos⁵x; x este real, în radiani.',answer,
            'Punem u=sin x,v=cos x. Avem u+v=m, u²+v²=1 și uv=(m²−1)/2. Identitatea u⁵+v⁵=m⁵−5uv·m³+5(uv)²m dă rezultatul. Valorile date ale lui m aparțin [−√2,√2], deci există unghiuri reale.',{'operation':'power_from_sum','sum':m,'power':5},True)


def build_banks():
    builder=Builder()
    foundations(builder)
    signs_reductions_relations(builder)
    from trigonometrie_advanced import populate
    populate(builder)
    assert [len(builder.banks[lesson]) for lesson in range(1,10)]==COUNTS
    assert sum(map(len,builder.banks.values()))==585
    assert len({q['text'] for bank in builder.banks.values() for q in bank})==585
    return builder.banks


def update_files(lessons=None):
    banks=build_banks()
    for lesson,items in banks.items():
        if not items or lessons and lesson not in lessons:continue
        path=next((ROOT/'clasa_9').glob(f'clasa_9_u07_l{lesson:02d}_*.json'))
        data=json.loads(path.read_text(encoding='utf-8'))
        retained=[q for q in data['questions'] if q.get('practice_scope',{}).get('bank')!=BANK]
        data['questions']=retained+items
        data['difficulty']='medium' if lesson<6 else 'hard'
        temporary=path.with_suffix('.json.tmp')
        temporary.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        temporary.replace(path)
        print(f'Trigonometry lesson {lesson}: {len(items)} original grids, {len(retained)} retained.')
    return banks


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--lessons',type=int,nargs='*')
    update_files(parser.parse_args().lessons)
