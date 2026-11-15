"""Original advanced G3 numeric/conclusion adaptations; called by main generator."""
import sympy as S

Q=S.Rational
SYMBOLS={name:S.Symbol(name,real=True) for name in ('x','y','z','t','a','b','c','k','n')}
ACTUAL={**SYMBOLS,'sin':S.sin,'cos':S.cos,'tan':S.tan,'cot':S.cot,'sqrt':S.sqrt,'Abs':S.Abs,'pi':S.pi}
DISPLAY={**SYMBOLS,**{name:S.Function(name) for name in ('sin','cos','tan','cot')},'sqrt':S.sqrt,'Abs':S.Abs,'pi':S.pi}
def exact(value):return S.sympify(value,locals=ACTUAL)
def tex(value):return r'\('+S.latex(value)+r'\)'
def expression_tex(formula):return S.latex(S.sympify(formula,locals=DISPLAY,evaluate=False))


def populate(B):
    def aggregate(section,typ,j,kind,term,lower,upper,givens,reason,partial=False):
        expr=exact(term);terms=[]
        for index in range(lower,upper+1):
            substitutions={SYMBOLS[name]:exact(value) for name,value in givens.items()}
            substitutions[SYMBOLS['k']]=S.Integer(index)
            value=S.simplify(expr.subs(substitutions))
            assert not value.has(S.zoo,S.nan,S.oo,-S.oo),(section,typ,j,index)
            terms.append(value)
        result=S.simplify(S.trigsimp(S.prod(terms) if kind=='product' else sum(terms)))
        shown=expression_tex(term);operator=r'\prod' if kind=='product' else r'\sum'
        formula=operator+'_{k='+str(lower)+'}^{'+str(upper)+'}'+r'\left('+shown+r'\right)'
        text='Toate argumentele sunt în radiani. Date: '+', '.join(name+'='+tex(exact(value)) for name,value in givens.items())+'. Calculați '+r'\('+formula+r'\).'
        B.emit(section,typ,j,text,result,reason,{'operation':'finite_'+kind,'term':term,'term_latex':shown,'index':'k','lower':lower,'upper':upper,'givens':givens},partial)

    for j in range(1,6):
        angle=[S.pi/12,S.pi/8,S.pi/6,S.pi/3,5*S.pi/12][j-1]
        def calc(section,typ,formula,givens,reason,context='Argumentele sunt în radiani.',partial=True):
            B.calc(section,typ,j,context,formula,givens,reason,partial)
        pairs=[(S.pi/4,S.pi/6),(S.pi/3,S.pi/4),(S.pi/4,S.pi/3),(5*S.pi/12,S.pi/6),(S.pi/6,S.pi/4)]
        first,second=pairs[j-1]
        calc('5',1,'sin(x-y)',{'x':first,'y':second},'Formula sinusului diferenței este sin x cos y−cos x sin y. Folosim valori remarcabile ale unghiurilor date și păstrăm semnul diferenței. Acesta este un calcul exact, fără aproximări.',partial=False)
        calc('5',2,'cos(pi/4-x)+sin(pi/4-x)',{'x':angle},'Dezvoltăm cele două funcții ale diferenței. Termenii cu sin x se anulează, iar expresia devine √2 cos x.')
        p,q,h=[(3,4,5),(5,12,13),(8,15,17),(7,24,25),(20,21,29)][j-1]
        sx=Q(p,h);cy=-Q(q,h);cx=Q(q,h);sy=Q(p,h)
        B.emit('5',3,j,'Se cunosc sin x='+tex(sx)+' și cos y='+tex(cy)+', cu x în cadranul I și y în cadranul II. Calculați sin(x+y). Argumentele sunt în radiani.',S.simplify(sx*cy+cx*sy),
            'Relația fundamentală și cadranele dau cos x>0 și sin y>0. Apoi sin(x+y)=sin x cos y+cos x sin y. Semnul cos y este negativ și nu poate fi înlocuit cu rădăcina pozitivă.',{'operation':'angle_sum_from_values','sine_x':sx,'cosine_y':cy,'quadrant_x':1,'quadrant_y':2,'requested':'sin_sum'},True)
        calc('5',4,'cos(x/2)',{'x':[S.pi/4,S.pi/2,3*S.pi/4,S.pi,3*S.pi/2][j-1]},'Folosim cos²(x/2)=(1+cos x)/2. Semnul lui cos(x/2) se alege după intervalul lui x/2; pentru x=3π/2 jumătatea este în cadranul II și cosinusul este negativ.',partial=False)
        calc('5',5,'sin(x)+sin(x+2*pi/3)+sin(x+4*pi/3)',{'x':Q(j,7)},'Dezvoltăm termenii decalați. Coeficientul lui sin x este 1+cos(2π/3)+cos(4π/3)=0, iar coeficientul lui cos x este sin(2π/3)+sin(4π/3)=0. Suma este identic zero.')
        xx,yy=S.pi/6,Q(j,12)*S.pi
        sin_sum=S.simplify(S.sin(xx)+S.sin(yy));cos_sum=S.simplify(S.cos(xx)+S.cos(yy))
        B.emit('5',6,j,'Două unghiuri reale satisfac sin x+sin y='+tex(sin_sum)+' și cos x+cos y='+tex(cos_sum)+'. Calculați cos(x−y).',S.simplify((sin_sum**2+cos_sum**2-2)/2),
            'Adunăm pătratele celor două sume. Relațiile fundamentale pentru x și y dau 2+2(sin x sin y+cos x cos y)=2+2cos(x−y). Izolăm cosinusul diferenței; nu este nevoie să recuperăm separat unghiurile.',{'operation':'difference_from_sums','sine_sum':sin_sum,'cosine_sum':cos_sum},True)
        calc('5',7,'sin(x+a)+sin(x-a)',{'x':Q(j,12)*S.pi,'a':5*S.pi/12},'Formula sumă–produs sau dezvoltarea adunării reduce expresia la 2sin x cos a. Unghiul fix este precizat și toate funcțiile există.')
        calc('5',8,'cos(x+y)*cos(x-y)',{'x':Q(j,12)*S.pi,'y':S.pi/6},'Prin formulele de adunare, produsul este cos²x cos²y−sin²x sin²y=cos²x−sin²y. Nu se impun condiții suplimentare de numitor.')
        calc('5',9,'sin(2*x)',{'x':Q(j,12)*S.pi},'Adunarea cu argumente egale dă sin2x=2sin x cos x. Înlocuim valorile exacte ale unghiului din această variantă.')
        calc('5',10,'2*tan(x)/(1-tan(x)**2)',{'x':angle},'Tangenta unghiului dublu este 2tan x/(1−tan²x). Se verifică atât cos x≠0, cât și 1−tan²x≠0 în datele acestei variante; nu sunt admise argumente la care tan2x nu există.')
        calc('5',11,'sin(2*x)/(1+cos(2*x))',{'x':angle},'Din sin2x=2sin x cos x și 1+cos2x=2cos²x rezultă tan x. Numitorul cere cos x≠0; datele satisfac această restricție.')
        quadrant=[1,2,3,4,3][j-1];cosine=Q(q,h)*(1 if quadrant in (1,4) else -1)
        half_sine=S.sqrt((1-cosine)/2);half_cosine=S.sqrt((1+cosine)/2)*(1 if quadrant in (1,2) else -1)
        B.emit('5',12,j,'Se cunoaște cos x='+tex(cosine)+f', cu x în cadranul {quadrant} și 0<x<2π. Determinați (sin(x/2);cos(x/2)).',S.Tuple(half_sine,half_cosine),
            'Formulele de înjumătățire dau pătratele celor două valori. Din 0<x<2π rezultă sin(x/2)>0; cos(x/2) este pozitiv pentru x<π și negativ pentru x>π. Aceste condiții aleg ramurile corecte ale radicalilor.',{'operation':'half_angle_from_cos','cosine':cosine,'quadrant':quadrant},True)
        calc('5',13,'sin(3*x)',{'x':angle},'Scriem 3x=2x+x și aplicăm formulele de adunare și dublare. După sin²x+cos²x=1 rezultă sin3x=3sin x−4sin³x.')
        calc('5',14,'cos(4*x)',{'x':angle},'Aplicăm de două ori formula cos2u=2cos²u−1, obținând cos4x=8cos⁴x−8cos²x+1.')
        ta,tb=Q(j,j+1),Q(1,j+2)
        result=S.simplify((2*ta+tb*(1-ta**2))/(1-ta**2-2*ta*tb))
        B.emit('5',15,j,'Unghiurile x,y sunt ascuțite, cu tan x='+tex(ta)+' și tan y='+tex(tb)+'. Calculați tan(2x+y).',result,
            'Mai întâi tan2x=2a/(1−a²), apoi tan(2x+y)=(tan2x+b)/(1−b tan2x). Echivalent, rezultatul este [2a+b(1−a²)]/[1−a²−2ab]. Ambele formule au numitori nenuli pentru valorile date.',{'operation':'double_sum_from_tangents','tangent_x':ta,'tangent_y':tb},True)
        calc('5',16,'tan(x)+2*tan(2*x)',{'x':angle},'Relația cot u−2cot2u=tan u, aplicată pentru u=x și u=2x, produce tan x+2tan2x=cot x−4cot4x. În această variantă toate tangentele/cotangentele folosite sunt definite.')
        sines=[Q(p,h),Q(p,h),-Q(p,h)];quads=[1,2,4]
        cosines=[Q(q,h),-Q(q,h),Q(q,h)]
        result=S.simplify(sines[0]*cosines[1]*cosines[2]+cosines[0]*sines[1]*cosines[2]+cosines[0]*cosines[1]*sines[2]-sines[0]*sines[1]*sines[2])
        B.emit('5',17,j,'Se cunosc (sin x;sin y;sin z)='+tex(S.Tuple(*sines))+', iar x,y,z sunt în cadranele I,II,IV, în această ordine. Calculați sin(x+y+z).',result,
            'Recuperăm cosinușii din relația fundamentală, cu semnele +,−,+ impuse de cadrane. Aplicăm adunarea de două ori: sin(x+y+z)=sin x cos y cos z+cos x sin y cos z+cos x cos y sin z−sin x sin y sin z.',{'operation':'three_angle_sum','sines':sines,'quadrants':quads,'requested':'sin_sum'},True)
        calc('5',18,'(sin(x)*cos(x)+cos(x)*sin(x))/(cos(x)**2-sin(x)**2)',{'x':angle},'Numărătorul este sin2x, iar numitorul cos2x. Raportul este tan2x; pentru valorile date cos2x≠0, deci fracția inițială este definită.')
        calc('5',19,'cos(x-x**2)*cos(x**2)-sin(x-x**2)*sin(x**2)-cos(x)',{'x':Q(j,4)},'Tratăm u=x−x² și v=x² ca două argumente reale. Primele două produse sunt cos(u+v)=cos x; scăderea lui cos x dă zero pentru orice x.',partial=True)
        aggregate('5',20,j,'product','cos(2**k*x)',0,j,{'x':S.pi/3},'Dublările succesive dau sin(2ⁿx)=2ⁿsin x·∏cos(2ᵏx), pentru n numărul de factori. Aici sin x≠0 și niciun pas nu împarte la un sinus nul; evaluarea directă confirmă produsul.',True)
        xx=[S.pi/3,S.pi/2,2*S.pi/3,3*S.pi/2,5*S.pi/3][j-1]
        aggregate('5',21,j,'product','(1+cos(x/2**k))*sin(x/2**(k+1))/sin(x/2**k)',0,1,{'x':xx},'Folosind 1+cos u=2cos²(u/2) și sin u=2sin(u/2)cos(u/2), fiecare factor devine cos(u/2). Sinusurile din numitorii inițiali sunt nenule în această variantă. Produsul rămas se calculează exact; este un produs finit explicit cu argumente înjumătățite.',True)

        xx,yy=Q(j+1,24)*S.pi,S.pi/2-Q(j+1,24)*S.pi
        calc('6',1,'cos(x)*cos(y)',{'x':xx,'y':yy},'Produs–sumă dă cos x cos y=[cos(x+y)+cos(x−y)]/2. Aici x+y=π/2, deci primul termen este zero, iar al doilea se evaluează exact.',partial=False)
        calc('6',2,'sin(a*x)-sin(b*x)',{'a':2*j+3,'b':2*j+1,'x':S.pi/6},'Formula diferenței de sinusuri este 2cos((a+b)x/2)sin((a−b)x/2). Ea păstrează ordinea diferenței și semnul rezultatului.')
        calc('6',3,'cos(a*x)+cos(b*x)',{'a':2*j+1,'b':2*j-1,'x':S.pi/6},'Suma de cosinusuri este 2cos((a+b)x/2)cos((a−b)x/2). Folosim semisuma și semidiferența argumentelor.')
        calc('6',4,'cos(x-y)+cos(x)+cos(x+y)',{'x':Q(j,12)*S.pi,'y':S.pi/6},'Împerechem termenii extremi, care dau 2cos x cos y. Extragem termenul median cos x și obținem cos x(1+2cos y).')
        calc('6',5,'sin(x)+cos(x)',{'x':Q(j,12)*S.pi},'Înlocuim cos x cu sin(π/2−x), apoi aplicăm sumă–produs. Echivalent, sin x+cos x=√2sin(x+π/4).')
        calc('6',6,'(sin(5*x)-sin(3*x))/(cos(5*x)-cos(3*x))',{'x':angle},'Numărătorul este 2cos4x sin x, iar numitorul −2sin4x sin x. Fracția este −cot4x numai pe domeniul inițial sin x·sin4x≠0, verificat pentru datele variantei.')
        calc('6',7,'sin(x)+sin(3*x)+sin(5*x)+sin(7*x)',{'x':Q(j,12)*S.pi},'Grupăm primul cu ultimul și cei doi termeni mediani: 2sin4x(cos3x+cos x)=4sin4x cos2x cos x.')
        calc('6',8,'sin(x)+sin(y)-sin(x+y)',{'x':Q(j,12)*S.pi,'y':S.pi/6},'Aplicarea succesivă sumă–produs și unghi dublu dă 4sin(x/2)sin(y/2)sin((x+y)/2). Identitatea este valabilă pentru toate argumentele reale.')
        calc('6',9,'(sin(x)+sin(y))**2+(cos(x)+cos(y))**2',{'x':Q(j,12)*S.pi,'y':S.pi/4},'Dezvoltarea pătratelor și relațiile fundamentale dau 2+2(sin x sin y+cos x cos y)=2+2cos(x−y).')
        xx=[S.pi/12,S.pi/8,S.pi/4,S.pi/3,5*S.pi/12][j-1]
        calc('6',10,'tan(3*x)-tan(x)',{'x':xx},'Punem la numitor comun cos3x cos x, nenul în această variantă. Numărătorul sin3x cos x−cos3x sin x este sin2x.')
        calc('6',11,'(cos(3*x)**2-cos(x)**2)/(sin(3*x)**2-sin(x)**2)',{'x':angle},'Din cos²u=1−sin²u, numărătorul este opusul numitorului. Numitorul se verifică nenul pentru unghiul dat, deci raportul este −1; punctele excluse nu sunt adăugate prin simplificare.')
        calc('6',12,'sin(x)+sin(y)+sin(z)-sin(x+y+z)',{'x':Q(j,12)*S.pi,'y':S.pi/6,'z':S.pi/4},'Grupările sumă–produs dau 4sin((x+y)/2)sin((y+z)/2)sin((z+x)/2). Varianta cere o valoare explicită a identității, nu doar numele formulei.')
        calc('6',13,'sin(x)*cos(2*x)*cos(4*x)',{'x':angle},'Înmulțind cu cos x și dublând sinusul de trei ori, obținem sin8x/(8cos x). Împărțirea este legitimă deoarece cos x≠0 în datele variantei; se poate verifica și direct prin produs–sumă.')
        xx=S.pi/6;yy=[S.pi/6,S.pi/4,S.pi/3,S.pi/2,2*S.pi/3][j-1];zz=S.pi-xx-yy
        calc('6',14,'sin(2*x)+sin(2*y)+sin(2*z)',{'x':xx,'y':yy,'z':zz},'Unghiurile sunt strict pozitive și au suma π. Înlocuim z=π−x−y și aplicăm sumă–produs, obținând 4sin x sin y sin z. Restricția de triunghi este verificată.',context='x,y,z sunt unghiurile unui triunghi, în radiani.')
        xx,yy=S.pi/6,Q(j,12)*S.pi;ss=S.simplify(S.sin(xx)+S.sin(yy));cs=S.simplify(S.cos(xx)+S.cos(yy))
        B.emit('6',15,j,'Unghiurile x,y sunt în (0;π/2), cu sin x+sin y='+tex(ss)+' și cos x+cos y='+tex(cs)+'. Aflați tan((x+y)/2).',S.simplify(ss/cs),
            'Sumele se factorizează ca 2sin((x+y)/2)cos((x−y)/2), respectiv 2cos((x+y)/2)cos((x−y)/2). Ambele cosinusuri comune sau din numitor sunt strict pozitive pentru x,y ascuțite. Raportul sumelor dă tangenta semisumei.',{'operation':'half_sum_from_sums','sine_sum':ss,'cosine_sum':cs},True)
        xx,yy=S.pi/3,Q(j,12)*S.pi
        calc('6',16,'sin(x)-sin(y)+sin(z)',{'x':xx,'y':yy,'z':xx+yy},'Datele satisfac z=x+y. Sumă–produs transformă expresia în 4sin(x/2)cos(y/2)cos((x+y)/2).',context='Argumentele reale x,y,z sunt în radiani și satisfac z=x+y.')
        calc('6',17,'cos(x)**3+cos(x+2*pi/3)**3+cos(x+4*pi/3)**3',{'x':Q(j,12)*S.pi},'Din cos³u=(cos3u+3cos u)/4, suma termenilor liniari decalați este zero, iar cele trei cosinusuri triple sunt egale cu cos3x. Rezultă 3cos3x/4.')

        aggregate('7',1,j,'sum','1/(sin(k*x)*sin((k+1)*x))',1,j,{'x':S.pi/12},'Identitatea cot(kx)−cot((k+1)x)=sin x/[sin(kx)sin((k+1)x)] produce o sumă telescopică. Sinusurile numitorilor sunt strict pozitive deoarece argumentele sunt între 0 și π. Suma se reduce la [cot x−cot((n+1)x)]/sin x.',True)
        aggregate('7',2,j,'product','cos(x/2**k)',1,2,{'x':[S.pi/3,S.pi/2,2*S.pi/3,3*S.pi/2,5*S.pi/3][j-1]},'Aplicând de două ori sin2u=2sin u cos u, produsul este sin x/[4sin(x/4)]. Numitorul este nenul în datele variantei. Semnele cosinusurilor nu sunt schimbate prin alegerea nejustificată a radicalului pozitiv.',True)
        aggregate('7',3,j,'product','cos(2**k*x)',0,j,{'x':2*S.pi/3},'Produsul cu n factori este sin(2ⁿx)/(2ⁿsin x), prin dublări succesive. Aici sin x≠0, iar evaluarea directă a cosinusurilor confirmă semnul produsului.',True)
        aggregate('7',4,j,'sum','2**k*tan(2**k*x)',0,j,{'x':S.pi/3},'Folosim tan u=cot u−2cot2u și înmulțim cu 2ᵏ. Termenii interiori se anulează și rămâne cot x−2ⁿcot(2ⁿx), cu n numărul de termeni. Toate funcțiile sunt definite pentru x=π/3.',True)
        finite_step=2*S.pi if j==5 else S.pi/6
        aggregate('7',5,j,'sum','sin(k*x)',1,j+1,{'x':finite_step},
            ('Aici x=2π, deci fiecare termen sin(kx)=sin(2kπ)=0. Suma directă este definită și egală cu 0. Formula cu numitorul sin(x/2) ar produce 0/0 și nu poate fi aplicată acestui caz; nu se exclude suma originală.' if j==5 else 'Înmulțirea cu 2sin(x/2), nenul aici, transformă suma într-o diferență telescopică de cosinusuri. Formula este sin(nx/2)sin((n+1)x/2)/sin(x/2).'),True)
        aggregate('7',6,j,'sum','cos(k*x)',1,j+1,{'x':finite_step},
            ('Aici x=2π, deci fiecare termen cos(kx)=cos(2kπ)=1. Suma directă este numărul termenilor, adică 6. Formula cu numitorul sin(x/2) nu se aplică deoarece ar împărți la zero, deși suma originală este perfect definită.' if j==5 else 'Înmulțirea cu 2sin(x/2) și produs–sumă telescopic dau sin(nx/2)cos((n+1)x/2)/sin(x/2). Numitorul nu se anulează în varianta dată.'),True)
        aggregate('7',7,j,'sum','sin((2*k-1)*x)',1,j+1,{'x':S.pi/6},'Argumentele impare sunt în PA cu pasul 2x. Suma este sin²(nx)/sin x când sin x≠0; în varianta dată sin x=1/2. Formula sau adunarea directă dau aceeași valoare.',True)
        aggregate('7',8,j,'sum','sin(k*x)**2',1,j+1,{'x':S.pi/6},'Reducem puterea: sin²(kx)=(1−cos2kx)/2. Suma devine n/2 minus jumătate dintr-o sumă de cosinusuri în PA, care se evaluează prin formula finită sau direct.',True)
        aggregate('7',9,j,'sum','k*sin(2*k*x)',1,j+1,{'x':S.pi/6},'Este o sumă finită ponderată. O metodă generală scade sume decalate după înmulțire cu 2sin x; pentru datele variantei evaluăm exact fiecare sin(2kx), apoi aplicăm ponderea k. Nu se pretinde formula generală olimpică.',True)
        aggregate('7',10,j,'product','2*cos(2**k*x)+1',0,1,{'x':[S.pi/6,S.pi/4,S.pi/3,S.pi/2,2*S.pi/3][j-1]},'Fiecare factor poate fi scris 2cos u+1=sin(3u/2)/sin(u/2), cu sinusurile numitorilor nenule în varianta dată. Produsul explicit are doi factori; factori nuli rămân permiși și dau produsul zero.',True)
        xx,yy=S.pi/6,S.pi/3;zz=[S.pi/6,S.pi/4,S.pi/3,S.pi/2,2*S.pi/3][j-1];tt=2*S.pi-xx-yy-zz
        calc('7',11,'sin(x)+sin(y)+sin(z)+sin(t)',{'x':xx,'y':yy,'z':zz,'t':tt},'Deoarece t=2π−x−y−z, sin t=−sin(x+y+z). Factorizarea în trei variabile dă 4sin((x+y)/2)sin((y+z)/2)sin((z+x)/2). Toate argumentele sunt explicit date și au suma 2π.',context='Cele patru argumente sunt în radiani și au suma 2π.')
