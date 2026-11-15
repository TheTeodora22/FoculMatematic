"""185 original G2 grids for position vectors and centroids only.

No database writes. Existing questions outside this bank are preserved.
"""
import json
from pathlib import Path

import sympy as S

ROOT=Path(__file__).resolve().parents[1]
BANK='g2_pozitie_centre_v1'
FILES={lesson:next((ROOT/'clasa_9').glob(f'clasa_9_u06_l{lesson:02d}_*.json')) for lesson in (1,3)}
Q=S.Rational
NAMES={1:[
 'Vectorul de poziție din coordonate','Identități afine cu mijloace','Identități cu puncte de împărțire',
 'Vectorul dintre mijloacele diagonalelor','Raportul determinat de intersecția cevienelor',
 'Patrulater din puncte omoloage ponderate','Coliniaritate în baza laturilor','Mijloace coliniare într-un patrulater',
 'Parametru pentru coliniaritate într-o figură regulată','Rapoarte naturale și paralelism',
 'Relații metrice din paralele','Punct interior și trei ceviene','Paralelogram din egalități de rapoarte',
 'Paralelism propagat într-o configurație','Loc geometric cu direcție fixă','Loc geometric prin sumă vectorială',
 'Intersecție de ceviene cu calcul de lungime'],2:[
 'Caracterizarea centrului de greutate prin raport','Vectori către simetricul centrului de greutate',
 'Centru de greutate într-o configurație de mijloace','Segmentul dintre două centre de greutate',
 'Patrulaterul centrelor de greutate','Coliniaritate cu centrul de greutate și paralele',
 'Același centru pentru triunghiul median și inițial','Triunghiuri alternate într-un hexagon',
 'Vector între centrele a două triunghiuri','Reducerea unei sume de trei vectori','Criteriu pentru centru comun',
 'Dreaptă care conține centrul de greutate','Triunghiuri echilaterale construite pe laturi',
 'Baricentru al unui patrulater derivat','Lungimi între vârfuri omoloage','Centru de greutate pe diagonală',
 'Coordonatele centrului de greutate','Centru pe mediană și centru comun cu puncte pe laturi',
 'Concurență a dreptelor prin centre derivate','Simetrice față de mijloace și centru comun']}
PARTIAL={(1,6),(1,9),(1,11),(1,12),(1,13),(1,14),(2,3),(2,5),(2,6),(2,15),(2,16)}


def v(*xy):return S.ImmutableMatrix(xy)
def pair(point):return S.Tuple(*point)
def tex(value):return r'\('+S.latex(S.sympify(value))+r'\)'
def pt(name,point):return name+tex(pair(point))
def average(*points):return sum(points,S.zeros(2,1))/len(points)
def serial(value):
    if isinstance(value,S.MatrixBase):return [str(c) for c in value]
    if isinstance(value,dict):return {k:serial(v) for k,v in value.items()}
    if isinstance(value,(tuple,list)):return [serial(v) for v in value]
    if isinstance(value,S.Basic):return str(value)
    return value


def build_banks():
    banks={1:[],3:[]}
    def emit(section,typ,j,text,answer,reason,givens):
        lesson=1 if section==1 else 3
        answer=pair(answer) if isinstance(answer,S.MatrixBase) else S.sympify(answer)
        values=[answer]
        for offset in (1,-1,2):
            values.append(S.Tuple(answer[0]+offset,*answer[1:]) if isinstance(answer,S.Tuple) else answer+offset)
        correct=len(banks[lesson])%4
        values.insert(correct,values.pop(0))
        assert len(set(values))==4
        binding_names={'p':'p','q':'q','lambda':'λ','mu':'μ','alpha':'α','nu':'ν'}
        bindings=[name+'='+tex(givens[key]) for key,name in binding_names.items() if key in givens]
        if bindings:reason='În explicație notăm '+', '.join(bindings)+'. '+reason
        banks[lesson].append({
            'text':text,'type':'multiple_choice','format':'grid','points':10,
            'explanation':reason+' Rezultatul cerut este '+tex(answer)+'.',
            'options':[{'text':tex(value),'is_correct':i==correct} for i,value in enumerate(values)],
            'practice_scope':{'bank':BANK,'catalog':'G2','section':section,'type':typ,
                'type_name':NAMES[section][typ-1],'variant':j,'pages':'185–191' if section==1 else '191–194',
                'coverage':'partial_case' if (section,typ) in PARTIAL else 'adapted_grid',
                'adaptation':'Caz original explicit. Demonstrația/construcția este adaptată în calcul sau concluzie, cu justificare în explicație.'},
            'verification':{**serial(givens),'option_values':[str(value) for value in values]},
        })

    for j in range(1,6):
        aa,bb,cc,dd=v(j,-j),v(7*j,-j),v(j,5*j),v(8*j,4*j)
        pts={'A':aa,'B':bb,'C':cc,'D':dd}
        desc=', '.join(pt(name,p) for name,p in zip('ABC',(aa,bb,cc)))
        def position(typ,text,answer,reason,givens=None):emit(1,typ,j,text,answer,reason,givens or pts)
        def centre(typ,text,answer,reason,givens=None):emit(2,typ,j,text,answer,reason,givens or pts)
        position(1,pt('A',aa)+'. O este originea reperului. Determinați coordonatele vectorului OA.',aa,
                 'Vectorul de poziție are coordonatele punctului atunci când originea este O=(0;0). În baza canonică, OA=xA·i+yA·j.')
        position(2,'În triunghiul cu '+desc+', M,N,P sunt mijloacele lui BC,CA,AB. Calculați OM+ON+OP, față de originea reperului.',aa+bb+cc,
                 'Fiecare mijloc are poziția egală cu semisuma pozițiilor extremităților. Adunând, fiecare vârf apare de două ori cu coeficient 1/2, deci OM+ON+OP=OA+OB+OC.')
        p,q=j+1,j+2
        divided=(q*bb+p*cc)/(p+q)
        position(3,'Punctele considerate sunt '+desc+f'. M∈BC, BM:MC={p}:{q}. Determinați OM față de originea reperului.',divided,
                 'Formula de împărțire internă este OM=(q·OB+p·OC)/(p+q). Ponderile extremităților sunt inverse raportului BM:MC. Suma coeficienților este 1, deci schimbarea originii păstrează identitatea afină.',{**pts,'p':p,'q':q})
        position(4,'Pentru '+desc+', '+pt('D',dd)+', M este mijlocul lui AC, N al lui BD. Determinați vectorul MN.',(bb+dd-aa-cc)/2,
                 'MN=ON−OM=(OB+OD−OA−OC)/2=(AB+CD)/2. Această relație nu cere ca patrulaterul să fie paralelogram.')
        position(5,f'Într-un triunghi necoliniar ABC, D∈BC cu BD:DC={p}:{q}, iar M este mijlocul lui AB. Cevienele AD și CM se intersectează în P. Aflați AP/PD.',Q(p+q,q),
                 'Luăm A ca origine și baza independentă (AB,AC). D are coeficienții (q/(p+q),p/(p+q)). Scriind P=tD=C+s(M−C), obținem t=(p+q)/(p+2q), cu 0<t<1. Raportul AP/PD este t/(1−t)=(p+q)/q.',{'p':p,'q':q})
        a2=2*aa+v(j,2*j);b2=2*bb+v(j,2*j);d1=aa+cc-bb;d2=2*d1+v(j,2*j)
        lam=Q(j,j+1)
        position(6,'ABCD și A′B′C′D′ sunt paralelograme, cu '+pt('A',aa)+', '+pt('B',bb)+', '+pt('D',d1)+', '+pt('A′',a2)+', '+pt('B′',b2)+', '+pt('D′',d2)+'. P,Q,R,S împart AA′,BB′,CC′,DD′ la același coeficient '+tex(lam)+' de la prima extremitate. Calculați PQ.',(1-lam)*(bb-aa)+lam*(b2-a2),
                 'PQ=(1−λ)AB+λA′B′, iar SR are aceeași expresie. Analog QR=PS. În configurația dată, al doilea paralelogram este imaginea primului printr-o omotetie de raport 2 și o translație; figura interpolată are raportul 1+λ>0, deci nu degenerează.',{'A':aa,'B':bb,'D':d1,'A2':a2,'B2':b2,'D2':d2,'lambda':lam})
        pp,qq=j+2,j+3
        position(7,f'În baza necoliniară u=AB, v=AC, M=A+{pp}u, N=A+{qq}v și P=A+αu+({Q(qq,2)})v. Pentru ce α sunt M,N,P coliniare?',Q(pp,2),
                 'Dreapta MN are ecuația afină α/p+β/q=1 în baza (u,v). Cum β=q/2, rezultă α=p/2. Astfel P este chiar mijlocul segmentului MN, deci este distinct de M și N.',{'p':pp,'q':qq,'beta':Q(qq,2)})
        position(8,'Pentru '+desc+', '+pt('D',dd)+', M,N sunt mijloacele lui AD,BC. E,F,H sunt mijloacele lui AB,MN,CD. Aflați F și precizați prin explicație de ce E,F,H sunt coliniare.',average(aa,bb,cc,dd),
                 'E=(A+B)/2 și H=(C+D)/2. F=(M+N)/2=(A+B+C+D)/4=(E+H)/2. Așadar F este mijlocul lui EH; pentru coordonatele date E≠H, deci cele trei puncte distincte sunt coliniare.')
        lam=Q(j,j+1)
        position(9,'În pătratul ABCD, M∈AC și N∈DC au AM=t·AC și DN='+tex(lam)+'·DC. Determinați t astfel încât B,M,N să fie coliniare.',1/(2-lam),
                 'În baza (AB,AD) normalizată, B=(1,0), M=(t,t), N=(λ,1). Determinantul vectorilor BM,BN este t(2−λ)−1. Anularea sa dă t=1/(2−λ), care este strict între 0 și 1 în datele problemei.',{'lambda':lam})
        position(10,f'D∈AB și E∈AC într-un triunghi necoliniar. AD/AB=m/{j+1}, AE/AC=n/{2*j+2}. Dacă DE∥BC, m,n sunt naturale pozitive și m+n={3*j}, determinați (m;n).',S.Tuple(j,2*j),
                 'Reciproca și teorema lui Thales impun egalitatea rapoartelor, deci n=2m. Combinarea cu suma prescrisă dă o singură pereche de naturale pozitive. Raportul comun '+tex(Q(j,j+1))+' este strict între 0 și 1, deci punctele sunt interioare.',{'denominators':[j+1,2*j+2],'sum':3*j})
        position(11,f'M∈BC, BM:MC={p}:{q}. Paralela prin M la AB taie AC în P, iar paralela la AC taie AB în Q. Calculați AP/AC.',Q(p,p+q),
                 'Cu A origine și B=(1,0), C=(0,1), M=(q/(p+q),p/(p+q)). Paralelele dau P=(0,p/(p+q)) și Q=(q/(p+q),0). De aici AP/AC=p/(p+q), AQ/AB=q/(p+q), iar suma rapoartelor este 1.',{'p':p,'q':q})
        weights=[j,j+1,j+2];total=sum(weights)
        ratios=S.Tuple(*[Q(total-w,w) for w in weights])
        position(12,'Punctul interior M are coordonatele baricentrice normalizate '+tex(S.Tuple(*(Q(w,total) for w in weights)))+' față de A,B,C. D,E,F sunt intersecțiile AM,BM,CM cu BC,CA,AB. Aflați (MA/MD; MB/ME; MC/MF).',ratios,
                 'Dacă α,β,γ>0 și α+β+γ=1, atunci pe ceviana AD avem MD/AD=α, MA/AD=1−α. Prin urmare MA/MD=(1−α)/α; analog pentru celelalte două. Se obține și identitatea sumei reciprocelor 1/(1+MA/MD)+1/(1+MB/ME)+1/(1+MC/MF)=1.',{'weights':weights})
        lam,mu=Q(j,j+1),Q(1,j+2)
        dpar=aa+cc-bb
        position(13,'În paralelogramul ABCD cu '+desc+', E∈AB, F∈BC, G∈CD, H∈DA au AE/AB=CG/CD='+tex(lam)+' și BF/BC=DH/DA='+tex(mu)+'. Calculați EF.',(1-lam)*(bb-aa)+mu*(cc-bb),
                 'E=A+λAB și F=B+μBC, de unde EF=(1−λ)AB+μBC. Din rapoartele egale pe laturile opuse rezultă E+G=A+C și F+H=B+D. Deoarece A+C=B+D, diagonalele EG,FH au același mijloc, deci EFGH este paralelogram. Coeficienții sunt interiori, astfel figura nu degenerează.',{**pts,'lambda':lam,'mu':mu})
        lam,mu=Q(j,j+1),Q(1,j+2)
        position(14,'În triunghiul ABC, AD/AB=AE/AC='+tex(lam)+', D∈AB, E∈AC. F∈AD, G∈AE și AF/AD=AG/AE='+tex(mu)+'. Aflați raportul FG/BC.',lam*mu,
                 'Prima aplicare a teoremei lui Thales dă DE∥BC și DE/BC=λ. A doua, în triunghiul ADE, dă FG∥DE și FG/DE=μ. Înmulțirea rapoartelor dă FG/BC=λμ; toate rapoartele sunt pozitive.',{'lambda':lam,'mu':mu})
        direction=v(j+1,2*j-1)
        slope=direction[1]/direction[0];intercept=aa[1]-slope*aa[0]
        position(15,pt('A',aa)+' și vectorul nenul v='+tex(pair(direction))+'. M parcurge toate punctele cu AM=t·v, t∈ℝ. Scrieți dreapta locului geometric ca y=mx+n și determinați (m;n).',S.Tuple(slope,intercept),
                 'Coordonatele parametrice sunt x=xA+t·vx, y=yA+t·vy. Deoarece vx≠0, eliminăm t și obținem panta vy/vx și interceptul yA−(vy/vx)xA. Orice punct al dreptei corespunde unui t real.',{'A':aa,'direction':direction})
        radius=j-1;center=aa+bb-cc
        position(16,'Punctele fixe sunt '+desc+'. Locul punctelor M care verifică |MA+MB−MC|='+str(radius)+' este descris de (h;k;R), unde (h;k) este centrul și R raza; R=0 înseamnă un singur punct. Aflați (h;k;R).',S.Tuple(*center,radius),
                 'Suma vectorială este (A−M)+(B−M)−(C−M)=A+B−C−M=P−M, cu P fix. Condiția devine PM=R: cerc de rază pozitivă sau doar punctul P dacă R=0.',{**pts,'radius':radius})
        scale=j+1;inter=v(Q(12*scale,5),Q(8*scale,5))
        position(17,f'În dreptunghiul A(0;0), B({3*scale};0), C({3*scale};{4*scale}), D(0;{4*scale}), M,N sunt mijloacele lui BC,CD. P=AM∩BN. Calculați lungimea AP.',Q(4*scale,5)*S.sqrt(13),
                 f'Notăm s={scale}, deci AB=3s și AD=4s. În coordonate, M=(3s,2s), N=(3s/2,4s). Egalăm P=tM=B+u(N−B), ceea ce dă t=4/5 și u=2/5. Norma lui AP este (4/5)|AM|=(4s/5)√13.',{'width':3*scale,'height':4*scale})

        centroid=average(aa,bb,cc)
        centre(1,'În triunghiul cu '+desc+', M este mijlocul lui BC. Aflați N care verifică AN+2MN=0.',centroid,
               'Ecuația este (N−A)+2(N−M)=0, deci 3N=A+2M=A+B+C. Prin urmare N este centrul de greutate, pe mediană, cu AN:NM=2:1.')
        centre(2,'Pentru triunghiul cu '+desc+', G este centrul de greutate și G′ este simetricul său față de mijlocul lui BC. Calculați GG′.',bb+cc-2*centroid,
               'Mijlocul BC are poziția (B+C)/2. Simetria centrală dă G′=B+C−G, deci GG′=B+C−2G. Înlocuim G=(A+B+C)/3.')
        centre(3,'ABCD este paralelogramul cu '+desc+'. M,N sunt mijloacele lui BC,DC. Aflați centrul de greutate al triunghiului AMN.',average(aa,cc),
               'D=A+C−B. Atunci A+M+N=A+(B+C)/2+(D+C)/2=3(A+C)/2. Împărțind la 3 obținem centrul diagonalelor, care este și centrul de greutate al lui AMN.')
        centre(4,'Pentru '+desc+', '+pt('D',dd)+', G₁,G₂ sunt centrele triunghiurilor ABC,ABD. Calculați G₁G₂.',(dd-cc)/3,
               'Scădem formulele baricentrice: G₂−G₁=(A+B+D−A−B−C)/3=(D−C)/3. Rezultă direcție paralelă cu CD, același sens și o treime din lungime.')
        centre(5,'ABCD este patrulater convex cu '+desc+', '+pt('D',aa+cc-bb)+'. O este intersecția diagonalelor. G₁,G₂,G₃,G₄ sunt centrele lui OAB,OBC,OCD,ODA. Calculați G₁G₂.',(cc-aa)/3,
               'G₂−G₁=(C−A)/3; analog G₃−G₄=(C−A)/3. Cealaltă pereche de laturi este determinată de BD/3. Diagonalele unui patrulater convex nu sunt paralele, deci figura centrelor este un paralelogram nedegenerat.')
        side=6*j
        centre(6,f'A=(0;0), B=({side};0), C=(0;{side}), G este centrul de greutate. G′ este simetricul lui G față de mijlocul BC. Prin G′ ducem paralele la AB,AC care taie AC,AB în E,F. Aflați E.',v(0,4*j),
               f'Notăm s={j}, deci AB=AC=6s. G=(2s,2s), mijlocul BC este (3s,3s), deci G′=(4s,4s). Paralelele au ecuațiile y=4s și x=4s: E=(0,4s), F=(4s,0). G=(E+F)/2, deci E,G,F sunt coliniare.',{'side':side})
        centre(7,'Pentru triunghiul cu '+desc+', M,N,P sunt mijloacele lui BC,CA,AB. Aflați centrul de greutate al triunghiului MNP.',centroid,
               'Suma M+N+P este A+B+C. Împărțirea la 3 dă aceeași poziție ca pentru centrul triunghiului inițial. Necoliniaritatea se păstrează pentru triunghiul median.')
        hexagon=[v(0,0),v(2*j,0),v(3*j,j),v(2*j,3*j),v(0,3*j),v(-j,j)]
        description=', '.join(pt(name,point) for name,point in zip('ABCDEF',hexagon))
        centre(8,'Hexagonul convex are '+description+'. M,N,P,Q,R,S sunt mijloacele laturilor AB,BC,CD,DE,EF,FA. Aflați centrul comun al triunghiurilor MPR și NQS.',average(*hexagon),
               'Suma M+P+R este jumătatea sumei celor șase vârfuri. Aceeași expresie apare pentru N+Q+S. Împărțind la 3, ambele centre au poziția (A+B+C+D+E+F)/6.',{'hexagon':hexagon})
        u,vv,w=v(3*j,0),v(0,3*j),v(-j,j)
        mm,nn,pp=aa+u,bb+vv,cc+w
        centre(9,'Triunghiurile ABC și MNP au '+desc+', '+pt('M',mm)+', '+pt('N',nn)+', '+pt('P',pp)+'. Calculați G₁G₂ între centrele lor, în această ordine.',(u+vv+w)/3,
               '3G₁G₂=(M+N+P)−(A+B+C)=AM+BN+CP. Împărțim suma deplasărilor omoloage la 3.',{**pts,'M':mm,'N':nn,'P':pp})
        centre(10,'Punctele fixe sunt '+desc+', iar '+pt('M',dd)+'. Calculați MA+MB+MC.',aa+bb+cc-3*dd,
               'MA+MB+MC=A+B+C−3M=3(G−M)=3MG. Identitatea este valabilă pentru orice origine mobilă M.')
        mm,nn=aa+v(j,0),bb+v(0,j)
        centre(11,'Triunghiul ABC are '+desc+'. Pentru '+pt('M',mm)+', '+pt('N',nn)+', determinați P astfel încât MNP și ABC să aibă același centru de greutate.',aa+bb+cc-mm-nn,
               'Egalitatea centrelor este echivalentă cu M+N+P=A+B+C sau cu AM+BN+CP=0. Aceasta determină unic P. Pentru datele alese triunghiul MNP este necoliniar.',{**pts,'M':mm,'N':nn})
        lam=Q(j+2,j+3);mu=lam/(3*lam-1)
        centre(12,'În triunghiul ABC, M∈AB și N∈AC sunt interioare, cu AM/AB='+tex(lam)+'. Ce valoare are AN/AC dacă dreapta MN trece prin centrul de greutate G?',mu,
               'În baza (AB,AC), G are coordonatele (1/3,1/3). Ecuația dreptei de interceptări M=(p,0),N=(0,q) este α/p+β/q=1. Pentru G rezultă 1/p+1/q=3, deci q=p/(3p−1). Datele dau 0<q<1.',{'lambda':lam})
        centre(13,'Pe laturile orientate AB,BC,CA ale triunghiului necoliniar, orientat trigonometric, cu '+desc+', construim spre exterior triunghiuri echilaterale cu vârfurile D,E,F. Aflați centrul de greutate al lui DEF.',centroid,
               'Pentru fiecare latură, vârful exterior este media extremităților minus √3/2 ori rotirea cu 90° a vectorului laturii. La însumarea ciclică, rotațiile se anulează deoarece AB+BC+CA=0. Rezultă D+E+F=A+B+C, deci centrele coincid.')
        convex_d=v(-j,3*j)
        centre(14,'Patrulaterul convex cu '+desc+', '+pt('D',convex_d)+' are E,F,H,K mijloacele laturilor AB,BC,CD,DA. Aflați baricentrul celor patru puncte E,F,H,K, cu ponderi egale.',average(aa,bb,cc,convex_d),
               'Suma pozițiilor celor patru mijloace este A+B+C+D. Împărțirea la 4 dă baricentrul lor, egal cu baricentrul cu ponderi egale al vârfurilor patrulaterului.',{**pts,'D':convex_d})
        la,lb=j+1,2*j+1
        centre(15,f'Două triunghiuri ABC și A′B′C′ au același centru de greutate; AA′={la} și BB′={lb}. Care este cea mai mare lungime CC′ permisă de relația vectorială dintre deplasările omoloage?',la+lb,
               'AA′+BB′+CC′=0 ca vectori. Deci |CC′|=|AA′+BB′|≤|AA′|+|BB′|. Egalitatea este permisă dacă primele două deplasări au același sens. Pot fi alese triunghiuri nedegenerate care realizează acest caz.',{'lengths':[la,lb]})
        lam,nu=Q(j,j+1),Q(1,j+2)
        centre(16,'Rombul are A=(0;0), B=(3;4), D=(3;−4), C=(6;0). M∈AB, N∈AD, P∈AC au AM/AB='+tex(lam)+', AN/AD=μ, AP/AC='+tex(nu)+'. Pentru ce μ centrul de greutate al lui MNP aparține diagonalei AC?',lam,
               'Ordonatele lui M,N,P sunt 4λ,−4μ,0. Ordonata centrului este 4(λ−μ)/3, care se anulează exact când μ=λ. Parametrii dați sunt interiori, iar triunghiul rezultat nu degenerează.',{'lambda':lam,'nu':nu})
        centre(17,'Determinați centrul de greutate al triunghiului cu '+desc+'.',centroid,
               'Coordonatele centrului de greutate sunt mediile aritmetice ale celor trei abscise și ale celor trei ordonate: G=(A+B+C)/3.')
        lam=Q(j,j+2)
        centre(18,'În triunghiul necoliniar ABC, M=(1−α)A+αB, N=(1−β)B+βC, P=(1−γ)C+γA. Dacă α='+tex(lam)+' și triunghiurile ABC,MNP au același centru de greutate, determinați (β;γ).',S.Tuple(lam,lam),
               'Suma M+N+P are coeficienții 1−α+γ, α+1−β, β+1−γ. Egalitatea cu A+B+C și independența afină a vârfurilor impun α=β=γ. Coeficientul dat este interior, deci punctele sunt pe laturi.',{'alpha':lam})
        centre(19,'În patrulaterul convex cu '+desc+', '+pt('D',aa+cc-bb)+', fiecare vârf este unit cu centrul de greutate al triunghiului format din celelalte trei. Aflați punctul comun al celor patru drepte.',average(aa,bb,cc,aa+cc-bb),
               'T=(A+B+C+D)/4 satisface T=A+(3/4)(GBCD−A), și analog față de fiecare vârf. Deci T aparține tuturor celor patru drepte. Convexitatea exclude coincidența unui vârf cu centrul celorlalte trei și garantează drepte bine definite.',{'A':aa,'B':bb,'C':cc,'D':aa+cc-bb})
        centre(20,'M,N,P sunt mijloacele lui BC,CA,AB pentru triunghiul cu '+desc+'. Simetricele unui punct O față de M,N,P formează un triunghi cu același centru de greutate ca ABC. Determinați O.',centroid,
               'Pozițiile simetricelor sunt B+C−O, C+A−O, A+B−O. Centrul lor este 2G−O. Egalitatea cu G impune O=G, necesar și suficient.')

    for lesson,total in ((1,85),(3,100)):
        assert len(banks[lesson])==total
        assert len({q['text'] for q in banks[lesson]})==total
    return banks


def update_files():
    for lesson,items in build_banks().items():
        path=FILES[lesson];data=json.loads(path.read_text(encoding='utf-8'))
        retained=[q for q in data['questions'] if q.get('practice_scope',{}).get('bank')!=BANK]
        data['questions']=retained+items;data['difficulty']='hard'
        path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        print(f'G2 lesson {lesson}: {len(items)} grids, {len(retained)} existing questions preserved.')


if __name__=='__main__':update_files()
