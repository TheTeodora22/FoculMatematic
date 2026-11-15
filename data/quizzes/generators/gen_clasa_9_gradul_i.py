"""315 grile originale: A3 §§1–5 (63 tipuri, câte cinci variante).

Regenerarea înlocuiește exclusiv cele cinci lecții de Funcția de gradul I.
Metadatele verification păstrează parametrii și valorile opțiunilor pentru
verificarea matematică independentă; nu sunt importate în baza de date.
"""
import json
from collections import Counter
from fractions import Fraction as F
from pathlib import Path
from catalog_grid_utils import GridBank

ROOT = Path(__file__).resolve().parents[1]
FILES = [
 'clasa_9_u03_l01_functia_de_gradul_i_definitie_si_reprezentare_grafica.json',
 'clasa_9_u03_l02_interpretarea_grafica_a_proprietatilor_algebrice_monotonie_si_semn.json',
 'clasa_9_u03_l03_inecuatii_de_forma_ax_b_0_si_studiul_lor_pe_r.json',
 'clasa_9_u03_l04_pozitia_relativa_a_doua_drepte.json',
 'clasa_9_u03_l05_sisteme_de_ecuatii_si_sisteme_de_inecuatii_de_gradul_i.json',
]
NAMES = [
 ['Interceptările graficului afin','Lungimea dintre interceptări','Funcție afină din valori date',
 'Funcție afină din relație funcțională','Grafic afin pe ℝ','Grafic pe domeniu restrâns',
 'Grafic afin pe ramuri','Parametru din lungimea interceptului','Parametru din aria triunghiului interceptat',
 'Involuții afine','Grafice cu sign și parte întreagă','Coliniaritate analitică',
 'Poziția față de axe și bisectoare','Argumente dependente de pragul ramurii',
 'Punct parametrizat pe un grafic pe ramuri','Două grafice determinate simultan',
 'Reconstrucția legii din desen','Prelungire pară sau impară','Funcție construită din distanțe pe axă',
 'Intersecția a două grafice ca mulțime dată','Existența unei valori iraționale'],
 ['Monotonie din pantă','Monotonie în funcție de parametru','Pantă determinată prin punct',
 'Monotonie ca filtru al soluțiilor','Pantă cu semn algebric cert','Monotonie globală pe ramuri afine',
 'Coeficienți întregi și monotonie','Monotonie cu parte întreagă','Monotonia compunerilor afine',
 'Monotonia iteratelor pe domenii mixte'],
 ['Tabelul de semn al funcției afine','Semnul produselor și rapoartelor','Funcții cu sign',
 'Funcții cu module de expresii afine','Parametru din intervalul exact de pozitivitate',
 'Semnul funcției cu parametru','Inecuații liniare după reducere','Inecuații raționale reductibile',
 'Panta exprimată prin fracție','Grafice de maxime și minime','Inecuații cu sumă de module',
 'Inecuații liniare cu parametru','Semnul unei compuneri pe ramuri','Semn uniform pe semidreaptă sau segment'],
 ['Poziția dreptelor date prin puncte','Sistem liniar și interpretare geometrică',
 'Sisteme liniare după dezvoltare','Sisteme cu reciproce','Sisteme cu module',
 'Sisteme cu expresii raționale comune','Discuția sistemului cu parametru','Probabilitatea tipului de sistem'],
 ['Intersecția soluțiilor inecuațiilor liniare','Inecuație cu modul și membru drept variabil',
 'Sisteme de inecuații raționale','Sisteme cu mai multe module','Ecuație cu maxim','Grafice anvelopă',
 'Apartenențe la intervale cu capete variabile','Intersecții cu capete dependente de x',
 'Pozitivitatea simultană a două funcții','Semne contrare pe interval'],
]

def affine(a,b):
    return rf'\(f(x)={a}x{b:+d}\)'

def interval(a,b,lc=False,rc=False):
    return ('[' if lc else '(')+f'{a}; {b}'+(']' if rc else ')')

def pair(x,y): return f'({x}; {y})'

def build():
    banks=[GridBank(f'A3.{i}', names) for i,names in enumerate(NAMES,1)]
    def add(s,t,j,text,correct,wrong,explanation,values=None):
        bank=banks[s-1]
        bank.add(t,text,correct,wrong,explanation)
        # Preserve candidate semantics in display order; verification never trusts is_correct.
        position=(len(bank.questions)-1)%4
        candidates=[correct,*wrong] if values is None else values
        candidates=list(candidates); candidates.insert(position,candidates.pop(0))
        bank.questions[-1]['verification']={'section':s,'type':t,'variant':j,'candidates':candidates}
    def num(s,t,j,text,value,explanation):
        value=F(value); vals=[value,value-1,value+1,value+2]
        add(s,t,j,text,str(vals[0]),[str(v) for v in vals[1:]],explanation,
            values=[str(v) for v in vals])
    def tup(s,t,j,text,value,explanation):
        x,y=map(F,value);vals=[(x,y),(x+1,y),(x,y+1),(x+1,y+1)]
        add(s,t,j,text,pair(x,y),[pair(*v) for v in vals[1:]],explanation,
            values=[[str(z) for z in v] for v in vals])
    for j in range(1,6):
        q=j+1
        add(1,1,j,f'Determinați intersecțiile graficului f(x)=2x−{2*j}, x∈ℝ, cu Ox și Oy, în această ordine.',
            f'A({j}; 0), B(0; {-2*j})',
            [f'A({-j}; 0), B(0; {-2*j})',f'A({j}; 0), B(0; {2*j})',f'A({2*j}; 0), B(0; {-j})'],
            f'Pe Ox avem y=0, deci 2x−{2*j}=0 și x={j}. Pe Oy avem x=0, deci y={-2*j}.',
            [[str(j),str(-2*j)],[str(-j),str(-2*j)],[str(j),str(2*j)],[str(2*j),str(-j)]])
        num(1,2,j,rf'Dreapta \(y=-\frac43x+{4*j}\) taie axele în A și B. Calculați lungimea AB.',5*j,
            f'Interceptările sunt A({3*j};0), B(0;{4*j}). Teorema lui Pitagora dă AB=√(({3*j})²+({4*j})²)={5*j}.')
        a,b=q,j-2
        vals=[(a,b),(a+1,b),(a,b+1),(a-1,b-1)]
        add(1,3,j,f'Fie f(x)=ax+b. Dacă f(1)={a+b} și f(3)={3*a+b}, care este formula lui f?',
            affine(a,b),[affine(*v) for v in vals[1:]],
            f'Avem a+b={a+b} și 3a+b={3*a+b}. Scăzând, 2a={2*a}, astfel a={a}, b={b}.',vals)
        add(1,4,j,f'Funcția afină f satisface f(2x−1)={2*a}x+({b-a}) pentru orice x∈ℝ. Determinați f.',
            affine(a,b),[affine(*v) for v in vals[1:]],
            f'Punem t=2x−1, deci x=(t+1)/2. Obținem f(t)={a}(t+1)+({b-a})={a}t+({b}).',vals)
        add(1,5,j,f'Care pereche de puncte distincte determină graficul funcției f(x)=−{q}x+{j}, x∈ℝ?',
            f'A(0; {j}), B(1; −1)',
            [f'A(0; {j+1}), B(1; −1)',f'A(0; {j}), B(1; 1)',f'A(1; {j}), B(0; −1)'],
            f'f(0)={j} și f(1)=−{q}+{j}=−1. Două puncte distincte ale graficului determină dreapta; celelalte perechi conțin cel puțin un punct care nu verifică ecuația.',
            [[0,j,1,-1],[0,j+1,1,-1],[0,j,1,1],[1,j,0,-1]])
        lo,hi=2*(-j)+j,2*(j+1)+j
        add(1,6,j,f'Pentru f(x)=2x+{j}, cu domeniul [−{j}; {j+1}), care este imaginea funcției?',
            interval(lo,hi,True,False),[interval(lo,hi),interval(lo,hi,True,True),interval(-hi,-lo,True,False)],
            f'Panta 2 este pozitivă. Imaginea păstrează ordinea și tipul capetelor: f(−{j})={lo} este inclus. Capătul drept {j+1} al domeniului este exclus, deci valoarea corespunzătoare {hi} nu este atinsă.',
            [[lo,hi,1,0],[lo,hi,0,0],[lo,hi,1,1],[-hi,-lo,1,0]])
        add(1,7,j,f'Fie f(x)=x+{j} pentru x<1 și f(x)=2x+{j-1} pentru x≥1. Ce descriere completă a graficului este corectă?',
            f'Ramura y=x+{j} pentru x<1; ramura y=2x+{j-1} pentru x≥1; punct comun (1; {j+1}).',
            [f'Aceleași ramuri, dar punctul (1; {j+1}) este exclus.',f'Întregul grafic este dreapta y=x+{j}.',f'Ramura y=2x+{j-1} pentru x<1; ramura y=x+{j} pentru x≥1.'],
            f'Fiecare formulă se trasează numai pe domeniul ei. Ambele expresii au la x=1 valoarea {j+1}; a doua ramură include punctul, prima îl apropie din stânga. Pantele 1 și 2 sunt diferite, deci nu rezultă o singură dreaptă.')
        num(1,8,j,f'Pentru m>0, dreapta y=mx+{4*j} determină pe axe un segment de lungime {5*j}. Aflați m.',F(4,3),
            f'Interceptările sunt (−{4*j}/m;0) și (0;{4*j}). Din AB²=({5*j})² rezultă ({4*j}/m)²={9*j*j}, deci |m|=4/3. Condiția m>0 selectează m=4/3.')
        num(1,9,j,f'Pentru m>0, graficul y=mx+{2*j} și axele formează un triunghi de arie {j}. Determinați m.',2*j,
            f'Interceptările au lungimile {2*j}/m și {2*j}. Aria este ({2*j})²/(2m)={2*j*j}/m. Egalând cu {j}, obținem m={2*j}; m>0 și interceptările sunt distincte de origine.')
        num(1,10,j,f'Fie f(x)=ax+{j}. Determinați a astfel încât f(f(x))=x pentru orice x∈ℝ.',-1,
            f'Compunerea este a²x+{j}(a+1). Identificăm a²=1 și {j}(a+1)=0. Deoarece {j}≠0, singura posibilitate este a=−1. Geometric, graficul y=−x+{j} este simetric față de y=x.')
        if j%2:
            add(1,11,j,f'Notați [x]=⌊x⌋. Pe ce interval graficul funcției f(x)=[x] coincide cu segmentul orizontal y=−{j}?',
                interval(-j,1-j,True,False),[interval(-j,1-j),interval(-j,1-j,False,True),interval(-j-1,-j,True,False)],
                f'Definiția părții întregi dă [x]=−{j} exact când −{j}≤x<−{j}+1={1-j}. Capătul stâng este inclus, cel drept exclus.',
                [[-j,1-j,1,0],[-j,1-j,0,0],[-j,1-j,0,1],[-j-1,-j,1,0]])
        else:
            add(1,11,j,f'Fie f(x)=sign(x−{j}), cu sign(0)=0. Pentru ce x graficul are ordonata 1?',
                interval(j,'+∞'),[interval(j,'+∞',True,False),interval('−∞',j),interval('−∞',j,False,True)],
                f'Funcția sign este 1 pentru argument strict pozitiv, 0 pentru argument nul și −1 pentru argument negativ. Prin urmare f(x)=1 exact când x−{j}>0, adică x>{j}; punctul de la prag are ordonata 0.')
        num(1,12,j,f'Pentru ce m sunt coliniare punctele A(0; {j}), B(1; {j+q}) și C(2; m)?',j+2*q,
            f'AB are panta ({j+q}−{j})/(1−0)={q}. Dreapta sa are ecuația y={q}x+{j}, astfel la x=2 obținem m={j+2*q}.')
        num(1,13,j,f'Pentru ce m graficul y=(m−{j})x+{q} este perpendicular pe bisectoarea y=x?',j-1,
            f'Bisectoarea are panta 1. Perpendicularitatea impune (m−{j})·1=−1, deci m={j-1}. Panta obținută este nenulă și definește o funcție de gradul I.')
        num(1,14,j,f'Fie f(x)=x dacă x<{j}, respectiv f(x)=2x−{j} dacă x≥{j}. Rezolvați f(m)+f(m−{j})={3*j}.',F(5*j,3),
            f'Dacă m<{j}, ambii termeni folosesc prima ramură: 2m−{j}={3*j} dă m={2*j}, inadmisibil. Dacă {j}≤m<{2*j}, suma este 3m−{2*j}, deci m={F(5*j,3)}, admisibil. Dacă m≥{2*j}, suma este 4m−{4*j}, deci m={F(7*j,4)}<{2*j}, inadmisibil. Singura soluție este {F(5*j,3)}.')
        num(1,15,j,f'Fie f(x)=x+{j} pentru x<0 și f(x)=2x+{j} pentru x≥0. Pentru ce m aparține A(m; m+{2*j}) graficului?',j,
            f'Dacă m<0, condiția m+{2*j}=m+{j} este imposibilă. Dacă m≥0, avem m+{2*j}=2m+{j}, deci m={j}, care respectă ramura.')
        tup(1,16,j,f'Fie f(x)=ax+b și g(x)=bx+a. Determinați (a;b) dacă f(1)={j+4} și g(2)={2*j+5}.',(3,q),
            f'Condițiile sunt a+b={j+4}, a+2b={2*j+5}. Scăderea dă b={q}, apoi a=3. Cele două ecuații independente determină unic ambii coeficienți.')
        add(1,17,j,f'Un grafic este format din două semidrepte unite în O, trecând prin A(−1; −{j}) la stânga și B(1; {2*j}) la dreapta. Care este legea funcției?',
            f'f(x)={j}x pentru x≤0; f(x)={2*j}x pentru x≥0.',
            [f'f(x)={2*j}x pentru x≤0; f(x)={j}x pentru x≥0.',f'f(x)=−{j}x pentru x≤0; f(x)={2*j}x pentru x≥0.',f'f(x)={j}x+1 pentru x≤0; f(x)={2*j}x+1 pentru x≥0.'],
            f'Ramura OA trece prin origine și are panta (−{j})/(−1)={j}. Ramura OB are panta {2*j}/1={2*j}. Ordonata la origine este 0 pentru ambele; cele două legi coincid în O.',
            [[j,2*j,0],[2*j,j,0],[-j,2*j,0],[j,2*j,1]])
        if j%2:
            vals=[(-q,j),(q,j),(-q,-j),(q,-j)]
            add(1,18,j,f'Funcția f(x)={q}x+{j} este dată pentru x≥0. Care este formula prelungirii pare pe x<0?',
                affine(-q,j),[affine(*v) for v in vals[1:]],
                f'O prelungire pară satisface f(x)=f(−x). Pentru x<0, argumentul −x este pozitiv: f(x)={q}(−x)+{j}=−{q}x+{j}. Graficul se reflectă în Oy.',vals)
        else:
            vals=[(q,0),(-q,0),(q,j),(-q,j)]
            add(1,18,j,f'Funcția f(x)={q}x este dată pentru x≥0. Care este formula prelungirii impare pe x<0?',
                affine(q,0),[affine(*v) for v in vals[1:]],
                f'O prelungire impară cere f(x)=−f(−x). Pentru x<0 obținem f(x)=−{q}(−x)={q}x. Valoarea existentă f(0)=0 respectă condiția de imparitate. Geometric, prelungirea este simetrică față de origine.',vals)
        add(1,19,j,f'Pe Oy sunt A(0; −{j}), B(0; {j}) și M(0;t). Care este expresia completă a lui MA+MB?',
            f'−2t dacă t<−{j}; {2*j} dacă −{j}≤t≤{j}; 2t dacă t>{j}.',
            [f'2t dacă t<−{j}; {2*j} dacă −{j}≤t≤{j}; −2t dacă t>{j}.',f'{2*j} pentru orice t∈ℝ.',f'−t dacă t<−{j}; {j} dacă −{j}≤t≤{j}; t dacă t>{j}.'],
            f'Distanțele sunt |t+{j}| și |t−{j}|. Sub −{j} ambele expresii sunt negative și suma este −2t; între capete distanțele însumează AB={2*j}; peste {j}, suma este 2t.')
        r,s=j,q; b=s-j*r;c=s-q*r
        tup(1,20,j,f'Graficele f(x)={j}x+b și g(x)={q}x+c au intersecția exact {{A({r}; {s})}}. Determinați (b;c).',(b,c),
            f'Apartenența lui A dă b={s}−{j}·{r}={b} și c={s}−{q}·{r}={c}. Pantele {j} și {q} sunt diferite, deci intersecția este unică.')
        add(1,21,j,f'Fie f(x)=ax+b, cu f(0)={j} și f(1)∈ℚ∖{{{j}}}. Care argument garantează o valoare irațională, pentru orice asemenea f?',
            rf'\({j}+\sqrt2\)',[str(j),str(j+1),str(F(j,2))],
            f'b=f(0)∈ℚ și a=f(1)−f(0)∈ℚ∖{{0}}. Dacă f({j}+√2)=a{j}+b+a√2 ar fi rațional, atunci √2 ar fi rațional după scădere și împărțire la a≠0, contradicție. Celelalte argumente sunt raționale și au imagini raționale.')

        add(2,1,j,f'Care este monotonia funcției f(x)=−{j}x+{q} pe ℝ?', 'Strict descrescătoare.',
            ['Strict crescătoare.','Constantă.','Nu este monotonă pe ℝ.'],f'Pentru x₁<x₂, f(x₂)−f(x₁)=−{j}(x₂−x₁)<0. Prin definiție, funcția este strict descrescătoare.')
        add(2,2,j,f'Pentru ce m funcția f(x)=(m−{j})x+{q} este strict crescătoare pe ℝ?',f'm>{j}',
            [f'm<{j}',f'm≥{j}',f'm={j}'],f'O funcție afină este strict crescătoare exact când panta este pozitivă: m−{j}>0. La m={j} este constantă, nu strict crescătoare.')
        add(2,3,j,f'Graficul f(x)=(m−{j})x+1 conține A(2; {1-2*j}). Care sunt m și monotonia?',
            'm=0; strict descrescătoare.',['m=0; strict crescătoare.',f'm={j}; constantă.',f'm={2*j}; strict crescătoare.'],
            f'Înlocuim A: 2(m−{j})+1={1-2*j}, deci 2m=0 și m=0. Panta devine −{j}<0, astfel f este strict descrescătoare.')
        num(2,4,j,f'Fie f(x)=mx+{j}. Graficul conține A(m; {j+q*q}), iar f este strict descrescătoare. Determinați m.',-q,
            f'Apartenența dă m²+{j}={j+q*q}, deci m=±{q}. Stricta descreștere cere m<0, astfel rămâne m=−{q}.')
        add(2,5,j,f'Pentru m real, studiați monotonia lui f(x)=((m−{j})²+1)x−{q}.',
            'Strict crescătoare pentru orice m∈ℝ.', ['Strict descrescătoare pentru orice m∈ℝ.',f'Constantă pentru m={j}.',f'Strict crescătoare numai pentru m>{j}.'],
            f'Pătratul (m−{j})² este nenegativ, deci panta este cel puțin 1 pentru orice m. Pentru x₂>x₁, diferența f(x₂)−f(x₁) este strict pozitivă, inclusiv când m={j}.')
        add(2,6,j,f'Fie f(x)=−x pentru x<0, respectiv f(x)=−2x+m−{j} pentru x≥0. Pentru ce m este f strict descrescătoare pe ℝ?',
            f'm≤{j}',[f'm<{j}',f'm≥{j}',f'm>{j}'],
            f'Ambele ramuri au pante negative. Pentru x<0≤y, avem f(x)>0 și f(y)≤m−{j}; condiția m≤{j} asigură ordinea strictă. Dacă m>{j}, alegem x<0 suficient de aproape de 0 și y=0: f(x)<f(0), contradicție.')
        num(2,7,j,f'Câte funcții f(x)=ax+b cu a,b∈ℤ sunt strict descrescătoare, satisfac f(2)={j} și 0≤b≤{j+6}?',3,
            f'Avem a<0 și 2a+b={j}, deci b={j}−2a. Din b≤{j+6} rezultă a≥−3. Sunt exact a=−3,−2,−1, iar b={j+6},{j+4},{j+2}, toate admise.')
        add(2,8,j,f'Pentru ce m funcția f(x)={j}x+(m−{j})[x], unde [x]=⌊x⌋, este strict crescătoare pe ℝ?',
            f'm≥{j}',[f'm>{j}',f'm≤{j}',f'm<{j}'],
            f'Între doi întregi panta este {j}>0. La fiecare întreg, saltul este m−{j}, deci nu trebuie să fie negativ. Pentru m≥{j}, ambele componente sunt nedescrescătoare și termenul {j}x este strict crescător. Dacă m<{j}, saltul negativ distruge monotonia.')
        add(2,9,j,f'Fie f(x)=−{j}x+1 și g(x)={q}x−1. Care sunt, în ordine, monotoniile lui f∘f, f∘g, g∘f, g∘g?',
            'Crescătoare, descrescătoare, descrescătoare, crescătoare (toate strict).',
            ['Descrescătoare, crescătoare, crescătoare, descrescătoare (toate strict).','Toate sunt strict crescătoare.','Toate sunt strict descrescătoare.'],
            f'Pantele compunerilor sunt produsele pantelor: {j*j}>0, −{j*q}<0, −{j*q}<0 și {q*q}>0. Semnul lor dă exact ordinea indicată.')
        add(2,10,j,f'Fie f(x)={q}x pentru x∈ℚ și f(x)=−{q}x pentru x∉ℚ. Care este f(f(x)) și monotonia sa pe ℝ?',
            f'f(f(x))={q*q}x; strict crescătoare.',
            [f'f(f(x))=−{q*q}x; strict descrescătoare.',f'f(f(x))={q}x; strict crescătoare.','f(f(x)) nu este monotonă.'],
            f'Înmulțirea cu întregul nenul {q} păstrează raționalitatea și iraționalitatea. Dacă x este rațional, aplicăm de două ori prima ramură și obținem {q*q}x. Dacă este irațional, aplicăm de două ori a doua ramură: −{q}(−{q}x)={q*q}x. Panta este pozitivă.')

        add(3,1,j,f'Pentru ce x este f(x)=−{q}x+{q*j} strict pozitivă?',interval('−∞',j),
            [interval(j,'+∞'),interval('−∞',j,False,True),interval(j,'+∞',True,False)],
            f'−{q}x+{q*j}>0 echivalează cu x<{j}, deoarece împărțirea la −{q} inversează sensul. La x={j} valoarea este zero, deci capătul este exclus.')
        correct=interval('−∞',j,False,True)+' ∪ '+interval(j+2,'+∞')
        add(3,2,j,rf'Rezolvați \((x-{j})/(x-{j+2})\geq0\), în ℝ.',correct,
            [interval(j,j+2,True,False),interval('−∞',j)+ ' ∪ '+interval(j+2,'+∞'),interval('−∞',j,False,True)+' ∪ '+interval(j+2,'+∞',True,False)],
            f'Domeniul exclude x={j+2}. Raportul este pozitiv în exteriorul rădăcinii {j} și polului {j+2}, negativ între ele. Numărătorul se anulează la {j}, care se include; polul nu se include.')
        add(3,3,j,f'Fie h(x)=sign(x−{j})+2x·sign({j}−x), cu sign(0)=0. Care este scrierea pe ramuri?',
            f'2x−1 pentru x<{j}; 0 la x={j}; 1−2x pentru x>{j}.',
            [f'1−2x pentru x<{j}; 0 la x={j}; 2x−1 pentru x>{j}.',f'2x−1 pentru x≤{j}; 1−2x pentru x>{j}.',f'−1 pentru x<{j}; 0 la x={j}; 1 pentru x>{j}.'],
            f'Pentru x<{j}, semnele sunt −1 și +1, deci h=−1+2x. La x={j} ambii factori sign sunt zero. Pentru x>{j}, semnele devin +1 și −1, deci h=1−2x.')
        add(3,4,j,f'Scrieți pe ramuri f(x)=x+|x−{j}|.',f'{j} pentru x≤{j}; 2x−{j} pentru x>{j}.',
            [f'2x−{j} pentru x≤{j}; {j} pentru x>{j}.',f'−{j} pentru x≤{j}; 2x+{j} pentru x>{j}.',f'x−{j} pentru orice x.'],
            f'Dacă x≤{j}, modulul este {j}−x și suma devine {j}. Dacă x>{j}, modulul este x−{j}, deci suma este 2x−{j}. La prag ambele expresii coincid.')
        num(3,5,j,f'Pentru ce m funcția f(x)=(m−{j})x−{q} este pozitivă exact pe intervalul ({q}; +∞)?',j+1,
            f'Pozitivitatea în dreapta impune m−{j}>0. Rădăcina trebuie să fie {q}, deci {q}/(m−{j})={q}. Rezultă m−{j}=1 și m={j+1}.')
        add(3,6,j,f'Pentru f(x)=m(m−1)x+{j}, notați a=m(m−1). Care este mulțimea unde f(x)>0, în toate cazurile?',
            f'a>0: x>−{j}/a; a<0: x<−{j}/a; a=0: ℝ.',
            [f'a>0: x<−{j}/a; a<0: x>−{j}/a; a=0: ℝ.',f'a>0: x>−{j}/a; a<0: x<−{j}/a; a=0: ∅.',f'a>0: x≥−{j}/a; a<0: x≤−{j}/a; a=0: ℝ.'],
            f'a>0 pentru m<0 sau m>1: împărțim fără schimbarea sensului. a<0 pentru 0<m<1: sensul se inversează. La m=0 sau 1, funcția este constanta {j}>0, pozitivă pe ℝ. Inegalitatea fiind strictă, rădăcina se exclude.')
        add(3,7,j,f'Rezolvați {q}x−{j}≥−x+{q*j}.',interval(j,'+∞',True,False),
            [interval(j,'+∞'),interval('−∞',j,False,True),interval(-j,'+∞',True,False)],
            f'Aducem termenii în aceeași parte: ({q}+1)x≥{q*j}+{j}={j*(q+1)}. Împărțim la {q+1}>0 și obținem x≥{j}.')
        add(3,8,j,rf'Rezolvați \(1/(x-{j})\geq1/(x-{j+1})\).',interval(j,j+1),
            [interval(j,j+1,True,True),interval('−∞',j)+' ∪ '+interval(j+1,'+∞'),interval(j,j+1,True,False)],
            f'Excludem {j} și {j+1}. Diferența este −1/((x−{j})(x−{j+1})), nenegativă exact când produsul numitorului este negativ. Aceasta se întâmplă numai între cele două praguri, fără capete.')
        add(3,9,j,rf'Pentru ce m funcția \(f(x)=\frac{{m-{j}}}{{m+{j}}}x+1\) este strict crescătoare?',
            interval('−∞',-j)+' ∪ '+interval(j,'+∞'),
            [interval(-j,j),interval('−∞',-j)+' ∪ '+interval(j,'+∞',True,False),interval('−∞',-j,False,True)+' ∪ '+interval(j,'+∞')],
            f'Expresia nu este definită pentru m=−{j}. Panta este pozitivă dacă numărătorul și numitorul au același semn, adică m<−{j} sau m>{j}. La m={j}, panta este 0, deci funcția este constantă.')
        r=F(2*j,q)
        add(3,10,j,f'Care este descrierea graficului lui h(x)=max({q}x−{j}, {j})?',
            f'h(x)={j} pentru x≤{r}; h(x)={q}x−{j} pentru x>{r}.',
            [f'h(x)={q}x−{j} pentru x≤{r}; h(x)={j} pentru x>{r}.',f'h(x)={j} pentru orice x.',f'h(x)={q}x−{j} pentru orice x.'],
            f'Cele două expresii sunt egale când {q}x−{j}={j}, adică x={r}. În stânga acestui punct dreapta este sub constanta {j}, deci maximul este constanta. În dreapta, maximul este dreapta; la prag coincid.')
        add(3,11,j,f'Rezolvați |x−{j}|+|x−{j+2}|≤4.',interval(j-1,j+3,True,True),
            [interval(j,j+2,True,True),interval(j-1,j+3),interval(j-2,j+4,True,True)],
            f'Între {j} și {j+2}, suma distanțelor este 2≤4. Pentru x<{j}, suma este {2*j+2}−2x≤4, deci x≥{j-1}. Pentru x>{j+2}, suma este 2x−{2*j+2}≤4, deci x≤{j+3}. Reunind ramurile, obținem intervalul închis [{j-1};{j+3}].')
        add(3,12,j,f'Discutați după m inecuația (m−{j})x≤{q}.',
            f'm>{j}: x≤{q}/(m−{j}); m<{j}: x≥{q}/(m−{j}); m={j}: ℝ.',
            [f'm>{j}: x≥{q}/(m−{j}); m<{j}: x≤{q}/(m−{j}); m={j}: ℝ.',f'm>{j}: x≤{q}/(m−{j}); m<{j}: x≥{q}/(m−{j}); m={j}: ∅.',f'm≠{j}: x≤{q}/(m−{j}); m={j}: ℝ.'],
            f'Când m−{j}>0 împărțim fără schimbarea sensului; când este negativ inversăm sensul. Când m={j}, inecuația devine 0≤{q}, adevărată pentru orice x.')
        add(3,13,j,rf'Fie f(t)=t pentru t<0 și f(t)=t−1 pentru t≥0, iar \(g(x)=(x-{j})/(x-{j+1})\). Rezolvați f(g(x))>0.',
            interval(j+1,'+∞'),[interval('−∞',j),interval(j,j+1),interval(j,'+∞')],
            f'Domeniul exclude x={j+1}. Pe ramura t<0 avem f(t)=t<0; pe t≥0 avem f(t)>0 exact pentru t>1. Așadar cerem g(x)>1. Dar g(x)−1=1/(x−{j+1}), pozitiv exact pentru x>{j+1}.')
        add(3,14,j,f'Pentru ce m avem mx+{j}>0 pentru orice x∈[−1;1]?',interval(-j,j),
            [interval(-j,j,True,True),interval('−∞',j),interval(-j,'+∞')],
            f'O funcție afină este pozitivă pe întreg segmentul exact când este pozitivă la ambele capete. Condițiile sunt −m+{j}>0 și m+{j}>0, adică −{j}<m<{j}. La egalitate unul dintre capete ar avea valoarea 0.')

        points,kind,why = {
            1: ([(1,0),(1,2),(2,-1),(2,3)], 'Paralele distincte.', 'AB este verticala x=1, iar CD este verticala x=2. Sunt drepte verticale distincte, deci paralele; nu folosim pante finite.'),
            2: ([(2,0),(2,2),(0,3),(4,3)], 'Perpendiculare.', 'AB este verticala x=2, iar CD este orizontala y=3. O verticală și o orizontală se intersectează într-un unghi drept.'),
            3: ([(3,0),(4,1),(5,2),(6,3)], 'Coincidente.', 'AB și CD au ambele panta 1 și ecuația y=x−3. Toate cele patru puncte sunt pe aceeași dreaptă, deci dreptele coincid.'),
            4: ([(4,0),(5,1),(4,1),(5,3)], 'Secante, dar nu perpendiculare.', 'Pantele sunt 1 și 2: diferite, deci există o intersecție unică. Produsul pantelor este 2, diferit de −1, deci unghiul nu este drept.'),
            5: ([(5,0),(6,1),(5,1),(6,2)], 'Paralele distincte.', 'Ambele pante sunt 1. Ecuațiile sunt y=x−5 și y=x−4; ordonatele la origine diferă, deci dreptele sunt paralele distincte.'),
        }[j]
        labels=['Paralele distincte.','Coincidente.','Perpendiculare.','Secante, dar nu perpendiculare.']
        add(4,1,j,'Fie '+', '.join(f'{letter}{pair(*point)}' for letter,point in zip('ABCD',points))+'. Care este poziția dreptelor AB și CD?',
            kind,[v for v in labels if v!=kind],why)
        tup(4,2,j,f'Rezolvați sistemul x+y={2*j+1}, 2x−y={j-1} și indicați punctul de intersecție.',(j,q),
            f'Adunând ecuațiile, 3x={3*j}, deci x={j}; apoi y={2*j+1}−{j}={q}. Determinantul coeficienților este −3≠0, deci dreptele au exact acest punct comun.')
        tup(4,3,j,f'Rezolvați sistemul 2(x−1)+y={3*j-1}, x−(y+1)=−2.',(j,q),
            f'Dezvoltăm: 2x+y={3*j+1} și x−y=−1. Adunând, 3x={3*j}, deci x={j}, iar y=x+1={q}. Înlocuirea în relațiile inițiale confirmă soluția.')
        tup(4,4,j,rf'Rezolvați în ℝ², cu x,y≠0: \(1/x+1/y={F(2*j+1,j*q)},\quad1/x-1/y={F(1,j*q)}\).',(j,q),
            f'Punem u=1/x, v=1/y. Adunarea ecuațiilor dă 2u={F(2,j)}, deci u=1/{j}; scăderea dă 2v={F(2,q)}, deci v=1/{q}. Ambele sunt nenule, așadar x={j}, y={q}.')
        allpairs=[pair(s*j,t*q) for s,t in [(1,1),(1,-1),(-1,1),(-1,-1)]]
        add(4,5,j,f'Care este mulțimea soluțiilor sistemului |x|+|y|={2*j+1}, |x|−|y|=−1?',
            '{'+'; '.join(allpairs)+'}',
            ['{'+allpairs[0]+'}','{'+ '; '.join(allpairs[:2])+'}','{'+ '; '.join(allpairs[2:])+'}'],
            f'Cu u=|x|≥0 și v=|y|≥0, sistemul devine u+v={2*j+1}, u−v=−1, de unde u={j}, v={q}. Ambele sunt strict pozitive; fiecare necunoscută are independent două semne, rezultând toate cele patru perechi.')
        tup(4,6,j,rf'Rezolvați \(1/(x+y)+1/(x-y)={F(3,j)},\quad1/(x+y)-1/(x-y)={F(-1,j)}\), cu x+y≠0 și x−y≠0.',(F(3*j,4),F(j,4)),
            f'Notăm u=1/(x+y), v=1/(x−y). Adunând, 2u={F(2,j)}, deci u=1/{j}; apoi v=2/{j}. Rezultă x+y={j}, x−y={F(j,2)}, de unde x={F(3*j,4)}, y={F(j,4)}. Blocurile sunt nenule, deci soluția este admisă.')
        add(4,7,j,f'Discutați sistemul mx+y={j}, x+my={j}, după m∈ℝ.',
            'm≠±1: soluție unică; m=1: infinit de multe soluții; m=−1: nicio soluție.',
            ['m≠±1: soluție unică; m=−1: infinit de multe; m=1: nicio soluție.','Soluție unică pentru orice m.','m≠±1: nicio soluție; m=±1: infinit de multe soluții.'],
            f'Determinantul este m²−1. Pentru m≠±1 este nenul. La m=1 ecuațiile coincid: x+y={j}. La m=−1, adunarea ecuațiilor ar da 0={2*j}, imposibil deoarece {j}>0.')
        add(4,8,j,f'Alegem uniform m din mulțimea întregilor {{−{j},…,{j}}}. Care este probabilitatea ca mx+y=1, x+my=1 să aibă soluție unică?',str(F(2*j-1,2*j+1)),
            [str(F(2*j,2*j+1)),str(F(2*j-1,2*j+2)),str(F(2*j+1,2*j+2))],
            f'Sunt {2*j+1} valori echiprobabile. Determinantul m²−1 este nul numai la m=−1 și m=1, ambele în mulțime. Rămân {2*j-1} valori favorabile; probabilitatea este {F(2*j-1,2*j+1)}.')

        add(5,1,j,f'Rezolvați simultan x≥{j} și 2x≤{2*j+6}.',interval(j,j+3,True,True),
            [interval(j,j+3),interval('−∞',j+3,False,True),interval(j,'+∞',True,False)],
            f'A doua inecuație dă x≤{j+3}. Intersecția cu x≥{j} este [{j};{j+3}], ambele capete respectând ambele condiții.')
        add(5,2,j,f'Rezolvați |2x−{j}|≤x+{j}.',interval(0,2*j,True,True),
            [interval(0,2*j),interval(-j,2*j,True,True),interval('−∞',2*j,False,True)],
            f'Cerem x+{j}≥0 și −(x+{j})≤2x−{j}≤x+{j}. Inegalitatea din stânga dă x≥0, cea din dreapta x≤{2*j}. Aceste condiții implică și x+{j}>0, deci soluția este [0;{2*j}].')
        add(5,3,j,rf'Rezolvați simultan \((x-{j})/(x-{j+1})\geq0\) și \((x-{j+2})/(x-{j+1})\leq0\).',
            interval(j+1,j+2,False,True),[interval(j,j+2,True,True),interval(j+1,j+2,True,True),interval(j+1,j+2)],
            f'Domeniul comun exclude {j+1}. Prima inecuație dă (−∞;{j}]∪({j+1};+∞); a doua dă ({j+1};{j+2}]. Intersecția este ({j+1};{j+2}], cu polul exclus și rădăcina celei de-a doua fracții inclusă.')
        add(5,4,j,f'Rezolvați sistemul |x−{j}|≤2 și |x−{j+1}|<2.',interval(j-1,j+2,False,True),
            [interval(j-1,j+2,True,True),interval(j-2,j+3),interval(j-1,j+2)],
            f'Prima condiție este x∈[{j-2};{j+2}], a doua x∈({j-1};{j+3}). Intersecția păstrează capătul stâng deschis din a doua și capătul drept închis din prima: ({j-1};{j+2}].')
        num(5,5,j,f'Rezolvați ecuația max(x+{j}, 2x−{j})={3*j}.',2*j,
            f'Maximul este {3*j} dacă ambele expresii sunt cel mult {3*j} și cel puțin una este egală. Ambele inecuații dau x≤{2*j}; oricare egalitate impune x={2*j}. La această valoare ambele expresii sunt {3*j}.')
        add(5,6,j,f'Care este formula valabilă pe ℝ pentru h(x)=min(x+{j}, −x+{j}, {2*j})?',
            f'h(x)={j}−|x|',[f'h(x)={j}+|x|',f'h(x)={2*j}−|x|',f'h(x)={j}'],
            f'Minimul primelor două expresii este {j}−|x|: prima este activă pentru x≤0 și a doua pentru x≥0. Această valoare este cel mult {j}<{2*j}, deci a treia expresie nu devine niciodată minimul.')
        add(5,7,j,rf'Aflați x real astfel încât \(1/(x-{j})\in[0;x-{j}]\).',interval(j+1,'+∞',True,False),
            [interval(j,'+∞'),interval(j+1,'+∞'),interval('−∞',j-1,False,True)],
            f'Capătul drept al intervalului depinde de x. Domeniul exclude x={j}; apartenența cere simultan 0≤1/(x−{j}) și 1/(x−{j})≤x−{j}. Prima condiție impune x>{j}. Putem înmulți a doua cu x−{j}>0: 1≤(x−{j})², deci x−{j}≥1 și x≥{j+1}.')
        add(5,8,j,f'Determinați, pentru orice x real, intersecția [x; x+{j}]∩[0; {j}].',
            f'[max(x,0); min(x+{j},{j})] pentru −{j}≤x≤{j}; ∅ în rest.',
            [f'[min(x,0); max(x+{j},{j})] pentru −{j}≤x≤{j}; ∅ în rest.',
             f'[max(x,0); min(x+{j},{j})] pentru −{j}<x<{j}; ∅ în rest.',
             f'[max(x,0); min(x+{j},{j})] pentru 0≤x≤{j}; ∅ în rest.'],
            f'Ambele intervale sunt bine definite deoarece {j}>0. Intersecția este nevidă exact când x≤{j} și x+{j}≥0, adică −{j}≤x≤{j}. În acest caz este [max(x,0); min(x+{j},{j})]; la extreme rămâne un singleton.')
        add(5,9,j,f'Pentru ce m funcțiile f(x)=x+m−{j} și g(x)=−x+{q} sunt ambele strict pozitive pe [−1;1]?',
            f'm>{j+1}',[f'm≥{j+1}',f'm<{j+1}',f'm>{j-1}'],
            f'Minimul lui f este f(−1)=m−{j+1}, deci cerem m>{j+1}. Minimul lui g este g(1)={q-1}={j}>0, indiferent de m. Prin urmare prima condiție este necesară și suficientă.')
        add(5,10,j,f'Pentru ce m funcțiile f(x)=(m−{j})x+1 și g(x)=−x−{j} au semne contrare pentru orice x≥0?',
            f'm≥{j}',[f'm>{j}',f'm<{j}',f'm≤{j}'],
            f'Pe x≥0, g este mereu strict negativă. Trebuie deci f(x)>0 pentru orice x≥0. Dacă m−{j}≥0, f(x)≥1. Dacă m−{j}<0, pentru x suficient de mare f devine negativă. Rezultă exact m≥{j}, inclusiv cazul f≡1.')
    return [bank.finish(Counter({t:5 for t in range(1,len(NAMES[i])+1)})) for i,bank in enumerate(banks)]

if __name__ == '__main__':
    for filename,questions in zip(FILES,build()):
        path=ROOT/'clasa_9'/filename
        data=json.loads(path.read_text(encoding='utf-8'))
        data['questions']=questions
        data['difficulty']='medium'
        path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        print(f'{filename}: {len(questions)}')
