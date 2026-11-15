"""200 original exact grids for G4 sections 4.1, 4.2, 4.3.

Five numeric/conclusion adaptations per catalog type, with explicit limits
where the catalog does not specify the original olympiad identity. No DB writes.
"""
import json
from pathlib import Path

import sympy as S

ROOT=Path(__file__).resolve().parents[1]
TARGET=ROOT/'clasa_9/clasa_9_u08_l03_rezolvarea_triunghiurilor_raza_cercului_circumscris_si_inscris_formule.json'
BANK='g4_triunghiuri_v1'
Q=S.Rational


def clean(value): return S.simplify(value)
def tex(value): return r'\('+S.latex(clean(value))+r'\)'
def serial(value):
    if isinstance(value,(list,tuple)): return [serial(item) for item in value]
    return str(clean(value))
def radians(degrees): return S.pi*degrees/180
def area_sides(a,b,c):
    assert a>0 and b>0 and c>0 and a+b>c and a+c>b and b+c>a
    p=(a+b+c)/2
    return clean(S.sqrt(p*(p-a)*(p-b)*(p-c)))
def point(raw): return S.Point(*raw)
def pt_text(label,raw): return label+'('+ '; '.join(str(v) for v in raw)+')'


def build_questions():
    questions=[]

    def emit(section,typ,j,text,result,reason,givens,adaptation='calcul exact într-un caz explicit; elementul cerut este precizat în enunț'):
        result=clean(result)
        values=[clean(result+offset) for offset in [0,1,-1,2]]
        assert all(clean(first-second)!=0 for i,first in enumerate(values) for second in values[i+1:])
        correct=len(questions)%4
        values.insert(correct,values.pop(0))
        questions.append({
            'text':text,'type':'multiple_choice','format':'grid','points':10,
            'explanation':'În calculele acestei variante, s='+tex(S.Integer(j+1))+'. '+reason+' Rezultatul cerut este '+tex(result)+'.',
            'options':[{'text':tex(value),'is_correct':index==correct} for index,value in enumerate(values)],
            'practice_scope':{'bank':BANK,'catalog':'G4','section':section,'type':typ,'variant':j,
                              'reference_pages':{'4.1':'239–241','4.2':'242','4.3':'242–245'}[section],
                              'adaptation':adaptation},
            'verification':givens,
        })

    triples=[(3,4,5),(5,12,13),(8,15,17),(7,24,25),(20,21,29)]
    for j in range(1,6):
        s=S.Integer(j+1)
        first,second,hyp=[s*n for n in triples[j-1]]
        angle=[30,45,60,15,75][j-1]
        emit('4.1',1,j,f'ABC este dreptunghic în A, a=BC={tex(2*s)}, B={angle}° (grade). Determinați cateta b=CA.',
             2*s*S.sin(radians(angle)),
             f'C=90°−B={90-angle}°. Într-un triunghi dreptunghic, sin B=b/a, deci b=a sin B. Cateta cealaltă este c=a cos B, pozitivă deoarece B este ascuțit.',
             {'hyp':serial(2*s),'B_deg':angle})
        emit('4.1',2,j,f'ABC este dreptunghic în A, a=BC={tex(hyp)} și '+r'\(\sin B='+S.latex(first/hyp)+r'\). Calculați cateta c=AB.',
             second,
             f'B este ascuțit, deci cos B este rădăcina pozitivă a lui 1−sin²B: '+tex(second/hyp)+'. Atunci c=a cos B. Cealaltă catetă este b=a sin B='+tex(first)+'. Nu se admite rădăcina negativă a cosinusului.',
             {'hyp':serial(hyp),'sin_B':serial(first/hyp)})
        m,n=first**2/hyp,second**2/hyp
        emit('4.1',3,j,f'Într-un triunghi dreptunghic, piciorul înălțimii din unghiul drept împarte ipotenuza în segmentele pozitive m={tex(m)}, n={tex(n)}. Aflați înălțimea h.',
             first*second/hyp,
             'Teorema înălțimii dă h²=mn. Întrucât înălțimea este lungime strict pozitivă, h=√(mn). În plus, a=m+n, iar catetele se recuperează din b²=am și c²=an; datele determină un triunghi nedegenerat.',
             {'m':serial(m),'n':serial(n)})
        emit('4.1',4,j,f'ABC este dreptunghic în A, ipotenuza are lungimea {tex(2*s)}, iar B=2C. Calculați cateta opusă unghiului B.',
             s*S.sqrt(3),
             'B+C=90° și B=2C, deci C=30° și B=60°. Cateta opusă lui B este a sin60°=a√3/2. Cealaltă catetă este a/2; ambele sunt pozitive.',
             {'hyp':serial(2*s),'angle_ratio':2})
        total=first+second
        emit('4.1',5,j,f'În triunghiul dreptunghic în A, b+c={tex(total)}, iar '+r'\(\tan B='+S.latex(first/second)+r'\). Aflați aria triunghiului.',
             first*second/2,
             f'Fiind B ascuțit, tan B=b/c. Catetele sunt proporționale cu {triples[j-1][0]} și {triples[j-1][1]}; suma fixează factorul de scară. Obținem b='+tex(first)+', c='+tex(second)+', apoi S=bc/2.',
             {'sum_legs':serial(total),'tan_B':serial(first/second)})
        sine=[Q(1,2),Q(3,5),Q(4,5),Q(5,13),Q(12,13)][j-1]
        rhs=sine+sine**2
        emit('4.1',6,j,f'ABC este dreptunghic în A, a={tex(10*s)} și '+r'\(\sin B+\cos^2 C='+S.latex(rhs)+r'\). Calculați cateta b.',
             10*s*sine,
             'Deoarece C=90°−B, cos C=sin B. Cu y=sin B∈(0,1), ecuația devine y²+y='+tex(rhs)+'. Rădăcinile sunt '+tex(sine)+' și '+tex(-1-sine)+'. Numai prima este admisă. Rezultă b=a sin B.',
             {'hyp':serial(10*s),'nonlinear_rhs':serial(rhs)})
        b,c=5*s*S.sqrt(3),5*s
        bisector_squared=clean(2*b*b*c*c/(b+c)**2)
        emit('4.1',7,j,f'ABC este dreptunghic în A, a={tex(10*s)}, C=30°. Dacă AD este bisectoarea interioară a unghiului drept, calculați AD².',
             bisector_squared,
             'B=60°, deci b=a sin60° și c=a sin30°. Formula bisectoarei este AD=2bc cos(A/2)/(b+c). Aici cos45°=√2/2, deci AD²=2b²c²/(b+c)². Numitorul este strict pozitiv.',
             {'hyp':serial(10*s),'C_deg':30})
        Adeg,Bdeg=[(105,30),(90,45),(75,60),(120,30),(45,60)][j-1]
        aa=2*s*S.sin(radians(Adeg))
        emit('4.1',8,j,f'În ABC, A={Adeg}°, B={Bdeg}° și a={tex(aa)}. Unghiurile sunt exprimate în grade. Aflați b.',
             2*s*S.sin(radians(Bdeg)),
             f'Al treilea unghi este C={180-Adeg-Bdeg}°>0. Teorema sinusurilor dă b=a sin B/sin A. Sin A este pozitiv, iar datele unghi–unghi–latură determină un singur triunghi până la congruență.',
             {'a':serial(aa),'A_deg':Adeg,'B_deg':Bdeg})
        Adeg=[30,45,60,90,120][j-1]
        b,c=2*s,3*s
        aa=clean(S.sqrt(b*b+c*c-2*b*c*S.cos(radians(Adeg))))
        emit('4.1',9,j,f'În ABC, b={tex(b)}, c={tex(c)}, iar unghiul cuprins A={Adeg}° (grade). Determinați a.',
             aa,
             'Prin teorema cosinusului, a²=b²+c²−2bc cos A. Unghiul este strict între 0° și 180°, deci triunghiul este nedegenerat. Alegem rădăcina pozitivă; datele latură–unghi cuprins–latură determină un singur triunghi.',
             {'b':serial(b),'c':serial(c),'A_deg':Adeg})
        base=[(13,14,15),(3,4,5),(4,5,6),(5,5,6),(7,8,9)][j-1]
        a,b,c=[s*n for n in base]
        area_sides(a,b,c)
        emit('4.1',10,j,f'Triunghiul ABC are a={tex(a)}, b={tex(b)}, c={tex(c)}. Calculați cos A.',
             (b*b+c*c-a*a)/(2*b*c),
             'Laturile sunt pozitive și satisfac strict cele trei inegalități ale triunghiului. Din a²=b²+c²−2bc cos A obținem cos A=(b²+c²−a²)/(2bc). Rezultatul aparține intervalului (−1,1), deci unghiul este unic în (0°,180°).',
             {'sides':serial([a,b,c])})
        emit('4.1',11,j,f'Trapezul dreptunghic convex ABCD are AB={tex(9*s)}, CD={tex(4*s)}, AB∥CD, AD⊥AB, iar diagonalele AC și BD sunt perpendiculare. Calculați perimetrul.',
             s*(19+S.sqrt(61)),
             'Alegem A=(0,0), B=(9s,0), D=(0,h), C=(4s,h), unde s este factorul comun al bazelor. Produsul scalar AC·BD=−36s²+h² este zero, deci h=6s>0. Latura oblică este √((9s−4s)²+h²)=s√61. Adunăm cele două baze și cele două laturi.',
             {'lower':serial(9*s),'upper':serial(4*s)})
        height=first*second/hyp
        emit('4.1',12,j,f'Un triunghi dreptunghic are suma catetelor {tex(total)} și înălțimea pe ipotenuză h={tex(height)}. Aflați cateta mai mare.',
             second,
             'Notăm L=b+c și a ipotenuza. Din bc=ha și a²=b²+c²=L²−2bc rezultă a²+2ha−L²=0. Rădăcina pozitivă este a=−h+√(h²+L²). Catetele sunt rădăcinile ecuației t²−Lt+ha=0; ambele sunt pozitive. Alegem rădăcina mai mare.',
             {'sum_legs':serial(total),'height':serial(height)})
        emit('4.1',13,j,f'Într-un triunghi dreptunghic, mediana la ipotenuză are lungimea {tex(hyp/2)}, iar suma catetelor este {tex(total)}. Determinați cateta mai mare.',
             second,
             'Mediana la ipotenuză este jumătate din aceasta, deci a=2m_a. Dacă L=b+c, atunci bc=(L²−a²)/2. Catetele sunt cele două rădăcini pozitive ale lui t²−Lt+bc=0. Alegem rădăcina mai mare; permutarea catetelor nu dă un triunghi necongruent.',
             {'median':serial(hyp/2),'sum_legs':serial(total)})
        vertices=[(3*s,0),(0,4*s),(-5*s,0),(0,-12*s)]
        perim=sum(point(vertices[i]).distance(point(vertices[(i+1)%4])) for i in range(4))
        emit('4.1',14,j,'Patrulaterul convex ABCD are '+', '.join(pt_text(name,p) for name,p in zip('ABCD',vertices))+'. Diagonalele AC și BD sunt perpendiculare și se intersectează în O=(0;0). Aflați perimetrul.',
             perim,
             'Segmentele OA,OB,OC,OD sunt strict pozitive, astfel că O este interior ambelor diagonale. Aplicăm Pitagora separat în cele patru triunghiuri dreptunghice AOB,BOC,COD,DOA și adunăm laturile obținute.',
             {'vertices':serial(vertices)},
             adaptation='adaptare parțială explicită: patru proiecții pe diagonale date, nu reconstrucția din trei laturi a catalogului')
        t=[0,15,30,36,45][j-1]
        sum_sines=clean(S.sqrt(3)*S.cos(radians(t)))
        emit('4.1',15,j,'Unghiurile unui triunghi sunt în progresie aritmetică, A≤B≤C, și '+r'\(\sin A+\sin C='+S.latex(sum_sines)+r'\). Toate unghiurile sunt exprimate în grade. Determinați A.',
             S.Integer(60-t),
             'Din suma unghiurilor rezultă B=60°. Scriem A=60°−u și C=60°+u, cu 0≤u<60°. Formula sumă–produs dă sin A+sin C=√3 cos u. Cosinusul este strict descrescător pe [0°,60°), deci valoarea lui determină unic u și apoi A=60°−u.',
             {'sum_sines':serial(sum_sines),'parameter_deg':t})

        side=2*s*S.sqrt(3)
        emit('4.2',1,j,f'Un triunghi echilateral are latura {tex(side)}. Calculați suma R+r a razelor cercurilor circumscris și înscris.',
             3*s,
             'Înălțimea este h=l√3/2, iar centrul comun împarte mediana în raport 2:1. Astfel R=2h/3=l√3/3 și r=h/3=l√3/6. În particular R=2r; adunăm cele două raze.',
             {'side':serial(side)})
        a,b,c=6*s,5*s,5*s
        emit('4.2',2,j,f'Triunghiul isoscel are laturile {tex(a)}, {tex(b)}, {tex(c)}. Aflați R+r.',
             Q(37,8)*s,
             'Înălțimea pe baza de 6s este √((5s)²−(3s)²)=4s, deci S=12s² și p=8s. Formulele R=abc/(4S) și r=S/p dau R=25s/8 și r=3s/2; suma este 37s/8.',
             {'sides':serial([a,b,c])})
        emit('4.2',3,j,f'Triunghiul dreptunghic are catetele {tex(first)}, {tex(second)} și ipotenuza {tex(hyp)}. Determinați raza r a cercului înscris.',
             (first+second-hyp)/2,
             'S=bc/2 și p=(a+b+c)/2, deci r=bc/(a+b+c). Înmulțind cu b+c−a și folosind a²=b²+c² obținem r=(b+c−a)/2. Raza circumcercului este separat R=a/2.',
             {'legs':serial([first,second]),'hyp':serial(hyp)})
        vertices=[(0,0),(4*s,0),(0,3*s)]
        emit('4.2',4,j,'ABC este dreptunghic în A, cu '+', '.join(pt_text(name,p) for name,p in zip('ABC',vertices))+'. M este mijlocul ipotenuzei BC. Dacă r₁,r₂ sunt razele cercurilor înscrise în ABM,ACM, calculați r₁+r₂.',
             Q(17,12)*s,
             'AM=BM=CM=5s/2. Cele două subtriunghiuri au fiecare aria 3s². Semiperimetrele sunt 9s/2, respectiv 4s, deci r₁=2s/3 și r₂=3s/4. Formula R=abc/(4S) ar da razele circumscrise 25s/12 și 25s/16; toate subtriunghiurile sunt nedegenerate.',
             {'vertices':serial(vertices)})
        emit('4.2',5,j,f'ABC este dreptunghic în A, AB={tex(4*s)}, AC={tex(3*s)}, iar AD este bisectoarea interioară, D∈BC. R₁,R₂ sunt razele circumcercurilor lui ABD,ACD. Calculați R₁/R₂.',
             Q(4,3),
             'Unghiurile BAD și DAC sunt egale cu 45°. Teorema sinusurilor în cele două subtriunghiuri dă R₁=BD/(2sin45°), R₂=DC/(2sin45°). Prin urmare R₁/R₂=BD/DC=AB/AC=4/3, folosind teorema bisectoarei. Sin45° este nenul.',
             {'AB':serial(4*s),'AC':serial(3*s)})
        emit('4.2',6,j,f'Un triunghi dreptunghic are raza cercului circumscris R={tex(hyp/2)} și raza cercului înscris r={tex((first+second-hyp)/2)}. Aflați cateta mai mare.',
             second,
             'Recuperăm ipotenuza a=2R și suma catetelor L=a+2r. Apoi bc=(L²−a²)/2, iar catetele sunt rădăcinile lui t²−Lt+bc=0. Datele dau două rădăcini strict pozitive; schimbarea ordinii lor reprezintă același triunghi.',
             {'R':serial(hyp/2),'r':serial((first+second-hyp)/2)})
        emit('4.2',7,j,f'Într-un triunghi nedegenerat, a={tex(hyp)}, b+c={tex(total)}, iar raza cercului înscris este r={tex((total-hyp)/2)}. Se verifică b+c=a+2r. Determinați unghiul A, opus lui a, în grade.',
             S.Integer(90),
             'Notăm p=(a+b+c)/2. Ipoteza dă p−a=r. Din Heron și S=pr rezultă p(p−a)=(p−b)(p−c); dezvoltarea și relația 2p=a+b+c conduc la a²=b²+c². Prin reciproca lui Pitagora, A=90°. Pozitivitatea lui r și a lui p−a permite simplificările.',
             {'witness_sides':serial([hyp,first,second]),'R':serial(hyp/2),'r':serial((total-hyp)/2)},
             adaptation='concluzie cu justificarea reciprocei; datele includ o configurație existentă')
        Adeg,Bdeg=[(120,45),(105,30),(75,60),(45,45),(60,60)][j-1]
        Cdeg=180-Adeg-Bdeg
        sides=[2*s*S.sin(radians(deg)) for deg in [Adeg,Bdeg,Cdeg]]
        emit('4.2',8,j,f'Un triunghi are R={tex(s)}, A={Adeg}°, B={Bdeg}° (grade). Calculați perimetrul.',
             sum(sides),
             f'C={Cdeg}° este pozitiv. Teorema sinusurilor extinsă dă a=2R sin A, b=2R sin B, c=2R sin C. Adunăm cele trei lungimi; toate sunt strict pozitive și datele determină forma triunghiului.',
             {'R':serial(s),'A_deg':Adeg,'B_deg':Bdeg})

        Adeg=[30,45,60,90,120][j-1]
        emit('4.3',1,j,f'Două laturi ale triunghiului au lungimile b={tex(3*s)}, c={tex(4*s)}, iar unghiul cuprins A={Adeg}° (grade). Aflați aria.',
             6*s*s*S.sin(radians(Adeg)),
             'Aria este S=bc sin A/2. Unghiul este strict între 0° și 180°, deci sinusul este pozitiv; nu se schimbă cu cosinusul și nu se omite factorul 1/2.',
             {'b':serial(3*s),'c':serial(4*s),'A_deg':Adeg})
        emit('4.3',2,j,f'În ABC se cunosc a={tex(2*s)}, A=30° și C=45°. Calculați aria; unghiurile sunt în grade.',
             s*s*(S.sqrt(3)+1),
             'B=105°. Din sinusuri b=a sin B/sin A și c=a sin C/sin A. Prin S=bc sin A/2 rezultă S=a² sin B sin C/(2sin A). Sin30° este pozitiv, deci numitorul nu se anulează.',
             {'a':serial(2*s),'A_deg':30,'C_deg':45})
        chosen_area=[3*s*s,6*s*s,7*s*s,3*S.sqrt(2)*s*s,3*S.sqrt(3)*s*s][j-1]
        sine=clean(chosen_area/(6*s*s))
        count=1 if sine==1 else (0 if sine>1 else 2)
        emit('4.3',3,j,f'Câte triunghiuri necongruente, nedegenerate, au două laturi a={tex(3*s)}, b={tex(4*s)} și aria S={tex(chosen_area)}? Reflexiile se consideră congruente.',
             S.Integer(count),
             'Unghiul cuprins C trebuie să satisfacă sin C=2S/(ab)='+tex(sine)+'. Dacă valoarea depășește 1 nu există triunghi. Dacă este 1, C=90° și există unul singur. Dacă este strict între 0 și 1, unghiurile C și 180°−C dau două valori diferite ale lui c²=a²+b²−2ab cos C, deci două triunghiuri necongruente. Niciun caz degenerat nu este admis.',
             {'a':serial(3*s),'b':serial(4*s),'area':serial(chosen_area)})
        emit('4.3',4,j,f'În ABC, a+c={tex(7*s)}, b={tex(s*S.sqrt(13))}, B=60° (grade). Aflați aria.',
             3*S.sqrt(3)*s*s,
             'Cosinusul dă b²=(a+c)²−2ac(1+cos B). Cum 1+cos60°=3/2, rezultă ac=12s². Suma 7s și produsul 12s² dau laturile 3s,4s, ambele pozitive. Aria este ac sin60°/2.',
             {'sum_ac':serial(7*s),'b':serial(s*S.sqrt(13)),'B_deg':60})
        a,b,c=13*s,14*s,15*s
        p=(a+b+c)/2
        emit('4.3',5,j,f'Triunghiul are a={tex(a)}, b={tex(b)}, c={tex(c)}, iar p este semiperimetrul. Calculați '+r'\(\frac{a}{p-a}+\frac{b}{p-b}+\frac{c}{p-c}\).',
             clean(a/(p-a)+b/(p-b)+c/(p-c)),
             'Toate diferențele p−a,p−b,p−c sunt pozitive. Suma se poate calcula direct. Identitatea echivalentă este Σa/(p−a)=4R/r−2: punând x=p−a,y=p−b,z=p−c, folosim xyz=pr² și xy+yz+zx=r(4R+r), apoi a=p−x. În acest caz Heron dă S=84s², r=4s și R=65s/8.',
             {'sides':serial([a,b,c])},
             adaptation='identitate explicită validă din familia relațiilor R,r,p; nu reproduce toate identitățile catalogului')
        vertices=[(-3*s,0),(3*s,0),(0,4*s)]
        emit('4.3',6,j,'Triunghiul ascuțitunghic ABC are '+', '.join(pt_text(name,p) for name,p in zip('ABC',vertices))+'. D,E,F sunt picioarele înălțimilor din A,B,C. Aflați aria triunghiului ortic DEF.',
             Q(1512,625)*s*s,
             'ABC are laturile 5s,5s,6s, astfel că toate cosinusurile sunt pozitive: cos A=cos B=3/5 și cos C=7/25. Aria sa este 12s². Pentru triunghiul ascuțitunghic, S_DEF=2S_ABC cos A cos B cos C; înlocuirea dă 1512s²/625. Restricția ascuțitunghic este esențială pentru această formă cu semn pozitiv.',
             {'vertices':serial(vertices)})
        a,b,c=5*s,3*s,4*s
        emit('4.3',7,j,f'Triunghiul ABC are a={tex(a)}, b={tex(b)}, c={tex(c)}. Calculați '+r'\(b^2\sin(2C)+c^2\sin(2B)\).',
             24*s*s,
             'Teorema sinusurilor și formula unghiului dublu dau b²sin2C+c²sin2B=(bc/R)(b cos C+c cos B). Formula proiecțiilor face paranteza egală cu a, deci expresia este abc/R=4S. Triunghiul este dreptunghic în A, cu S=bc/2=6s².',
             {'sides':serial([a,b,c])})
        emit('4.3',8,j,f'Un triunghi nedegenerat are R={tex(2*s)} și r={tex(s)}, deci r=R/2. Determinați A, în grade.',
             S.Integer(60),
             'Inegalitatea lui Euler este R≥2r, cu egalitate exact pentru triunghiul echilateral. Aici se atinge egalitatea, astfel că toate unghiurile sunt de 60°. O realizare are latura R√3, deci datele sunt compatibile.',
             {'R':serial(2*s),'r':serial(s)},
             adaptation='concluzie din cazul de egalitate Euler, cu configurație existentă')
        vertices=[(-3*s,0),(3*s,0),(0,4*s)]
        mobile=(Q(15,8)*s,Q(27,8)*s)
        emit('4.3',9,j,'Triunghiul ABC are '+', '.join(pt_text(name,p) for name,p in zip('ABC',vertices))+', iar M'+str(tuple(mobile)).replace(',',';')+' aparține circumcercului. Calculați '+r'\(MA^2\sin(2A)+MB^2\sin(2B)+MC^2\sin(2C)\).',
             48*s*s,
             'Circumcentrul este O=(0;7s/8), R=25s/8; punctul M verifică OM=R. Pentru un punct al circumcercului, identitatea este ΣMA²sin2A=4S. Ea rezultă prin dezvoltare cu originea O, din ΣOA sin2A=0 și Σsin2A=2S/R². Se poate verifica și direct cu cos A=cos B=3/5, cos C=7/25. Aici S=12s², deci valoarea este 48s².',
             {'vertices':serial(vertices),'M':serial(mobile)},
             adaptation='verificarea unui punct explicit pe circumcerc și explicarea invariantului')
        a,b,c=13*s,14*s,15*s
        emit('4.3',10,j,f'Triunghiul ABC are a={tex(a)}, b={tex(b)}, c={tex(c)}. Calculați '+r'\(a^2\cot A+b^2\cot B+c^2\cot C\).',
             336*s*s,
             'Heron dă S=84s²>0. Într-un triunghi nedegenerat, cot A=(b²+c²−a²)/(4S), și ciclic, deoarece sin A>0. După însumare, numărătorul este 16S², deci suma este 4S=336s². Nu se împarte la cosinusuri care s-ar putea anula.',
             {'sides':serial([a,b,c])})
        emit('4.3',11,j,'Triunghiul ascuțitunghic ABC are '+', '.join(pt_text(name,p) for name,p in zip('ABC',vertices))+'. O este circumcentrul, iar R₁,R₂,R₃ sunt razele cercurilor circumscrise lui BOC,COA,AOB. Aflați R₁+R₂+R₃.',
             Q(3625,336)*s,
             'Pentru triunghiul acut, unghiurile la centru relevante au sinusuri pozitive. Din sinusuri, R₁=R/(2cos A), R₂=R/(2cos B), R₃=R/(2cos C). Aici R=25s/8, cos A=cos B=3/5 și cos C=7/25. Toate cele trei subtriunghiuri sunt nedegenerate și numitorii sunt nenuli.',
             {'vertices':serial(vertices)})
        theta=[30,45,60,90,120][j-1]
        emit('4.3',12,j,f'Un patrulater convex are diagonalele AC={tex(8*s)}, BD={tex(6*s)}, care se intersectează în O, iar ∠AOB={theta}° (grade). Determinați aria.',
             24*s*s*S.sin(radians(theta)),
             'Adunăm ariile celor patru triunghiuri de la intersecția diagonalelor. Suma produselor segmentelor se factorizează ca (AO+OC)(BO+OD)=AC·BD. Deci S=AC·BD·sin∠AOB/2. Convexitatea asigură intersecția interioară și adunarea ariilor fără semne.',
             {'AC':serial(8*s),'BD':serial(6*s),'angle_deg':theta})
        emit('4.3',13,j,f'Într-un triunghi nedegenerat, a={tex(5*s)}, mediana m_a={tex(Q(5,2)*s)} și aria S={tex(6*s*s)}. Aflați unghiul A, în grade.',
             S.Integer(90),
             'Formula medianei este 4m_a²=2b²+2c²−a². Ipoteza m_a=a/2 o transformă în a²=b²+c², deci A=90°. Reciproc, în cazul dreptunghic mediana are lungimea a/2 și aria bc/2. Catetele 3s,4s arată că aria dată este compatibilă.',
             {'witness_sides':serial([5*s,3*s,4*s]),'median':serial(Q(5,2)*s),'area':serial(6*s*s)},
             adaptation='adaptare parțială: criteriu explicit prin mediană și verificarea ariei, fără identitatea olimpică neprecizată în catalog')
        theta=[30,45,60,90,120][j-1]
        emit('4.3',14,j,f'Paralelogramul convex ABCD are AB=CD={tex(3*s)}, BC=DA={tex(4*s)}, A=C={theta}° (grade). Calculați aria folosind formula lui Bretschneider.',
             12*s*s*S.sin(radians(theta)),
             'Formula este S²=(p−a)(p−b)(p−c)(p−d)−abcd cos²((A+C)/2), cu p semiperimetrul. Aici p=7s și A+C='+str(2*theta)+'°, deci S²=144s⁴(1−cos²A). Alegem rădăcina pozitivă: S=12s²sin A. Termenul cu cosinus dispare numai pentru A+C=180°, adică în varianta dreptunghiului; în celelalte variante patrulaterul nu este inscriptibil.',
             {'sides':serial([3*s,4*s,3*s,4*s]),'A_deg':theta,'C_deg':theta})
        pfrac,qfrac=Q(j,j+1),Q(j+1,j+2)
        emit('4.3',15,j,f'M,N sunt puncte interioare laturilor AB,AC ale unui triunghi nedegenerat, cu AM/AB={tex(pfrac)}, AN/AC={tex(qfrac)}. Aflați raportul dintre aria triunghiului AMN și aria patrulaterului BMNC.',
             pfrac*qfrac/(1-pfrac*qfrac),
             'Cele două triunghiuri au unghiul A comun, deci S_AMN/S_ABC=(AM/AB)(AN/AC). Patrulaterul BMNC este restul triunghiului și are aria (1−pq)S_ABC. Cum 0<p,q<1, numitorul este pozitiv. Raportul cerut este pq/(1−pq).',
             {'AM_AB':serial(pfrac),'AN_AC':serial(qfrac)})
        hb,hc=3*s/S.sqrt(5),4*s/S.sqrt(5)
        emit('4.3',16,j,f'În triunghiul ABC se cunosc înălțimile h_b={tex(hb)}, h_c={tex(hc)} și relația a=R cos A, unde R este raza cercului circumscris. Determinați aria.',
             6*s*s/S.sqrt(5),
             'Din a=2R sin A și a=R cos A, cu R>0, rezultă 2sin A=cos A. Deoarece sin A>0, cos A>0, deci tan A=1/2 și sin A=1/√5. Din h_b=c sin A și h_c=b sin A obținem c=3s și b=4s. Atunci S=bc sin A/2=6s²/√5. Unghiul ascuțit și laturile pozitive dau un triunghi nedegenerat.',
             {'h_b':serial(hb),'h_c':serial(hc),'circumradius_relation':'a=R*cos(A)'})
        emit('4.3',17,j,f'Care este aria maximă a unui patrulater convex cu perimetrul P={tex(8*s)}?',
             4*s*s,
             'Bretschneider dă S²≤(p−a)(p−b)(p−c)(p−d). Cele patru numere pozitive au suma 2p=P, deci media aritmetică–geometrică dă produsul cel mult (P/4)⁴. Rezultă S≤P²/16. Egalitatea cere a=b=c=d și A+C=180°, adică patrulaterul este pătrat. Pătratul de latură P/4 realizează maximul.',
             {'perimeter':serial(8*s)})

    assert len(questions)==200
    assert len({question['text'] for question in questions})==200
    return questions


def update_file():
    data=json.loads(TARGET.read_text(encoding='utf-8'))
    retained=[q for q in data['questions'] if q.get('practice_scope',{}).get('bank')!=BANK]
    data['questions']=retained+build_questions()
    data['difficulty']='hard'
    TARGET.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return len(data['questions'])


if __name__=='__main__':
    print(f'{update_file()} questions; 200 original G4 triangle grids; no DB import.')
