"""85 original grids inspired by G2 section 4 (17 types x 5 variants).

Exact rational geometry. These are explicitly identified numeric cases or
conclusion adaptations, not reproductions of the book's olympiad proofs.
No Django import or database writes. Retain questions owned by other banks.
"""
import json
from fractions import Fraction as F
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / 'clasa_9/clasa_9_u06_l05_teorema_lui_menelau.json'
BANK = 'g2_menelau_v1'
CONVENTION = ('Folosim rapoarte orientate: dacă X=U+t(V−U), atunci '
              'UX/XV=t/(1−t). Raportul este pozitiv în interior și negativ '
              'în exterior. Pentru D∈BC, E∈CA, F∈AB coliniare, '
              '(BD/DC)(CE/EA)(AF/FB)=−1.')
TYPE_NAMES = {
    1: 'Picioarele bisectoarelor exterioare', 2: 'Raportul unei transversale',
    3: 'Bisectoare și transversală', 4: 'Configurație de trapez cu punct mobil',
    5: 'Relație multiplicativă într-un patrulater',
    6: 'Coliniaritate din simetrii centrale', 7: 'Mijloace coliniare ale segmentelor',
    8: 'Transferul concurenței într-un patrulater',
    9: 'Concurență din bisectoare în triunghiuri auxiliare',
    10: 'Dreapta Newton–Gauss', 11: 'Relația lui Van Aubel',
    12: 'Teorema lui Pappus', 13: 'Teorema lui Desargues',
    14: 'Simetrice ale unei transversale', 15: 'Concurență prin teorema lui Ceva',
    16: 'Caracterizarea circumcentrului din rapoarte', 17: 'Teorema lui Pascal',
}


def add(a, b): return tuple(F(x)+F(y) for x, y in zip(a, b))
def sub(a, b): return tuple(F(x)-F(y) for x, y in zip(a, b))
def mul(k, a): return tuple(F(k)*F(x) for x in a)
def det(a, b): return a[0]*b[1]-a[1]*b[0]
def pair(a): return '('+'; '.join(str(F(x)) for x in a)+')'
def serial(a): return [str(F(x)) for x in a]


def intersect(a, b, c, d):
    """Finite intersection of two different nonparallel affine lines."""
    u, v = sub(b, a), sub(d, c)
    denominator = det(u, v)
    assert denominator != 0
    return add(a, mul(F(det(sub(c, a), v), denominator), u))


def ratio(u, x, v):
    direction = sub(v, u)
    assert direction != (0, 0) and det(sub(x, u), direction) == 0
    i = 0 if direction[0] else 1
    t = F(x[i]-u[i], direction[i])
    assert t != 1
    return t/(1-t)


def midpoint(a, b): return mul(F(1, 2), add(a, b))


def build_questions():
    questions = []

    def emit(typ, j, text, answer, explanation, givens, *, choices=None,
             adaptation='caz numeric explicit; nu este demonstrația generală a tipului din catalog'):
        if choices is None:
            if isinstance(answer, tuple):
                values = [answer, add(answer, (1, 0)), add(answer, (0, 1)), add(answer, (-1, -1))]
                options = [pair(value) for value in values]
            else:
                options = [str(F(answer)+offset) for offset in (0, 1, -1, 2)]
        else:
            options = [answer, *choices]
        assert len(options) == len(set(options)) == 4
        result_text = pair(answer) if isinstance(answer, tuple) else str(answer)
        correct = len(questions) % 4
        options.insert(correct, options.pop(0))
        questions.append({
            'text': text, 'type': 'multiple_choice', 'format': 'grid', 'points': 10,
            'explanation': explanation+' Rezultatul este '+result_text+'.',
            'options': [{'text': value, 'is_correct': index == correct} for index, value in enumerate(options)],
            'practice_scope': {'bank': BANK, 'catalog': 'G2', 'section': '4', 'type': typ,
                               'type_name': TYPE_NAMES[typ], 'variant': j,
                               'reference_pages': '201' if typ <= 5 else ('202' if typ <= 13 else '203'),
                               'adaptation': adaptation},
            'verification': givens,
        })

    for j in range(1, 6):
        s = j+1
        a, b, c = (0, 0), (4*s, 0), (0, 3*s)
        # Scalene 3-4-5 triangle: all three exterior feet are finite.
        d, e, f = (-12*s, 12*s), (0, -12*s), (-6*s, 0)
        emit(1, j,
             f'În triunghiul dreptunghic A{pair(a)}, B{pair(b)}, C{pair(c)}, D∈dreapta BC, E∈dreapta CA, F∈dreapta AB sunt picioarele bisectoarelor exterioare din A,B,C. Determinați coordonatele lui D și folosiți explicația pentru a verifica alinierea D,E,F.',
             d,
             f'Laturile sunt AB={4*s}, AC={3*s}, BC={5*s}, toate diferite, deci picioarele exterioare sunt finite. '
             +'Cu convenția UX/XV=t/(1−t), teorema bisectoarei exterioare dă BD/DC=−AB/AC=−4/3. '
             +'D=B+t(C−B), t/(1−t)=−4/3, deci t=4. Celelalte rapoarte sunt CE/EA=−5/4 și AF/FB=−3/5; produsul este −1, deci Menelau dă coliniaritatea. '
             +f'În acest caz E{pair(e)}, F{pair(f)}, iar F este chiar mijlocul lui DE.',
             {'A': serial(a), 'B': serial(b), 'C': serial(c)})

        a, b, c = (0, 0), (6*s, 0), (0, 6*s)
        m = midpoint(b, c); t = F(j+1, j+2)
        p = add(a, mul(t, sub(m, a))); x = (s, 0)
        y = intersect(x, p, c, a); z = intersect(x, p, b, c)
        emit(2, j,
             f'A{pair(a)}, B{pair(b)}, C{pair(c)}. M este mijlocul lui BC, P∈AM are AP:PM={j+1}:1, iar X∈AB are AX:XB=1:5. Dreapta XP taie CA în Y și BC în Z. Calculați raportul orientat CY/YA (negativ pentru Y exterior lui CA).',
             ratio(c, y, a),
             f'Avem M{pair(m)}, P{pair(p)}, X{pair(x)}. Intersecțiile sunt Y{pair(y)}, Z{pair(z)}. '
             +f'Y este exterior segmentului CA. Menelau în ABC dă (AX/XB)(BZ/ZC)(CY/YA)=−1. Aici AX/XB=1/5 și BZ/ZC={ratio(b,z,c)}, deci CY/YA={ratio(c,y,a)}. ',
             {'A': serial(a), 'B': serial(b), 'C': serial(c), 'P': serial(p), 'X': serial(x), 'median_parameter': str(t)})

        a, b, c = (0, 0), (4*s, 0), (0, 3*s)
        d = (F(12*s, 7), F(12*s, 7))
        e = (0, F(3*s*j, j+1)); p = intersect(a, d, b, e)
        emit(3, j,
             f'A{pair(a)}, B{pair(b)}, C{pair(c)}. AD este bisectoarea interioară, D∈BC. E∈AC verifică AE:EC={j}:1, iar P=BE∩AD. Calculați raportul pozitiv AP/PD.',
             ratio(a, p, d),
             f'Bisectoarea dă BD/DC=AB/AC=4/3 și D{pair(d)}. Din AE:EC={j}:1 rezultă E{pair(e)}. '
             +f'P{pair(p)} este interior lui AD. Aplicăm Menelau în ADC cu transversala B,E,P: (DB/BC)(CE/EA)(AP/PD)=−1. '
             +f'DB/BC=−4/7 și CE/EA=1/{j}, de unde AP/PD=7·{j}/4.',
             {'A': serial(a), 'B': serial(b), 'C': serial(c), 'E': serial(e)})

        h = 3*s
        a, b, c, d = (-6*s, 0), (6*s, 0), (2*s, h), (-2*s, h)
        p = (0, F(h*(j+1), j+2)); m = (0, 0)
        x = intersect(a, p, c, d); y = intersect(b, p, c, d)
        emit(4, j,
             f'Trapezul isoscel ABCD are A{pair(a)}, B{pair(b)}, C{pair(c)}, D{pair(d)}. M este mijlocul lui AB, iar P{pair(p)} este pe axa de simetrie. Notăm X=AP∩dreapta CD și Y=BP∩dreapta CD. Care este raportul lungimilor MX/MY?',
             F(1),
             f'Prin parametrizare sau Thales rezultă X{pair(x)}, Y{pair(y)}. Ele au ordonate egale și abscise opuse. '
             +'Cum M=(0;0), pătratele distanțelor MX și MY sunt egale și strict pozitive. '
             +'Este un caz particular simetric al configurațiilor cu trapez și punct mobil; nu demonstrează afirmația olimpică generală a catalogului.',
             {'A': serial(a), 'B': serial(b), 'C': serial(c), 'D': serial(d), 'P': serial(p)},
             adaptation='adaptare parțială: trapez isoscel și punct pe axa de simetrie')

        a, b, c, d = (0, 0), (6*s, 0), (6*s, 4*s), (0, 4*s)
        intercept = F(s*j, j+1)
        line1, line2 = (intercept, 0), (intercept+1, 1)
        e = intersect(line1, line2, a, b); f = intersect(line1, line2, b, c)
        g = intersect(line1, line2, c, d); h = intersect(line1, line2, d, a)
        ratios = [ratio(a,e,b), ratio(b,f,c), ratio(c,g,d), ratio(d,h,a)]
        emit(5, j,
             f'O transversală neparalelă cu AC taie dreptele AB,BC,CD,DA ale unui patrulater convex în E,F,G,H, fără a trece prin vârfuri. Se cunosc rapoartele orientate AE/EB={ratios[0]}, BF/FC={ratios[1]}, CG/GD={ratios[2]}. Determinați DH/HA; convenția este UX/XV=t/(1−t) pentru X=U+t(V−U).',
             ratios[3],
             'Dacă T este intersecția transversalei cu AC, Menelau în ABC și ACD dă două produse egale cu −1. '
             +'Înmulțind, rapoartele CT/TA și AT/TC se simplifică. Rezultă (AE/EB)(BF/FC)(CG/GD)(DH/HA)=1. '
             +f'Înlocuind cele trei valori, obținem DH/HA={ratios[3]}; semnul negativ arată că H este exterior lui DA. '
             +f'Există configurația explicită A{pair(a)}, B{pair(b)}, C{pair(c)}, D{pair(d)} și transversală y=x−({intercept}).',
             {'A': serial(a), 'B': serial(b), 'C': serial(c), 'D': serial(d), 'line': [serial(line1), serial(line2)], 'ratios': [str(r) for r in ratios[:3]]})

        a, b, c = (0, 0), (6*s, 0), (0, 4*s)
        t = F(j, 2*j+1); p = add(b, mul(t, sub(c, b)))
        m, n = midpoint(a,b), midpoint(a,c)
        d, e = sub(mul(2,m),p), sub(mul(2,n),p)
        emit(6, j,
             f'A{pair(a)}, B{pair(b)}, C{pair(c)}. P∈BC are BP:PC={j}:{j+1}. M,N sunt mijloacele lui AB,AC. D și E sunt simetricele lui P față de M,N. Punctele A,D,E sunt coliniare. Calculați raportul lungimilor AD/AE.',
             F(j,j+1),
             'Simetria centrală dă D=A+B−P și E=A+C−P. Așadar AD=B−P, AE=C−P; deoarece B,P,C sunt coliniare, și A,D,E sunt coliniare. '
             +f'Cum P este interior lui BC, AD=BP și AE=PC ca lungimi, deci AD/AE={j}/{j+1}. În acest caz D{pair(d)}, E{pair(e)}.',
             {'A': serial(a), 'B': serial(b), 'C': serial(c), 'P': serial(p)})

        q = midpoint(a,p)
        emit(7, j,
             f'A{pair(a)}, B{pair(b)}, C{pair(c)}. P∈BC are BP:PC={j}:{j+1}. M,N,Q sunt mijloacele lui AB,AC,AP. Determinați MQ/QN, ca raport de lungimi, și consultați explicația pentru alinierea mijloacelor.',
             F(j,j+1),
             'Omotetia de centru A și raport 1/2 trimite B,P,C în M,Q,N. Deci M,Q,N sunt coliniare, Q este interior lui MN și MQ/QN=BP/PC. '
             +f'Explicit M{pair(m)}, Q{pair(q)}, N{pair(n)}. Este o adaptare în triunghi de mijloace, fără reproducerea configurației complete din culegere.',
             {'A': serial(a), 'B': serial(b), 'C': serial(c), 'P': serial(p)},
             adaptation='adaptare parțială: aliniere într-un triunghi de mijloace')

        a, b, c, d = (0,0), (6*s,0), (6*s,4*s), (0,4*s)
        t, m, pp = (F(12*s,5),F(8*s,5)), (s,0), (3*s,4*s)
        n = intersect(m,t,b,c); q = intersect(pp,t,d,a)
        v = intersect(n,pp,m,q)
        emit(8, j,
             f'ABCD este dreptunghiul A{pair(a)}, B{pair(b)}, C{pair(c)}, D{pair(d)}. T{pair(t)}∈AC, M{pair(m)}∈AB și P{pair(pp)}∈CD. N=MT∩dreapta BC și Q=PT∩dreapta DA. Aflați V=NP∩MQ; explicația verifică faptul că V∈BD.',
             v,
             f'Prin intersecții finite obținem N{pair(n)}, Q{pair(q)}, apoi V{pair(v)}. '
             +f'Ecuația diagonalei BD este x/({6*s})+y/({4*s})=1, verificată de V. Astfel concurența MN,PQ,AC în T se transferă, în acest caz explicit, la NP,MQ,BD în V.',
             {'A': serial(a), 'B': serial(b), 'C': serial(c), 'D': serial(d), 'T': serial(t), 'M': serial(m), 'P': serial(pp)})

        a, b, c = (0,0), (4*s,0), (0,3*s)
        e, f = (0,F(4*s,3)), (F(3*s,2),0)
        p = intersect(b,e,c,f)
        emit(9, j,
             f'În triunghiul A{pair(a)}, B{pair(b)}, C{pair(c)}, BE și CF sunt bisectoarele interioare, E∈CA, F∈AB. AD este a treia bisectoare. Aflați P=BE∩CF și verificați în explicație P∈AD.',
             p,
             f'Teorema bisectoarei dă CE/EA=5/4 și AF/FB=3/5, deci E{pair(e)}, F{pair(f)}. Intersecția este P{pair(p)}. '
             +'Deoarece AB și AC sunt perpendiculare pe axe, bisectoarea interioară din A are ecuația y=x, pe care P o satisface. '
             +'Produsul cu BD/DC=4/3 este 1, în acord cu Ceva. Este cazul particular al bisectoarelor triunghiului inițial, nu o demonstrație a oricărei configurații auxiliare.',
             {'A': serial(a), 'B': serial(b), 'C': serial(c)},
             adaptation='adaptare parțială: concurența bisectoarelor în triunghiul dreptunghic 3-4-5')

        a, b, c, d = (0,0), (6*s,0), (5*s,4*s), (s,3*s)
        e = intersect(a,b,c,d); f = intersect(a,d,b,c)
        k = midpoint(e,f); m,n = midpoint(a,c),midpoint(b,d)
        emit(10, j,
             f'Patrulaterul complet este determinat de dreptele AB,BC,CD,DA, unde A{pair(a)}, B{pair(b)}, C{pair(c)}, D{pair(d)}. E=AB∩CD și F=AD∩BC. Aflați mijlocul K al lui EF; verificați dreapta Newton–Gauss prin mijloacele lui AC și BD.',
             k,
             f'Intersecțiile sunt E{pair(e)}, F{pair(f)}, deci K=(E+F)/2={pair(k)}. Mijloacele diagonalelor AC și BD sunt M{pair(m)}, N{pair(n)}. '
             +'Calculul determinantului (N−M,K−M) dă zero; M,N sunt distincte. Acesta verifică efectiv dreapta Newton–Gauss în configurația dată.',
             {'A': serial(a), 'B': serial(b), 'C': serial(c), 'D': serial(d)})

        a, b, c = (0,0), (6*s,0), (0,4*s)
        x,y,z = j+1,2,3
        p = mul(F(1,x+y+z),add(add(mul(x,a),mul(y,b)),mul(z,c)))
        emit(11, j,
             f'În triunghiul A{pair(a)}, B{pair(b)}, C{pair(c)}, cevienele AD,BE,CF sunt concurente în punctul interior P; D∈BC,E∈CA,F∈AB. Dacă AE/EC={F(z,x)} și AF/FB={F(y,x)}, aflați AP/PD (rapoarte pozitive de lungimi).',
             F(y+z,x),
             f'Relația lui Van Aubel este AP/PD=AE/EC+AF/FB, deci suma este {F(z,x)}+{F(y,x)}={F(y+z,x)}. '
             +f'O justificare afină: pentru P cu ponderi pozitive ({x},{y},{z}) la A,B,C, cele trei rapoarte sunt ({y}+{z})/{x}, {z}/{x}, {y}/{x}; identitatea urmează prin adunare. Configurația efectivă are P{pair(p)}.',
             {'A': serial(a), 'B': serial(b), 'C': serial(c), 'weights':[x,y,z]})

        a,b,c = (0,0),(2*s,0),(5*s,0)
        aa,bb,cc = (s,5*s),(4*s,5*s),(8*s,5*s)
        x,y,z = intersect(a,bb,aa,b),intersect(a,cc,aa,c),intersect(b,cc,bb,c)
        emit(12, j,
             f'A{pair(a)}, B{pair(b)}, C{pair(c)} sunt pe o dreaptă; A′{pair(aa)}, B′{pair(bb)}, C′{pair(cc)} pe alta. X=AB′∩A′B, Y=AC′∩A′C, Z=BC′∩B′C. Determinați Z și verificați în explicație coliniaritatea Pappus.',
             z,
             f'Rezolvând sistemele liniilor se obțin X{pair(x)}, Y{pair(y)}, Z{pair(z)}; toate intersecțiile sunt finite și distincte. '
             +'Determinantul (Y−X,Z−X) este zero, confirmând teorema lui Pappus pentru cele două triplete date. Acest calcul explicit nu ține locul demonstrației generale.',
             {'A':serial(a),'B':serial(b),'C':serial(c),'A_prime':serial(aa),'B_prime':serial(bb),'C_prime':serial(cc)})

        a,b,c = (s,s),(4*s,s),(2*s,4*s)
        aa,bb,cc = mul(2,a),mul(3,b),mul(4,c)
        x,y,z = intersect(a,b,aa,bb),intersect(b,c,bb,cc),intersect(c,a,cc,aa)
        emit(13, j,
             f'O=(0;0), A{pair(a)}, B{pair(b)}, C{pair(c)}. A′=2A, B′=3B, C′=4C (vectori de poziție față de O), deci AA′,BB′,CC′ sunt concurente în O. X=AB∩A′B′, Y=BC∩B′C′, Z=CA∩C′A′. Aflați Z și verificați axa de perspectivă.',
             z,
             f'Triunghiurile sunt nedegenerate, iar intersecțiile laturilor omoloage sunt finite: X{pair(x)}, Y{pair(y)}, Z{pair(z)}. '
             +'Determinantul (Y−X,Z−X) este zero; astfel cele trei puncte sunt coliniare, în acord cu Desargues. Este verificarea unui caz în perspectivă, nu demonstrația generală.',
             {'A':serial(a),'B':serial(b),'C':serial(c),'factors':[2,3,4]})

        a,b,c = (0,0),(6*s,0),(0,4*s)
        line1,line2 = (s,0),(s+1,1)
        d,e,f = intersect(line1,line2,b,c),intersect(line1,line2,c,a),intersect(line1,line2,a,b)
        dd,ee,ff = sub(add(b,c),d),sub(add(c,a),e),sub(add(a,b),f)
        emit(14, j,
             f'A{pair(a)}, B{pair(b)}, C{pair(c)}. Dreapta y=x−{s} taie BC,CA,AB în D,E,F. Reflectăm D,E,F față de mijloacele laturilor corespunzătoare, obținând D′,E′,F′. Aflați raportul orientat AF′/F′B și verificați alinierea simetricelor.',
             ratio(a,ff,b),
             f'Din intersecții rezultă D{pair(d)}, E{pair(e)}, F{pair(f)}. Simetriile dau D′{pair(dd)}, E′{pair(ee)}, F′{pair(ff)}. '
             +'Reflectarea față de mijloc schimbă parametrul t în 1−t, deci inversează raportul orientat. Produsul Menelau −1 rămâne −1 după inversare, iar simetricele sunt coliniare. '
             +f'Aici F′ este interior lui AB, iar AF′/F′B={ratio(a,ff,b)}.',
             {'A':serial(a),'B':serial(b),'C':serial(c),'line':[serial(line1),serial(line2)]})

        a,b,c,p = (0,0),(4*s,0),(0,3*s),(s,s)
        emit(15, j,
             f'P{pair(p)} este interior triunghiului A{pair(a)}, B{pair(b)}, C{pair(c)}. Bisectoarele interioare din P în triunghiurile PBC,PCA,PAB taie BC,CA,AB în D,E,F. Ce rezultă despre AD,BE,CF?',
             'Sunt concurente într-un punct finit interior triunghiului ABC.',
             'Teorema bisectoarei în cele trei triunghiuri auxiliare dă BD/DC=PB/PC, CE/EA=PC/PA și AF/FB=PA/PB. '
             +'Toate lungimile sunt pozitive și produsul este 1. Reciproca lui Ceva dă concurența. Picioarele sunt interioare laturilor, iar primele două ceviene au intersecție interioară, deci concurența este finită. Nu se afirmă că punctul comun este P.',
             {'A':serial(a),'B':serial(b),'C':serial(c),'P':serial(p)},
             choices=['Sunt toate paralele.', 'Sunt concurente obligatoriu în P.', 'Nu pot fi concurente.'],
             adaptation='concluzie Ceva cu demonstrație pentru bisectoarele unghiurilor auxiliare dintr-un punct interior')

        a,b,c = (-3*s,0),(3*s,0),(0,4*s)
        m = (0,F(7*s,8))
        emit(16, j,
             f'A{pair(a)}, B{pair(b)}, C{pair(c)}. Aflați unicul punct M pentru care rapoartele lungimilor MA/MB și MB/MC sunt ambele 1. Lungimile din numitori trebuie să fie nenule.',
             m,
             'Egalitățile rapoartelor înseamnă MA=MB=MC>0, adică M este circumcentrul. Din MA²=MB² rezultă xM=0. '
             +f'Apoi 9·({s})²+yM²=(4·{s}−yM)², de unde yM={F(7*s,8)}. Triunghiul este nedegenerat și punctul obținut are toate cele trei distanțe nenule. '
             +'Aceasta este numai o caracterizare explicită prin rapoarte de distanțe; nu pretinde echivalența olimpică cu rapoarte pe ceviene și Van Aubel din catalog.',
             {'A':serial(a),'B':serial(b),'C':serial(c)},
             adaptation='adaptare parțială declarată: circumcentru din rapoarte de distanțe egale cu 1; fără echivalența Van Aubel neprecizată de catalog')

        parameters = [-3,-1,0,1,2,4]
        points = [mul(s, (F(1-t*t,1+t*t),F(2*t,1+t*t))) for t in parameters]
        a,b,c,d,e,f = points
        x,y,z = intersect(a,b,d,e),intersect(b,c,e,f),intersect(c,d,f,a)
        emit(17, j,
             f'Cele șase puncte distincte A{pair(a)}, B{pair(b)}, C{pair(c)}, D{pair(d)}, E{pair(e)}, F{pair(f)} sunt pe cercul x²+y²={s*s}. X=AB∩DE, Y=BC∩EF și Z=CD∩FA. Determinați Z și verificați în explicație coliniaritatea Pascal.',
             z,
             f'Fiecare punct verifică x²+y²={s*s}. Intersecțiile finite sunt X{pair(x)}, Y{pair(y)}, Z{pair(z)}. '
             +'Calculând determinantul (Y−X,Z−X) obținem zero; X și Y sunt distincte. Acesta verifică teorema lui Pascal pentru hexagonul înscris dat, fără a înlocui demonstrația generală bazată pe Menelau și puterea punctului.',
             {**{name:serial(value) for name,value in zip('ABCDEF',points)},'radius':s})

    assert len(questions) == 85
    assert len({question['text'] for question in questions}) == 85
    return questions


def update_file():
    data = json.loads(TARGET.read_text(encoding='utf-8'))
    retained = [question for question in data['questions'] if question.get('practice_scope',{}).get('bank') != BANK]
    data['difficulty'] = 'hard'
    data['questions'] = retained+build_questions()
    TARGET.write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    return len(data['questions'])


if __name__ == '__main__':
    print(f'{update_file()} questions; 85 original Menelaus grids; no DB import.')
