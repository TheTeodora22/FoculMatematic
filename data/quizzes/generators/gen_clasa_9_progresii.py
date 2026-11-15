"""Grile originale după A2 §2.1–2.3. Catalogul este sursă de tipologii."""
import json
from collections import Counter
from fractions import Fraction as F
from pathlib import Path
from catalog_grid_utils import GridBank

NAMES = [
 ['Termen de rang dat în PA','Recuperarea primului termen','Rația din doi termeni','Apartenența la PA','Sume din termeni egal depărtați','Completarea progresiei','Suma primilor n termeni','Determinarea PA din relații liniare','Determinarea PA din produse sau pătrate','Recuperarea PA din Sₙ','Trei sau cinci termeni cu sumă și produs','Recunoașterea PA din termenul general','Recunoașterea PA din suma parțială','Numărul termenilor unei PA','Sume ale multiplilor și nemultiplilor','Relații între sume de lungimi multiple','PA obținute prin grupare','Subșir cu indici în PA'],
 ['Termen general al PG','Recuperarea PG din termeni','Recunoașterea PG explicite','PG din suma parțială','Transformări ale termenilor PG','Recurențe geometrice','Apartenența la PG','Suma finită a PG','Determinarea PG din condiții neliniare','PG modificată în PA','Legarea unei PA de o PG','Linearizarea unei recurențe afine','Linearizarea unei recurențe omografice','Diferențe consecutive geometrice','Recurență cu termen dependent de rang','Sume de termeni geometrici derivați','Sume aritmetico-geometrice','Subșiruri și diferențe de PG','Sume de numere cu cifră repetată','Identități și inegalități între termenii PG'],
 ['Condiția de PA pentru trei expresii','Condiția de PA cu module','Condiția de PA pentru fracții','Numărul termenilor din date mixte','Ecuații cu sumă în PA','Patru termeni succesivi în PA','PA cu părți întregi','Apartenență simultană la o PA','Unghiuri sau laturi în progresie','Modele practice aritmetice','Progresii și mediane','Transformări care păstrează PA','Pătrat perfect din patru termeni în PA','Sume de produse ale termenilor PA','Sume de inverse în PA','Condiția de PG pentru expresii','Inserarea mediilor geometrice','Excluderea apartenenței la PG','PG finite din sume de grupe','PA și PG simultane sau după translații','Numere cu cifre repetate și pătrate perfecte','Ecuații în numărul de termeni ai PG','Caracterizări algebrice ale PG','Infinit de mulți pătrați într-o PA'],
]


def build():
    banks = [GridBank(f'A2.2.{i+1}', names) for i,names in enumerate(NAMES)]
    for j in range(1,6):
        a=j+2; r=j; n=j+4; q=j+1
        pa=lambda k: a+(k-1)*r
        sp=lambda k: F(k*(2*a+(k-1)*r),2)
        sg=lambda k: a*(q**k-1)//(q-1)
        b=banks[0]
        def num(t,text,v,why): b.numeric(t,text,v,why)
        def choice(t,text,v,wrong,why): b.add(t,text,v,wrong,why)
        num(1,f'Într-o PA, a₁={a}, r={r}. Calculați a_{n}.',pa(n),f'aₙ=a₁+(n−1)r; aici {a}+{n-1}·{r}={pa(n)}.')
        num(2,f'Într-o PA, a_{n}={pa(n)} și r={r}. Aflați a₁.',a,f'a₁=aₙ−(n−1)r={pa(n)}−{n-1}·{r}={a}.')
        num(3,f'O PA are a₂={pa(2)} și a₇={pa(7)}. Aflați rația.',r,f'a₇−a₂=5r, deci r=({pa(7)}−{pa(2)})/5={r}.')
        num(4,f'În PA cu a₁={a}, r={r}, ce rang are termenul {pa(n)}?',n,f'Rezolvăm {a}+(k−1)·{r}={pa(n)}: k={n}, număr natural pozitiv.')
        num(5,f'Într-o PA, a₂+a₈={2*pa(5)}. Calculați suma primilor 9 termeni.',9*pa(5),f'a₂+a₈=2a₅, iar S₉=9a₅. Rezultă 9·{pa(5)}={9*pa(5)}.')
        num(6,f'Într-o PA, a₁={a}, a₅={pa(5)}. Completați termenul a₃.',pa(3),f'Între rangurile 1 și 5 sunt patru pași: r=({pa(5)}−{a})/4={r}, deci a₃={pa(3)}.')
        num(7,f'Calculați S_{n} pentru PA cu a₁={a} și r={r}.',sp(n),f'Sₙ=n(2a₁+(n−1)r)/2={n}·({2*a}+{(n-1)*r})/2={sp(n)}.')
        choice(8,f'O PA satisface a₁+a₃={a+pa(3)} și a₂+a₅={pa(2)+pa(5)}. Aflați (a₁; r).',f'({a}; {r})',[f'({a+1}; {r})',f'({a}; {r+1})',f'({a-1}; {r+2})'],f'Ecuațiile sunt 2a₁+2r={a+pa(3)} și 2a₁+5r={pa(2)+pa(5)}. Scăderea dă 3r={3*r}, apoi a₁={a}.')
        num(9,f'O PA strict crescătoare are a₁+a₃={2*a} și a₁a₃={a*a-r*r}. Aflați r.',r,f'a₁={a}−r, a₃={a}+r. Produsul dă {a*a}−r²={a*a-r*r}; r²={r*r}. Creșterea impune r>0, deci r={r}.')
        num(10,f'Suma unei PA este Sₙ={j}n²+{a}n, n≥1. Aflați rația.',2*j,f'aₙ=Sₙ−Sₙ₋₁={2*j}n+{a-j}, inclusiv la n=1. Diferența aₙ₊₁−aₙ={2*j}.')
        num(11,f'Trei numere strict crescătoare în PA au suma {3*a} și produsul {a*(a*a-r*r)}. Aflați primul număr.',a-r,f'Scriem {a}−d,{a},{a}+d. Produsul este {a}({a*a}−d²), deci d²={r*r}. Din d>0 rezultă d={r}; primul număr este {a-r}.')
        choice(12,f'Care șir este PA cu rația {r}, pentru n≥1?',f'aₙ={r}n+{a}',[f'aₙ={r}n²+{a}',f'aₙ={r}n³+{a}',f'aₙ={r}/n+{a}'],f'Pentru formula liniară, aₙ₊₁−aₙ={r}. Celelalte diferențe depind de n.')
        num(13,f'Pentru n≥1, Sₙ={j}n²+{a}n+c. Pentru ce c termenii recuperați formează o PA de la primul termen?',0,f'La n≥2, aₙ={2*j}n+{a-j}, deci r={2*j}. Primul termen trebuie să fie {a+j}; S₁={a+j}+c, ceea ce impune c=0.')
        num(14,f'O PA pozitivă are a₁={a}, r={r} și Sₙ={sp(n)}. Aflați n.',n,f'Sₙ=n(2·{a}+(n−1)·{r})/2. Valoarea n={n} verifică ecuația. Cum toți termenii sunt pozitivi, Sₙ crește strict și rangul este unic.')
        limit=(j+2)*10; d=j+2; total=sum(k for k in range(1,limit+1) if k%d)
        num(15,f'Calculați suma numerelor de la 1 la {limit}, inclusiv, care nu sunt divizibile cu {d}.',total,f'Din suma {limit}·{limit+1}/2 scădem suma multiplilor {d},2·{d},…,10·{d}, egală cu {d}·10·11/2. Rezultatul este {total}.')
        num(16,f'Într-o PA cu r={r}, S_{n}={sp(n)}. Calculați S_{2*n}.',sp(2*n),f'S₂ₙ=2Sₙ+n²r, prin formula sumei. Aici 2·{sp(n)}+{n*n}·{r}={sp(2*n)}.')
        num(17,f'Într-o PA cu r={r}, definim bₙ=a₂ₙ₋₁+a₂ₙ. Aflați rația lui bₙ.',4*r,f'bₙ₊₁−bₙ=(a₂ₙ₊₁−a₂ₙ₋₁)+(a₂ₙ₊₂−a₂ₙ)=2r+2r=4r={4*r}.')
        num(18,f'Într-o PA cu r={r}, bₙ=a_{{{j}+{q}(n−1)}}, n≥1. Aflați rația lui bₙ.',q*r,f'Rangurile consecutive diferă cu {q}; diferența termenilor este {q}r={q*r}.')
        b=banks[1]
        num(1,f'O PG are b₁={a}, q={q}. Calculați b_{n}.',a*q**(n-1),f'bₙ=b₁qⁿ⁻¹={a}·{q}^{n-1}={a*q**(n-1)}.')
        num(2,f'O PG cu rație pozitivă are b₂={a*q}, b₄={a*q**3}. Aflați q.',q,f'b₄/b₂=q²={q*q}. Condiția q>0 selectează q={q}.')
        num(3,f'Fie bₙ=({q}/{q+1})ⁿ, n≥1. Aflați rația PG.',F(q,q+1),f'Termenii sunt nenuli și raportul bₙ₊₁/bₙ={q}/{q+1} este constant.')
        num(4,f'Suma primilor n termeni este Sₙ={a}({q}ⁿ−1), n≥1. Aflați rația șirului termenilor.',q,f'b₁={a*(q-1)}; pentru n≥2, bₙ=Sₙ−Sₙ₋₁={a*(q-1)}·{q}ⁿ⁻¹. Formula include și primul termen, deci q={q}.')
        num(5,f'O PG nenulă are rația {q}. Care este rația șirului cₙ=bₙbₙ₊₁?',q*q,f'cₙ₊₁/cₙ=bₙ₊₂/bₙ=q²={q*q}.')
        num(6,f'Fie b₁={a}, b₂={a*q}, bₙ₊₂={q}bₙ₊₁, n≥1. Aflați rația PG.',q,f'Primul raport este b₂/b₁={q}, iar recurența impune același raport la toate rangurile următoare.')
        num(7,f'În PG b₁={a}, q=−{q}, ce rang are termenul {a*(-q)**(n-1)}?',n,f'Ecuația (−{q})ᵏ⁻¹=(−{q})^{n-1} impune k={n}: modulele fixează exponentul, iar semnul este compatibil.')
        qq=1 if j==1 else q; val=sum(a*qq**k for k in range(n))
        num(8,f'Calculați suma primilor {n} termeni ai PG b₁={a}, q={qq}.',val,f'Pentru q=1 suma este nb₁; pentru q≠1 este b₁(qⁿ−1)/(q−1). În cazul dat rezultatul este {val}.')
        num(9,f'Trei termeni pozitivi crescători în PG au termenul median {a*q} și suma extremelor {a+a*q*q}. Aflați primul termen.',a,f'Produsul extremelor este pătratul medianului, {(a*q)**2}. Ele sunt rădăcinile lui t²−{a+a*q*q}t+{(a*q)**2}=0: {a}, {a*q*q}. Creșterea selectează primul termen {a}.')
        num(10,f'Termenii {a}, {a}x, {a}x² formează o PG cu x>1. Scăzând {a*(q-1)**2} din ultimul termen, obținem PA. Aflați x.',q,f'Condiția PA este 2·{a}x={a}+{a}x²−{a*(q-1)**2}. Deci (x−1)²={ (q-1)**2}; din x>1 obținem x={q}.')
        num(11,f'O PA și o PG au primul termen comun {a} și al doilea termen comun {a*q}. Aflați diferența dintre al treilea termen al PG și al treilea termen al PA.',a*(q-1)**2,f'Rația PA este {a*(q-1)}, rația PG este {q}. Termenii de rang 3 sunt {a*q*q} și {a*(2*q-1)}; diferența este {a*(q-1)**2}.')
        num(12,f'Fie aₙ₊₁={q}aₙ+{q-1}. Pentru ce c șirul bₙ=aₙ+c satisface bₙ₊₁={q}bₙ pentru orice aₙ?',1,f'Comparăm termenii constanți: {q-1}+c={q}c, deci c=1.')
        num(13,f'Fie a₁={a}, aₙ₊₁={q}aₙ/(1+{q-1}aₙ). Pentru bₙ=(aₙ−1)/aₙ, aflați rația PG bₙ.',F(1,q),f'Din a₁>1 și q>1 rezultă prin inducție aₙ>1: numitorii sunt pozitivi. Avem 1−1/aₙ₊₁=(1−1/aₙ)/{q}, deci bₙ₊₁=bₙ/{q}.')
        num(14,f'Fie a₁={a}, aₙ₊₁−aₙ={q}ⁿ⁻¹, n≥1. Calculați a_{n}.',a+(q**(n-1)-1)//(q-1),f'Însumăm diferențele: aₙ=a₁+1+q+⋯+qⁿ⁻². Aici {a}+({q}^{n-1}−1)/({q}−1)={a+(q**(n-1)-1)//(q-1)}.')
        num(15,f'Fie u₁={a}, uₙ₊₁=2uₙ+n−{j}. Pentru vₙ=uₙ+n+{1-j}, aflați v_{n}.',(a+2-j)*2**(n-1),f'vₙ₊₁=2uₙ+n−{j}+n+1+{1-j}=2(uₙ+n+{1-j})=2vₙ. v₁={a+2-j}; deci v_{n}={a+2-j}·2^{n-1}.')
        num(16,rf'Calculați \(\sum_{{k=1}}^{{{n}}}(2^k+3^k)^2\).',sum((2**k+3**k)**2 for k in range(1,n+1)),f'Dezvoltăm (2ᵏ+3ᵏ)²=4ᵏ+2·6ᵏ+9ᵏ. Aplicăm formula sumei PG fiecăreia: 4(4ⁿ−1)/3+12(6ⁿ−1)/5+9(9ⁿ−1)/8, cu n={n}.')
        num(17,rf'Calculați \(\sum_{{k=1}}^{{{n}}}k\,2^{{k-1}}\).',sum(k*2**(k-1) for k in range(1,n+1)),f'Notăm suma cu T. Scăderea 2T−T dă n2ⁿ−(1+2+⋯+2ⁿ⁻¹)=(n−1)2ⁿ+1. Pentru n={n}: {(n-1)*2**n+1}.')
        num(18,f'O PG nenulă are q={q}. Definim cₙ=b₂ₙ₋₁−b₂ₙ. Aflați rația lui cₙ.',q*q,f'cₙ=b₁q²ⁿ⁻²(1−q). Cum q≠1 și b₁≠0, termenii sunt nenuli și raportul este q²={q*q}.')
        num(19,f'Calculați suma numerelor cu 1, 2, …, {j+2} cifre, toate cifrele egale cu {j}.',sum(j*(10**k-1)//9 for k in range(1,j+3)),f'Numărul cu k cifre este {j}(10ᵏ−1)/9. Însumarea pentru k=1,…,{j+2} dă ({j}/9)[10(10^{j+2}−1)/9−{j+2}].')
        num(20,f'O PG pozitivă are b₁={a*a}, q=4. Calculați suma rădăcinilor pătrate ale primilor {n} termeni.',a*(2**n-1),f'√bₖ={a}·2ᵏ⁻¹; rădăcinile formează PG cu rația 2. Suma este {a}(2^{n}−1)={a*(2**n-1)}.')
        b=banks[2]
        num(1,f'Pentru ce x numerele x−{j}, x+{j}, 2x+{j} sunt, în această ordine, în PA?',2*j,f'2(x+{j})=(x−{j})+(2x+{j}) dă x={2*j}.')
        num(2,f'Pentru x≥{j}, numerele |x−{j}|, x+{j}, 2x sunt în PA. Aflați x.',3*j,f'Din domeniu, |x−{j}|=x−{j}. Condiția 2(x+{j})=x−{j}+2x dă x={3*j}, care respectă domeniul.')
        num(3,f'Pentru x>0, numerele 1/x, {j+2}/x, {2*j+4}/(x+1) sunt în PA. Aflați x.',2*j+3,f'Condiția este (2·{j+2}−1)/x={2*j+4}/(x+1). Înmulțim cu x(x+1)>0: {2*j+3}(x+1)={2*j+4}x. Rezultă x={2*j+3}.')
        num(4,f'O PA are a₁={a}, a₂+a₃={pa(2)+pa(3)} și Sₙ={sp(n)}. Aflați numărul n de termeni.',n,f'a₂+a₃=2a₁+3r dă r={r}. Formula Sₙ=n(2a₁+(n−1)r)/2 dă n={n}. Toți termenii sunt pozitivi, deci suma este strict crescătoare.')
        num(5,f'În suma {a}+{pa(2)}+{pa(3)}+⋯+x={sp(n)}, termenii cresc cu {r}. Aflați ultimul termen x.',pa(n),f'Suma primilor m termeni este m(2·{a}+(m−1)·{r})/2. Ea este strict crescătoare; m={n} este soluția, deci x={pa(n)}.')
        choice(6,f'Numerele {a}, x, y, {pa(4)} sunt termeni consecutivi ai unei PA. Aflați (x; y).',f'({pa(2)}; {pa(3)})',[f'({pa(2)+1}; {pa(3)})',f'({pa(2)}; {pa(3)+1})',f'({a}; {pa(4)})'],f'Cele trei diferențe sunt egale: r=({pa(4)}−{a})/3={r}. Rezultă x={pa(2)}, y={pa(3)}.')
        num(7,f'Fie ⌊x⌋ cel mai mare întreg ≤x. Pentru x∈[{j},{j+1}), numerele ⌊x⌋, x+1/2, ⌊x⌋+2 sunt în PA. Aflați x.',F(2*j+1,2),f'În intervalul dat, ⌊x⌋={j}. Condiția PA este 2x+1=2·{j}+2; x={F(2*j+1,2)} aparține intervalului.')
        choice(8,f'Pot numerele {j}, {j+1}, {j}+√2 să aparțină aceleiași PA reale cu rație nenulă?', 'Nu, raportul diferențelor ar trebui să fie rațional', ['Da, cu rația 1','Da, cu rația √2','Da, cu rația 1/2'], 'Dacă rangurile sunt p,q,s, raportul diferențelor (aₛ−aₚ)/(a_q−aₚ)=(s−p)/(q−p) este rațional. Aici raportul este √2, irațional: contradicție.')
        num(9,f'Cele trei unghiuri ale unui triunghi sunt în PA, cu rația {j*5}°. Aflați unghiul cel mai mic, în grade.',60-j*5,f'Scriem unghiurile u−{j*5},u,u+{j*5}. Suma este 3u=180°, deci u=60° și minimul este {60-j*5}°.')
        num(10,f'O sală are {n} rânduri. Primul are {a+10} locuri și fiecare rând următor are cu {r} locuri mai mult. Câte locuri sunt în total?',sp(n)+10*n,f'Locurile formează PA: totalul este {n}(2·{a+10}+{n-1}·{r})/2={sp(n)+10*n}.')
        aa=9+j;bb=aa+4;cc=aa+8
        num(11,f'Un triunghi are pătratele laturilor a²={aa}, b²={bb}, c²={cc}. Calculați m_a²+m_c²−2m_b², unde m_a,m_b,m_c sunt medianele corespunzătoare.',0,'Teorema medianei dă m_a²=(2b²+2c²−a²)/4 și formulele ciclice. Prin combinare, m_a²+m_c²−2m_b²=3(2b²−a²−c²)/4=0, deoarece pătratele laturilor sunt în PA.')
        num(12,f'O PA (aₙ) are rația {r}. Pentru cₙ={j+2}aₙ−{j}, aflați rația lui (cₙ).',(j+2)*r,f'cₙ₊₁−cₙ={j+2}(aₙ₊₁−aₙ)={j+2}·{r}={(j+2)*r}.')
        x=j+1; d=j; product=x*(x+d)*(x+2*d)*(x+3*d); root=x*x+3*x*d+d*d
        assert root*root==product+d**4
        num(13,f'Fie a={x}, b={x+d}, c={x+2*d}, d={x+3*d}, patru întregi consecutivi în PA. Calculați √((a−b)⁴+abcd).',root,f'Pentru termenii t,t+r,t+2r,t+3r avem r⁴+t(t+r)(t+2r)(t+3r)=(t²+3tr+r²)². Aici t={x}, r={d}; expresia din paranteză este pozitivă și rădăcina este {root}.')
        num(14,rf'Fie aₖ=k+{j}. Calculați \(\sum_{{k=1}}^{{{n}}}a_ka_{{k+1}}\).',sum((k+j)*(k+j+1) for k in range(1,n+1)),f'aₖaₖ₊₁=k²+{2*j+1}k+{j*(j+1)}. Aplicăm Σk=n(n+1)/2 și Σk²=n(n+1)(2n+1)/6 pentru n={n}.')
        num(15,rf'Calculați \(\sum_{{k=1}}^{{{n}}}\frac1{{(k+{j})(k+{j+1})}}\).',F(1,j+1)-F(1,n+j+1),f'Fiecare fracție este 1/(k+{j})−1/(k+{j+1}). Suma telescopică este 1/{j+1}−1/{n+j+1}={F(1,j+1)-F(1,n+j+1)}; toți numitorii sunt pozitivi.')
        num(16,f'Pentru x>0, numerele {a}, x, {a*q*q} sunt în PG. Aflați x.',a*q,f'Condiția este x²={a}·{a*q*q}={a*a*q*q}. Din x>0 obținem x={a*q}. Toți termenii sunt nenuli, deci condiția este suficientă.')
        choice(17,f'Inserați două numere pozitive între {a} și {a*q**3} astfel încât cele patru numere să fie în PG.',f'({a*q}; {a*q*q})',[f'({a*q+1}; {a*q*q})',f'({a*q}; {a*q*q+1})',f'({a}; {a*q**3})'],f'Rația pozitivă satisface q³={q**3}, deci q={q}. Termenii intermediari sunt {a*q} și {a*q*q}.')
        choice(18,f'Pot {j}, {2*j}, {3*j} să aparțină aceleiași PG reale cu termeni nenuli?', 'Nu, ar rezulta o egalitate imposibilă între puteri ale lui 2 și 3', ['Da, cu rația 2','Da, cu rația 3','Da, cu rația 3/2'], 'Dacă rangurile distincte sunt p,s,t, raporturile față de primul dau qˢ⁻ᵖ=2 și qᵗ⁻ᵖ=3. Eliminând q rezultă 2ᵗ⁻ᵖ=3ˢ⁻ᵖ, imposibil pentru exponenți întregi nenuli prin unicitatea descompunerii în factori primi.')
        num(19,f'Patru numere pozitive consecutive în PG au suma termenilor de rang impar {a*(1+q*q)} și suma termenilor de rang par {a*q*(1+q*q)}. Aflați rația.',q,f'Sumele sunt b₁(1+q²) și b₁q(1+q²). Raportul lor este q={q}.')
        num(20,f'Trei numere în PA sunt {a}, x, 2x−{a}. Dacă mărim ultimul cu {a*(q-1)**2}, obținem o PG pozitivă cu x>{a}. Aflați x.',a*q,f'Condiția PG este x²={a}(2x−{a}+{a*(q-1)**2}), deci (x−{a})²={a*a*(q-1)**2}. Din x>{a}, rezultă x={a*q}.')
        nn=j+2; z=10**nn-1
        num(21,f'Fie R numărul cu exact {nn} cifre, toate egale cu 9. Calculați √(R²+2R+1).',10**nn,f'R=10^{nn}−1. Avem R²+2R+1=(R+1)²; R+1>0, deci rădăcina este R+1=10^{nn}={10**nn}.')
        num(22,f'Determinați n≥1 dacă 1+2+2²+⋯+2ⁿ⁻¹={2**n-1}.',n,f'Suma este 2ⁿ−1. Rezultă 2ⁿ={2**n}, deci n={n}.')
        choice(23,f'Pentru a,b,c>0 cu a+c={j+4}, care egalitate este echivalentă cu faptul că a,b,c sunt în PG?',f'b²=ac',['2b=a+c','a²=bc','c²=ab'],'Pentru termeni pozitivi, rapoartele b/a și c/b sunt definite și egale exact când b²=ac. Celelalte relații nu caracterizează PG în această ordine.')
        num(24,f'O PA infinită cu rația {r} are aₚ={a*a} pentru un rang p. Care este cel mai mic întreg pozitiv h pentru care aₚ₊ₕ=({a}+{r})²?',2*a+r,f'aₚ₊ₕ={a*a}+h·{r}. Egalăm cu ({a}+{r})²: h=2·{a}+{r}={2*a+r}. Mai general, h=2·{a}t+{r}t² produce pătratul ({a}+{r}t)² pentru orice t≥1, deci infinit de mulți pătrați.')
    result=[]
    for bank,names in zip(banks,NAMES):
        result.extend(bank.finish(Counter({i:5 for i in range(1,len(names)+1)})))
    assert len({z['text'] for z in result})==310
    return result


if __name__=='__main__':
    root=Path(__file__).resolve().parents[1]/'clasa_9'
    questions=build()
    for i,(suffix,title) in enumerate([
        ('a_progresii_aritmetice','Progresii aritmetice'),
        ('b_progresii_geometrice','Progresii geometrice'),
        ('c_aplicatii_progresii','Aplicații'),
    ],1):
        path=root/f'clasa_9_u02_l02{suffix}.json'
        data={'title':title,'description':'Clasa a 9-a · Funcții',
              'difficulty':'medium', 'questions':[q for q in questions if q['catalog']['section']==f'A2.2.{i}']}
        path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        print(len(data['questions']), 'grile:', path.name)
