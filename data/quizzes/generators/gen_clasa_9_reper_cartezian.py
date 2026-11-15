"""70 de grile originale după A2 §3.1, p. 86–89."""
import json
from collections import Counter
from fractions import Fraction as F
from itertools import product
from pathlib import Path
from catalog_grid_utils import GridBank

NAMES = ['Produs cartezian finit','Poziții pe tabla de șah',
 'Recuperarea factorilor produsului','Comutativitatea condiționată a produsului',
 'Produsul a două intervale','Cardinal și probabilitate pe produs',
 'Produse cu un singleton','Drepte paralele cu axele',
 'Lectura unei regiuni desenate','Relații ca submulțimi ale produsului',
 'Incluziuni între produse','Submulțimi stabile la o relație',
 'Compararea relațiilor finite','Cardinale de produse și diferențe']

def pairs(values):
    return '{'+ '; '.join(f'({x}, {y})' for x,y in sorted(values))+'}'

def build():
    b=GridBank('A2.3.1',NAMES)
    for j in range(1,6):
        a={j,j+1}; c={-j,0,j}
        correct=pairs(product(a,c))
        b.add(1,f'Fie A={{{j}; {j+1}}} și B={{{-j}; 0; {j}}}. Care este A×B?',correct,
            [pairs(product(c,a)),pairs(product(a,{-j,j})),pairs(product({j},c))],
            'A×B conține toate perechile ordonate cu prima coordonată în A și a doua în B. Fiecare dintre cele două elemente ale lui A se asociază cu fiecare dintre cele trei elemente ale lui B: șase perechi.')
        x,y=[(1,1),(2,2),(3,3),(4,4),(8,7)][j-1]
        moves={(x+dx,y+dy) for dx,dy in [(1,2),(2,1),(-1,2),(-2,1),(1,-2),(2,-1),(-1,-2),(-2,-1)] if 1<=x+dx<=8 and 1<=y+dy<=8}
        b.numeric(2,f'Pe o tablă de șah goală, coloanele și liniile sunt numerotate de la 1 la 8. Un cal se află în ({x}, {y}). Câte destinații distincte poate atinge printr-o singură mutare?',len(moves),
            f'Mutările au deplasări (±1,±2) sau (±2,±1). Păstrăm numai coordonatele din 1,…,8: {pairs(moves)}. Sunt {len(moves)} destinații.')
        b.add(3,f'Știind că A×B={pairs(product(a,{j+3,j+4}))}, aflați A și B.',
            f'A={{{j}; {j+1}}}, B={{{j+3}; {j+4}}}',
            [f'A={{{j+3}; {j+4}}}, B={{{j}; {j+1}}}',f'A={{{j}}}, B={{{j+3}; {j+4}}}',f'A={{{j}; {j+1}}}, B={{{j+3}}}'],
            f'Produsul este nevid. Proiecția pe prima coordonată este A={{{j}; {j+1}}}; proiecția pe a doua coordonată este B={{{j+3}; {j+4}}}.')
        b.add(4,f'Fie A={{{j}; {j+1}}}. Care sunt toate mulțimile B pentru care A×B=B×A?',
            f'B=∅ sau B={{{j}; {j+1}}}',
            [f'Numai B={{{j}; {j+1}}}','Numai B=∅','Orice mulțime B'],
            'Dacă B=∅, ambele produse sunt vide. Dacă B este nevidă, și A este nevidă; egalitatea produselor impune egalitatea proiecțiilor pe prima coordonată, deci B=A. Reciproc, B=A verifică egalitatea.')
        b.add(5,f'Care punct aparține regiunii [−{j}, {j+2})×(0, {j+1}]?',f'({-j}, {j+1})',
            [f'({j+2}, 1)',f'(0, 0)',f'({-j-1}, 1)'],
            f'Condițiile sunt −{j}≤x<{j+2} și 0<y≤{j+1}. Punctul ({-j},{j+1}) le îndeplinește. Celelalte încalcă, în ordine, capătul drept exclus, capătul inferior exclus și limita stângă.')
        n=2*(j+2);m=3*(j+1)
        favorable=[(u,v) for u in range(1,n+1) for v in range(1,m+1) if u%2==0 and v%3==0]
        b.numeric(6,f'Alegem uniform o pereche din A×B, unde A={{1,…,{n}}} și B={{1,…,{m}}}. Care este probabilitatea ca prima coordonată să fie pară și a doua divizibilă cu 3?',F(len(favorable),n*m),
            f'Sunt {n*m} perechi echiprobabile. Prima coordonată are {n//2} alegeri favorabile, a doua {m//3}; probabilitatea este ({n//2}·{m//3})/{n*m}=1/6.')
        b.add(7,f'Ce mulțime de puncte reprezintă {{{j}}}×[−{j}, {j+1}]?',
            f'Segment vertical: x={j}, −{j}≤y≤{j+1}',
            [f'Segment orizontal: y={j}, −{j}≤x≤{j+1}',f'Dreapta verticală x={j}',f'Dreapta orizontală y={j}'],
            f'Prima coordonată este fixată la {j}; a doua parcurge un interval închis și mărginit. Obținem segmentul vertical cu extremitățile ({j},−{j}) și ({j},{j+1}), incluse.')
        b.add(8,f'Ce dreaptă este descrisă în plan de ecuația {j+1}x−{(j+1)*(j+2)}=0?',
            f'x={j+2}, paralelă cu Oy',
            [f'y={j+2}, paralelă cu Ox',f'x={-j-2}, paralelă cu Oy',f'y={-j-2}, paralelă cu Ox'],
            f'Împărțim la {j+1}≠0: x={j+2}. Coordonata y este orice număr real, deci dreapta este verticală, paralelă cu Oy.')
        # Schiță în LaTeX: frontiera continuă și hașura interioară sunt explicite.
        diagram=(rf'\[\begin{{array}}{{r|ccc}}'
                 rf'{j+2}&\bullet&\rule{{3em}}{{0.06em}}&\bullet\\'
                 rf'&\vert&\text{{hașurat}}&\vert\\'
                 rf'1&\bullet&\rule{{3em}}{{0.06em}}&\bullet\\'
                 rf'\hline y\backslash x&-{j}&&{j+1}'
                 rf'\end{{array}}\]')
        b.add(9,f'Desenul schematic arată un dreptunghi hașurat cu toate cele patru laturi și vârfuri incluse. Etichetele indică abscisele și ordonatele extremelor. Scrieți regiunea ca produs cartezian. {diagram}',
            f'[−{j}, {j+1}]×[1, {j+2}]',
            [f'(−{j}, {j+1})×(1, {j+2})',f'[1, {j+2}]×[−{j}, {j+1}]',f'[−{j}, {j+1}]×(1, {j+2})'],
            f'Proiecția pe Ox este [−{j},{j+1}], iar pe Oy este [1,{j+2}]. Frontiera este inclusă, așadar folosim paranteze pătrate la toate capetele. Interiorul și frontiera formează produsul acestor intervale.')
        size=j+2
        relation={(u,v) for u,v in product(range(1,size+1),repeat=2) if u<=v}
        b.numeric(10,f'Pentru A={{1,…,{size}}}, câte perechi are relația R={{(x,y)∈A×A | x≤y}}?',len(relation),
            f'Pentru x=1 sunt {size} valori ale lui y, apoi {size-1},…,1. Totalul este {size}·{size+1}/2={len(relation)}.')
        b.numeric(11,f'Fie C={{{j}}}, D={{{j}; {j+1}; {j+2}}}. Câte perechi ordonate de mulțimi (A,B) satisfac C×C⊆A×B⊆D×D?',16,
            f'Cum C este nevidă, proiecțiile impun C⊆A⊆D și C⊆B⊆D. Fiecare factor conține obligatoriu {j}; celelalte două elemente sunt opționale. Există 2²·2²=16 alegeri independente.')
        good={(j,2*j),(j+1,2*(j+1))}
        bad1={(j,2*j),(j+1,2*(j+1)+1)}
        bad2={(j,2*j),(j+1,j+1)}
        bad3={(j,2*j),(j+1,3*(j+1))}
        b.add(12,f'Fie A={{1,…,{3*(j+1)}}}. Care submulțime M⊆A×A are proprietatea ad=bc pentru ORICARE două perechi (a,b),(c,d)∈M?',
            pairs(good),[pairs(bad1),pairs(bad2),pairs(bad3)],
            'În mulțimea corectă fiecare pereche (a,b) are b=2a. Astfel ad=a·2c=2a·c=bc pentru oricare două perechi. În celelalte variante, cele două perechi au raporturi diferite ale coordonatelor și nu satisfac egalitatea.')
        b.add(13,f'Pe A={{1,…,{size}}}, definim E={{(x,y) | x=y}}, L={{(x,y) | x≤y}} și S={{(x,y) | x<y}}. Care relație este corectă?',
            'L=E∪S și E∩S=∅',['E=L∪S','S=E∪L','E∩S=E'],
            'Orice pereche cu x≤y are exact una dintre proprietățile x=y și x<y. Așadar L este reuniunea disjunctă a lui E și S. E este nevidă, în timp ce intersecția E∩S este vidă.')
        aa=set(range(1,j+3));bb={2,4,6,8};cc={4,8,10}
        count=len(set(product(aa,bb))-set(product(aa,cc)))
        b.numeric(14,f'Fie A={{1,…,{j+2}}}, B={{2;4;6;8}}, C={{4;8;10}}. Calculați card((A×B)∖(A×C)).',count,
            f'(A×B)∖(A×C)=A×(B∖C). B∖C={{2;6}}, deci cardinalul este {j+2}·2={count}.')
    return b.finish(Counter({i:5 for i in range(1,15)}))

if __name__=='__main__':
    path=Path(__file__).resolve().parents[1]/'clasa_9/clasa_9_u02_l03_functii_reper_cartezian_produs_cartezian_si_reprezentare_grafica.json'
    payload=json.loads(path.read_text(encoding='utf-8'))
    payload['questions']=build()
    payload['difficulty']='medium'
    path.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('70 grile generate')
