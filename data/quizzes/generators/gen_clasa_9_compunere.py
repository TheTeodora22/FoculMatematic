"""115 grile originale după cele 23 de tipuri A2 §5, p. 111–115."""
import json
from collections import Counter
from fractions import Fraction as F
from math import floor
from pathlib import Path
from catalog_grid_utils import GridBank, number_set

FILENAME='clasa_9_u02_l07_compunerea_functiilor.json'
NAMES=json.loads(Path(__file__).with_name('composition_type_names.json').read_text(encoding='utf-8'))

def build():
    b=GridBank('A2.5',NAMES)
    for j in range(1,6):
        q=j+1;n=j+2;t=F(1,j+2)
        b.numeric(1,rf'Fie \(f:({j-1},{j+1})\to(-1,1),\ f(x)=\frac{{2(x-{j})}}{{1+(x-{j})^2}}\) și \(g:(-1,1)\to({j-1},{j+1}),\ g(y)={j}+\frac{{\sqrt{{1+y}}-\sqrt{{1-y}}}}{{\sqrt{{1+y}}+\sqrt{{1-y}}}}\). Calculați \((g\circ f)({j}+1/{j+2})\).',j+t,
            f'Punem u=x−{j}∈(−1,1). Pentru y=2u/(1+u²), avem √(1±y)=(1±u)/√(1+u²), deoarece 1±u>0. Raportul din g devine u, deci g(f(x))={j}+u=x. Argumentul {j}+1/{j+2} este în domeniu, astfel rezultatul este {j+t}. Radicalii și numitorul sunt strict pozitivi. Reciproc, raportul v din g satisface |v|<1 și 2v/(1+v²)=y, deci și f(g(y))=y.')
        b.add(2,f'Fie f(x)={q}x+{j}, g(x)=x−{j}, ambele pe ℝ. Care este formula lui f∘g?',
            f'(f∘g)(x)={q}x−{j*j}',[f'(f∘g)(x)={q}x+{j}',f'(f∘g)(x)={q}x',f'(f∘g)(x)={q}x−{j*j+1}'],
            f'Aplicăm întâi g, apoi f: f(g(x))={q}(x−{j})+{j}={q}x−{j*j}. În ordinea inversă, g(f(x))={q}x, deci compunerea nu este în general comutativă. Ambele compuneri sunt definite pe tot ℝ.')
        b.numeric(3,f'Fie f(x)=|x| și g(x)=x−{j}, pe ℝ. Calculați (f∘g)(−2)−(g∘f)(−2).',2*j,
            f'f(g(−2))=|−2−{j}|={j+2}. În schimb, g(f(−2))=2−{j}={2-j}. Diferența este {j+2}−({2-j})={2*j}.')
        b.numeric(4,f'Pe ℕ={{0,1,…}}, f(n) este ultima cifră a lui 3ⁿ, iar g(n) ultima cifră a lui 2ⁿ. Calculați (f∘g)({j+3}).',pow(3,pow(2,j+3,10),10),
            f'Întâi g({j+3})={pow(2,j+3,10)}. Apoi calculăm ultima cifră a lui 3^{pow(2,j+3,10)}, care este {pow(3,pow(2,j+3,10),10)}. Se folosesc succesiv cele două reguli, nu ultima cifră a unui produs.')
        b.add(5,rf'Fie \(f(t)=\begin{{cases}}t^2,&t<0\\t+1,&t\ge0\end{{cases}}\), t∈ℝ, și g(x)=x−{j}. Care este f∘g?',
            rf'\((f\circ g)(x)=\begin{{cases}}(x-{j})^2,&x<{j}\\x-{j}+1,&x\ge {j}\end{{cases}}\)',
            [rf'\((f\circ g)(x)=\begin{{cases}}(x-{j})^2,&x<0\\x-{j}+1,&x\ge0\end{{cases}}\)',
             rf'\((f\circ g)(x)=\begin{{cases}}(x-{j})^2,&x\le {j}\\x-{j}+1,&x>{j}\end{{cases}}\)',
             rf'\((f\circ g)(x)=\begin{{cases}}x^2-{j},&x<{j}\\x-{j}+1,&x\ge {j}\end{{cases}}\)'],
            f'Ramura se alege după g(x), nu după x: g(x)<0 exact când x<{j}. Pentru x≥{j}, inclusiv x={j}, folosim ramura t+1, obținând x−{j}+1. La prag valoarea este 1, nu 0.')
        b.numeric(6,f'Fie f(x)={q}x+{j} și g(x)=2x+a, x∈ℝ. Pentru ce a avem f∘g=g∘f?',1,
            f'f(g(x))={2*q}x+{q}a+{j}; g(f(x))={2*q}x+{2*j}+a. Egalitatea termenilor liberi dă ({q}−1)a={j}, deci a=1.')
        val=q**n+j*sum(q**k for k in range(n))
        b.numeric(7,f'Fie f(x)={q}x+{j}, x∈ℝ. Calculați f aplicată succesiv de {n} ori argumentului 1. Iterarea înseamnă compunere, nu ridicare la putere.',val,
            f'Iterata de ordin n este fⁿ(x)={q}ⁿx+{j}(1+{q}+⋯+{q}ⁿ⁻¹), obținută prin inducție din fⁿ⁺¹(x)={q}fⁿ(x)+{j}. Pentru n={n}, x=1, rezultatul este {val}.')
        b.add(8,f'Există o funcție monotonă f:ℝ→ℝ care satisface f(f(x))=−x+{j} pentru orice x?',
            'Nu, compunerea f∘f ar fi ne-descrescătoare',
            ['Da, f(x)=−x','Da, f(x)=x','Da, orice funcție constantă'],
            'Dacă f este ne-descrescătoare, compunerea cu ea însăși este ne-descrescătoare. Dacă f este ne-crescătoare, cele două inversări ale ordinii dau tot o compunere ne-descrescătoare. Dar −x plus o constantă este strict descrescătoare pe ℝ, deci egalitatea este imposibilă.')
        b.add(9,f'Dacă f,g:ℝ→ℝ sunt strict descrescătoare, ce monotonie are h(x)=f(g(x))+{j}?',
            'Strict crescătoare',['Strict descrescătoare','Constantă','Obligatoriu nemonotonă'],
            f'Pentru x<y avem g(x)>g(y), apoi f(g(x))<f(g(y)), deoarece f inversează ordinea. Adăugarea lui {j} păstrează comparația, deci h este strict crescătoare.')
        b.add(10,f'Funcțiile f,g:ℝ→ℝ sunt impare și satisfac f({q})={q}, g({q})={q}. Ce paritate are h=f∘g?',
            'Impară, dar nu pară',['Pară, dar nu impară','Atât pară, cât și impară','Nici pară, nici impară'],
            f'h(−x)=f(g(−x))=f(−g(x))=−f(g(x))=−h(x). În plus h({q})={q}≠0; o funcție simultan pară și impară ar fi nulă, deci h nu este pară.')
        b.add(11,f'Definim f:ℝ→ℝ prin f(x)=x dacă x∈ℚ și f(x)={2*j}−x dacă x∉ℚ. Ce proprietăți au f și f∘f?',
            'f este nemonotonă, iar f∘f este identitatea',
            ['f este strict crescătoare, iar f∘f este constantă','f este strict descrescătoare, iar f∘f este identitatea','f∘f este strict descrescătoare'],
            f'Raționalele sunt fixate; pentru x irațional, {2*j}−x rămâne irațional și a doua aplicare dă x. Deci f(f(x))=x. Pe ({j+1},{j+2}), raționalele au imagini >{j}, iar iraționalele au imagini <{j}. Densitatea ambelor mulțimi permite atât creșteri, cât și descreșteri, deci f nu este monotonă.')
        b.add(12,f'Fie f(x)={q}x+{j}, g(x)=ax+b, pe ℝ. Determinați (a;b) astfel încât f(g(x))=x pentru orice x.',
            f'({F(1,q)};{F(-j,q)})',[f'({q};{-j})',f'({F(1,q)};{F(j,q)})',f'({F(-1,q)};{F(-j,q)})'],
            f'Avem f(g(x))={q}ax+{q}b+{j}. Identificăm coeficienții: {q}a=1 și {q}b+{j}=0, deci a={F(1,q)}, b={F(-j,q)}. Panta este nenulă, iar aceste funcții sunt inverse în ambele sensuri.')
        b.numeric(13,f'Fie f(x)={q}x+{j}, pe ℝ. Dacă f(g(x))={2*q}x+{q+j} pentru orice x, calculați g({j+2}).',2*(j+2)+1,
            f'Relația devine {q}g(x)+{j}={2*q}x+{q+j}. Scădem {j} și împărțim la {q}≠0: g(x)=2x+1. Deci g({j+2})={2*(j+2)+1}.')
        b.add(14,f'Fie f(x)=x²+{j}, x∈ℝ. Rezolvați ecuația f(f(x))={q*q+j}.',number_set([-1,1]),
            [number_set([1]),number_set([-q,q]),'∅'],
            f'Ecuația este (x²+{j})²+{j}={q*q+j}, deci (x²+{j})²={q*q}. Cum x²+{j}>0, alegem numai x²+{j}={q}. Rezultă x²=1 și x=±1. Ambele verifică ecuația; ramura negativă a rădăcinii nu este admisă.')
        b.numeric(15,f'Fie f:ℝ→ℝ strict crescătoare și f(f(x))=x pentru orice x. Calculați f({j+2}).',j+2,
            'Dacă f(x)>x, aplicarea strictei creșteri dă f(f(x))>f(x), adică x>f(x), contradicție. Dacă f(x)<x, obținem invers x<f(x), tot contradicție. Așadar f(x)=x pentru orice x.')
        b.add(16,f'Pe ℕ={{0,1,…}}, fie f(n)={q}n și g(n)=⌊n/{q}⌋. Care relație este adevărată?',
            'g∘f=Id, dar f∘g≠Id',['f∘g=Id, dar g∘f≠Id','Ambele compuneri sunt Id','Niciuna dintre compuneri nu este Id'],
            f'g(f(n))=⌊{q}n/{q}⌋=n. În schimb, f(g(1))={q}⌊1/{q}⌋=0≠1. În plus, nicio funcție h:ℕ→ℕ nu poate satisface f∘h=Id, deoarece 1 nu este în imaginea lui f.')
        b.add(17,f'Poate exista f:ℝ→ℝ cu f²(x)={q}x și f³(x)={q+1}x pentru orice x? Aici f² și f³ sunt iterate prin compunere.',
            'Nu, cele două moduri de a calcula f⁶ sunt incompatibile',
            [f'Da, f(x)={q}x',f'Da, f(x)={q+1}x','Da, f(x)=0'],
            f'Din f² rezultă f⁶(x)={q**3}x, prin trei compuneri; din f³ rezultă f⁶(x)={(q+1)**2}x, prin două compuneri. La x=1 acestea sunt distincte ({q**3}≠{(q+1)**2}), deci nu poate exista f.')
        b.numeric(18,f'Pentru ce a∈ℝ există f:ℝ→ℝ cu f²(x)=x și f³(x)=ax+{j} pentru orice x? Puterile desemnează iterate.',-1,
            f'Din f²=Id rezultă f³=f, deci f(x)=ax+{j}. Atunci f²(x)=a²x+{j}(a+1). Pentru egalitate cu x sunt necesare a²=1 și {j}(a+1)=0; cum {j}>0, a=−1. Funcția f(x)=−x+{j} verifică ambele relații, deci valoarea este și suficientă.')
        b.numeric(19,f'O mulțime A are {2*j+1} elemente. O funcție f:A→A satisface f(f(x))=x pentru orice x∈A. Care este numărul MINIM posibil de puncte fixe?',1,
            f'Elementele nefixate se împart în perechi distincte {{x,f(x)}}. Cum {2*j+1} este impar, rămâne cel puțin un punct fix. Minimul 1 se atinge fixând un element și împerechind celelalte {2*j}.')
        xx=F(-3*j-1,3);k=floor(xx);val=q**n*k+(xx-k)
        b.numeric(20,f'Fie f(x)=x+{j}⌊x⌋, x∈ℝ. Calculați iterata de ordin {n} în x=−{3*j+1}/3.',val,
            f'Scriem x=k+r, k=⌊x⌋, 0≤r<1. Atunci f(x)={q}k+r; partea fracționară r rămâne aceeași, iar partea întreagă se înmulțește cu {q}. Prin inducție, fⁿ(x)={q}ⁿk+r. Aici k={k}, r={xx-k}, n={n}, deci valoarea este {val}. Formula este valabilă și pentru x negativ.')
        b.numeric(21,f'Fie f:{{−{j},…,{j}}}→ℝ, f(x)=x. Câte restricții la subdomenii NEVIDE A au numai valori strict pozitive?',2**j-1,
            f'Argumentele cu imagine pozitivă sunt exact {{1,…,{j}}}. Orice submulțime nevidă a acestei mulțimi dă o restricție admisă și nu există altele. Numărul este 2^{j}−1={2**j-1}; am exclus domeniul vid.')
        b.numeric(22,f'Câte funcții f:{{1;2;3}}→{{{j};{j+1};{j+3}}} satisfac f(1)+f(2)+f(3)={3*j+3}?',4,
            f'Scădem {j} din fiecare valoare: cele trei valori noi aparțin {{0,1,3}} și au suma 3. Posibilitățile sunt (1,1,1) și cele trei permutări distincte ale lui (3,0,0). Total: 1+3=4 funcții. Repetarea imaginilor este permisă.')
        b.numeric(23,f'Fie f:ℝ→ℝ cu f(x)+2f({2*j}−x)=x pentru orice x. Calculați f({j+1}).',F(j,3)-1,
            f'Scriem relația și la {2*j}−x: f({2*j}−x)+2f(x)={2*j}−x. Înmulțim aceasta cu 2 și scădem prima relație: 3f(x)={4*j}−3x. Deci f(x)={F(4*j,3)}−x, care verifică relația inițială. Rezultă f({j+1})={F(j,3)-1}. În plus f(f(x))=x.')
    return b.finish(Counter({i:5 for i in range(1,24)}))

if __name__=='__main__':
    path=Path(__file__).resolve().parents[1]/'clasa_9'/FILENAME
    data=json.loads(path.read_text(encoding='utf-8'))
    data.update(difficulty='hard',questions=build())
    path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('115 grile generate')
