"""240 original grids: five adaptations of each G1 §2.1/§2.2 type.

Proof tasks become conclusions or explicit cases, with the argument in the
explanation. This is not a claim to reproduce the full original proofs.
"""
import json
from fractions import Fraction as F
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGET = next((ROOT / 'clasa_9').glob('clasa_9_u05_l03_*.json'))
BANK = 'vectori_operatii_grile_v1'


def add(a, b): return tuple(F(x)+F(y) for x, y in zip(a, b))
def sub(a, b): return tuple(F(x)-F(y) for x, y in zip(a, b))
def mul(k, a): return tuple(F(k)*F(x) for x in a)
def pair(a): return '('+'; '.join(str(F(x)) for x in a)+')'
def serial(a): return [str(F(x)) for x in a]


def build_questions():
    questions = []

    def emit(section, typ, variant, text, answer, explanation, givens, choices=None, adaptation='calcul într-un caz explicit'):
        if choices is None:
            if isinstance(answer, tuple):
                values = [answer, add(answer, (1, 0)), add(answer, (0, 1)), add(answer, (-1, -1))]
                choices = [pair(value) for value in values]
            else:
                choices = [str(F(answer)+offset) for offset in (0, 1, -1, 2)]
        else:
            choices = [answer, *choices]
        assert len(choices) == len(set(choices)) == 4, (section, typ, variant)
        correct = len(questions) % 4
        choices.insert(correct, choices.pop(0))
        questions.append({
            'text': text, 'type': 'multiple_choice', 'format': 'grid', 'points': 10,
            'explanation': explanation + (f' Rezultatul este {pair(answer)}.' if isinstance(answer, tuple) else ''),
            'options': [{'text': value, 'is_correct': i == correct} for i, value in enumerate(choices)],
            'practice_scope': {'bank': BANK, 'catalog': 'G1', 'section': section, 'type': typ,
                               'variant': variant, 'adaptation': adaptation,
                               'reference_pages': '163–169' if section == '2.1' else '170–175'},
            'verification': givens,
        })

    for j in range(1, 6):
        a, b, c, d = (j, -j), (3*j+1, j+2), (-j-2, 4*j+1), (2*j+3, -2*j-1)
        u, v = sub(b, a), sub(c, a)
        pts = {name: serial(value) for name, value in zip('ABCD', (a, b, c, d))}

        def vector(typ, text, answer, explanation, given=None, **kwargs):
            emit('2.1', typ, j, text, answer, explanation, given or pts, **kwargs)

        vector(1, f'Punctele considerate sunt A{pair(a)}, B{pair(b)}, C{pair(c)}. Calculați vectorul AB + BC.', sub(c, a),
               'Regula triunghiului dă AB+BC=AC, deoarece vârful primului este originea celui de-al doilea. Scădem coordonatele lui A din cele ale lui C.')
        vector(2, f'În paralelogramul ABCD, A{pair(a)}, B{pair(b)}, D{pair(d)}. Calculați AB+AD.', add(u, sub(d, a)),
               'Regula paralelogramului: AB+AD=AC. Punctul C are poziția B+D−A, deci AC=B+D−2A.')
        vector(3, f'Pentru A{pair(a)}, B{pair(b)}, C{pair(c)}, D{pair(d)}, aflați AB+CD.', add(u, sub(d, c)),
               'Transportăm CD cu originea în B, fără a-i schimba direcția, sensul sau lungimea. Pe componente, rezultanta este (B−A)+(D−C).')
        vector(4, f'În patrulaterul cu A{pair(a)}, B{pair(b)}, C{pair(c)}, D{pair(d)}, calculați AB+DC și comparați cu AC+DB.', add(u, sub(c, d)),
               'Pentru orice patru puncte, AB+DC=(B−A)+(C−D)=B+C−A−D=(C−A)+(B−D)=AC+DB. Identitatea nu cere ca patrulaterul să fie paralelogram.')
        vector(5, f'Pentru A{pair(a)}, B{pair(b)}, C{pair(c)}, D{pair(d)}, calculați BA−CD.', sub(sub(a, b), sub(d, c)),
               'BA=−AB, iar scăderea lui CD înseamnă adunarea lui DC. Prin urmare BA−CD=(A−B)+(C−D).')
        vector(6, f'În triunghiul ABC, A{pair(a)}, B{pair(b)}, C{pair(c)}, M este mijlocul lui BC. Calculați AB+AC.', add(u, v),
               'M=(B+C)/2. Atunci AB+AC=B+C−2A=2(M−A)=2AM. Aceasta este formula vectorială a medianei.')
        vector(7, f'A{pair(a)}, B{pair(b)}, C{pair(c)} sunt fixe, iar M este mobil în plan. Ce vector constant este AM+BC−BM?', sub(c, a),
               'Scriem prin poziții: (M−A)+(C−B)−(M−B)=C−A=AC. Termenii cu M se anulează pentru orice poziție, nu doar într-un exemplu.', adaptation='identitate demonstrată prin anularea punctului mobil')
        lengths = [j+1, j+2, 2*j+4]
        vector(8, f'Pot trei vectori de lungimi {lengths[0]}, {lengths[1]} și {lengths[2]} să aibă suma nulă?',
               'Nu, lungimea maximă depășește suma celorlalte două.',
               f'Dacă u+v+w=0, atunci |w|=|u+v|≤|u|+|v|. Dar {lengths[2]}>{lengths[0]}+{lengths[1]}, contradicție.',
               {'lengths': lengths}, choices=['Da, pentru orice direcții.', 'Da, dacă cei trei vectori sunt necoliniari.', 'Da, dacă vectorul cel mai lung are sens opus celorlalți.'])
        vector(9, f'Doi vectori perpendiculari au lungimile {3*j} și {4*j}. Care este modulul sumei lor?', F(5*j),
               f'În paralelogram unghiul este drept. Prin Pitagora, |u+v|²=({3*j})²+({4*j})²=({5*j})².', {'legs': [3*j, 4*j]})
        vector(10, f'A{pair(a)}, B{pair(b)}, C{pair(c)} sunt trei vârfuri consecutive ale unui paralelogram ABCD. Determinați D.', add(a, sub(c, b)),
               'Diagonalele au același mijloc: A+C=B+D, deci D=A+C−B. Reciproc, această relație dă AD=BC și AB=DC.')
        vector(11, f'A{pair(a)}, B{pair(b)}, C{pair(c)}. Aflați D astfel încât AD=AB+AC.', sub(add(b, c), a),
               'Ecuația este D−A=(B−A)+(C−A), de unde D=B+C−A. O translație cu vector prescris are un singur vârf pentru o origine fixată.')
        vector(12, f'A{pair(a)}, B{pair(b)}. Aflați O pentru care OA+OB=0.', mul(F(1, 2), add(a, b)),
               'A−O+B−O=0, deci 2O=A+B. Punctul O este mijlocul segmentului AB.')
        vector(13, f'În paralelogramul ABCD, AB=u și AD=v. Pentru u={pair(u)}, v={pair(v)}, calculați DB.', sub(u, v),
               'DB=DA+AB=−v+u. Ordinea extremităților este esențială: BD ar fi v−u.', {'u': serial(u), 'v': serial(v)})
        vector(14, f'Trei puncte distincte A, B, C sunt la distanța {j+2} de O și OA+OB+OC=0. Ce natură are triunghiul ABC?',
               'Echilateral.',
               'Din OA+OB=−OC și egalitatea modulelor R>0 rezultă R²=2R²+2 OA·OB, deci OA·OB=−R²/2. Analog pentru celelalte perechi. Toate pătratele laturilor sunt 3R², deci laturile sunt egale.',
               {'radius': j+2}, choices=['Dreptunghic.', 'Isoscel neechilateral.', 'Degenerat.'], adaptation='concluzie geometrică cu demonstrație')
        vector(15, f'Patru puncte distincte A, B, C, D sunt pe cercul de centru O și rază {j+3}, iar OA+OB+OC+OD=0. Ce se poate spune despre patrulaterul lor convex, luat în ordine pe cerc?',
               'Este dreptunghi, posibil pătrat.',
               'Dacă suma unei perechi de vectori de rază R este nenulă, mijlocul coardei și perpendicularitatea pe ea determină unic perechea neordonată de extremități. Perechea cu sumă opusă este perechea diametral opusă. Dacă suma este zero, perechea este deja diametrală, la fel și cealaltă. Cele patru puncte distincte se grupează deci în două diametre. Unghiurile înscrise ce subîntind diametre sunt drepte.',
               {'radius': j+3}, choices=['Este obligatoriu pătrat.', 'Este obligatoriu romb nepătrat.', 'Poate fi un trapez cu exact o pereche de laturi paralele.'], adaptation='concluzie geometrică cu ipoteze de nedegenerare')
        vector(16, f'Față de O se cunosc OA={pair(a)}, OB={pair(b)}, OC={pair(c)}. Aflați OD astfel încât OA+OB+OC+OD=0.', mul(-1, add(add(a, b), c)),
               'Pentru a închide poligonul vectorial, ultimul vector este opusul sumei celor cunoscuți: OD=−(OA+OB+OC).')
        # Basis answers are ordered coefficients, not Cartesian components.
        target = add(mul(j+1, u), mul(-j, v))
        vector(17, f'Vectorii necoliniari u={pair(u)}, v={pair(v)} sunt direcții de descompunere. Pentru w={pair(target)}, aflați perechea (α; β) din w=αu+βv.', (F(j+1), F(-j)),
               'Egalăm cele două componente și rezolvăm sistemul liniar. Determinantul bazei este nenul, deci descompunerea este unică; coeficienții se verifică înlocuind în αu+βv.',
               {'u': serial(u), 'v': serial(v), 'w': serial(target)})
        vector(18, f'B′ și C′ sunt simetricele lui B{pair(b)} și C{pair(c)} față de A{pair(a)}. Calculați AB′+AC′.', mul(-1, add(u, v)),
               'Simetria centrală dă B′=2A−B și C′=2A−C. Astfel AB′=−AB, AC′=−AC, iar suma este −(AB+AC).')
        vector(19, f'Pentru A{pair(a)}, B{pair(b)}, C{pair(c)}, D{pair(d)}, M este mijlocul lui AB, N al lui CD. Calculați 2MN.', sub(add(c, d), add(a, b)),
               '2MN=2(N−M)=C+D−A−B=AC+BD. Formula rezultă direct din mediile coordonatelor, pentru orice patrulater.')
        vector(20, f'În paralelogramul ABCD, A{pair(a)}, B{pair(b)}, C{pair(c)}. P este simetricul punctului M{pair(d)} față de mijlocul lui AB. Aflați P.', sub(add(a, b), d),
               'Dacă E=(A+B)/2 și E este și mijlocul lui MP, atunci P=2E−M=A+B−M. Pentru cele patru mijloace ale laturilor unui paralelogram rezultă P+R=Q+S, deci simetricele au diagonalele cu același mijloc.', adaptation='calculul unui simetric și explicarea paralelogramului derivat')
        vector(21, f'Vectorii nenuli u și v au aceeași lungime {j+1}; unghiul dintre ei este strict între 0° și 180°. Ce direcție și sens are u+v?',
               'Sensul bisectoarei interioare a unghiului dintre u și v.',
               'Paralelogramul construit pe u,v este un romb. Diagonala spre vârful opus originii, adică u+v, bisectează unghiul interior. Excluderea unghiului de 180° asigură că suma nu este nulă.',
               {'length': j+1}, choices=['Sensul opus bisectoarei interioare.', 'Direcția bisectoarei exterioare.', 'Suma este obligatoriu nulă.'], adaptation='identificarea direcției cu condiții explicite')
        vector(22, f'A{pair(a)}, B{pair(b)}, C{pair(c)}, D{pair(d)}. Aflați unicul O pentru care OA+OB+OC+OD=0.', mul(F(1, 4), add(add(a, b), add(c, d))),
               'Suma este A+B+C+D−4O. Prin urmare O=(A+B+C+D)/4 există și este unic, deoarece coeficientul 4 este nenul.')
        vector(23, f'Se știe numai că |u|={j+2} și |v|={2*j+1}. Care este cea mai mică bornă superioară valabilă pentru toate direcțiile lui |u+v|?', F(3*j+3),
               'Inegalitatea triunghiulară dă |u+v|≤|u|+|v|. Borna este atinsă dacă vectorii au aceeași direcție și același sens, deci nu poate fi micșorată.', {'lengths': [j+2, 2*j+1]})
        vector(24, f'Vectorii u,v au lungimi strict pozitive {j+1} și {j+4}. Când este |u+v|=|u|+|v|?',
               'Când sunt coliniari și au același sens.',
               'Ridicând la pătrat rezultă u·v=|u||v|. Pentru vectori nenuli aceasta înseamnă cos θ=1, adică același sens. Dacă unul era nul, egalitatea era automată, dar cazul este exclus în enunț.',
               {'lengths': [j+1, j+4]}, choices=['Când au sensuri opuse.', 'Când sunt perpendiculari.', 'Pentru orice direcții dacă lungimile sunt egale.'], adaptation='caracterizarea cazului de egalitate')
        vector(25, f'În patrulaterul cu A{pair(a)}, B{pair(b)}, C{pair(c)}, D{pair(d)}, G este mijlocul segmentului ce unește mijloacele lui AB și CD. Aflați OG față de originea reperului.', mul(F(1, 4), add(add(a, b), add(c, d))),
               'M=(A+B)/2, N=(C+D)/2, iar G=(M+N)/2=(A+B+C+D)/4. Aceeași expresie se obține din cealaltă bimediană, deci bimedianele se înjumătățesc.')
        o = (j, j+2)
        vector(26, f'Un cerc de centru O{pair(o)} și rază {3*j+8} intersectează cele două axe perpendiculare în A,B, respectiv C,D. Originea este P=(0;0). Calculați PA+PB+PC+PD.', mul(2, o),
               'Mijlocul coardei AB este proiecția lui O pe axa orizontală, iar mijlocul lui CD este proiecția pe axa verticală. Sumele extremităților sunt (2xO;0), respectiv (0;2yO). Suma lor este 2PO. Raza aleasă este mai mare decât PO, deci cele două coarde există.', {'O': serial(o), 'radius': 3*j+8}, adaptation='caz cu două coarde perpendiculare și calcul explicit')
        t = F(j, j+5); cosine = (1-t*t)/(1+t*t); sine = 2*t/(1+t*t)
        vector(27, f'Trei vectori unitari sunt u={pair((cosine,sine))}, v=(1;0), w={pair((cosine,-sine))}, în același semiplan deschis x>0. Calculați |u+v+w|.', 1+2*cosine,
               f'Componentele verticale se anulează, iar componenta orizontală este 1+2·({cosine})>0. Fiecare vector are modulul 1 deoarece ({cosine})²+({sine})²=1. În acest caz simetric modulul sumei este chiar componenta sa orizontală.', {'u': serial((cosine,sine)), 'v': ['1','0'], 'w': serial((cosine,-sine))}, adaptation='caz explicit simetric; nu înlocuiește demonstrația estimării generale')
        vector(28, f'Doi vectori necoliniari u={pair(u)}, v={pair(v)} sunt primele două laturi orientate consecutive ale unui triunghi. Care este a treia latură orientată w, pentru închiderea triunghiului?', mul(-1, add(u, v)),
               'Regula poligonului închis cere u+v+w=0, deci w=−u−v. Necoliniaritatea primelor două laturi asigură un triunghi nedegenerat.', {'u': serial(u), 'v': serial(v)})

        def scalar(typ, text, answer, explanation, given=None, **kwargs):
            emit('2.2', typ, j, text, answer, explanation, given or pts, **kwargs)

        scalar(1, f'OA={pair(a)}, OB={pair(b)}. Dacă N este mijlocul lui AB, aflați ON.', mul(F(1,2),add(a,b)),
               'Formula mijlocului, valabilă față de orice origine, este ON=(OA+OB)/2.')
        scalar(2, f'În paralelogramul ABCD, AB=u={pair(u)}, BC=v={pair(v)}. Calculați 2AC−DB.', add(u,mul(3,v)),
               'AC=u+v și DB=u−v. Atunci 2AC−DB=2u+2v−u+v=u+3v.', {'u':serial(u),'v':serial(v)})
        scalar(3, f'În hexagonul regulat ABCDEF, AB=u, AF=v. Aflați coeficienții (α;β) din AD=αu+βv dacă lungimea laturii este {j+1}.', (F(2),F(2)),
               'Diagonala AD este dublul lui AB+AF: într-un hexagon regulat, AB+AF=AO, unde O este centrul, iar AD=2AO. Lungimea laturii nu schimbă coeficienții.', {'side':j+1}, adaptation='coeficienți abstracți într-o bază geometrică')
        k = F(j-3,2)
        scalar(4, f'A{pair(a)}, B{pair(b)}. Aflați M definit prin AM=({k})AB.', add(a,mul(k,u)),
               f'M=A+k(B−A), cu k={k}. Pentru k<0 punctul este pe semidreapta opusă lui AB; pentru 0<k<1 este interior; k=0 dă A, k=1 dă B.', {**pts,'k':str(k)})
        scalar(5, f'Pentru u={pair(u)}, v={pair(v)}, calculați {j+2}(2u−v)−{j}(u+v).', sub(mul(j+4,u),mul(2*j+2,v)),
               f'Distributivitatea dă coeficientul lui u egal cu 2·{j+2}−{j}={j+4}, iar al lui v egal cu −{j+2}−{j}=−{2*j+2}.', {'u':serial(u),'v':serial(v)})
        scalar(6, f'A{pair(a)}, B{pair(b)}. Aflați M astfel încât MA+{j+1}AB=0.', add(a,mul(j+1,u)),
               f'A−M+{j+1}(B−A)=0, deci M=A+{j+1}(B−A). Punctul este unic deoarece coeficientul lui M este −1.')
        p,q=j+1,j+2
        divided=mul(F(1,p+q),add(mul(q,b),mul(p,c)))
        scalar(7, f'B{pair(b)}, C{pair(c)}, A{pair(a)}. P este interior lui BC și BP:PC={p}:{q}. Calculați AP.',sub(divided,a),
               f'Din q·BP=p·PC obținem P=({q}B+{p}C)/{p+q}. Vectorul cerut este P−A; ponderile extremităților apar în ordine inversă raportului.', {**pts,'p':p,'q':q})
        scalar(8, f'A{pair(a)}, B{pair(b)} și C=A+({F(j+2,2)})AB. Care este raportul vectorial AC/AB?', F(j+2,2),
               'Din definiția lui C avem AC=kAB. Cum A≠B, vectorul AB este nenul, iar raportul scalar este unic. Relația dovedește coliniaritatea.', {**pts,'k':str(F(j+2,2))})
        scalar(9, f'Triunghiul ABC are A{pair(a)}, B{pair(b)}, C{pair(c)}. P{pair(d)}, Q=P+{j+1}AB și R=P+tAC. Ce valoare a lui t face QR paralel cu BC?', F(j+1),
               f'QR=tAC−{j+1}AB. În baza necoliniară (AB,AC), paralelismul cu BC=AC−AB cere coeficienți proporționali: t={j+1}. Atunci PQ, PR și QR sunt toate paralele cu laturile omoloage.', {'scale':j+1,'u':serial(u),'v':serial(v)})
        scalar(10, f'A{pair(a)}, B{pair(b)}, iar C are vectorul de poziție OC=({j+1})OA−{j}OB. Ce concluzie rezultă?',
               'A, B și C sunt coliniare.',
               f'Coeficienții {j+1}, −{j}, −1 din ({j+1})OA−{j}OB−OC=0 au suma zero și nu sunt toți nuli. Mai direct, AC=−{j}AB, deci cele trei puncte sunt coliniare, indiferent de originea O.',
               {'k':j}, choices=['A, B și C formează obligatoriu un triunghi dreptunghic.', 'C este obligatoriu mijlocul lui AB.', 'A, B și C sunt obligatoriu necoliniare.'], adaptation='concluzie afină justificată printr-un multiplu')
        weighted=mul(F(1,p+q),add(mul(p,a),mul(q,b)))
        scalar(11, f'A{pair(a)}, B{pair(b)}. Aflați G pentru care {p}GA+{q}GB=0.',weighted,
               f'{p}(A−G)+{q}(B−G)=0 dă ({p+q})G={p}A+{q}B. Suma ponderilor este nenulă, deci G există și este unic.', {**pts,'p':p,'q':q})
        scalar(12, f'G verifică {p}GA+{q}GB=0. Pentru M{pair(c)} și G{pair(weighted)}, calculați {p}MA+{q}MB.',mul(p+q,sub(weighted,c)),
               f'MA=MG+GA și MB=MG+GB. După ponderare, termenii {p}GA+{q}GB se anulează, iar suma rămasă este {p+q}MG.', {**pts,'G':serial(weighted),'p':p,'q':q})
        scalar(13, f'În triunghiul ABC, B{pair(b)}, C{pair(c)}, M și N sunt mijloacele lui AB și AC. Calculați MN.',mul(F(1,2),sub(c,b)),
               'M=(A+B)/2, N=(A+C)/2, deci MN=N−M=(C−B)/2=BC/2. Vectorii au același sens, iar lungimea liniei mijlocii este jumătate din BC.')
        scalar(14, f'Trapezul ABCD are AB paralel cu DC, cu AB={3*j+2} și DC={j+2}. M,N sunt mijloacele laturilor AD,BC. Care este lungimea lui MN?',F(4*j+4,2),
               '2MN=AB+DC ca vectori orientați în același sens pe bazele trapezului convex. Lungimea liniei mijlocii este semisuma lungimilor bazelor.', {'bases':[3*j+2,j+2]})
        scalar(15, f'În patrulaterul ABCD, A{pair(a)}, C{pair(c)}. M,N,P,Q sunt mijloacele lui AB,BC,CD,DA. Calculați MN.',mul(F(1,2),sub(c,a)),
               'MN=(C−A)/2 și QP=(C−A)/2. Analog NP=MQ=(D−B)/2, deci MNPQ este paralelogramul lui Varignon. Nu presupunem că ABCD este paralelogram.')
        # A concrete extension configuration: A=(0,0), B=(s,0), C=(0,s).
        s=j+2; extension_b=(2*s,-s); extension_c=(-s,2*s)
        scalar(16, f'A=(0;0), B=({s};0), C=(0;{s}). D=2B−C și E=2C−B sunt pe prelungirile lui BC. Aflați M pentru care DM=({F(j, j+1)})DE.',add(extension_b,mul(F(j,j+1),sub(extension_c,extension_b))),
               'D și E sunt combinații afine ale lui B,C, cu suma coeficienților 1, deci sunt pe dreapta BC. Și M=D+k(E−D) este pe aceeași dreaptă. Înlocuim coordonatele și raportul k pentru a determina M.', {'s':s,'k':str(F(j,j+1))}, adaptation='caz explicit pe prelungiri; calcul și justificarea alinierii')
        scalar(17, f'ABCD și A′B′C′D′ sunt paralelograme. A{pair(a)}, B{pair(b)}, A′{pair(c)}, B′{pair(d)}. M,N,P,Q sunt mijloacele AA′,BB′,CC′,DD′. Calculați MN.',mul(F(1,2),add(sub(b,a),sub(d,c))),
               'MN=(AB+A′B′)/2. Cum AB=DC și A′B′=D′C′, rezultă MN=QP; analog NP=MQ. Mijloacele satisfac relațiile vectoriale ale unui paralelogram, posibil degenerat. Pentru un paralelogram nedegenerat trebuie ca direcțiile a două laturi consecutive ale figurii rezultate să nu fie coliniare.')
        scalar(18, f'Într-un patrulater convex ABCD, M,N sunt mijloacele lui AD,BC. AB={j+2}, CD={2*j+3}, iar MN=({3*j+5})/2. Ce rezultă despre AB și CD?',
               'AB este paralelă cu CD.',
               'Identitatea 2MN=AB+DC și ipoteza lungimilor dau |AB+DC|=|AB|+|DC|. Vectorii sunt nenuli, deci egalitatea triunghiulară impune aceeași direcție și același sens pentru AB și DC. Prin urmare bazele sunt paralele; nu rezultă obligatoriu egalitatea lungimilor.',
               {'lengths':[j+2,2*j+3]}, choices=['AB este perpendiculară pe CD.', 'AB și CD au obligatoriu lungimi egale.', 'ABCD este obligatoriu pătrat.'], adaptation='reciprocă dedusă din egalitatea triunghiulară')
        scalar(19, f'În patrulaterul convex ABCD, O este intersecția diagonalelor și este mijlocul ambelor bimediane. Pentru A{pair(a)}, B{pair(b)}, C{pair(c)}, aflați D.',sub(add(a,c),b),
               'Centrul bimedianelor este G=(A+B+C+D)/4. Dacă G aparține ambelor diagonale, în baza direcțiilor AC,BD neparalele, relația (A−G)+(C−G)+(B−G)+(D−G)=0 impune ca fiecare pereche să aibă sumă nulă. Diagonalele se înjumătățesc în G=O, deci A+C=B+D și D=A+C−B.', adaptation='caracterizarea paralelogramului; bimediane înjumătățite explicit')
        lower,upper=3*j+2,j+2
        scalar(20, f'Trapezul ABCD are A=(0;0), B=({lower};0), D=(0;{j+3}), C=({upper};{j+3}). Diagonalele se intersectează în O. Paralela prin O la baze taie AD în E și BC în F. Care este lungimea EF?',F(2*lower*upper,lower+upper),
               f'Parametrizând AC și BD, înălțimea relativă a lui O este t=AB/(AB+DC)={lower}/{lower+upper}. Lungimea secțiunii la această înălțime este (1−t)AB+t·DC=2AB·DC/(AB+DC). Coordonata orizontală a lui O este AB·DC/(AB+DC), jumătatea secțiunii, deci O este și mijlocul lui EF.', {'lower':lower,'upper':upper,'height':j+3}, adaptation='secțiune într-un trapez explicit și demonstrarea înjumătățirii')

    assert len(questions) == 240
    assert len({q['text'] for q in questions}) == 240
    return questions


def update_file():
    data = json.loads(TARGET.read_text(encoding='utf-8'))
    before = [q for q in data['questions'] if q.get('type') == 'vector_workbench']
    retained = [q for q in data['questions'] if q.get('practice_scope', {}).get('bank') != BANK]
    data['questions'] = retained + build_questions()
    data['difficulty'] = 'hard'
    assert before == [q for q in data['questions'] if q.get('type') == 'vector_workbench']
    TARGET.write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    return len(data['questions'])


if __name__ == '__main__':
    print(f'{update_file()} questions, 240 new grids, existing interactive objects preserved.')
