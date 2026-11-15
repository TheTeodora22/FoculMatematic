"""130 grile originale pentru bisectoare și relația lui Sylvester (G2 §3).

Problemele proprii au configurații explicite. Metadatele disting adaptările
de calcul și cazurile pregătitoare de configurațiile integrale din catalog.
Fără import în Django sau modificarea altor lecții.
"""
import json
from pathlib import Path

import sympy as S

TARGET = Path(__file__).resolve().parents[1] / "clasa_9/clasa_9_u06_l04_teorema_bisectoarei_relatia_lui_sylvester.json"
BANK = "g2_bisectoare_sylvester_v1"
NAMES = [
    "Împărțirea laturii prin bisectoare", "Recunoașterea bisectoarei",
    "Forma vectorială a bisectoarei", "Vectorul de poziție al incentrului",
    "Relația dintre incentru și centru de greutate", "Bisectoarea exterioară",
    "Trisectoare și rapoarte", "Bisectoare într-o configurație de paralele",
    "Coliniaritate echivalentă cu bisectoare", "Bisectoare, înălțime și mediană",
    "Paralelism între intersecțiile bisectoarelor", "Raport pe mediana intersectată de bisectoare",
    "Unghi trisectat de mediană și înălțime", "Direcție paralelă bisectoarei",
    "Relația lui Sylvester", "Ortocentre în triunghiul anticomplementar",
    "Dreapta lui Euler", "Centrul cercului lui Euler", "Cercul celor nouă puncte",
    "Ortocentru și paralelogram", "Triunghiul ortic",
    "Simetricele ortocentrului pe circumcerc", "Caracterizarea triunghiului echilateral prin centre",
    "Suma vectorilor bisectoarelor", "Lungimea bisectoarei",
    "Proiecții pe bisectoare și coliniaritate",
]
PARTIAL = {
    7: "Caz explicit cu un unghi drept trisectat; nu acoperă relația generală dintre trei ceviene.",
    8: "Calcul pregătitor cu o paralelă; nu reproduce concluzia originală despre un centru.",
    9: "Configurație proprie explicită cu un mijloc; nu reproduce trapezul auxiliar nespecificat în catalog.",
    10: "Raport calculat în configurația proprie înălțime/bisectoare/mediană; nu se atribuie produsul original cu alte puncte.",
    12: "Intersecție explicită a bisectoarei B cu mediana A; nu pretinde identitatea din configurația nedefinită a exemplului de catalog.",
    13: "Ordinea înălțime-mediană este precizată; nu include toate ordonările posibile.",
    14: "Direcția sumei a doi vectori unitari, într-o configurație proprie de mijloc.",
    26: "Exercițiu pregătitor de proiecție a mijlocului pe bisectoare; NU demonstrează alinierea celor patru proiecții din problema originală.",
}


def v(x, y):
    return S.Matrix([S.Rational(x), S.Rational(y)])


def pair(value):
    return "(" + "; ".join(str(S.Rational(x)) for x in value) + ")"


def serial(value):
    if isinstance(value, S.MatrixBase):
        return [str(S.simplify(x)) for x in value]
    if isinstance(value, dict):
        return {k: serial(x) for k, x in value.items()}
    if isinstance(value, (tuple, list)):
        return [serial(x) for x in value]
    if isinstance(value, S.Basic):
        return str(value)
    return value


def norm(vector):
    return S.sqrt(vector.dot(vector))


def projection(point, first, second):
    direction = second - first
    return first + ((point-first).dot(direction)/direction.dot(direction))*direction


def emit(family, variant, text, answer, explanation, data):
    if isinstance(answer, S.MatrixBase):
        answer = tuple(answer)
    if isinstance(answer, tuple):
        answer = tuple(S.Rational(x) for x in answer)
        values = [answer, (answer[0]+1, answer[1]), (answer[0], answer[1]-1), (answer[0]-1, answer[1]+1)]
        answers = [pair(x) for x in values]
        kind = "pair"
    else:
        answer = S.Rational(answer)
        answers = [str(answer), str(answer+1), str(answer-1), str(answer+2)]
        kind = "number"
    assert len(set(answers)) == 4
    correct = ((family-1)*5+variant-1) % 4
    answers.insert(correct, answers.pop(0))
    return {
        "text": text, "type": "multiple_choice", "format": "grid", "points": 10,
        "explanation": explanation,
        "options": [{"text": option, "is_correct": i == correct} for i, option in enumerate(answers)],
        "practice_scope": {
            "bank": BANK, "catalog": "G2_catalog.md", "section": "3", "pages": "195–200",
            "family": family, "family_name": NAMES[family-1], "variant": variant,
            "coverage": "partial_explicit_case" if family in PARTIAL else "original_grid_adaptation",
            "adaptation": PARTIAL.get(family, "Exercițiu original de calcul/recunoaștere; demonstrația și construcția din catalog sunt adaptate în grilă, cu justificare în explicație."),
        },
        "verification": serial({"family": family, "answer_kind": kind, **data}),
    }


def build_questions():
    questions = []
    triangles = [(14, 5, 12), (21, 5, 12), (36, 15, 20), (17, 7, 24), (28, 8, 15)]
    for j, (base, x, height) in enumerate(triangles, 1):
        A, B, C = v(0, 0), v(base, 0), v(x, height)
        a, b, c = norm(C-B), norm(C-A), norm(B-A)
        assert all(side.is_Rational for side in (a,b,c)) and b != c
        assert all(p.dot(q) > 0 for p,q in ((B-A,C-A),(A-B,C-B),(A-C,B-C)))
        perimeter = a+b+c
        D = (b*B+c*C)/(b+c)  # Internal bisector from A.
        I = (a*A+b*B+c*C)/perimeter
        G = (A+B+C)/3
        O = v(S.Rational(base,2), S.Rational(x*x+height*height-base*x,2*height))
        H = A+B+C-2*O
        N = (O+H)/2
        M = (B+C)/2
        foot = projection(A,B,C)
        R2 = (A-O).dot(A-O)
        common = {"A": A, "B": B, "C": C}
        intro = f"În triunghiul ABC cu A{pair(A)}, B{pair(B)}, C{pair(C)}"
        lengths = f"Lungimile sunt a=BC={a}, b=CA={b}, c=AB={c}. "

        def add(family, text, answer, explanation, extra=None, own=False):
            data = ({} if own else common) | (extra or {})
            questions.append(emit(family,j,text,answer,explanation,data))

        bd, dc = a*c/(b+c), a*b/(b+c)
        add(1, intro+", bisectoarea interioară AD întâlnește BC în D. Cât este lungimea BD?",
            bd, lengths+f"Teorema bisectoarei dă BD/DC=c/b={c}/{b}, iar BD+DC=a={a}. De aici BD=ac/(b+c)={bd}, DC=ab/(b+c)={dc}. Ambele sunt pozitive și suma lor este BC.")

        add(2, intro+f", punctul D este interior lui BC și BD={bd}. Ce raport BD/DC confirmă, prin reciproca teoremei bisectoarei, că AD este bisectoare interioară?",
            c/b, lengths+f"DC=BC−BD={dc}>0. Calculăm BD/DC={bd}/({dc})={c/b}=AB/AC. Deoarece D se află în interiorul laturii BC, reciproca teoremei bisectoarei se aplică și AD împarte unghiul A în două unghiuri egale.")

        add(3, intro+", D este piciorul bisectoarei interioare din A. Care sunt coeficienții (α; β) din egalitatea vectorială AD=α·AB+β·AC?",
            (b/(b+c),c/(b+c)), lengths+f"Deoarece BD/DC=c/b, avem D=(bB+cC)/(b+c). Scăzând A, rezultă AD=[b/(b+c)]AB+[c/(b+c)]AC. Așadar (α;β)={pair((b/(b+c),c/(b+c)))}. Ponderile sunt opuse segmentelor BD și DC; sunt pozitive și au suma 1.")

        add(4, intro+", determinați coordonatele incentrului I.", I,
            lengths+"Incentrul este intersecția bisectoarelor interioare și are formula I=(aA+bB+cC)/(a+b+c), cu ponderile egale lungimilor laturilor opuse vârfurilor. "
            +f"Înlocuind, I={pair(I)}. Toate ponderile sunt pozitive, deci punctul este interior triunghiului; distanțele sale la cele trei laturi sunt egale.")

        add(5, intro+", G este centrul de greutate și I incentrul. Determinați coordonatele vectorului GI.", I-G,
            lengths+f"G=(A+B+C)/3={pair(G)}, iar I=(aA+bB+cC)/(a+b+c)={pair(I)}. Vectorul GI este I−G={pair(I-G)}. În general GI=[(3a−p)A+(3b−p)B+(3c−p)C]/(3p), p=a+b+c; suma coeficienților este 0, deci vectorul nu depinde de originea reperului.")

        exterior = (b*B-c*C)/(b-c)
        add(6, intro+", bisectoarea exterioară a unghiului A intersectează dreapta BC în E. Care sunt coordonatele lui E?",
            exterior, lengths+f"Avem b≠c, deci această intersecție este finită. În raport orientat BE/EC=−c/b; forma afină este E=(bB−cC)/(b−c)={pair(exterior)}. Coeficienții au suma 1 și semne opuse, astfel E este exterior segmentului BC. Direcția AE este diferența vectorilor unitari AB/c−AC/b, până la un factor nenul.")

        p,q = S.Integer(j+2), S.Integer(j+3)
        add(7, f"În triunghiul dreptunghic ABC cu unghiul A=90°, razele AD și AE trisectează unghiul în ordinea AB, AD, AE, AC; D,E∈BC. Dacă AB={p} și AE={q}, calculați BD/DE.",
            p/q, f"Unghiurile BAD și DAE sunt ambele de 30°, deci AD este bisectoarea interioară în triunghiul ABE. Aplicând teorema bisectoarei în acest triunghi auxiliar, obținem BD/DE=AB/AE={p}/{q}={p/q}. Datele sunt realizabile: AE<2AB, astfel dreapta BE întâlnește semidreapta AC dincolo de E. Nu confundăm raportul BD/DE cu BD/DC.",
            {"AB":p,"AE":q}, own=True)

        add(8, intro+", AD este bisectoare interioară. Paralela prin D la AB întâlnește AC în E. Calculați raportul CE/CA.",
            b/(b+c), lengths+f"Din bisectoare, CD/CB=b/(b+c)={b/(b+c)}. Deoarece DE∥AB, triunghiurile CDE și CBA sunt asemenea, cu E∈AC. Prin Thales, CE/CA=CD/CB={b/(b+c)}. Aceasta este o configurație explicită de calcul, fără ipoteze despre un centru al altei figuri.")

        t = c/(c-b)
        add(9, intro+", AD este bisectoare interioară, M este mijlocul lui AB, iar N aparține dreptei AC. Pentru ca M,D,N să fie coliniare, care este scalarul t din AN=t·AC (egalitate vectorială)?",
            t, lengths+f"În baza independentă AB,AC avem M=(1/2;0), D=({b/(b+c)};{c/(b+c)}) și N=(0;t). Ecuația dreptei MN este 2u+v/t=1. Substituirea lui D dă 2b/(b+c)+c/[(b+c)t]=1, deci t=c/(c−b)={t}. Numitorul este nenul deoarece AB≠AC; t poate fi negativ, iar N nu este presupus interior segmentului AC.")

        ratio = (b+c)**2/a**2
        add(10, intro+", E este piciorul bisectoarei interioare din A, D piciorul înălțimii din A, iar M mijlocul lui BC. Calculați raportul lungimilor DM/EM.",
            ratio, lengths+"AB≠AC, deci E≠M și raportul este definit. Prin formulele proiecției pe BC, BD=(a²+c²−b²)/(2a), iar BM=a/2. Prin bisectoare, BE=ac/(b+c). "
            +f"Rezultă DM=|c²−b²|/(2a), EM=a|c−b|/[2(b+c)]. Împărțind și simplificând |c−b|≠0, obținem DM/EM=(b+c)²/a²={ratio}. Lungimile folosesc valori absolute, indiferent de ordinea lui D,E,M.")

        factor = (b-c)/b
        add(11, intro+". Se consideră paralelogramul ABKC, cu K=B+C−A. Bisectoarele interioare ale unghiurilor A și B se întâlnesc în P, iar cele ale unghiurilor C și K în Q. Care este scalarul λ din PQ=λ·AC (egalitate vectorială)?",
            factor, lengths+"Notăm e=AB/c și f=AC/b, vectori unitari necoliniari. Bisectoarele A,B au direcțiile e+f și −e+f, de unde P=A+(c/2)(e+f). Cele din C,K dau Q=A+(c/2)e+(b−c/2)f. "
            +f"Așadar PQ=(b−c)f=[(b−c)/b]AC={factor}·AC. Deoarece b≠c, P≠Q și dreapta PQ este paralelă cu AC, respectiv cu BK.")

        add(12, intro+", M este mijlocul lui BC. Bisectoarea interioară din B întâlnește mediana AM în P. Calculați AP/PM.",
            2*c/a, lengths+"Dacă E este piciorul bisectoarei din B pe AC, atunci AE/EC=c/a. În coordonate baricentrice, punctele de pe BE satisfac p_A:p_C=a:c. Pe AM avem p_B=p_C. "
            +f"Rezultă P=(aA+cB+cC)/(a+2c), adică P=A+[2c/(a+2c)](M−A). Coeficientul este între 0 și 1, deci AP/PM=2c/a={2*c/a}.")

        angle_targets = ["A", "B", "C", "B+C", "B−C"]
        target = angle_targets[j-1]; angle_answers = [90,60,30,90,30]
        add(13, f"În triunghiul ABC, D∈BC este piciorul înălțimii din A, M este mijlocul lui BC, iar razele sunt în ordinea AB, AD, AM, AC. Cele trei unghiuri BAD, DAM, MAC sunt egale; AD={j+2}. Cât este {target}, în grade? A,B,C desemnează unghiurile triunghiului.",
            angle_answers[j-1], "Notăm cele trei unghiuri egale cu θ, h=AD>0. Avem BD=h·tanθ, DC=h·tan(2θ), DM=h·tanθ. Deoarece M este mijlocul lui BC și B,D,M,C sunt în această ordine, DC−BD=2DM. "
            +"Prin urmare tan(2θ)=3tanθ. Pentru 0<θ<45°, formula tangentei duble dă tan²θ=1/3, deci θ=30°. Rezultă A=90°, B=60°, C=30°; valoarea cerută se calculează din aceste unghiuri. Ordinea razelor este esențială.",
            {"height":j+2,"target":target}, own=True)

        r=S.Integer(j)
        factor=r*(b+c)/(2*b*c)
        add(14, intro+f", AD este bisectoarea interioară. P∈AB și Q∈AC satisfac AP=AQ={r}; M este mijlocul lui PQ. Care este scalarul λ din AM=λ·AD (egalitate vectorială)?",
            factor, lengths+f"Punctele există pe segmente deoarece {r}<min(AB,AC). Notând e=AB/c și f=AC/b, avem AM=({r}/2)(e+f), iar AD=bc(e+f)/(b+c). "
            +f"Suma e+f este nenulă într-un triunghi necoliniar și are direcția bisectoarei interioare. Împărțind coeficienții, λ={r}(b+c)/(2bc)={factor}; în particular AM și AD sunt paralele și au același sens.", {"radius":r})

        add(15, intro+", O este circumcentrul. Determinați coordonatele ortocentrului H.", H,
            f"Circumcentrul este O={pair(O)}, obținut din OA²=OB²=OC². Relația lui Sylvester este OH=OA+OB+OC (egalitate vectorială cu originea O), deci H=A+B+C−2O={pair(H)}. Formula este coerentă cu înălțimile: (H−A) este perpendicular pe BC și (H−B) pe CA, deoarece OA²=OB²=OC².")

        X,Y,Z=B+C-A,C+A-B,A+B-C
        K=X+Y+Z-2*H
        add(16, intro+", se construiesc X=B+C−A, Y=C+A−B, Z=A+B−C (coordonate vectoriale). Care sunt coordonatele ortocentrului K al triunghiului anticomplementar XYZ?",
            K, f"Ortocentrul triunghiului ABC este H={pair(H)}. Deoarece X−Y=2(B−A) și mijlocul lui XY este C, înălțimea CH⊥AB este mediatoarea lui XY. Analog, H este circumcentrul lui XYZ. Aplicând Sylvester în XYZ, K=X+Y+Z−2H=A+B+C−2H={pair(K)}. Cele două triunghiuri sunt necoliniare, fiind legate printr-o omotetie de raport −2.")

        ratios=[("OH/OG",S.Integer(3)),("GH/OG",S.Integer(2)),("OG/OH",S.Rational(1,3)),("OG/GH",S.Rational(1,2)),("GH/OH",S.Rational(2,3))]
        target,answer=ratios[j-1]
        assert O!=G and G!=H
        add(17, intro+f", O,G,H sunt circumcentrul, centrul de greutate și ortocentrul. Calculați raportul lungimilor {target}.",
            answer, f"G=(A+B+C)/3={pair(G)}, O={pair(O)}, H={pair(H)}. Din Sylvester rezultă OH=3OG (vectori), deci O,G,H sunt coliniare și G se află între O și H. Punctele sunt distincte pentru triunghiul dat. Avem OH=3OG și GH=2OG; raportul cerut este {answer}. Nu se presupune o dreaptă Euler unică pentru un triunghi echilateral, caz exclus aici.", {"target":target})

        total=(A-N)+(B-N)+(C-N)
        add(18, intro+", O este circumcentrul, H ortocentrul, iar N mijlocul lui OH. Calculați coordonatele sumei vectoriale NA+NB+NC.",
            total, f"O={pair(O)}, H={pair(H)}, N=(O+H)/2={pair(N)}. Din A+B+C=H+2O rezultă NA+NB+NC=A+B+C−3N=H+2O−3(O+H)/2=(O−H)/2=NO={pair(total)}. N este centrul cercului celor nouă puncte; originea N nu poate fi confundată cu circumcentrul O.")

        add(19, intro+", care este pătratul razei cercului celor nouă puncte?",
            R2/4, f"Circumcentrul este O={pair(O)}, deci R²=OA²={R2}. Cercul celor nouă puncte are centrul N=(O+H)/2={pair(N)} și raza R/2, deci pătratul razei este R²/4={R2/4}. Omotetia cu centrul H și raport 1/2 trimite circumcercul pe cercul mijloacelor lui HA,HB,HC; mijloacele laturilor și picioarele înălțimilor se află pe același cerc.")

        antipode=2*O-A
        add(20, intro+", H este ortocentrul, iar D punctul diametral opus lui A pe circumcerc. Patrulaterul BHCD este paralelogram. Determinați coordonatele lui D.",
            antipode, f"O={pair(O)}, deci D=2O−A={pair(antipode)}. Deoarece AD este diametru, BD⊥AB și CD⊥AC. În același timp CH⊥AB și BH⊥AC, astfel BD∥CH și CD∥BH. Rezultă paralelogramul BHCD și D=B+C−H, relație care dă aceeași pereche de coordonate. Triunghiul dat este ascuțit și configurația nu degenerează.")

        feet=[projection(A,B,C),projection(B,C,A),projection(C,A,B)]
        add(21, intro+", E,F,K sunt picioarele înălțimilor din A,B,C. Determinați coordonatele incentrului triunghiului ortic EFK.",
            H, f"Triunghiul ABC este ascuțit (pătratul fiecărei laturi este mai mic decât suma pătratelor celorlalte două), deci ortocentrul H={pair(H)} este interior triunghiului ortic. Patrulaterele dreptunghice inscriptibile formate de picioarele înălțimilor arată că EH,FH,KH sunt bisectoarele interioare ale triunghiului EFK. Prin urmare incentrul lui EFK este H. Pentru triunghiuri obtuze, afirmația despre incentrul interior nu poate fi folosită fără modificări.")

        reflected=2*projection(H,B,C)-H
        add(22, intro+", H este ortocentrul. Care sunt coordonatele simetricului H′ al lui H față de dreapta BC?",
            reflected, f"Ortocentrul este H={pair(H)}. Piciorul perpendicularei pe BC este D={pair(foot)}; A,H,D sunt coliniare. Reflexia are formula H′=2D−H={pair(reflected)}. Într-un triunghi ascuțit, ∠BHC=180°−A; reflexia păstrează unghiurile și H′ se află de cealaltă parte a lui BC, astfel A,B,H′,C sunt conciclice. Echivalent, OH′²=OA².")

        side=S.Integer(j+4)
        add(23, f"Într-un triunghi necoliniar ABC, AB=AC={side}, iar I este incentrul. Dacă suma vectorială IA+IB+IC este zero, cât este BC?",
            side, "Suma nulă dă 3I=A+B+C, deci I coincide cu centrul de greutate G. Formula incentrului I=(aA+bB+cC)/(a+b+c), comparată cu G=(A+B+C)/3, implică ponderi egale: a=b=c, prin independența afină a vârfurilor. "
            +f"Triunghiul este echilateral, deci BC=AB=AC={side}. Reciproc, într-un triunghi echilateral I=G și suma vectorilor este zero.", {"side":side}, own=True)

        add(24, f"În triunghiul necoliniar ABC, AB={side}; D∈BC, E∈CA și F∈AB sunt picioarele bisectoarelor interioare din A,B,C. Dacă AD+BE+CF=0 (sumă de vectori), care este perechea lungimilor (BC; CA)?",
            (side,side), "Notăm a=BC, b=CA, c=AB>0. Teorema bisectoarei dă D=(bB+cC)/(b+c), E=(cC+aA)/(c+a), F=(aA+bB)/(a+b). În suma AD+BE+CF, coeficienții lui A,B,C au suma zero. Independența afină arată că fiecare coeficient este zero; cel al lui A dă a/(a+c)+a/(a+b)=1, adică a²=bc. Analog b²=ac și c²=ab. "
            +f"Pozitivitatea implică a=b=c, deci (BC;CA)=({side};{side}). Reciproc, în cazul echilateral bisectoarele sunt mediane, iar suma celor trei vectori este zero.", {"side":side}, own=True)

        length2=(D-A).dot(D-A)
        add(25, intro+", AD este bisectoarea interioară. Calculați AD².",
            length2, lengths+f"Prin bisectoare, BD={bd} și DC={dc}. Formula metrică obținută din Stewart și BD/DC=c/b este AD²=bc−BD·DC. Prin urmare AD²={b}·{c}−({bd})·({dc})={length2}. Echivalent AD²=bc[1−a²/(b+c)²], pozitiv deoarece a<b+c.")

        projected=projection(M,A,D)
        add(26, intro+", AD este bisectoarea interioară și M mijlocul lui BC. Determinați coordonatele proiecției ortogonale N a lui M pe dreapta AD.",
            projected, f"Bisectoarea are piciorul D={pair(D)}, iar M=(B+C)/2={pair(M)}. Pentru d=D−A≠0, proiecția este N=A+[(M−A)·d/(d·d)]d={pair(projected)}. Astfel N∈AD și MN⊥AD. Proiecția este o aplicație afină: N este și mijlocul proiecțiilor lui B și C pe AD. Aceasta justifică relația cu liniile mijlocii; nu susține teorema mai dificilă a alinierii celor patru proiecții din configurația originală de catalog.")
    assert len(questions)==130 and len({q["text"] for q in questions})==130
    return sorted(questions,key=lambda q:(q["practice_scope"]["family"],q["practice_scope"]["variant"]))


def update_file(path=TARGET):
    path=Path(path)
    data=json.loads(path.read_text(encoding="utf-8"))
    existing=[q for q in data["questions"] if q.get("practice_scope",{}).get("bank")!=BANK]
    data["questions"]=existing+build_questions()
    data["difficulty"]="hard"
    path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    return len(data["questions"])


if __name__=="__main__":
    print(f"{update_file()} questions; 130 original grids; no database import.")
