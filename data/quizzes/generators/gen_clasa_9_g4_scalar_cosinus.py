"""230 original G4 §1/§2 grids; update only u08 lesson 1, no DB writes."""
import json
from pathlib import Path

import sympy as S

ROOT=Path(__file__).resolve().parents[1]
TARGET=next((ROOT/'clasa_9').glob('clasa_9_u08_l01_*.json'))
BANK='g4_scalar_cosinus_v1'
Q=S.Rational
NAMES={1:[
 'Produs scalar din laturile triunghiului','Produs scalar în coordonate','Produs scalar al combinațiilor',
 'Unghiul a doi vectori','Parametru pentru ortogonalitate','Parametru pentru unghi prescris',
 'Ortogonalitate simultană','Produse între vectori de puncte','Produse scalare într-o figură regulată',
 'Pătratul unei sume vectoriale','Vector necunoscut din norme și produs','Puncte pe axe din condiții scalare',
 'Caracterizarea unghiului drept','Caracterizarea paralelismului','Relația scalară a lui Euler',
 'Concurența înălțimilor','Concurența mediatoarelor','Diagonalele rombului','Identitatea paralelogramului',
 'Caracterizări metrice ale dreptunghiului','Diagonale perpendiculare în patrulater',
 'Identitatea lui Euler pentru patrulater','Pătrate de distanțe față de centru de greutate',
 'Teoremele catetei și înălțimii','Lungimea bisectoarei prin produs scalar','Concurența a patru perpendiculare'],
 2:['Cosinusurile din trei laturi','Teorema proiecțiilor în triunghi oblic','Identități mixte laturi–unghiuri',
 'Transformarea laturilor în sinusuri','Caracterizarea unghiului drept trigonometric','Triunghi obtuzunghic din laturi',
 'Existența triunghiului parametrizat','Unghi fix într-o familie de triunghiuri','Progresii de laturi și cotangente',
 'Unghiuri din raportul laturilor','Rigiditate metrică în patrulater','Relație reciprocă între laturi',
 'Teorema lui Stewart','Relația lui Steiner','Menelau prin sinusuri','Lungimea AH și raza circumcercului',
 'Optimizarea unei ceviene prin raporturi','Caracterizarea perpendicularității prin patru distanțe',
 'Invariant cu transversală variabilă','Teorema lui Ptolemeu']}
PARTIAL={(1,13),(1,14),(1,16),(1,17),(1,18),(1,20),(1,21),(1,22),(1,24),(1,25),(1,26),
         (2,5),(2,6),(2,8),(2,9),(2,10),(2,11),(2,12),(2,14),(2,15),(2,17),(2,18),(2,20)}


def v(*values):return S.ImmutableMatrix(values)
def pair(value):return S.Tuple(*value)
def tex(value):return r'\('+S.latex(S.sympify(value))+r'\)'
def pt(name,value):return name+tex(pair(value))
def dot(a,b):return S.simplify(a.dot(b))
def norm(a):return S.sqrt(dot(a,a))
def cosines(a,b,c):return S.Tuple((b*b+c*c-a*a)/(2*b*c),(a*a+c*c-b*b)/(2*a*c),(a*a+b*b-c*c)/(2*a*b))
def serial(value):
    if isinstance(value,S.MatrixBase):return [str(c) for c in value]
    if isinstance(value,dict):return {k:serial(v) for k,v in value.items()}
    if isinstance(value,(list,tuple)):return [serial(v) for v in value]
    if isinstance(value,S.Basic):return str(value)
    return value


def build_questions():
    questions=[]
    def emit(section,typ,j,text,answer,reason,givens):
        answer=pair(answer) if isinstance(answer,S.MatrixBase) else S.sympify(answer)
        if isinstance(answer,S.Interval):
            values=[answer,S.Interval(answer.start,answer.end),S.Interval.open(answer.start-1,answer.end),S.Interval.open(answer.start,answer.end+1)]
        elif isinstance(answer,S.Tuple):values=[answer,*[S.Tuple(answer[0]+k,*answer[1:]) for k in (1,-1,2)]]
        else:values=[answer,*[S.simplify(answer+k) for k in (1,-1,2)]]
        assert len(set(values))==4,(section,typ,j)
        correct=len(questions)%4;values.insert(correct,values.pop(0))
        questions.append({'text':text,'type':'multiple_choice','format':'grid','points':10,
            'explanation':reason+' Rezultatul cerut este '+tex(answer)+'.',
            'options':[{'text':tex(value),'is_correct':i==correct} for i,value in enumerate(values)],
            'practice_scope':{'bank':BANK,'catalog':'G4','section':section,'type':typ,'type_name':NAMES[section][typ-1],
                'pages':'230–233' if section==1 else '233–235','variant':j,
                'coverage':'partial_case' if (section,typ) in PARTIAL else 'adapted_grid',
                'adaptation':'Exercițiu original. Tipul de demonstrație/construcție este adaptat în calcul sau concluzie într-o configurație explicită; justificarea este în explicație.'},
            'verification':{**serial(givens),'option_values':[str(value) for value in values]}})

    for j in range(1,6):
        s=j+1
        a,b,c=map(S.Integer,(j+3,j+4,j+5))
        u,w,z=v(j+1,-j),v(2*j-1,j+2),v(-j,3*j+1)
        aa,bb,cc,oo=v(j,-j),v(2*j+1,j+2),v(-j,3*j),v(j-1,1)
        desc=', '.join(pt(name,p) for name,p in zip('ABC',(aa,bb,cc)))
        def scalar(typ,text,answer,reason,givens):emit(1,typ,j,text,answer,reason,givens)
        def cosine(typ,text,answer,reason,givens):emit(2,typ,j,text,answer,reason,givens)
        scalar(1,f'În triunghiul ABC, BC={a}, CA={b}, AB={c}. Calculați produsul scalar AB·AC.',(b*b+c*c-a*a)/2,
               'Din BC=AC−AB rezultă BC²=AB²+AC²−2AB·AC. Rezolvăm pentru produsul scalar. Cele trei lungimi pozitive satisfac inegalitățile stricte ale triunghiului.',{'sides':[a,b,c]})
        scalar(2,'Calculați u·v pentru u='+tex(pair(u))+' și v='+tex(pair(w))+'.',dot(u,w),
               'Într-o bază ortonormată, produsul scalar este u₁v₁+u₂v₂. Înmulțim componentele omoloage și adunăm; rezultatul este un scalar.',{'u':u,'v':w})
        scalar(3,'Vectorii au u='+tex(pair(u))+', v='+tex(pair(w))+', w='+tex(pair(z))+'. Calculați (u−2v)·(3u+w).',dot(u-2*w,3*u+z),
               'Biliniaritatea dă 3|u|²+u·w−6u·v−2v·w. Echivalent, întâi calculăm cele două combinații pe componente, apoi produsul lor scalar.',{'u':u,'v':w,'w':z})
        angle=[30,60,90,120,150][j-1];theta=S.pi*angle/180
        av,bv=v(j,0),v((j+1)*S.cos(theta),(j+1)*S.sin(theta))
        scalar(4,'Pentru vectorii nenuli u='+tex(pair(av))+' și v='+tex(pair(bv))+', aflați (cos θ; θ în grade), unde θ∈[0°;180°] este unghiul lor.',S.Tuple(S.cos(theta),angle),
               'Calculăm cos θ=(u·v)/(|u||v|). Normele sunt strict pozitive. Pe intervalul [0°,180°], cosinusul determină unic unghiul, inclusiv cazul obtuz, fără pierderea semnului.',{'u':av,'v':bv})
        scalar(5,f'Pentru ce m vectorii u=(m;{j+1}) și v=(2;{j-1}) sunt perpendiculari?',-Q(j*j-1,2),
               f'Ortogonalitatea este echivalentă cu produsul scalar nul: 2m+({j+1})({j-1})=0. Ambii vectori sunt nenuli pentru soluția obținută.',{'u_constant':j+1,'v':[2,j-1]})
        angle=[30,45,60,120,135][j-1];theta=S.pi*angle/180
        scalar(6,f'Vectorii u=(m;{j}) și v=(1;0) trebuie să formeze un unghi de {angle}°. Determinați m.',S.simplify(j/S.tan(theta)),
               'Ecuația nesupusă pătrării este m/√(m²+k²)=cos θ, cu k pozitiv dat în enunț. După pătrare se păstrează numai semnul lui m egal cu semnul cosinusului. Rezultatul m=k·cot θ verifică ecuația inițială; pentru unghi obtuz este negativ.',{'height':j,'angle':angle})
        scalar(7,f'Vectorul u=(1;m) este perpendicular simultan pe v=(n;{j}) și w=(2;−{j}). Determinați (m;n).',S.Tuple(Q(2,j),-2),
               f'Cele două produse nule dau n+{j}m=0 și 2−{j}m=0. A doua ecuație determină m, apoi prima determină n. Toți cei trei vectori sunt nenuli; v și w sunt opuși la soluție.',{'j':j})
        scalar(8,'Punctele considerate sunt '+desc+'. Calculați AB·AC.',dot(bb-aa,cc-aa),
               'Vectorii AB și AC se obțin scăzând coordonatele originii lor comune A. Aplicăm apoi formula produsului scalar în coordonate.',{'A':aa,'B':bb,'C':cc})
        scalar(9,f'ABCDEF este hexagon regulat de latură {s}, cu vârfuri în această ordine. Calculați AB·AD.',S.Integer(s*s),
               'AD este un diametru al circumcercului, deci are lungimea dublă a laturii. Unghiul BAD este 60°. Prin urmare AB·AD=|AB||AD|cos60°=s², unde s este latura dată.',{'side':s})
        scalar(10,'Pentru u='+tex(pair(u))+', v='+tex(pair(w))+', w='+tex(pair(z))+', calculați |u+v+w|².',dot(u+w+z,u+w+z),
               'Pătratul normei este suma pătratelor normelor și dublul fiecărui produs mixt. Se poate verifica și prin adunarea componentelor înaintea ridicării la pătrat.',{'u':u,'v':w,'w':z})
        scalar(11,f'u=(1;0), |v|={5*s} și u·v={3*s}. Dacă a doua componentă a lui v este pozitivă, aflați v.',v(3*s,4*s),
               'Produsul cu vectorul (1;0) fixează prima componentă. Ecuația normei determină pătratul celei de-a doua; condiția de pozitivitate selectează rădăcina pozitivă și elimină ambiguitatea celor două soluții.',{'length':5*s,'dot':3*s})
        scalar(12,f'A=(0;{s}), B=({4*s};{s}), M=(m;0), m>{2*s}. Dacă MA·MB=0, determinați M.',v((2+S.sqrt(3))*s,0),
               'Produsul scalar dă m²−4sm+s²=0, unde s este ordonata comună a lui A și B. Rădăcinile sunt s(2±√3). Restricția m>2s selectează semnul plus; vectorii MA și MB rămân nenuli.',{'scale':s})
        scalar(13,f'În triunghiul ABC, AB={3*s}, AC={4*s}, BC={5*s}. Cât măsoară unghiul A, în grade?',S.Integer(90),
               'Egalitatea BC²=AB²+AC² este echivalentă cu AB·AC=0 prin formula produsului scalar din laturi. Laturile formează un triunghi nedegenerat, deci unghiul de la A este drept.',{'legs':[3*s,4*s],'hypotenuse':5*s})
        scalar(14,f'u=({j};{2*j}) și v=(m;{j+1}) sunt nenuli. Pentru ce m relația (u·v)²=|u|²|v|² caracterizează paralelismul lor?',Q(j+1,2),
               'În plan, |u|²|v|²−(u·v)² este pătratul determinantului. Egalitatea se reduce la det(u,v)=0, deci componentele sunt proporționale. Ambii vectori au componente fixe nenule, astfel paralelismul are sens.',{'u':[j,2*j],'v_y':j+1})
        euler=dot(aa-oo,cc-bb)+dot(bb-oo,aa-cc)
        scalar(15,'Pentru '+desc+', '+pt('O',oo)+', calculați OA·BC+OB·CA folosind identitatea scalară a lui Euler.',euler,
               'Identitatea OA·BC+OB·CA+OC·AB=0 se demonstrează dezvoltând prin aceeași origine; termenii în perechi se anulează prin comutativitate. Prin urmare suma cerută este −OC·AB.',{'A':aa,'B':bb,'C':cc,'O':oo})
        at,bt,ct=v(0,0),v(4*s,0),v(s,3*s)
        scalar(16,'În triunghiul cu '+', '.join(pt(n,p) for n,p in zip('ABC',(at,bt,ct)))+', H este intersecția înălțimilor din A și C. Determinați H.',v(s,s),
               'Înălțimea din C este verticala prin C. Înălțimea din A impune AH·BC=0. Cele două condiții determină H; identitatea scalară a lui Euler arată apoi că și BH·CA=0, deci a treia înălțime trece prin același punct.',{'A':at,'B':bt,'C':ct})
        scalar(17,f'În triunghiul A=(0;0), B=({4*s};0), C=(0;{6*s}), determinați punctul O egal depărtat de A,B,C.',v(2*s,3*s),
               'Egalitățile OA²=OB² și OA²=OC² devin două ecuații liniare după anularea termenilor pătratici comuni. Soluția este unică pentru un triunghi necoliniar, iar egalitatea OB²=OC² urmează automat.',{'width':4*s,'height':6*s})
        scalar(18,f'ABCD este romb, AB=({3*s};{4*s}) și AD=({3*s};−{4*s}). Calculați produsul AC·BD.',S.Integer(0),
               'AC=AB+AD, BD=AD−AB. Produsul este |AD|²−|AB|²=0, deoarece laturile rombului au aceeași lungime. Diagonalele sunt nenule și perpendiculare.',{'u':[3*s,4*s],'v':[3*s,-4*s]})
        scalar(19,f'Un paralelogram are laturile alăturate {j+2} și {j+3}, iar unghiul dintre ele este 60°. Calculați suma pătratelor diagonalelor.',2*((j+2)**2+(j+3)**2),
               'Diagonalele au vectorii u+v și v−u. La adunarea pătratelor normelor, produsele mixte se anulează: |u+v|²+|v−u|²=2(|u|²+|v|²).',{'sides':[j+2,j+3],'angle':60})
        scalar(20,f'Într-un paralelogram nedegenerat, AB=(m;{j}), AD=(1;{j+1}). Pentru ce m avem MA²+MC²=MB²+MD² pentru orice punct M?',-j*(j+1),
               'Luăm A origine și notăm AB=u, AD=v. Diferența celor două sume de distanțe este 2u·v, independent de M. Anularea ei impune u·v=0 și caracterizează dreptunghiul în clasa paralelogramelor nedegenerate.',{'u_y':j,'v':[1,j+1]})
        scalar(21,f'Patrulaterul convex are A=(0;0), B=({2*s};−{s}), C=({4*s};0), D=(m;{2*s}). Aflați m dacă AB²+CD²=AD²+BC².',S.Integer(2*s),
               'Diferența AD²+BC²−AB²−CD² este 2AC·BD. Egalitatea dată implică diagonale perpendiculare. AC este orizontală și nenulă, deci BD trebuie să fie verticală; abscisele lui B și D coincid. Soluția produce un patrulater convex.',{'scale':s})
        quad=[v(0,0),v(4*s,0),v(5*s,3*s),v(0,2*s)]
        scalar(22,'Patrulaterul convex are '+', '.join(pt(n,p) for n,p in zip('ABCD',quad))+'. M,N sunt mijloacele diagonalelor AC,BD. Calculați 4MN².',S.Integer(2*s*s),
               'Identitatea lui Euler pentru patrulater este AB²+BC²+CD²+DA²=AC²+BD²+4MN², pentru mijloacele diagonalelor. Se obține dezvoltând pătratele normelor cu o origine comună. Calculul direct al mijloacelor confirmă rezultatul.',{'quad':quad})
        scalar(23,f'Triunghiul ABC are BC={a}, CA={b}, AB={c}, iar G este centrul de greutate. Calculați GA²+GB²+GC².',(a*a+b*b+c*c)/3,
               'Din GA+GB+GC=0, dezvoltarea pătratelor diferențelor dă AB²+BC²+CA²=3(GA²+GB²+GC²). Triunghiul dat satisface inegalitățile stricte.',{'sides':[a,b,c]})
        scalar(24,f'Triunghiul ABC este dreptunghic în A, AB={3*s}, AC={4*s}. H este proiecția lui A pe BC. Calculați AH.',Q(12*s,5),
               f'Notăm s={s}; ipotenuza este 5s. Teorema catetei dă BH=AB²/BC și HC=AC²/BC. Teorema înălțimii AH²=BH·HC dă aceeași valoare ca formula ariei AH=AB·AC/BC.',{'legs':[3*s,4*s]})
        scalar(25,f'Triunghiul ABC are AB={3*s}, AC={4*s}, BC={5*s}. Bisectoarea interioară AD taie BC în D. Calculați AD².',Q(288*s*s,49),
               'Teorema bisectoarei dă BD:DC=AB:AC=3:4, deci BD=3BC/7 și DC=4BC/7. Formula scalară a bisectoarei este AD²=AB·AC−BD·DC. Toate lungimile sunt pozitive, iar D este interior.',{'sides':[5*s,4*s,3*s]})
        origin=v(j,-j);quad=[origin+v(s,0),origin+v(6*s,0),origin+v(0,3*s),origin+v(0,2*s)]
        scalar(26,'Patrulaterul convex are '+', '.join(pt(n,p) for n,p in zip('ABCD',quad))+'. Perpendicularele prin mijloacele lui AB,BC,CD pe laturile opuse CD,DA,AB sunt concurente în P. Determinați P; explicația verifică și perpendiculara prin mijlocul DA pe BC.',origin,
               'Primele două ecuații de perpendicularitate determină P, iar a treia se verifică în coordonate. Suma ciclică a celor patru produse (P−mijlocul unei laturi)·(vectorul laturii opuse) este identic zero. Deci primele trei produse nule îl anulează pe al patrulea. În datele alese toate cele patru drepte sunt distincte și laturile sunt nenule.',{'quad':quad})

        # The cosine/sine section uses actual nondegenerate triangles.
        triples=[(3,4,5),(5,12,13),(8,15,17),(7,24,25),(20,21,29)]
        sides=list(map(S.Integer,triples[j-1]));ca,cb,ccos=cosines(*sides)
        cosine(1,'Laturile opuse unghiurilor A,B,C sunt '+tex(S.Tuple(*sides))+'. Determinați (cos A; cos B; cos C).',S.Tuple(ca,cb,ccos),
               'Aplicăm teorema cosinusului pentru fiecare unghi: cos A=(b²+c²−a²)/(2bc), apoi ciclic. Toți numitorii sunt pozitivi, iar triunghiul este nedegenerat.',{'sides':sides})
        ca,cb,ccos=cosines(a,b,c)
        cosine(2,f'În triunghiul cu a={a}, b={b}, c={c}, calculați b·cos C+c·cos B.',a,
               'Înlocuim cosinusurile prin expresiile din laturi. Termenii b²,c² se anulează în sumă și rămâne a. Aceasta este teorema proiecțiilor, inclusiv când o proiecție ar avea semn negativ.',{'sides':[a,b,c]})
        cosine(3,f'Pentru un triunghi cu a={a}, b={b}, c={c}, calculați ab·cos C+ac·cos B+bc·cos A.',(a*a+b*b+c*c)/2,
               'Fiecare termen se scrie ca semidiferență de pătrate: ab cos C=(a²+b²−c²)/2, și ciclic. Adunarea lasă jumătatea sumei celor trei pătrate.',{'sides':[a,b,c]})
        angles=[(30,60,90),(45,45,90),(30,45,105),(15,75,90),(60,60,60)][j-1]
        cosine(4,f'Triunghiul are unghiurile (A;B;C)={angles}° și raza circumcercului R={s}. Calculați a·sin(B−C)+b·sin(C−A)+c·sin(A−B), unde a,b,c sunt laturile opuse.',S.Integer(0),
               'Teorema sinusurilor dă a=2R sin A, și ciclic. Dezvoltând sinusurile diferențelor, cele șase produse se anulează în perechi. Identitatea este valabilă pentru orice triunghi, nu doar pentru valorile alese.',{'angles':list(angles),'radius':s})
        bang=[20,30,40,50,60][j-1]
        cosine(5,f'Într-un triunghi nedegenerat, B={bang}° și sin²B+sin²C=sin²A. Determinați A în grade.',S.Integer(90),
               'Din A+B+C=180° rezultă sin²B+sin²C−sin²A=2sin B sin C cos A. Pentru un triunghi nedegenerat, sin B și sin C sunt strict pozitive, deci cos A=0 și A=90°. Valoarea lui B lasă C=90°−B pozitiv.',{'B':bang})
        ob_a,ob_b=2*j+3,j+2
        cosine(6,f'Triunghiul are a={ob_a}, b=c={ob_b}. Calculați cos A și verificați natura unghiului A.',Q(2*ob_b**2-ob_a**2,2*ob_b**2),
               'Latura maximă a este mai mică decât b+c, deci triunghiul există. Totuși a²>b²+c². Teorema cosinusului dă un numărător negativ, deci cos A<0 și A este obtuz.',{'sides':[ob_a,ob_b,ob_b]})
        cosine(7,f'Pentru ce valori reale ale lui m numerele m, {j+2}, {j+4} sunt laturile unui triunghi nedegenerat?',S.Interval.open(2,2*j+6),
               'Trebuie |b−c|<m<b+c. Aceste inegalități stricte asigură simultan pozitivitatea lui m și toate cele trei inegalități ale triunghiului. Capetele ar da un triunghi degenerat și se exclud.',{'fixed_sides':[j+2,j+4]})
        bbv,ccv=S.Integer(j+1),S.Integer(j+2);aa_fixed=S.sqrt(bbv*bbv+ccv*ccv+bbv*ccv)
        cosine(8,'Un triunghi are a='+tex(aa_fixed)+f', b={bbv}, c={ccv}. Aflați A în grade.',S.Integer(120),
               'Formula cosinusului reduce raportul (b²+c²−a²)/(2bc) la −1/2, independent de scară. Deoarece A este un unghi interior în (0°,180°), singura valoare este 120°. Aceste laturi sunt compatibile cu un triunghi nedegenerat.',{'sides':[aa_fixed,bbv,ccv]})
        pa_sides=[S.sqrt(j+2),S.sqrt(j+4),S.sqrt(j+6)]
        cosine(9,'Un triunghi are a='+tex(pa_sides[0])+', b='+tex(pa_sides[1])+', c='+tex(pa_sides[2])+'. Calculați cot A+cot C−2cot B.',S.Integer(0),
               'Pătratele laturilor sunt în PA. Folosind cot A=(b²+c²−a²)/(4Δ), cu Δ aria pozitivă, combinația cerută are numărătorul 4b²−2a²−2c²=0. Rezultatul nu presupune că unghiurile sunt în PA.',{'sides':pa_sides})
        ratio_sides=[(1,1,S.sqrt(2)),(1,S.sqrt(3),2),(S.sqrt(3),1,2),(1,1,1),(1,S.sqrt(2),S.sqrt(3))][j-1]
        ratio_sides=list(map(S.sympify,ratio_sides))
        cosine(10,'Laturile unui triunghi satisfac a:b:c='+tex(S.Tuple(*ratio_sides))+'. Calculați cos A.',S.simplify(cosines(*ratio_sides)[0]),
               'Normalizăm scara comună a laturilor, care se anulează în formula cos A=(b²+c²−a²)/(2bc). Cosinusul rezultat determină unic unghiul interior A.',{'sides':ratio_sides})
        cosine(11,f'Un patrulater convex are toate cele patru laturi egale cu {s}, iar diagonalele sunt egale. Calculați pătratul unei diagonale.',S.Integer(2*s*s),
               'Patrulaterul cu toate laturile egale este romb. Într-un paralelogram, egalitatea diagonalelor impune perpendicularitatea laturilor alăturate, deci rombul este pătrat. Diagonala are pătratul 2s². Acesta este un caz explicit de rigiditate metrică, nu problema generală cu șase lungimi într-un interval.',{'side':s})
        reciprocal_a=S.sqrt(bbv*bbv-bbv*ccv+ccv*ccv)
        cosine(12,f'Un triunghi are b={bbv}, c={ccv} și 1/(a+b)+1/(a+c)=3/(a+b+c). Determinați A în grade.',S.Integer(60),
               'Numitorii sunt strict pozitivi. Înmulțirea și reducerea dau a²=b²−bc+c². Teorema cosinusului impune cos A=1/2, deci A=60°. Relația este compatibilă cu un triunghi nedegenerat pentru b,c>0.',{'sides':[reciprocal_a,bbv,ccv]})
        cosine(13,f'În triunghiul ABC, BC={6*s}, CA=AB={5*s}. D∈BC cu BD={2*s}, DC={4*s}. Calculați AD.',s*S.sqrt(17),
               'Teorema lui Stewart: b²·BD+c²·DC=a(AD²+BD·DC). Rezolvăm pentru AD² și luăm rădăcina pozitivă, deoarece AD este lungime. Configurația este nedegenerată, cu D interior.',{'sides':[6*s,5*s,5*s],'parts':[2*s,4*s]})
        cosine(14,f'În triunghiul ABC, AB={j+2}, AC={j+3}, BC={j+4}. Cevienele AM,AN sunt izogonale și interioare. Calculați (BM·BN)/(CM·CN).',Q((j+2)**2,(j+3)**2),
               'Relația lui Steiner dă produsul rapoartelor BM/CM și BN/CN egal cu AB²/AC². Se obține aplicând teorema sinusurilor în triunghiurile determinate de ceviene și folosind egalitatea unghiurilor izogonale. Toți numitorii sunt pozitivi.',{'sides':[j+4,j+3,j+2]})
        p,q,r,tt=j,j+1,j+2,j+3
        cosine(15,f'D∈BC, E∈CA, BD:DC={p}:{q}, CE:EA={r}:{tt}. Dreapta DE intersectează dreapta AB în F, în exteriorul segmentului AB. Aflați AF/BF (lungimi pozitive).',Q(q*tt,p*r),
               f'Notăm p={p}, q={q}, r={r}, s={tt}. Menelau, în rapoarte de lungimi pozitive cu un punct exterior, dă (BD/DC)(CE/EA)(AF/FB)=1. Rezultă AF/BF=qs/(pr). În datele alese q·s>p·r, deci intersecția F este dincolo de B și este finită.',{'ratios':[p,q,r,tt]})
        ang=[30,60,90,120,135][j-1];R=j+2
        cosine(16,f'Triunghiul ABC are raza circumcercului R={R} și A={ang}°. H este ortocentrul. Calculați lungimea AH.',S.simplify(2*R*S.Abs(S.cos(S.pi*ang/180))),
               'Relația metrică este AH=2R·|cos A|. Valoarea absolută este necesară și pentru unghi obtuz; dacă A=90°, ortocentrul coincide cu A și lungimea este zero.',{'radius':R,'angle':ang})
        cosine(17,f'În triunghiul ABC, AB={j+2}, AC={j+3}. D este interior lui BC. Pentru ce BD/DC se minimizează T=(BD·AC)/(DC·AB)+(DC·AB)/(BD·AC)?',Q(j+2,j+3),
               'Punem t=(BD·AC)/(DC·AB)>0. Inegalitatea t+1/t≥2 are egalitate numai la t=1. Prin urmare BD/DC=AB/AC, deci ceviana de minim este bisectoarea interioară. Raportul poate fi realizat de un punct interior unic.',{'AB':j+2,'AC':j+3})
        quad=[v(-s,0),v(0,-2*s),v(2*s,0),v(0,3*s)]
        cosine(18,'Patrulaterul convex are '+', '.join(pt(n,p) for n,p in zip('ABCD',quad))+'. Folosind cele patru distanțe AB,BC,CD,DA, calculați AC·BD și stabiliți dacă diagonalele sunt perpendiculare.',S.Integer(0),
               'Prin dezvoltare, 2AC·BD=AD²+BC²−AB²−CD². Înlocuirea distanțelor date produce zero. Diagonalele sunt nenule, deci produsul nul echivalează cu perpendicularitatea.',{'quad':quad})
        half_angle=[30,45,60,15,75][j-1];dist=j+1
        cosine(19,f'Un unghi are măsura {2*half_angle}°. Punctul A este pe bisectoarea interioară, OA={dist}. O transversală prin A taie laturile unghiului în M,N, cu OM,ON>0. Calculați invariantul 1/OM+1/ON.',S.simplify(2*S.cos(S.pi*half_angle/180)/dist),
               'Notăm θ jumătatea unghiului. În baza vectorilor unitari ai laturilor, A are ambii coeficienți OA/(2cos θ). Ecuația transversalei de interceptări M,N impune OA/(2cos θ)·(1/OM+1/ON)=1. Rezultatul este independent de transversala admisă; cos θ este pozitiv.',{'half_angle':half_angle,'distance':dist})
        cyclic=[v(s,0),v(Q(3*s,5),Q(4*s,5)),v(-s,0),v(0,-s)]
        AB,BC,CD,DA=[norm(cyclic[(i+1)%4]-cyclic[i]) for i in range(4)];AC=norm(cyclic[2]-cyclic[0])
        cosine(20,'În patrulaterul convex inscriptibil ABCD, AB='+tex(AB)+', BC='+tex(BC)+', CD='+tex(CD)+', DA='+tex(DA)+', AC='+tex(AC)+'. Calculați BD.',S.simplify(norm(cyclic[3]-cyclic[1])),
               'Teorema lui Ptolemeu dă AB·CD+AD·BC=AC·BD. Diagonala AC este pozitivă, deci împărțim pentru a afla BD. Lungimile provin dintr-un patrulater convex cu toate vârfurile pe același cerc, astfel ipoteza de inscriptibilitate este realizabilă.',{'cyclic':cyclic})

    assert len(questions)==230 and len({q['text'] for q in questions})==230
    return questions


def update_file():
    data=json.loads(TARGET.read_text(encoding='utf-8'))
    retained=[q for q in data['questions'] if q.get('practice_scope',{}).get('bank')!=BANK]
    data['questions']=retained+build_questions();data['difficulty']='hard'
    TARGET.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(f'G4 lesson1: 230 grids, {len(retained)} existing questions preserved.')


if __name__=='__main__':update_file()
