"""80 de grile originale pentru A1 §1.5, toate cele 23 de tipuri."""
from fractions import Fraction as F
from math import isqrt, floor, ceil
from catalog_grid_utils import GridBank, number_set


TYPE_NAMES = [
    "Parte întreagă și fracționară numerică", "Părți întregi ale multiplilor", "Radicali vecini de întregi",
    "Sume telescopice și parte fracționară", "Încadrarea radicalilor combinați", "Sume de părți întregi",
    "Părți întregi după simplificare algebrică", "Reconstrucție din parte întreagă și sumă",
    "Partea întreagă a unei sume", "Partea întreagă a produsului", "Sume cu n variabile",
    "Multiplii unui număr real", "Opusul și partea fracționară", "Caracterizări ale integrității",
    "Ecuații elementare cu parte întreagă", "Ecuații cu parte întreagă și termen liber real",
    "Ecuații polinomiale în [x]", "Ecuații mixte polinom–parte întreagă", "Egalitatea părților opuse",
    "Pătrate perfecte din sume cu parte întreagă", "Identități cu divizori fixați",
    "Parametri cu proprietate universală", "Relația lui Hermite",
]


def build_floor_questions():
    bank = GridBank("A1.1.5", TYPE_NAMES, " Notație: [u] este cel mai mare întreg ≤u, iar {u}=u−[u].")
    add, num = bank.add, bank.numeric

    for raw in ["-3.28", "2.75", "-0.04", "5"]:
        x=F(raw);k=floor(x);frac=x-k
        answer=f"({k}; {frac})"
        add(1, f"Pentru x={raw.replace('.',',').replace('-', '−')}, determinați perechea ([x]; {{x}}).", answer,
            [f"({k+1}; {frac})", f"({k}; {frac+1})", f"({k-1}; {frac})"],
            f"Avem {k}≤x<{k+1}, deci [x]={k}. Partea fracționară este x−[x]={frac}, în intervalul [0,1).")

    for k,r,m in [(2,F(3,4),5),(-2,F(1,3),4),(0,F(9,10),3),(3,F(1,5),5)]:
        x=k+r;answer=floor(m*x)
        num(2, f"Dacă [x]={k} și {{x}}={r}, calculați [{m}x].", answer,
            f"x=[x]+{{x}}={x}. Atunci {m}x={m*x} și partea întreagă este {answer}.")

    for n in [1,3,5,10]:
        num(3, f"Pentru n={n}, calculați [√(n²+n)].", n,
            f"n²<n²+n<(n+1)² pentru n>0. Prin urmare n<√(n²+n)<n+1 și partea întreagă este {n}.")

    for n in [2,4,7,9]:
        num(4, f"Fie S=Σ[k=1,…,{n}] 1/[k(k+1)]. Calculați partea fracționară {{S}}; parantezele din numitor grupează factorii.", F(n,n+1),
            f"1/[k(k+1)]=1/k−1/(k+1), deci S=1−1/{n+1}={F(n,n+1)}. Avem 0<S<1, astfel [S]=0 și {{S}}=S.")

    for a,b,m in [(2,3,3),(5,7,4),(8,10,5),(13,17,7)]:
        # Verificări exacte ale comparațiilor după ridicare la pătrat.
        low=m*m-a-b;high=(m+1)**2-a-b
        assert low<0 or low*low<4*a*b
        assert high>0 and 4*a*b<high*high
        num(5,f"Calculați [√{a}+√{b}] fără aproximări zecimale.",m,
            f"Pătratul sumei este {a+b}+2√{a*b}. Comparând termenul cu radical prin pătrare, obținem {m*m}<(√{a}+√{b})²<{(m+1)**2}. Suma este pozitivă, deci {m}<√{a}+√{b}<{m+1}; partea întreagă este {m}.")

    for n in [8,15,24,35]:
        answer=sum(isqrt(k) for k in range(1,n+1))
        blocks=[f"{j}·{min(n,(j+1)**2-1)-j*j+1}" for j in range(1,isqrt(n)+1)]
        num(6,f"Calculați Σ[k=1,…,{n}] [√k].",answer,
            "Pentru j²≤k<(j+1)², [√k]=j. Gruparea în blocuri dă "+"+".join(blocks)+f"={answer}.")

    for n,k in [(2,2),(5,3),(6,2),(10,3)]:
        answer=isqrt(k*k*(n+1))
        num(7,f"Fie A=1/(√{n+1}−√{n})−√{n}. Calculați [{k}A].",answer,
            f"Raționalizarea dă 1/(√{n+1}−√{n})=√{n+1}+√{n}, deci A=√{n+1}. Cum {answer}²≤{k*k*(n+1)}<{answer+1}², rezultă [{k}A]={answer}.")

    for total,k,r in [(5,2,F(1,4)),(3,-1,F(1,3)),(0,-2,F(2,5)),(8,3,F(3,4))]:
        x=F(k+1)-r;y=total-x
        num(8,f"x,y sunt reale, x+y={total}, [x]={k} și {{y}}={r}. Determinați xy.",x*y,
            f"Suma este întreagă și 0<{{y}}<1, deci {{x}}=1−{{y}}={1-r}. Astfel x={x}, y={y}, iar xy={x*y}.")

    for r,s in [(F(1,5),F(3,10)),(F(7,10),F(3,5)),(F(2,5),F(3,5)),(F(0),F(9,10))]:
        answer=floor(r+s)
        num(9,f"Dacă {{x}}={r} și {{y}}={s}, calculați [x+y]−[x]−[y].",answer,
            f"Diferența este [{{x}}+{{y}}]=[{r+s}]={answer}. Ea este 0 sau 1, în funcție de depășirea pragului 1.")

    add(10,"Care comparație este valabilă pentru toate x,y≥0?","[xy]≥[x][y]",
        ["[xy]<[x][y]","[xy]>[x][y]","[xy]=[x][y]"],
        "x≥[x]≥0 și y≥[y]≥0, deci xy≥[x][y]. Ultimul produs este întreg, astfel [xy]≥[x][y]. Egalitatea și inegalitatea strictă pot apărea în exemple diferite.")
    num(10,"Pentru x=1,8 și y=2,4, calculați [xy]−[x][y].",2,
        "xy=4,32, deci [xy]=4. Avem [x]=1 și [y]=2, astfel diferența este 4−2=2.")
    add(10,"Pentru x=y=−1/2, care este comparația dintre [xy] și [x][y]?","[xy]<[x][y]",
        ["[xy]=[x][y]","[xy]>[x][y]","[xy] și [x][y] nu sunt definite."],
        "xy=1/4 și [xy]=0, dar [x]=[y]=−1, deci [x][y]=1. Ipotezele de semn contează în inegalitatea pentru produs.")
    num(10,"Dacă x∈[2;3) și y∈[3;4), care este valoarea maximă a lui [xy]?",11,
        "6≤xy<12, deci [xy]≤11. Valoarea 11 se atinge, de exemplu, la x=2,9 și y=3,9, când xy=11,31.")

    for n in [2,3,4,5]:
        num(11,f"Pentru {n} numere reale x₁,…,x{n}, care este maximul lui [x₁+…+x{n}]−([x₁]+…+[x{n}])?",n-1,
            f"Diferența este partea întreagă a sumei celor {n} părți fracționare, fiecare în [0,1). Suma este sub {n}, deci maximul este {n-1}; alegând fiecare parte fracționară 1−1/{2*n}, maximul se atinge.")

    for n in [3,5,8]:
        num(12,f"Pentru x real, care este valoarea maximă a lui [{n}x]−{n}[x]?",n-1,
            f"Diferența este [{n}{{x}}]. Din 0≤{{x}}<1 rezultă valori între 0 și {n-1}; ultima se atinge pentru {{x}}=1−1/{2*n}.")

    add(13,"Pentru x neîntreg, care formulă este corectă?","[−x]=−[x]−1",
        ["[−x]=−[x]","[−x]=[x]−1","[−x]=1−[x]"],"Scriem x=k+r cu k întreg și 0<r<1. Atunci −x=−k−r∈(−k−1,−k), deci [−x]=−k−1.")
    num(13,"Dacă {x}=2/7, calculați {−x}.",F(5,7),"x nu este întreg. Formula {−x}=1−{x} dă 1−2/7=5/7.")
    num(13,"Dacă x este întreg, calculați [x]+[−x].",0,"Pentru x întreg, ambele părți întregi sunt numerele însele: x+(−x)=0.")

    add(14,"Ce condiție este echivalentă cu {x}=0?","x∈Z",["x∈R∖Z","x>0","x≥0"],"{x}=0 înseamnă x=[x], deci x este întreg; orice întreg are partea fracționară zero.")
    add(14,"Ce condiție este echivalentă cu [x]+[−x]=−1?","x∈R∖Z",["x∈Z","x>0","x<0"],"Pentru x întreg suma este 0; pentru x neîntreg avem [−x]=−[x]−1, deci suma este −1.")
    add(14,"Ce condiție este echivalentă cu {x}+{−x}=0?","x∈Z",["x∈R∖Z","x=1/2","x≤0"],"Părțile fracționare sunt nenegative; suma lor este zero doar când ambele sunt zero. Pentru x neîntreg, suma este 1.")

    for expr,correct,wrong,proof in [
        ("[3x−6]=7","[13/3; 14/3)",["(13/3; 14/3]","[7/3; 8/3)","{13/3}"],"7≤3x−6<8, deci 13≤3x<14 și 13/3≤x<14/3."),
        ("[2x+1]=−2","[−3/2; −1)",["(−3/2; −1]","[−1; −1/2)","{−1}"],"−2≤2x+1<−1, deci −3≤2x<−2 și −3/2≤x<−1."),
        ("[−2x+3]=1","(1/2; 1]",["[1/2; 1)","[1; 2)","{1}"],"1≤−2x+3<2. Împărțirea la −2 inversează sensurile: 1/2<x≤1."),
    ]:
        add(15,f"Rezolvați în R ecuația {expr}.",correct,wrong,proof)

    for c in [F(1),F(1,2),F(-1,3)]:
        k=ceil(2*c);x=k-c
        add(16,f"Rezolvați în R ecuația [2x]=x+({c}).",number_set([x]),
            [number_set([x+1]),number_set([x-1]),"∅"],
            f"Notăm k=x+({c})=[2x]∈Z, deci x=k−({c}). Ecuația dă k=2k+[−2·({c})], astfel k=⌈2·({c})⌉={k}. Rezultă x={x}, care verifică ecuația.")

    for expr,correct,wrong,proof in [
        ("7[x]²−8[x]+1=0","[1; 2)",["[1/7; 8/7)","[1/7; 8/7) ∪ [1; 2)","{1}"],"Cu k=[x]∈Z, (7k−1)(k−1)=0. Respingem k=1/7, păstrăm k=1, deci x∈[1,2)."),
        ("[x]²−[x]−2=0","[−1; 0) ∪ [2; 3)",["{−1; 2}","[−1; 3)","(−1; 0] ∪ (2; 3]"],"Cu k=[x], (k−2)(k+1)=0. Pentru k=−1 avem [−1,0), iar pentru k=2 avem [2,3)."),
        ("([x]−3)²=0","[3; 4)",["{3}","(3; 4]","[−3; −2)"],"[x]=3 este echivalent cu 3≤x<4."),
    ]:
        add(17,f"Determinați soluțiile reale ale ecuației {expr}.",correct,wrong,proof)

    add(18,"Rezolvați în R ecuația x²=[x].","{0; 1}",["{−1; 0; 1}","[0; 1]","{1}"],"Punem k=[x]=x²≥0, deci x≥0 și x=√k. Condiția k≤√k<k+1 admite k=0 sau k=1; pentru k≥2, √k<k. Rezultă x=0 sau 1.")
    add(18,"Rezolvați în R ecuația 4x⁴−4[x²]+1=0.","∅",["{−1/2; 1/2}","{0}","{−1; 1}"],"Cu t=x² și k=[t]≤t, membrul stâng este ≥4t²−4t+1=(2t−1)². Ca să fie zero trebuie simultan t=1/2 și k=t, imposibil deoarece k este întreg.")
    add(18,"Rezolvați în R ecuația x²+[x²]=2.","{−1; 1}",["{0; 1}","{−2; 2}","∅"],"Cu t=x² și k=[t], t=2−k. Din k≤2−k<k+1 rezultă 2k≤2<2k+1, deci k=1 și t=1. Soluțiile sunt x=±1.")

    for expr,correct,wrong,proof in [
        ("[x−5]=[−x−1]","{2}",["[1; 3)","{−2}","∅"],"Scriem u=x−2: ecuația devine [u−3]=[−u−3], deci [u]=[−u]. Aceasta impune u=0, deci x=2."),
        ("[x²−x−6]=[−x²+x−2]","{−1; 2}",["{−2; 1}","[−1; 2]","∅"],"Cu u=x²−x−2, avem [u−4]=[−u−4]. Egalitatea [u]=[−u] impune u=0, deci (x−2)(x+1)=0."),
        ("[(x−1)²−2]=[−(x−1)²−4]","∅",["{1}","{0; 2}","R"],"Cu u=(x−1)²+1, ecuația este [u−3]=[−u−3], deci ar cere u=0. Dar u≥1. În general [u]=[−u] este posibil doar pentru u=0."),
    ]:
        add(19,f"Rezolvați în R ecuația {expr}.",correct,wrong,proof)

    for m in [4,6,10]:
        n=2*m-1
        num(20,f"Calculați S=Σ[k=1,…,{n}] [(k+1)/2] și identificați pătratul perfect obținut.",m*m,
            f"Valorile 1,…,{m-1} apar de două ori, iar {m} apare o dată. S=2(1+…+{m-1})+{m}={m}²={m*m}.")

    for p,n in [(3,8),(4,-3),(5,12)]:
        num(21,f"Pentru n={n}, calculați Σ[j=0,…,{p-1}] [(n+j)/{p}].",n,
            f"Scriem n={p}q+r, cu 0≤r<{p}. Dintre cei {p} termeni, r sunt q+1 și ceilalți q. Suma este {p}q+r=n={n}, inclusiv când n este negativ.")

    add(22,"Determinați toate valorile reale p pentru care [x+p]=[x]+p pentru orice x real.","p∈Z",["p≥0","0≤p<1","p∈R"],"La x=0 obținem [p]=p, deci p este întreg. Reciproc, adăugarea unui întreg deplasează partea întreagă cu acel întreg.")
    add(22,"Determinați x real astfel încât [nx]=n pentru orice n∈N*.","x=1",["1≤x<2","x=0","x=2"],"Condiția echivalează cu 1≤x<1+1/n pentru orice n pozitiv. Intersecția acestor intervale este {1}; această valoare verifică toate egalitățile.")
    add(22,"Determinați p>0 astfel încât [n/p]=n pentru orice n∈N*.","p=1",["0<p≤1","p=2","p≥1"],"Punând x=1/p, condiția devine [nx]=n pentru orice n pozitiv, ceea ce impune x=1. Rezultă p=1, valoare suficientă.")

    for n,x in [(3,F(7,10)),(4,F(-1,5))]:
        answer=floor(n*x)
        num(23,f"Pentru x={x}, calculați Σ[k=0,…,{n-1}] [x+k/{n}].",answer,
            f"Relația lui Hermite dă suma egală cu [{n}x]=[{n*x}]={answer}. Identitatea rezultă prin împărțirea lui {{x}} în cele {n} intervale de lungime 1/{n}.")
    add(23,"Care este forma corectă a relației lui Hermite pentru x real și n∈N*?","Σ[k=0,…,n−1] [x+k/n]=[nx]",
        ["Σ[k=0,…,n−1] [x+k/n]=n[x]","Σ[k=0,…,n−1] [x+k/n]=[nx]+1","Σ[k=0,…,n−1] [x+k/n]=[x/n]"],
        "Scriem x=m+r, 0≤r<1, și j=[nr]. Dintre cei n termeni [r+k/n], exact j sunt 1, restul 0. Suma este nm+j=[nx].")

    return bank.finish({i:4 if i<=11 else 3 for i in range(1,24)})
