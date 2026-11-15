"""115 grile G4 §3: aplicații vectoriale, mediane și relația lui Leibniz.

Exerciții originale cu date exacte; tipurile 12/16 sunt explicit cazuri
pregătitoare, fără atribuirea configurațiilor complete nespecificate.
"""
import json
from pathlib import Path

import sympy as S

TARGET=Path(__file__).resolve().parents[1]/"clasa_9/clasa_9_u08_l02_aplicatii_vectoriale_in_geometria_plana_coliniaritate_si_relatia_lui_l.json"
BANK="g4_vectoriale_leibniz_v1"
NAMES=[
    "Teorema medianei", "Unghi drept caracterizat prin mediane",
    "Relații globale între mediane", "Invariant metric în dreptunghi",
    "Lungimea unei ceviene cu raport dat", "Progresii ale pătratelor laturilor și medianelor",
    "Triunghi dreptunghic din mediane", "Distanță dedusă dintr-o mediană",
    "Medianele perpendiculare", "Reconstrucția laturilor din mediane",
    "Identități între vârfuri și mijloace", "Invariant cu punct mobil pe cerc",
    "Identități metrice în patrulater", "Caracterizarea paralelogramului prin Apollonius",
    "Sumă de pătrate pe circumcercul pătratului", "Distanțe care formează un triunghi dreptunghic",
    "Relația lui Leibniz", "Distanțe între centrele triunghiului",
    "Echilateralitate din egalitate metrică", "Loc geometric de sumă a două pătrate de distanțe",
    "Loc geometric de sumă a trei pătrate", "Optimizare pe latură",
    "Caracterizarea paralelismului sau dreptunghiului",
]
PARTIAL={
    12:"Configurație proprie de secante prin puncte simetrice: inverse de produse de distanțe, nu expresia originală de inverse de pătrate nespecificată în catalog.",
    16:"Caz circular explicit care produce trei distanțe pitagoreice; nu reproduce configurația originală nespecificată.",
}


def point(x,y):
    return S.Matrix([S.Rational(x),S.Rational(y)])


def pair(value):
    return "("+"; ".join(str(S.Rational(x)) for x in value)+")"


def squared(value):
    return S.simplify(value.dot(value))


def serial(value):
    if isinstance(value,S.MatrixBase):
        return [str(S.simplify(x)) for x in value]
    if isinstance(value,dict):
        return {k:serial(v) for k,v in value.items()}
    if isinstance(value,(list,tuple)):
        return [serial(x) for x in value]
    if isinstance(value,S.Basic):
        return str(value)
    return value


def emit(family,variant,text,answer,explanation,data,wrong=None):
    if isinstance(answer,S.MatrixBase):
        answer=tuple(answer)
    if isinstance(answer,tuple):
        answer=tuple(S.Rational(x) for x in answer)
        values=[answer,(answer[0]+1,answer[1]),(answer[0],answer[1]-1),(answer[0]-1,answer[1]+1)]
        options=[pair(v) for v in values]; kind="pair"
    elif isinstance(answer,str):
        options=[answer,*wrong]; kind="locus"
    else:
        answer=S.Rational(answer)
        options=[str(answer),str(answer+1),str(answer-1),str(answer+2)]; kind="number"
    assert len(options)==4 and len(set(options))==4
    correct=((family-1)*5+variant-1)%4
    options.insert(correct,options.pop(0))
    return {
        "text":text,"type":"multiple_choice","format":"grid","points":10,
        "explanation":explanation,
        "options":[{"text":o,"is_correct":i==correct} for i,o in enumerate(options)],
        "practice_scope":{
            "bank":BANK,"catalog":"G4_catalog.md","section":"3","pages":"236–238",
            "family":family,"family_name":NAMES[family-1],"variant":variant,
            "coverage":"partial_explicit_case" if family in PARTIAL else "original_grid_adaptation",
            "adaptation":PARTIAL.get(family,"Problemă originală de calcul/recunoaștere; demonstrațiile de catalog sunt adaptate în grile cu justificare în explicație."),
        },
        "verification":serial({"family":family,"answer_kind":kind,**data}),
    }


def locus(center,radius2):
    empty="Mulțimea vidă"
    singleton="Punctul "+pair(center)
    circle=lambda r:"Cercul cu centrul "+pair(center)+" și raza la pătrat "+str(r)
    if radius2<0:
        return empty,[singleton,circle(1),"Întregul plan"]
    if radius2==0:
        return singleton,[empty,circle(1),"Întregul plan"]
    return circle(radius2),[empty,singleton,circle(radius2+1)]


def build_questions():
    questions=[]
    triangles=[(14,5,12),(21,5,12),(36,15,20),(17,7,24),(28,8,15)]
    for j,(base,x,height) in enumerate(triangles,1):
        A,B,C=point(0,0),point(base,0),point(x,height)
        a2,b2,c2=squared(C-B),squared(C-A),squared(B-A)
        a,b,c=S.sqrt(a2),S.sqrt(b2),S.sqrt(c2)
        side_sum=a2+b2+c2
        ma2=(2*b2+2*c2-a2)/4
        mb2=(2*a2+2*c2-b2)/4
        mc2=(2*a2+2*b2-c2)/4
        G=(A+B+C)/3
        O=point(S.Rational(base,2),S.Rational(x*x+height*height-base*x,2*height))
        H=A+B+C-2*O
        R2=squared(O-A)
        intro=f"În triunghiul ABC cu A{pair(A)}, B{pair(B)}, C{pair(C)}"
        lengths=f"Cu a=BC, b=CA, c=AB, avem a²={a2}, b²={b2}, c²={c2}. "
        common={"A":A,"B":B,"C":C}

        def add(family,text,answer,explanation,extra=None,own=False,wrong=None):
            data=({} if own else common)|(extra or {})
            questions.append(emit(family,j,text,answer,explanation,data,wrong))

        add(1,intro+", M este mijlocul lui BC. Calculați AM².",ma2,
            lengths+f"Teorema medianei (Apollonius) dă 4AM²=2AB²+2AC²−BC². Prin urmare AM²=[2·{c2}+2·{b2}−{a2}]/4={ma2}. Formula rezultă și din AM=(AB+AC)/2 și dezvoltarea pătratului normei.")

        k=S.Integer(j+1)
        add(2,f"Într-un triunghi ABC, AB={3*k}, BC={5*k}, iar mediana din A are lungimea {5*k/2}. Calculați AC².",16*k*k,
            f"Notăm b=AC, c=AB={3*k}, a=BC={5*k}. Din m_a=a/2 și 4m_a²=2b²+2c²−a² rezultă a²=b²+c², deci unghiul A este drept prin reciproca lui Pitagora. Astfel AC²={25*k*k}−{9*k*k}={16*k*k}. Laturile {3*k},{4*k},{5*k} sunt pozitive și formează un triunghi necoliniar.",
            {"AB":3*k,"BC":5*k,"median_A":5*k/2},own=True)

        add(3,intro+", m_a,m_b,m_c sunt lungimile celor trei mediane. Calculați m_a²+m_b²+m_c².",3*side_sum/4,
            lengths+f"Însumând formulele 4m_a²=2b²+2c²−a² și variantele ciclice, obținem 4(m_a²+m_b²+m_c²)=3(a²+b²+c²). Suma este deci 3·{side_sum}/4={3*side_sum/4}. Fiecare pătrat al unei laturi apare cu coeficientul total 2+2−1=3.")

        width,height_rect=S.Integer(j+3),S.Integer(2*j+1)
        add(4,f"ABCD este un dreptunghi cu A(0;0), B({width};0), C({width};{height_rect}), D(0;{height_rect}). Pentru un punct M oarecare din plan, calculați MA²+MC²−MB²−MD².",0,
            "Scriem M=(u;v). Cele patru pătrate de distanțe se obțin din diferențele coordonatelor. În MA²+MC²−MB²−MD², termenii u²,v² și termenii liniari se anulează, iar termenul constant este tot 0. Echivalent, diagonalele au același mijloc O și aceeași lungime: fiecare sumă către două vârfuri opuse este 2MO²+AC²/2. Identitatea este valabilă pentru orice M, interior sau exterior.",
            {"width":width,"height":height_rect},own=True)

        p,q=S.Integer(j+1),S.Integer(j+2)
        D=(q*B+p*C)/(p+q)
        cevian2=squared(D-A)
        add(5,intro+f", D∈BC și BD:DC={p}:{q}. Calculați AD².",cevian2,
            lengths+f"Avem BD=ap/(p+q) și DC=aq/(p+q). Stewart dă b²·BD+c²·DC=a(AD²+BD·DC). Așadar AD²=(p·b²+q·c²)/(p+q)−a²pq/(p+q)²={cevian2}. Același rezultat rezultă din D=(qB+pC)/(p+q)={pair(D)} și distanța față de A. Raportul este pozitiv, deci D este interior laturii.",
            {"BD_DC":[p,q]})

        s,d=S.Integer(10+3*j),S.Integer(j+1)
        add(6,f"Într-un triunghi, a²={s-d}, b²={s}, c²={s+d}. Dacă m_a²,m_b²,m_c² sunt considerate în această ordine, care este rația progresiei lor aritmetice?",-3*d/4,
            f"Pătratele laturilor sunt în PA cu rația d={d}. Din formula medianei, m_b²−m_a²=3(a²−b²)/4=−3d/4, iar m_c²−m_b²=3(b²−c²)/4=−3d/4. Rația cerută este {(-3*d/4)}, cu semn opus rației pătratelor laturilor. Toate laturile sunt pozitive și verifică inegalitățile stricte ale triunghiului.",
            {"sides_squared":[s-d,s,s+d]},own=True)

        median_b2,median_c2=13*k*k,S.Rational(73,4)*k*k
        add(7,f"ABC este dreptunghic în A. Se cunosc m_b²={median_b2} și m_c²={median_c2}, unde m_b este mediana din B și m_c mediana din C. Care este perechea (AC²; AB²)?",(16*k*k,9*k*k),
            f"Notăm b=AC, c=AB. Deoarece a²=b²+c², formulele medianelor devin b²+4c²=4m_b²={4*median_b2} și 4b²+c²=4m_c²={4*median_c2}. Rezolvând sistemul cu determinant −15≠0, obținem b²={16*k*k}, c²={9*k*k}, iar a²={25*k*k}. Rădăcinile pozitive {4*k},{3*k},{5*k} satisfac Pitagora și inegalitățile triunghiului; rădăcinile negative nu sunt lungimi.",
            {"median_b_squared":median_b2,"median_c_squared":median_c2},own=True)

        area2=S.Rational(base*height,2)**2
        distance2=area2/a2
        add(8,f"În triunghiul ABC se cunosc AB={c}, BC={a}. M este mijlocul lui AC și BM²={mb2}. Calculați pătratul distanței de la M la dreapta BC.",distance2,
            f"Teorema medianei din B dă AC²=2AB²+2BC²−4BM²={b2}, deci AC={b}>0. Cele trei laturi formează un triunghi. Formula lui Heron dă aria S cu S²={area2}. Înălțimea din A are pătratul 4S²/BC². Deoarece M este mijlocul lui AC și C∈BC, distanța lui M la BC este jumătate din înălțimea din A. Pătratul cerut este S²/BC²={distance2}.",
            {"AB":c,"BC":a,"median_b_squared":mb2},own=True)

        u=S.Integer(j+1)
        add(9,f"În triunghiul ABC, BC²={4*u*u} și AB²={10*u*u}. Medianele din B și C sunt perpendiculare. Calculați AC².",10*u*u,
            "Dacă N și P sunt mijloacele lui AC și AB, dezvoltarea produsului scalar dă BN·CP=(b²+c²−5a²)/8. Medianele sunt nenule și perpendiculare exact când b²+c²=5a². "
            +f"Prin urmare AC²=5BC²−AB²=5·{4*u*u}−{10*u*u}={10*u*u}. Laturile pozitive rezultate formează un triunghi isoscel necoliniar; substituirea în produsul scalar dă 0.",
            {"BC_squared":4*u*u,"AB_squared":10*u*u},own=True)

        add(10,f"Într-un triunghi ABC, pătratele medianelor din A,B,C sunt, în această ordine, {ma2}, {mb2}, {mc2}. Calculați BC².",a2,
            "Inversarea sistemului celor trei formule ale medianelor dă a²=4(2m_b²+2m_c²−m_a²)/9 și formulele ciclice pentru b²,c². "
            +f"Înlocuind, obținem a²={a2}, b²={b2}, c²={c2}. Toate sunt pozitive; rădăcinile pozitive sunt {a},{b},{c} și satisfac inegalitățile stricte ale triunghiului. Astfel datele medianelor sunt realizabile, iar BC²={a2}.",
            {"medians_squared":[ma2,mb2,mc2]},own=True)

        add(11,intro+", D,E,F sunt mijloacele lui BC,CA,AB. Pentru M oarecare, calculați constanta MA²+MB²+MC²−MD²−ME²−MF².",side_sum/4,
            lengths+"Aplicând teorema medianei în triunghiurile MBC,MCA,MAB, avem MD²=(MB²+MC²)/2−BC²/4 și relațiile ciclice. Prin însumare, MD²+ME²+MF²=MA²+MB²+MC²−(a²+b²+c²)/4. "
            +f"Diferența cerută este deci {side_sum}/4={side_sum/4}, independent de poziția lui M.")

        radius,offset=S.Integer(j+3),S.Integer(j+1)
        invariant=S.Rational(2,radius*radius-offset*offset)
        add(12,f"Cercul cu centrul O are raza {radius}. A și B sunt puncte interioare simetrice față de O, cu OA=OB={offset}. O secantă prin A taie cercul în P,Q, iar o secantă prin B în U,V. Folosind lungimi pozitive, calculați 1/(AP·AQ)+1/(BU·BV).",invariant,
            f"Punctele sunt strict interioare deoarece {offset}<{radius}; fiecare secantă are două intersecții distincte și distanțele sunt nenule. Puterea punctului dă AP·AQ=R²−OA²={radius*radius-offset*offset}, pentru lungimi pozitive; la fel BU·BV=R²−OB². Suma este 2/(R²−OA²)={invariant}, independent de direcțiile celor două secante. Aceasta este o configurație proprie cu inverse de produse, nu o atribuire a expresiei de catalog nespecificate.",
            {"radius":radius,"offset":offset},own=True)

        QA,QB,QC,QD=point(0,0),point(j+4,0),point(j+6,j+3),point(-1,j+2)
        midAC,midBD=(QA+QC)/2,(QB+QD)/2
        gap2=squared(midAC-midBD)
        quad={"A":QA,"B":QB,"C":QC,"D":QD}
        quad_intro=f"În patrulaterul convex ABCD cu A{pair(QA)}, B{pair(QB)}, C{pair(QC)}, D{pair(QD)}"
        add(13,quad_intro+", M și N sunt mijloacele diagonalelor AC și BD. Calculați MN².",gap2,
            "Identitatea lui Euler pentru un patrulater este AB²+BC²+CD²+DA²=AC²+BD²+4MN². Ea rezultă aplicând repetat teorema medianei sau dezvoltând diferențele de coordonate. "
            +f"Aici M={pair(midAC)}, N={pair(midBD)}, deci MN²={gap2}. Valoarea coincide cu un sfert din diferența dintre suma pătratelor laturilor și cea a diagonalelor.",quad,own=True)

        Dpara=A+C-B
        add(14,intro+", punctul D este ales astfel încât ABCD să fie un patrulater și AB²+BC²+CD²+DA²=AC²+BD². Care sunt coordonatele lui D?",Dpara,
            "Pentru orice patrulater, diferența dintre suma pătratelor laturilor și suma pătratelor diagonalelor este 4MN², unde M,N sunt mijloacele diagonalelor. Egalitatea dată impune MN²=0, deci M=N: A+C=B+D. "
            +f"Prin urmare D=A+C−B={pair(Dpara)}. Cele două diagonale au același mijloc, astfel ABCD este paralelogram; necoliniaritatea lui A,B,C exclude degenerarea.")

        side=S.Integer(j+2)
        add(15,f"ABCD este un pătrat de latură {side}. M este un punct oarecare pe cercul circumscris pătratului. Calculați MA²+MB²+MC²+MD².",4*side*side,
            f"Notăm O centrul pătratului și R raza circumcercului, cu R²=l²/2={side*side/2}. Grupând vârfurile opuse, teorema medianei dă MA²+MC²=2MO²+2R² și MB²+MD²=2MO²+2R². Deoarece M este pe circumcerc, MO²=R². Suma este 8R²=4l²={4*side*side}, inclusiv când M coincide cu un vârf.",
            {"side":side},own=True)

        add(16,f"Punctele considerate sunt A({-u};0), B({u};0), C(0;{2*u}). Punctul M(x;y) aparține cercului x²+(y+{2*u})²={6*u*u}. Calculați raportul (MA²+MB²)/MC².",1,
            f"Avem MA²+MB²=2(x²+y²)+{2*u*u}, iar MC²=x²+y²−{4*u}y+{4*u*u}. Diferența lor este x²+(y+{2*u})²−{6*u*u}=0, prin ecuația cercului. Deci MA²+MB²=MC² și raportul este 1. A și B nu aparțin cercului: distanța lor la centrul (0;{-2*u}) are pătratul {5*u*u}≠{6*u*u}; nici C nu îi aparține. Cele trei distanțe sunt pozitive, astfel formează un triunghi dreptunghic cu ipotenuza MC.",
            {"scale":u},own=True)

        mobile=point(j,-j)
        mg2=squared(mobile-G)
        total=3*mg2+side_sum/3
        add(17,intro+f", G este centrul de greutate. Dacă MG²={mg2}, calculați MA²+MB²+MC².",total,
            lengths+"Relația lui Leibniz este MA²+MB²+MC²=3MG²+GA²+GB²+GC². Termenii micști se anulează deoarece GA+GB+GC=0. În plus GA²+GB²+GC²=(a²+b²+c²)/3. "
            +f"Rezultă suma 3·({mg2})+{side_sum}/3={total}. Condiția MG²≥0 este îndeplinită și descrie un cerc sau un punct în jurul lui G.",{"M":mobile,"MG_squared":mg2})

        targets=["OG²","GH²","OH²","OG²","GH²"]
        target=targets[j-1]
        values={"OG²":squared(G-O),"GH²":squared(H-G),"OH²":squared(H-O)}
        add(18,intro+f", O,G,H sunt circumcentrul, centrul de greutate și ortocentrul. Calculați {target}.",values[target],
            lengths+f"R²=OA²={R2}. Aplicând Leibniz pentru M=O, obținem 3R²=3OG²+(a²+b²+c²)/3, deci OG²=R²−(a²+b²+c²)/9. Din Sylvester, OH=3OG ca vectori, iar GH=2OG. Astfel OH²=9OG² și GH²=4OG². Valoarea cerută este {values[target]}. Aceste formule rămân valide și în cazul echilateral, când toate trei sunt zero, dar aici centrele sunt distincte.",{"target":target})

        median=S.Integer(j+2)
        add(19,f"Într-un triunghi ABC, toate cele trei mediane au aceeași lungime {median}. Calculați BC².",S.Rational(4,3)*median*median,
            "Scăzând formulele medianelor, 4(m_a²−m_b²)=3(b²−a²). Egalitatea celor trei mediane implică a²=b²=c²; fiind lungimi pozitive, a=b=c și triunghiul este echilateral. "
            +f"Într-un triunghi echilateral, m²=3a²/4. Cu m={median}, rezultă BC²=4m²/3={S.Rational(4,3)*median*median}. Reciproc, un triunghi echilateral are medianele egale, deci configurația există.",{"median":median},own=True)

        center=point(j,-j); half=S.Integer(j+1)
        LA,LB=center-point(half,0),center+point(half,0)
        r2=S.Integer([-1,0,1,4,9][j-1])
        constant=2*half*half+2*r2
        answer,wrong=locus(center,r2)
        add(20,f"Se dau punctele fixe A{pair(LA)}, B{pair(LB)}. Care este locul geometric al punctelor M cu MA²+MB²={constant}?",answer,
            f"Mijlocul lui AB este O{pair(center)}, iar AB²={4*half*half}. Teorema medianei dă MA²+MB²=2MO²+AB²/2. Prin urmare MO²=({constant}−{2*half*half})/2={r2}. "
            +(f"Valoarea este negativă, deci nu există puncte reale: mulțimea este vidă." if r2<0 else "Valoarea este zero, deci singurul punct este O." if r2==0 else f"Valoarea este pozitivă, deci locul este cercul de centru O și rază la pătrat {r2}."),
            {"A":LA,"B":LB,"constant":constant},own=True,wrong=wrong)

        r2=S.Integer([-2,0,1,4,9][j-1])
        constant=side_sum/3+3*r2
        answer,wrong=locus(G,r2)
        add(21,intro+f". Care este locul geometric al punctelor M cu MA²+MB²+MC²={constant}?",answer,
            f"Centrul de greutate este G{pair(G)}. Prin Leibniz, suma distanțelor la pătrat este 3MG²+(a²+b²+c²)/3=3MG²+{side_sum/3}. Ecuația se reduce la MG²=({constant}−{side_sum/3})/3={r2}. "
            +(f"Un pătrat de distanță nu poate fi negativ, deci locul este mulțimea vidă." if r2<0 else "Rezultă MG=0: locul este punctul G, nu un cerc cu rază pozitivă." if r2==0 else f"Rezultă un cerc cu centrul G și raza la pătrat {r2}."),
            {"constant":constant},wrong=wrong)

        OA,OC=point(0,0),point(6,0)
        OB=point([-8,-6,0,3,12][j-1],j+1)
        K=(OB+OC)/2
        t0=(K-OA).dot(OC-OA)/squared(OC-OA)
        t=max(S.Integer(0),min(S.Integer(1),t0))
        optimum=OA+t*(OC-OA)
        minvalue=squared(optimum-OB)+squared(optimum-OC)
        add(22,f"Punctele considerate sunt A{pair(OA)}, B{pair(OB)}, C{pair(OC)}. Pentru M pe segmentul închis [AC], determinați coordonatele punctului care minimizează MB²+MC².",optimum,
            f"Notăm K mijlocul lui BC: K{pair(K)}. Teorema medianei dă MB²+MC²=2MK²+BC²/2. Parametrizăm M=A+t(C−A), 0≤t≤1. Proiecția lui K pe dreapta AC corespunde lui t₀={t0}. "
            +(f"Deoarece t₀≤0, minimul pe segment este la A, adică t=0. " if t0<=0 else "Deoarece t₀≥1, minimul pe segment este la C, adică t=1. " if t0>=1 else f"Deoarece 0<t₀<1, proiecția este interioară și t=t₀={t0}. ")
            +f"Punctul unic de minim este M{pair(optimum)}, iar valoarea minimă este {minvalue}. Convexitatea strictă a pătratului distanței justifică alegerea proiecției sau a capătului apropiat; nu folosim proiecția din afara segmentului.",
            {"A":OA,"B":OB,"C":OC},own=True)

        width,h=S.Integer(j+2),S.Integer(2*j+1)
        add(23,f"Se consideră paralelogramul ABCD cu A(0;0), B({width};0), D(t;{h}), C(t+{width};{h}). Pentru ce valoare a lui t avem MA²+MC²=MB²+MD² pentru orice punct M din plan?",0,
            f"Scriind M=(x;y) și dezvoltând pătratele distanțelor, diferența MA²+MC²−MB²−MD² se reduce la 2·{width}·t. Deoarece {width}>0, identitatea pentru orice M este echivalentă cu t=0. Atunci AB este orizontală și AD verticală, deci paralelogramul este dreptunghi (posibil pătrat). Înălțimea {h}>0 exclude degenerarea; condiția dată nu trebuie aplicată unui patrulater arbitrar fără ipoteza de paralelogram.",
            {"width":width,"height":h},own=True)
    assert len(questions)==115 and len({q["text"] for q in questions})==115
    return sorted(questions,key=lambda q:(q["practice_scope"]["family"],q["practice_scope"]["variant"]))


def update_file(path=TARGET):
    path=Path(path)
    data=json.loads(path.read_text(encoding="utf-8"))
    retained=[q for q in data["questions"] if q.get("practice_scope",{}).get("bank")!=BANK]
    data["questions"]=retained+build_questions()
    data["difficulty"]="hard"
    path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    return len(data["questions"])


if __name__=="__main__":
    print(f"{update_file()} questions; 115 original grids; no database import.")
