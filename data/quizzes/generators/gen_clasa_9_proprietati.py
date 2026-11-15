"""330 de grile originale după A2 §4.1–4.4; cinci pentru fiecare tip."""
import json
from collections import Counter
from fractions import Fraction as F
from math import gcd, lcm, floor, comb
from pathlib import Path
from catalog_grid_utils import GridBank, number_set
from clasa_9_property_lessons import LESSONS

NAMES=json.loads(Path(__file__).with_name('property_type_names.json').read_text(encoding='utf-8'))
CLASSIFICATIONS=['Strict crescătoare','Strict descrescătoare','Constantă','Nemonotonă']
PARITIES=['Pară, dar nu impară','Impară, dar nu pară','Atât pară, cât și impară','Nici pară, nici impară']

def classify(b,t,text,index,why,options=CLASSIFICATIONS):
    b.add(t,text,options[index],[v for k,v in enumerate(options) if k!=index],why)

def build():
    banks=[GridBank(f'A2.4.{i+1}',names) for i,names in enumerate(NAMES)]
    for j in range(1,6):
        q=j+1
        b=banks[0]
        vals=[x*x-j for x in [-2,-1,0,1,2]]
        b.add(1,f'Fie f:{{−2;−1;0;1;2}}→ℝ, f(x)=x²−{j}. Aflați (min f; max f).',
            f'({min(vals)}; {max(vals)})',[f'({min(vals)-1}; {max(vals)})',f'({min(vals)}; {max(vals)+1})',f'({max(vals)}; {min(vals)})'],
            f'Imaginea este {number_set(vals)}. Minimul {min(vals)} se atinge la 0, iar maximul {max(vals)} la ±2. Domeniul finit asigură mărginirea.')
        b.numeric(2,f'Fie f(n)=cmmdc(n,{6*q}), n∈ℕ*, unde cmmdc este cel mai mare divizor comun. Care este maximul funcției?',6*q,
            f'cmmdc(n,{6*q}) este un divizor pozitiv al lui {6*q}, deci 1≤f(n)≤{6*q}. Pentru n={6*q} se atinge valoarea {6*q}; aceasta este maximul.')
        b.add(3,f'Fie f:[0,+∞)→ℝ, f(x)=min(x,{q}). Care este imaginea sa?',f'[0, {q}]',
            [f'[0, {q})',f'(0, {q}]',f'[0, {q+1}]'],
            f'Pentru 0≤x≤{q}, f(x)=x; pentru x≥{q}, f(x)={q}. Se obțin exact valorile din [0,{q}], ambele capete fiind atinse.')
        b.add(4,f'Notăm {{x}}=x−⌊x⌋. Pentru f:ℝ→ℝ, f(x)={j}+{q}{{x}}, care este imaginea?',f'[{j}, {j+q})',
            [f'[{j}, {j+q}]',f'({j}, {j+q})',f'({j}, {j+q}]'],
            f'0≤{{x}}<1 implică {j}≤f(x)<{j+q}. Orice valoare din interval se obține alegând x∈[0,1) corespunzător. Capătul inferior este atins la întregi; cel superior nu este atins.')
        b.add(5,f'Fie f:ℝ→ℝ, f(x)={q}x²/(1+x²). Care este imaginea?',f'[0, {q})',
            [f'[0, {q}]',f'(0, {q})',f'(-∞, {q})'],
            f'f(x)={q}−{q}/(1+x²), deci 0≤f(x)<{q}. Minimul 0 se atinge la x=0. Pentru 0≤y<{q}, ecuația x²=y/({q}−y) are soluții reale, deci toate aceste valori sunt atinse.')
        b.numeric(6,f'Fie f:(0,1]→ℝ, f(x)=1/x+{j}. Calculați f(1/{j+3}); acest șir de argumente ilustrează nemărginirea superioară.',2*j+3,
            f'În general, pentru xₙ=1/n, avem f(xₙ)=n+{j}. Pentru orice prag M alegem întregul n>M−{j}, deci nu există o margine superioară. La n={j+3}, valoarea este {2*j+3}.')
        b.numeric(7,f'Pentru ce a∈ℝ funcția f(x)={q}{{x}}+(a−{j})⌊x⌋, x∈ℝ, este mărginită? Aici {{x}}=x−⌊x⌋.',j,
            f'La întregul n, f(n)=(a−{j})n. Dacă a≠{j}, valorile sunt nemărginite când n parcurge ℤ. Pentru a={j}, rămâne {q}{{x}}, cu valori în [0,{q}).')
        b.add(8,f'Pentru n≥1, f(n) este rădăcina pozitivă t a ecuației t²+{2*j}t−n²=0. Care afirmație este corectă?',
            'Mărginită inferior, nemărginită superior',['Mărginită superior și inferior','Nemărginită inferior','Constantă'],
            f'Rădăcina pozitivă este f(n)=√(n²+{j*j})−{j}>0. Cum √(n²+{j*j})≥n, avem f(n)≥n−{j}, deci funcția depășește orice prag. Cealaltă rădăcină este negativă și nu este selectată.')
        b=banks[1]
        classify(b,1,f'Clasificați paritatea lui f:ℝ→ℝ, f(x)=x³+{j}x.',1,
            f'Domeniul este simetric și f(−x)=−x³−{j}x=−f(x). Funcția nu este nulă, de exemplu f(1)={q}, deci nu este și pară.',PARITIES)
        classify(b,2,f'Clasificați f:[−{j},{j+1}]→ℝ, f(x)=x², folosind definiția care cere un domeniu simetric.',3,
            f'Domeniul nu este simetric: {j+1} aparține, dar −{j+1} nu aparține. Astfel funcția nu este nici pară, nici impară în sensul definiției, chiar dacă formula x² este pară pe ℝ.',PARITIES)
        classify(b,3,rf'Clasificați paritatea lui \(f(x)=\begin{{cases}}x^2,&|x|\le {j}\\{j},&|x|>{j}\end{{cases}}\), cu domeniul ℝ.',0,
            'Înlocuirea lui x cu −x păstrează condiția fiecărei ramuri. Pe prima ramură (−x)²=x², iar pe a doua valoarea este constantă; deci f(−x)=f(x). Funcția este nenulă și nu poate fi simultan impară.',PARITIES)
        b.numeric(4,f'Pentru ce a funcția f(x)=x²+(a−{j})x+1, x∈ℝ, este pară?',j,
            f'f(x)−f(−x)=2(a−{j})x. Aceasta se anulează pentru orice x exact când a={j}; termenii rămași sunt pari.')
        classify(b,5,f'Clasificați f:ℝ→ℝ, f(x)=max({q}x,0)−max(−{q}x,0).',1,
            f'Pentru x≥0 expresia este {q}x; pentru x<0 este tot {q}x. Funcția liniară nenulă {q}x este impară și nu este pară.',PARITIES)
        b.add(6,f'Fie f(x)=x³+{j}x²+{q}, x∈ℝ. Care este partea pară g din descompunerea f=g+h, cu g pară și h impară?',
            f'g(x)={j}x²+{q}',[f'g(x)=x³',f'g(x)=x³+{j}x²',f'g(x)={j}x²'],
            f'g(x)=(f(x)+f(−x))/2={j}x²+{q}. Partea impară este h(x)=(f(x)−f(−x))/2=x³. Suma celor două este f.')
        b.numeric(7,f'Graficul lui f(x)=(x−{j})²+{q}, x∈ℝ, are axa verticală x=a. Aflați a.',j,
            f'f(2·{j}−x)=({j}−x)²+{q}=f(x). Domeniul ℝ este stabil la reflexie. Vârful parabolei are abscisa {j}, deci aceasta este unica axă verticală.')
        b.numeric(8,f'Pentru ce m graficul lui f(x)=x²+mx+{q} are axa verticală x={j}?',-2*j,
            f'Axa parabolei x²+mx+{q} este x=−m/2, prin completarea pătratului. Egalitatea −m/2={j} dă m=−{2*j}.')
        b.numeric(9,f'O funcție f:ℝ→ℝ satisface f({2*j}−x)=f(x) pentru orice x. Ce abscisă are axa verticală garantată de relație?',j,
            f'Argumentele x și {2*j}−x sunt simetrice față de semisuma lor {j}. Relația arată că punctele reflectate au aceeași ordonată, deci x={j} este axă. Nu se afirmă că ar fi singura axă.')
        b.add(10,f'Care este centrul de simetrie al graficului lui f(x)=(x−{j})³+{q}, x∈ℝ?',f'({j};{q})',
            [f'({-j};{q})',f'({j};{-q})',f'(0;{q})'],
            f'În coordonatele u=x−{j}, v=y−{q}, graficul este v=u³, impar. Echivalent, f(2·{j}−x)+f(x)=2·{q}; centrul este ({j},{q}).')
        b.add(11,f'Pentru c>0, familia f_c(x)={q}+c/(x−{j}), x≠{j}, are un centru comun. Care este acesta?',f'({j};{q})',
            [f'({j};0)',f'(0;{q})',f'({-j};{-q})'],
            f'Domeniul ℝ∖{{{j}}} este simetric față de {j}. Avem f_c(2·{j}−x)+f_c(x)=2·{q}, deoarece fracțiile au numitori opuși. Centrul ({j},{q}) nu depinde de c.')
        b.numeric(12,f'Fie f(x)=⌊x⌋+{j}, definită pe ℝ∖ℤ. Ce ordonată are centrul de simetrie cu abscisa 0?',F(2*j-1,2),
            f'Pentru x∉ℤ, ⌊x⌋+⌊−x⌋=−1. Astfel f(x)+f(−x)={2*j-1}=2b, deci b={F(2*j-1,2)}. Excluderea întregilor este esențială pentru această identitate.')
        b.add(13,f'Aflați centrul de simetrie al graficului lui f(x)=2x+1/(x−{j}), x≠{j}.',f'({j};{2*j})',
            [f'({j};{j})',f'(0;{2*j})',f'({-j};{-2*j})'],
            f'Punem x={j}+u: f(x)=2·{j}+2u+1/u. Expresia 2u+1/u este impară pe ℝ∖{{0}}, deci centrul este ({j},{2*j}). Un centru trebuie să păstreze și punctul exclus din domeniu, ceea ce impune abscisa {j}.')
        b.add(14,rf'Pentru f(x)=cos(2πx/{q}), x∈ℝ, care familie este alcătuită numai din axe verticale de simetrie?',
            rf'\(x=k\,{q}/2,\quad k\in\mathbb{{Z}}\)',
            [rf'\(x={q}/4+k\,{q}/2,\quad k\in\mathbb{{Z}}\)',rf'\(x={q}/8+k\,{q}/2,\quad k\in\mathbb{{Z}}\)',rf'\(x={q}/3+k\,{q},\quad k\in\mathbb{{Z}}\)'],
            f'Pentru a=k·{q}/2, f(2a−x)=cos(2kπ−2πx/{q})=f(x). Valorile întregi ale lui k dau infinit de multe axe. Pentru celelalte familii, deja primul membru nu satisface identitatea la x=0.')
        b.add(15,f'Care este cea mai mare submulțime simetrică față de 0 a intervalului [−{j},{j+2}], pe care poate fi restrânsă f(x)=x² pentru a fi pară?',f'[−{j},{j}]',
            [f'[−{j},{j+2}]',f'[0,{j}]',f'(−{j},{j})'],
            f'Domeniul restricției trebuie să conțină −x ori de câte ori conține x. Intersecția D∩(−D)=[−{j},{j}] este cea mai mare mulțime cu această proprietate; x² este pară pe ea. Intervalul deschis este mai mic și nu este maximal.')
        b.add(16,f'Fie f(x)=x pe D=ℝ∖{{{j};{j+2}}}. Care este unicul centru al graficului?',f'({j+1};{j+1})',
            [f'({j};{j})',f'({j+2};{j+2})',f'(0;0)'],
            f'Un centru (a,b) al dreptei restrânse trebuie să aibă b=a și să păstreze mulțimea celor două abscise excluse. Reflexia le schimbă între ele, deci a=({j}+{j+2})/2={j+1}. Acest centru păstrează domeniul și graficul; este unic.')
        classify(b,17,f'O funcție nenulă f:ℝ→ℝ satisface f(x+y)=f(x)+f(y) pentru orice x,y și f(1)={j}. Ce paritate are?',1,
            f'La x=y=0 rezultă f(0)=0. Pentru y=−x, 0=f(x)+f(−x), deci f este impară. Deoarece f(1)={j}≠0, nu poate fi și pară.',PARITIES)
        b=banks[2]
        b.numeric(1,f'Fie f:ℤ→ℝ, f(n)={j}(−1)ⁿ. Care este cea mai mică perioadă întreagă pozitivă?',2,
            f'f(n+2)=f(n), iar f(0)={j} și f(1)=−{j} sunt distincte; 1 nu este perioadă. Deci perioada principală este 2.')
        base=[3,7,9,2,8][j-1];period=2 if base==9 else 4
        b.numeric(2,f'Fie f(n) ultima cifră a lui {base}ⁿ, n∈ℕ*. Care este perioada principală întreagă?',period,
            f'Primele valori sunt {", ".join(str(pow(base,k,10)) for k in range(1,period+1))}, după care ciclul se repetă. Nicio deplasare pozitivă mai mică decât {period} nu păstrează întregul ciclu, deci perioada principală este {period}.')
        b.numeric(3,f'Fie r(n) restul euclidian al lui n la împărțirea cu {q}, n∈ℤ. Care este perioada principală pozitivă?',q,
            f'r(n+{q})=r(n). Dacă T este perioadă, r(T)=r(0)=0, deci T este multiplu de {q}. Cel mai mic multiplu pozitiv este {q}.')
        b.numeric(4,f'Pe ℕ={{0,1,…}}, definim f(n)={j+3} dacă n<{j}, iar f(n)=(−1)ⁿ dacă n≥{j}. Care este cel mai mic N≥0 de la care relația f(n+2)=f(n) este valabilă pentru orice n≥N?',j,
            f'Pentru n≥{j}, termenii sunt alternanți și se repetă după 2. La n={j-1}, valoarea excepțională {j+3} diferă de f({j+1})∈{{−1,1}}, deci niciun N≤{j-1} nu funcționează. Acesta este un prag de periodicitate eventuală, nu periodicitate pe tot ℕ.')
        b.numeric(5,f'Fie f(x)={{x/{q}}}, x∈ℝ, unde {{u}}=u−⌊u⌋. Care este perioada principală pozitivă?',q,
            f'Adăugarea lui {q} la x adaugă 1 argumentului părții fracționare. Orice perioadă T>0 trebuie să satisfacă f(T)=f(0)=0, adică T/{q}∈ℤ; minimul pozitiv este {q}.')
        b.numeric(6,f'Funcțiile f și g au perioadele {q} și {q+1}. Care este cel mai mic număr pozitiv care este multiplu întreg al ambelor perioade și este astfel o perioadă garantată pentru f+g?',lcm(q,q+1),
            f'Folosim cmmmc({q},{q+1})={lcm(q,q+1)}. Translația cu acest număr păstrează separat f și g. Nu afirmăm că este perioada principală a sumei, care poate avea o perioadă mai mică sau poate fi constantă.')
        b.numeric(7,f'Fie f(x)={j}(−1)^⌊x⌋{{x}}, x∈ℝ, cu {{x}}=x−⌊x⌋. Care este perioada principală pozitivă?',2,
            f'La x+2 partea întreagă crește cu 2, iar partea fracționară rămâne neschimbată. Dacă T este perioadă, f(T)=f(0)=0, deci T este întreg. Translația cu 1 schimbă semnul valorii nenule f(1/2)={F(j,2)}, deci cel mai mic T>0 este 2.')
        p=[2,3,5,7,11][j-1]
        b.numeric(8,f'Fie p={p} și f(n) restul lui nᵖ la împărțirea cu p, n∈ℤ. Care este perioada principală întreagă pozitivă?',p,
            f'Pentru p prim, nᵖ≡n (mod p), inclusiv dacă p divide n. Așadar f este funcția restului modulo {p}, cu perioada principală {p}: f(T)=f(0)=0 impune p∣T.')
        b.add(9,f'Fie f:ℝ→ℝ cu f(x)={j} pentru x∈ℚ și f(x)=0 pentru x∉ℚ. Care afirmație despre perioade este corectă?',
            'Toate raționalele pozitive sunt perioade; nu există perioadă principală',
            ['Perioada principală este 1','Toate numerele reale pozitive sunt perioade','Funcția nu este periodică'],
            'Translația cu un rațional păstrează atât raționalele, cât și iraționalele. Orice T irațional eșuează la x=0, deoarece f(T)≠f(0). Nu există cel mai mic rațional pozitiv: pentru orice astfel de T, și T/2 este perioadă.')
        b.numeric(10,f'O funcție neconstantă f:ℝ→ℝ are axele verticale x={j} și x={j+q}. Ce perioadă pozitivă rezultă prin compunerea celor două reflexii?',2*q,
            f'Reflexiile sunt x↦2·{j}−x și x↦2·{j+q}−x. Compunerea dă translația x↦x+{2*q}, deci f(x+{2*q})=f(x). Aceasta este o perioadă garantată, nu neapărat principala.')
        xx=F(-j,3);nn=j+2;hermite=sum(floor(xx+F(k,nn)) for k in range(nn))
        b.numeric(11,rf'Folosind relația lui Hermite, calculați \(\sum_{{k=0}}^{{{nn-1}}}\left\lfloor -{j}/3+k/{nn}\right\rfloor\).',hermite,
            f'Identitatea este Σₖ₌₀ⁿ⁻¹⌊x+k/n⌋=⌊nx⌋. Pentru justificare, diferența celor două membre este invariantă la x↦x+1/n. Reducem la 0≤x<1/n, unde toate părțile întregi sunt 0. Aici rezultatul este ⌊−{nn*j}/3⌋={hermite}.')
        b.add(12,f'Care funcție definită pe ℝ are perioada principală pozitivă exact {q}?',f'f(x)={{x/{q}}}',
            [f'f(x)=x/{q}',f'f(x)={{x/{2*q}}}',f'f(x)=0'],
            f'Pentru {{x/{q}}}, perioada {q} funcționează, iar f(T)=f(0) impune T/{q} întreg. Funcția liniară nenulă nu este periodică; {{x/{2*q}}} are perioada principală {2*q}; funcția nulă admite orice T>0 și nu are perioadă principală.')
        b.numeric(13,f'Funcția f:ℝ→ℝ are perioada principală {q}. Care este perioada principală a lui g(x)=f({q}x+{j})?',1,
            f'O translație T a argumentului lui g produce deplasarea {q}T pentru f. Deoarece x↦{q}x+{j} parcurge tot ℝ, T este perioadă a lui g exact când {q}T este perioadă a lui f. Minimul este {q}/{q}=1.')
        b.numeric(14,f'Funcțiile f și g au perioadele {2*q} și {3*q}. Care este cel mai mic multiplu întreg comun al lor, garantat ca perioadă atât pentru f+g, cât și pentru fg?',6*q,
            f'cmmmc({2*q},{3*q})={6*q}. La această translație fiecare factor și fiecare termen își păstrează valoarea. Poate exista o perioadă mai mică a sumei sau produsului; aici cerem multiplul comun minim.')
        b.numeric(15,f'Funcția g:ℝ→ℝ are perioada {q}, iar f(x)={j}g(x)+g(x+1). Ce perioadă a lui f se deduce direct din relație?',q,
            f'f(x+{q})={j}g(x+{q})+g(x+1+{q})={j}g(x)+g(x+1)=f(x). Se garantează perioada {q}, fără a afirma minimalitatea ei.',wrong=[F(q,2),F(q,3),F(q,4)])
        b.add(16,f'Pe ℕ, definim f(n)={j} dacă n este pătrat perfect și f(n)=0 altfel. Care afirmație este corectă?',
            'Imaginea este finită, dar funcția nu este periodică',
            ['Funcția are perioada 2','Funcția este constantă','Imaginea este infinită'],
            f'Imaginea este {{0;{j}}}. Dacă T≥1 ar fi perioadă, alegem pătratul k² cu 2k+1>T. Atunci k²<k²+T<(k+1)², deci f(k²)={j}, dar f(k²+T)=0: contradicție. Imaginea finită nu implică periodicitate.')
        b.numeric(17,f'Funcția f:ℝ→ℝ satisface f(x+T)=f(x) pentru orice x și orice T irațional, iar f(0)={j}. Cât este f({j+2})?',j,
            f'Orice deplasare rațională r este suma iraționalelor √2 și r−√2; aplicarea succesivă a invariabilității arată că și r păstrează valoarea. Deplasările iraționale o păstrează prin ipoteză, deci f este constantă și egală cu {j}.')
        b.numeric(18,f'Fie f:ℝ→ℝ∖{{0;1}} cu f(x+{q})=1/(1−f(x)) pentru orice x. Ce perioadă pozitivă se obține după trei aplicări ale relației?',3*q,
            f'Pentru H(t)=1/(1−t), t≠0,1, avem H²(t)=(t−1)/t și H³(t)=t. Prin urmare f(x+{3*q})=f(x). Excluderea valorilor 0 și 1 asigură existența tuturor fracțiilor.')
        b.add(19,f'O funcție periodică f:ℝ→ℝ are mulțimea {{f(n):n∈ℕ}} infinită și f(0)={j}. Ce se poate afirma despre orice perioadă pozitivă T?',
            'T este irațional',['T este întreg','T este rațional neîntreg','T este obligatoriu 1'],
            'Dacă T=p/q>0 ar fi rațională, cu p,q întregi pozitivi, atunci p=qT ar fi perioadă. Valorile f(n) ar depinde doar de n modulo p, deci ar fi cel mult p valori. Contradicția exclude toate perioadele raționale; nu se presupune existența unei perioade principale.')
        b=banks[3]
        classify(b,1,f'Clasificați monotonia lui f(x)={q}x+{j}, x∈ℝ.',0,
            f'Pentru x<y, f(y)−f(x)={q}(y−x)>0, deci funcția este strict crescătoare.')
        classify(b,2,f'Clasificați f(n)={j+3}n+cmmdc(n,n+2), n∈ℕ*.',0,
            f'cmmdc(n,n+2)=cmmdc(n,2)∈{{1,2}}. Diferența termenilor cmmdc este cel puțin −1, deci f(n+1)−f(n)≥{j+3}−1={j+2}>0. Prin însumarea diferențelor, f crește strict pe ℕ*.')
        b.add(3,f'Care sunt intervalele maximale de monotonie ale lui f(x)=(x−{j})², x∈ℝ?',
            f'Strict descrescătoare pe (−∞,{j}], strict crescătoare pe [{j},+∞)',
            [f'Strict crescătoare pe ℝ',f'Strict descrescătoare pe ℝ',f'Constantă pe [−{j},{j}]'],
            f'La stânga lui {j}, distanța |x−{j}| scade când x crește; la dreapta crește. Pătratul păstrează ordinea distanțelor nenegative. Vârful separă cele două intervale maximale.')
        b.add(4,f'Pentru f(x)=|x−{j+1}|−|x−{j}|, x∈ℝ, care descriere este corectă?',
            f'Constantă pe (−∞,{j}] și [{j+1},+∞); strict descrescătoare pe [{j},{j+1}]',
            [f'Strict crescătoare pe ℝ',f'Strict descrescătoare pe ℝ',f'Constantă pe ℝ'],
            f'Pe x≤{j}, expresia este 1. Pe [{j},{j+1}], este {2*j+1}−2x, strict descrescătoare. Pe x≥{j+1}, este −1. Funcția este necreșcătoare global, dar nu strict pe intervalele constante.')
        b.add(5,f'Fie f(x)=(x−{j})/(x−{j+1}), x≠{j+1}. Care afirmație este corectă?',
            'Strict descrescătoare pe fiecare componentă a domeniului',
            ['Strict crescătoare pe fiecare componentă','Strict descrescătoare pe întregul domeniu','Constantă pe fiecare componentă'],
            f'f(x)=1+1/(x−{j+1}). Pentru x<y pe aceeași componentă, f(y)−f(x)=(x−y)/((x−{j+1})(y−{j+1}))<0. Global nu este descrescătoare: pentru x={j}, y={j+2}, valorile sunt 0 și 2.')
        classify(b,6,f'Clasificați f(x)={j}x/(1+x²) pe intervalul [0,1].',0,
            f'Pentru 0≤x<y≤1, f(y)−f(x)={j}(y−x)(1−xy)/((1+x²)(1+y²)). Toți factorii sunt pozitivi, inclusiv 1−xy deoarece x<y≤1; funcția crește strict.')
        classify(b,7,f'Clasificați f(x)={q}ˣ+{q+1}ˣ, x∈ℝ.',0,
            f'Ambele baze {q} și {q+1} sunt mai mari ca 1. Pentru x<y, fiecare putere la x este strict mai mică decât cea la y; adunarea dă f(x)<f(y).')
        b.numeric(8,f'Care este cel mai mic m∈ℝ pentru care f_m(x)=x²+2mx+{j} este crescătoare pe [2m+{3*j},+∞)?',-j,
            f'Vârful este la x=−m. Pentru ca întreaga semidreaptă să fie pe ramura crescătoare este necesar și suficient 2m+{3*j}≥−m, adică m≥−{j}. La egalitate, intervalul începe în vârf și funcția crește strict după acesta.')
        classify(b,9,f'Clasificați f(x)=x+{j}⌊x⌋, x∈ℝ.',0,
            f'Pentru x<y avem ⌊x⌋≤⌊y⌋, deci f(y)−f(x)=(y−x)+{j}(⌊y⌋−⌊x⌋)>0. Termenul x elimină segmentele constante ale părții întregi.')
        classify(b,10,f'Dacă f:ℝ→ℝ este strict crescătoare, cum este g(x)=x³+{j}f(x)?',0,
            f'Pentru x<y avem x³<y³ și {j}f(x)<{j}f(y). Adunarea acestor inegalități arată că g(x)<g(y).')
        classify(b,11,f'Funcția f:ℝ→ℝ este strict crescătoare, iar g este ne-descrescătoare. Cum este h(x)=f(x)+{j}g(x)?',0,
            f'Pentru x<y, f(x)<f(y), g(x)≤g(y). Înmulțind a doua inegalitate cu {j}>0 și adunând, obținem h(x)<h(y).')
        classify(b,12,f'Funcțiile f,g:ℝ→(0,+∞) sunt strict crescătoare. Cum este h(x)={j}f(x)g(x)?',0,
            f'Pentru x<y, 0<f(x)<f(y) și 0<g(x)<g(y). Astfel f(x)g(x)<f(y)g(x)<f(y)g(y). Înmulțirea cu {j}>0 păstrează strictețea.')
        classify(b,13,f'Dacă f:ℝ→ℝ este strict crescătoare, clasificați g(x)=f(−{q}x+{j}).',1,
            f'Dacă x<y, atunci −{q}x+{j}>−{q}y+{j}. Aplicarea funcției strict crescătoare f păstrează această ordine, deci g(x)>g(y).')
        classify(b,14,f'Dacă f:ℝ→(0,+∞) este strict crescătoare, clasificați g(x)={j}/f(x).',1,
            f'Pentru x<y, 0<f(x)<f(y). Trecerea la inverse pozitive schimbă sensul: 1/f(x)>1/f(y). Factorul {j}>0 păstrează ordinea; condiția de pozitivitate evită traversarea lui zero.')
        classify(b,15,f'O funcție f:ℝ→ℝ este ne-descrescătoare și periodică cu perioada {q}>0. Ce concluzie este obligatorie?',2,
            f'Pentru x<y alegem n astfel încât y<x+n·{q}. Monotonia dă f(x)≤f(y)≤f(x+n·{q})=f(x), deci f(y)=f(x). Astfel funcția este constantă pe ℝ.')
        b.add(16,rf'Pentru ce a∈ℝ funcția \(f(x)=\begin{{cases}}x+{j},&x<0\\2x+a,&x\ge0\end{{cases}}\) este ne-descrescătoare pe ℝ?',
            f'a≥{j}',[f'a<{j}',f'a≤{j}',f'a>{j+1}'],
            f'Ambele ramuri au pante pozitive. Pentru a nu apărea un salt în jos la 0, este necesar a=f(0)≥{j}, limita valorilor din stânga. Dacă a≥{j}, orice valoare din stânga este <{j}≤a și orice valoare din dreapta este ≥a, deci condiția este și suficientă.')
        classify(b,17,f'Funcția f:ℝ→ℝ satisface f(x)+f(−x)=2x² și f(x)−f(−x)={2*j}x, pentru orice x. Cum este g(x)=f(x)−x²?',0,
            f'Adunând relațiile, 2f(x)=2x²+{2*j}x, deci f(x)=x²+{j}x. Atunci g(x)={j}x, strict crescătoare deoarece {j}>0.')
        b.add(18,f'Fie f(x)={j} dacă x∈ℚ și f(x)=0 dacă x∉ℚ. Pe ce intervale cu lungime pozitivă este f monotonă?',
            'Pe niciun interval cu lungime pozitivă',
            ['Pe toate intervalele','Numai pe intervale cu capete raționale','Numai pe intervale cu capete iraționale'],
            f'Raționalele și iraționalele sunt dense în orice interval de lungime pozitivă. Putem alege x<y cu valori ({j},0), încălcând creșterea, și alte x<y cu valori (0,{j}), încălcând descreșterea. Alegerea capetelor intervalului nu schimbă argumentul.')
        b.numeric(19,f'Câte funcții strict crescătoare f:{{1;2;3}}→{{1;2;…;{j+3}}} există?',comb(j+3,3),
            f'Alegem trei valori distincte din cele {j+3}; ordinea lor crescătoare fixează imaginile lui 1,2,3 în mod unic. Numărul este C({j+3},3)={comb(j+3,3)}.')
        b.add(20,f'Fie f:ℝ→ℝ ne-descrescătoare, cu f(0)={j}. Care descompunere f=g+h garantează că g este strict crescătoare și h strict descrescătoare?',
            f'g(x)=f(x)+{j}x, h(x)=−{j}x',
            [f'g(x)=f(x)−{j}x, h(x)={j}x',f'g(x)=f(x), h(x)=0',f'g(x)=f(x)+{j}, h(x)=−{j}'],
            f'Suma este f. Pentru x<y, g(y)−g(x)=f(y)−f(x)+{j}(y−x)>0. În același timp, h(y)−h(x)=−{j}(y−x)<0. Constanța posibilă a lui f nu afectează strictețea acestor două funcții.')
        b.numeric(21,f'Fie A={{1;…;{j+3}}} și f:A→A strict crescătoare. Calculați f({j+1}).',j+1,
            f'O aplicație strict crescătoare este injectivă; pe o mulțime finită cu același codomeniu este bijectivă. Imaginile elementelor enumerate crescător sunt deci exact aceleași elemente, în aceeași ordine: f(k)=k. Astfel f({j+1})={j+1}.')
        b.numeric(22,f'Fie f:ℝ→ℝ ne-descrescătoare, cu f(r)=r pentru orice r∈ℚ. Calculați f({j}+√2)−√2.',j,
            f'Dacă f(x)>x, alegem un rațional r între x și f(x); monotonia ar da f(x)≤f(r)=r, contradicție. Dacă f(x)<x, alegem r între f(x) și x și obținem r=f(r)≤f(x), iarăși contradicție. Deci f(x)=x pentru orice real, inclusiv {j}+√2; diferența cerută este {j}.')
    return [bank.finish(Counter({i:5 for i in range(1,len(names)+1)})) for bank,names in zip(banks,NAMES)]

if __name__=='__main__':
    root=Path(__file__).resolve().parents[1]/'clasa_9'
    for (filename,title),questions,difficulty in zip(LESSONS,build(),['medium','hard','hard','hard']):
        path=root/filename
        data=json.loads(path.read_text(encoding='utf-8'))
        data.update(title=title,difficulty=difficulty,questions=questions)
        path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        print(path.name,len(questions),difficulty)
