"""315 grile originale după tipologiile A1.4.1 și A1.4.2, catalog Burtea IX.

Generator independent pentru lecția de raționamente logice. Enunțurile sunt
reformulări didactice ale metodelor, nu transcrieri ale exercițiilor scanate.
"""
import json
import re
from collections import Counter
from fractions import Fraction as F
from itertools import combinations, permutations, product
from math import comb, factorial, gcd, isqrt, lcm, prod
from pathlib import Path


NAMES = {
    "4.1": ["Pătrat perfect din condiție universală cu parte întreagă", "Inducție pentru sume de puteri",
            "Sume alternante", "Sume de sume", "Sume ponderate de polinoame", "Sume de fracții telescopice",
            "Sume cu mai mulți factori consecutivi", "Produse telescopice", "Produse exponențiale",
            "Dominarea puterilor de către exponențiale", "Estimarea sumelor prin inducție", "Inegalități cu radicali",
            "Inegalități cu variabile ordonate", "Inegalitatea lui Bernoulli", "Divizibilitate polinomială",
            "Divizibilitate exponențială", "Divizibilitate și coprimalitate a produselor", "Radicali imbricați finiți",
            "Integritatea puterilor simetrice", "Verificarea formulei unui șir recurent", "Mărginirea unui șir recurent",
            "Exponentul unui factor prim", "Produs de sume de două pătrate", "Reprezentări cu semne ale întregilor",
            "Partiționarea pătratului în pătrate", "Partiții în poligoane congruente", "Reconstrucție din sume parțiale",
            "Reprezentarea sumelor de bani", "Partiționarea triunghiului echilateral", "Partiții în trei poligoane congruente"],
    "4.2": ["Cardinalul reuniunii a două mulțimi", "Numărul submulțimilor", "Probleme cu două activități",
            "Probleme cu trei activități sau culori", "Multipli într-un interval", "Divizibilitate simultană",
            "Divizibilitate alternativă", "Numere prime cu un întreg dat", "Perechi neordonate și perechi ordonate",
            "Numărarea valorilor unei formule", "Principiul multiplicării pentru cifre", "Numere cu sau fără repetarea cifrelor",
            "Extrageri succesive cu culori impuse", "Triplete fără reintroducere", "Repartizarea obiectelor",
            "Repartizări cu beneficiari nevidați", "Colorări independente", "Poziția unei cifre într-o concatenare",
            "Numărarea cifrelor de paginare", "Exponenți primi în factorial", "Zerouri terminale ale factorialului",
            "Factorizări coprime", "Diagonale ale poligoanelor", "Diagonale ale unei prisme",
            "Regiuni determinate de drepte concurente", "Drepte determinate de puncte fără trei coliniare",
            "Numărare prin subdiviziune repetată", "Numărul radicalilor raționali", "Bijeția prin complementarea submulțimilor",
            "Numărul divizorilor din factorizare", "Numere cu exact patru divizori", "Mulțime necunoscută într-o egalitate de reuniuni",
            "Numărarea soluțiilor unei ecuații diofantice liniare"],
}


def number(value):
    value = F(value)
    return str(value.numerator) if value.denominator == 1 else str(value)


def valuation(n, p):
    count = 0
    while n % p == 0:
        n //= p
        count += 1
    return count


def factorial_valuation(n, p):
    result = 0
    while n:
        n //= p
        result += n
    return result


def induction_explanation(question):
    """Explicații didactice: inducție explicită sau metodă directă, după caz."""
    kind=question["catalog"]["type"]
    text=question["text"]
    answer=next(o["text"] for o in question["options"] if o["is_correct"])
    old=question["explanation"]
    def args(pattern):
        match=re.search(pattern,text)
        assert match,(kind,pattern,text)
        return tuple(map(int,match.groups()))
    def math(tex): return r"\("+tex+r"\)"
    def result(): return "Aplicarea la datele grilei dă răspunsul: "+answer+"."
    def proof(prop,base,hypothesis,step,conclusion,application=None):
        return (
            "Proprietatea urmărită: "+prop+"\n\n"
            "1. Verificarea inițială: "+base+"\n\n"
            "2. Ipoteza de inducție: "+hypothesis+"\n\n"
            "3. Pasul inductiv: "+step+"\n\n"
            "4. Concluzia: "+conclusion+
            ("\n\n"+application if application else "")
        )
    if kind in {1,27} or (kind==24 and "lui k+4" not in text):
        label={1:"Verificare directă și contraexemple",27:"Scăderea a două relații consecutive",24:"Calcul direct al reprezentării"}[kind]
        question["catalog"]["proof_method"]="direct"
        return label+".\n\n"+old
    question["catalog"]["proof_method"]="induction"
    if kind==2:
        p,=args(r"k\^(\d+)")
        f=answer.split("=",1)[1].strip()
        return proof(math(r"P(n): S_n=F(n),\quad S_n=\sum_{k=1}^{n}k^{"+str(p)+"}")+", unde F(n)="+f+".",
            "Pentru n=1, suma are un singur termen, 1, iar F(1)=1. Deci P(1) este adevărată.",
            "Fixăm un n≥1 arbitrar și presupunem că P(n) este adevărată, adică Sₙ=F(n).",
            "Adăugăm termenul următor la suma pentru care folosim ipoteza: "+math(r"S_{n+1}=S_n+(n+1)^{"+str(p)+r"}=F(n)+(n+1)^{"+str(p)+r"}=F(n+1)")+". Ultima egalitate se obține prin dezvoltare și factorizare; exact aici rezultă P(n+1).",
            "Din P(1) și P(n)⇒P(n+1), formula este adevărată pentru orice n≥1.",
            "Formula verificată este F(n)="+f+".")
    if kind==3:
        return proof(math(r"P(n):\ \sum_{k=1}^{n}(-1)^{k+1}k^2=\frac{(-1)^{n+1}n(n+1)}2"),
            "La n=1, ambele membre sunt 1, deci P(1) este adevărată.",
            "Fixăm n≥1 și presupunem că suma primilor n termeni este (−1)^(n+1)n(n+1)/2.",
            math(r"S_{n+1}=\frac{(-1)^{n+1}n(n+1)}2+(-1)^{n+2}(n+1)^2=\frac{(-1)^{n+2}(n+1)(n+2)}2")+". Am folosit ipoteza pentru Sₙ și am scos factorul (−1)^(n+2)(n+1). Obținem P(n+1), cu semnul corect.",
            "P(n) este adevărată pentru orice n≥1.",result())
    if kind==4:
        return proof(math(r"P(n):\ \sum_{k=1}^{n}(1+2+\cdots+k)=\frac{n(n+1)(n+2)}6"),
            "La n=1, suma este 1, iar 1·2·3/6=1.",
            "Pentru un n≥1 arbitrar, presupunem Sₙ=n(n+1)(n+2)/6.",
            "Termenul nou este 1+2+⋯+(n+1)=(n+1)(n+2)/2. Prin ipoteză, "+math(r"S_{n+1}=\frac{n(n+1)(n+2)}6+\frac{(n+1)(n+2)}2=\frac{(n+1)(n+2)(n+3)}6")+", deci P(n+1) este adevărată.",
            "Formula este valabilă pentru orice n≥1.",result())
    if kind==5:
        c,=args(r"k\((\d+)k")
        f=rf"F(n)=\frac{{{c}n(n+1)(2n+1)}}6+\frac{{n(n+1)}}2"
        return proof(math(r"P(n):\ S_n=F(n),\quad S_n=\sum_{k=1}^{n}k("+str(c)+"k+1)")+", unde "+math(f)+".",
            f"La n=1, suma este {c+1}, iar F(1)={c+1}.",
            "Fixăm n≥1 și presupunem Sₙ=F(n), unde "+math(f)+".",
            math(r"S_{n+1}=S_n+(n+1)("+str(c)+r"(n+1)+1)=F(n)+(n+1)("+str(c)+r"(n+1)+1)=F(n+1)")+". Substituția lui Sₙ folosește ipoteza; ultima egalitate rezultă prin factorizare.",
            "Formula este adevărată pentru orice n≥1.",result())
    if kind==6:
        return proof(math(r"P(n):\ S_n=\sum_{k=1}^{n}\frac1{k(k+1)}=\frac n{n+1}"),
            "La n=1, S₁=1/2, egal cu 1/(1+1).",
            "Fixăm n≥1 și presupunem Sₙ=n/(n+1).",
            math(r"S_{n+1}=S_n+\frac1{(n+1)(n+2)}=\frac n{n+1}+\frac1{(n+1)(n+2)}=\frac{n+1}{n+2}")+". Am obținut P(n+1).",
            "Pentru orice n≥1, Sₙ=n/(n+1).",result())
    if kind==7:
        return proof(math(r"P(n):\ S_n=\sum_{k=1}^{n}\frac1{k(k+1)(k+2)}=\frac14-\frac1{2(n+1)(n+2)}"),
            "La n=1, S₁=1/6, iar 1/4−1/12=1/6.",
            "Presupunem formula P(n) pentru un n≥1 arbitrar.",
            math(r"S_{n+1}=\frac14-\frac1{2(n+1)(n+2)}+\frac1{(n+1)(n+2)(n+3)}=\frac14-\frac1{2(n+2)(n+3)}")+". După aducerea la același numitor, acesta este exact P(n+1).",
            "Formula este valabilă pentru orice n≥1.",result())
    if kind==8:
        return proof(math(r"P(n):\ T_n=\prod_{k=2}^{n}\left(1-\frac1{k^2}\right)=\frac{n+1}{2n}"),
            "Produsul începe la 2, deci verificăm P(2): T₂=1−1/4=3/4, exact (2+1)/(2·2).",
            "Fixăm n≥2 și presupunem Tₙ=(n+1)/(2n).",
            math(r"T_{n+1}=T_n\left(1-\frac1{(n+1)^2}\right)=\frac{n+1}{2n}\frac{n(n+2)}{(n+1)^2}=\frac{n+2}{2(n+1)}")+". Folosim ipoteza și obținem P(n+1).",
            "Formula este adevărată pentru orice n≥2; baza corectă este P(2), nu P(1).",result())
    if kind==9:
        a,=args(r"\(1\+(\d+)\^")
        return proof(math(r"P(n):\ T_n=\prod_{k=0}^{n}(1+a^{2^k})=\frac{a^{2^{n+1}}-1}{a-1}")+f", pentru a={a}.",
            "La n=0, T₀=1+a=(a²−1)/(a−1), deci P(0) este adevărată. Aici a>1, astfel că numitorul nu este zero.",
            "Fixăm n≥0 și presupunem formula P(n).",
            math(r"T_{n+1}=T_n(1+a^{2^{n+1}})=\frac{(a^{2^{n+1}}-1)(a^{2^{n+1}}+1)}{a-1}=\frac{a^{2^{n+2}}-1}{a-1}")+". Aplicăm ipoteza și diferența de pătrate; rezultă P(n+1).",
            "Formula este adevărată pentru orice n≥0.",result())
    if kind==10:
        a,p=args(r"(\d+)ⁿ > n\^(\d+)"); start=int(answer)
        return proof(math(rf"P(n):\ {a}^n>n^{{{p}}}"),
            f"Pragul propus este N={start}. Verificăm P({start}): {a}^{start}={a**start}>{start**p}={start}^{p}.",
            f"Fixăm un n≥{start} arbitrar și presupunem P(n), adică {a}ⁿ>n^{p}.",
            math(rf"{a}^{{n+1}}={a}\cdot {a}^n>{a}n^{{{p}}}\ge(n+1)^{{{p}}}")+". Prima inegalitate folosește ipoteza. A doua urmează din "+math(rf"\left(1+\frac1n\right)^{{{p}}}\le\left(1+\frac1{{{start}}}\right)^{{{p}}}\le {a}")+". Deci P(n+1) este adevărată.",
            f"P(n) este adevărată pentru orice n≥{start}.",
            f"Minimalitatea pragului se verifică separat: la n={start-1}, {a}^{start-1}={a**(start-1)}≤{(start-1)**p}. Orice prag mai mic ar include acest eșec.")
    if kind==11:
        c,=args(r"ⁿ (\d+)/k²")
        return proof(math(rf"P(n):\ S_n=\sum_{{k=1}}^n\frac{{{c}}}{{k^2}}\le {c}\left(2-\frac1n\right)"),
            f"La n=1, ambele membre sunt {c}; P(1) este adevărată cu egalitate.",
            "Fixăm n≥1 și presupunem P(n).",
            math(rf"S_{{n+1}}=S_n+\frac{{{c}}}{{(n+1)^2}}\le {c}\left(2-\frac1n\right)+\frac{{{c}}}{{(n+1)^2}}<{c}\left(2-\frac1n\right)+\frac{{{c}}}{{n(n+1)}}={c}\left(2-\frac1{{n+1}}\right)")+". Folosim ipoteza și (n+1)²>n(n+1).",
            "Estimarea este adevărată pentru orice n≥1 și este strictă de la n=2. Majorantul dat în enunț se calculează telescopic.",result())
    if kind==12:
        return proof(math(r"P(n):\ S_n=\sum_{k=1}^{n}\frac1{\sqrt{k}}>2(\sqrt{n+1}-1)"),
            "La n=1, 1>2(√2−1), deoarece √2<3/2; deci P(1) este adevărată.",
            "Fixăm n≥1 și presupunem Sₙ>2(√(n+1)−1).",
            "Raționalizând, "+math(r"\frac1{\sqrt{n+1}}>\frac2{\sqrt{n+2}+\sqrt{n+1}}=2(\sqrt{n+2}-\sqrt{n+1})")+". Adăugăm această inegalitate la ipoteză și obținem "+math(r"S_{n+1}>2(\sqrt{n+2}-1)")+", adică P(n+1).",
            "Estimarea strictă este valabilă pentru orice n≥1.",result())
    if kind==13:
        return proof(math(r"P(n):\ \sum_{k=1}^{n}(2k-1)x_k^2\le n^2x_n^2")+", pentru orice șir 0≤x₁≤⋯≤xₙ.",
            "La n=1, relația este x₁²≤x₁², adevărată cu egalitate.",
            "Pentru un n≥1 arbitrar presupunem P(n) pentru orice șir ordonat de n termeni. Considerăm acum un șir de n+1 termeni.",
            "Aplicăm ipoteza primilor n termeni și folosim xₙ²≤xₙ₊₁². Atunci "+math(r"\sum_{k=1}^{n+1}(2k-1)x_k^2\le n^2x_n^2+(2n+1)x_{n+1}^2\le(n^2+2n+1)x_{n+1}^2=(n+1)^2x_{n+1}^2")+", deci P(n+1).",
            "Inegalitatea este adevărată pentru orice n≥1. Constanta n² este minimă: x₁=⋯=xₙ=1 dă egalitate.",result())
    if kind==14:
        return proof(math(r"P(n):\ (1+x)^n\ge1+nx")+", pentru un x≥−1 fixat.",
            "La n=1 avem 1+x=1+x, deci P(1) este adevărată.",
            "Fixăm n≥1 și presupunem (1+x)ⁿ≥1+nx.",
            "Deoarece 1+x≥0, putem înmulți ipoteza cu 1+x fără să schimbăm sensul: "+math(r"(1+x)^{n+1}\ge(1+nx)(1+x)=1+(n+1)x+nx^2\ge1+(n+1)x")+". Ultimul pas folosește nx²≥0. Rezultă P(n+1).",
            "Inegalitatea lui Bernoulli este adevărată pentru orice n≥1.","În grilă x=1/100. "+result())
    if kind==15:
        c,=args(r"f\(n\)=(\d+)\(n³−n\)")
        return proof(f"P(n): 6 divide f(n), unde f(n)={c}(n³−n).",
            "La n=1, f(1)=0, divizibil cu 6.","Fixăm n≥1 și presupunem 6|f(n).",
            math(rf"f(n+1)=f(n)+{3*c}n(n+1)")+". Primul termen este multiplu de 6 prin ipoteză. Produsul n(n+1) este par, deci și al doilea termen este multiplu de 6. Prin urmare 6|f(n+1), adică P(n+1).",
            "Divizibilitatea este adevărată pentru orice n≥1.","Identitatea cerută este f(n+1)−f(n)="+str(3*c)+"n(n+1).")
    if kind==16:
        a,=args(r"a=(\d+)")
        return proof(f"P(n): (a−1) divide aⁿ−1, pentru a={a}.",
            "La n=1, a¹−1=a−1, deci P(1) este adevărată.",
            "Fixăm n≥1 și presupunem (a−1)|(aⁿ−1).",
            math(r"a^{n+1}-1=a(a^n-1)+(a-1)")+". Primul termen este divizibil cu a−1 prin ipoteză, iar al doilea este chiar a−1. Rezultă P(n+1).",
            "Divizibilitatea este adevărată pentru orice n≥1.",result())
    if kind==17:
        return proof("P(n): dacă n divizori pozitivi, primi între ei două câte două, divid N, atunci produsul lor divide N.",
            "La n=1, produsul are un singur factor și afirmația coincide cu ipoteza problemei.",
            "Fixăm n≥1 și presupunem P(n). Considerăm n+1 divizori pozitivi, primi între ei două câte două.",
            "Prin ipoteză, produsul primilor n divizori divide N. Acest produs este prim cu al (n+1)-lea divizor; și acesta divide N. Lema lui Euclid arată că produsul tuturor celor n+1 divizori divide N. Am obținut P(n+1).",
            "Afirmația este adevărată pentru orice număr pozitiv de divizori.",old)
    if kind==18:
        a,=args(r"u₁=√(\d+)"); limit=int(answer)
        return proof(f"P(n): 0<uₙ<{limit}.",
            f"La n=1, u₁=√{a} și {limit-1}<√{a}<{limit}, deci P(1) este adevărată.",
            f"Fixăm n≥1 și presupunem 0<uₙ<{limit}.",
            math(rf"0<{a}+u_n<{a+limit}={limit}^2")+". Radicalul este definit și strict crescător pe numere nenegative, deci "+math(rf"0<u_{{n+1}}=\sqrt{{{a}+u_n}}<{limit}")+". Rezultă P(n+1).",
            f"Pentru orice n≥1, uₙ<{limit}.",f"Minimalitatea limitei întregi: u₁>{limit-1}, deci niciun întreg mai mic decât {limit} nu poate fi o astfel de bornă.")
    if kind==19:
        a,=args(r"x\+1/x=(\d+)")
        return proof("P(n): Sₙ=xⁿ+x^(−n) este întreg.",
            f"Avem S₀=2 și S₁={a}, ambele întregi. Sunt necesare două baze, deoarece recurența folosește doi termeni anteriori.",
            "Fixăm n≥1 și presupunem simultan că Sₙ₋₁ și Sₙ sunt întregi (inducție de ordinul doi).",
            math(rf"S_{{n+1}}={a}S_n-S_{{n-1}}")+". Recurența rezultă dezvoltând (x+1/x)(xⁿ+x^(−n)). Fiind combinație cu coeficienți întregi a celor doi termeni din ipoteză, Sₙ₊₁ este întreg.",
            "Toți termenii Sₙ, n≥0, sunt întregi.",old)
    if kind==20:
        b,=args(r"aₙ₊₁=(\d+)aₙ")
        return proof(math(rf"P(n):\ a_n={b}^n-1"),
            f"Șirul începe la 0. La n=0, a₀=0={b}⁰−1, deci verificăm P(0).",
            f"Fixăm n≥0 și presupunem aₙ={b}ⁿ−1.",
            math(rf"a_{{n+1}}={b}a_n+{b-1}={b}({b}^n-1)+{b-1}={b}^{{n+1}}-1")+". Prima egalitate este recurența, a doua folosește ipoteza. Rezultă P(n+1).",
            "Formula este adevărată pentru orice n≥0.")
    if kind==21:
        a,=args(r"uₙ₊₁=\(uₙ\+(\d+)\)/2")
        return proof(math(rf"P(n):\ u_n={a}-\frac{{{a-1}}}{{2^{{n-1}}}}")+f" și 1≤uₙ<{a}.",
            f"La n=1, formula dă {a}−{a-1}=1=u₁; avem 1≤u₁<{a}.",
            "Fixăm n≥1 și presupunem formula și încadrarea P(n).",
            math(rf"u_{{n+1}}=\frac{{u_n+{a}}}2={a}-\frac{{{a-1}}}{{2^n}}")+f". Prin ipoteză, media dintre uₙ și {a} este cel puțin 1 și strict sub {a}. Obținem atât formula, cât și încadrarea P(n+1).",
            f"Formula și bornarea sunt adevărate pentru orice n≥1. Deoarece {a-1}/2^(n−1) poate fi oricât de mic, termenii se apropie oricât de mult de {a} din stânga.",
            f"Prin urmare {a} este cea mai mică bornă superioară; o valoare mai mică ar fi depășită de un termen suficient de înaintat.")
    if kind==22:
        return proof(math(r"P(n):\ T_n=\prod_{k=1}^{n}k(k+1)=n!\,(n+1)!"),
            "La n=1, T₁=1·2=2=1!·2!, deci P(1) este adevărată.",
            "Fixăm n≥1 și presupunem Tₙ=n!·(n+1)!.",
            math(r"T_{n+1}=T_n(n+1)(n+2)=n!\,(n+1)!\,(n+1)(n+2)=(n+1)!\,(n+2)!")+". Am folosit ipoteza și definiția factorialului; rezultă P(n+1).",
            "Formula produsului este adevărată pentru orice n≥1. Exponentul lui 2 se obține apoi adunând exponenții din cele două factoriale.",old)
    if kind==23:
        return proof("P(n): un produs de n sume de două pătrate întregi este tot o sumă de două pătrate întregi.",
            "La n=1, factorul este deja o sumă de două pătrate; P(1) este imediată.",
            "Fixăm n≥1 și presupunem că produsul primilor n factori este u²+v², cu u și v întregi.",
            "Adăugăm factorul c²+d². Identitatea "+math(r"(u^2+v^2)(c^2+d^2)=(uc-vd)^2+(ud+vc)^2")+" produce din nou baze întregi pentru cele două pătrate. Aceasta este P(n+1).",
            "Proprietatea este adevărată pentru orice număr pozitiv de factori.",old)
    if kind==24:
        return proof("P(k): întregul nenegativ k admite o reprezentare cu semne folosind toate pătratele de la 1² la un anumit n².",
            "Pasul va fi de 4, deci verificăm patru baze: 0=1²+2²−3²+4²−5²−6²+7²; 1=1²; 2=−1²−2²−3²+4²; 3=−1²+2²−3²−4²+5².",
            "Presupunem P(k), cu o reprezentare care folosește exact pătratele 1²,…,n².",
            math(r"(n+1)^2-(n+2)^2-(n+3)^2+(n+4)^2=4")+". Adăugăm blocul reprezentării din ipoteză. Obținem k+4 și folosim exact pătratele 1²,…,(n+4)², deci P(k+4).",
            "Cele patru baze și pasul +4 acoperă toate resturile modulo 4, deci toți întregii nenegativi. Inversând toate semnele obținem și întregii negativi.","În grilă alegem exact blocul cu semnele +, −, −, +.")
    if kind==25:
        return proof("P(n): un pătrat poate fi partiționat în n pătrate, posibil de mărimi diferite.",
            "Verificăm trei baze, deoarece pasul este +3: P(6), într-un pătrat 3×3 luăm un pătrat 2×2 și cinci unitare; P(7), rafinăm un sfert din partiția în patru sferturi; P(8), într-un pătrat 4×4 luăm un pătrat 3×3 și șapte unitare.",
            "Presupunem că există o partiție în n pătrate, pentru un n≥6.",
            "Alegem o singură piesă și o împărțim în patru pătrate egale. Celelalte piese nu se modifică; numărul total devine n−1+4=n+3. Rezultă P(n+3).",
            "Bazele 6, 7, 8 și pasul +3 acoperă toate ordinele n≥6.",old.split("Aici ",1)[-1] if "Aici " in old else result())
    if kind==26:
        vertices,=args(r"are (\d+) vârfuri intermediare")
        r=vertices//2; base=3 if "două vârfuri opuse" in text else 4
        return proof(f"P(r): tăietura simetrică cu 2r vârfuri intermediare produce două poligoane congruente cu {base}+2r laturi.",
            ("La r=0, o diagonală produce două triunghiuri congruente, fiecare cu 3 laturi." if base==3 else "La r=0, segmentul dintre mijloacele laturilor opuse produce două dreptunghiuri congruente, fiecare cu 4 laturi."),
            f"Presupunem P(r) pentru un r≥0, cu o tăietură simplă și invariantă la rotația de 180°.",
            "Introducem o pereche de vârfuri noi, simetrice, cu modificări suficient de mici ca tăietura să rămână simplă și fără coliniarități. Fiecare piesă câștigă două laturi, iar rotația păstrează congruența. Astfel P(r+1) este adevărată.",
            f"Proprietatea este adevărată pentru orice r≥0. Pentru r={r}, numărul laturilor este {base}+2·{r}={answer}.")
    if kind==28:
        d,=args(r"și de (\d+) lei")
        return proof("P(n): suma n lei poate fi plătită cu monedele date.",
            f"Pasul este +2, deci verificăm două sume consecutive: {d-1} se plătește cu {(d-1)//2} monede de 2 lei; {d} se plătește cu o monedă de {d} lei.",
            f"Presupunem P(n) pentru un n≥{d-1}.",
            "La plata sumei n adăugăm o monedă de 2 lei. Obținem plata sumei n+2, deci P(n+2).",
            f"Cele două baze acoperă ambele parități, astfel încât orice sumă n≥{d-1} se poate plăti.",
            f"Pragul este minim: {d-2} este impar și mai mic decât {d}, deci nu poate fi plătit numai cu monede de 2 și nici nu poate folosi o monedă de {d}.")
    if kind==29:
        return proof("P(n): rețeaua triunghiulară cu n diviziuni pe latură are n² piese triunghiulare mici.",
            "La n=1 avem un singur triunghi, iar 1²=1.",
            "Fixăm n≥1 și presupunem că o rețea de latură n unități conține n² triunghiuri unitare.",
            "Extindem rețeaua la latura n+1 unități: stratul nou conține 2n+1 triunghiuri unitare. Din ipoteză, numărul total este n²+(2n+1)=(n+1)². Rescalarea la triunghiul inițial păstrează numărul și congruența pieselor, deci P(n+1).",
            "Formula n² este adevărată pentru orice n≥1 și numără numai piesele mici ale partiției.",result())
    if kind==30:
        r,=args(r"cu (\d+) vârfuri intermediare")
        base=3 if "trei triunghiuri congruente" in text else 4
        return proof(f"P(r): cele trei piese congruente au fiecare {base}+2r laturi după introducerea a r vârfuri pe fiecare frontieră interioară.",
            f"La r=0 folosim partiția inițială din enunț, cu trei piese congruente având fiecare {base} laturi.",
            "Presupunem P(r), cu frontiere simple, obținute una din alta prin rotații de 120°.",
            "Introducem câte un vârf suplimentar pe fiecare dintre cele trei frontiere, cu deformări mici și simetrice, fără intersecții noi sau laturi consecutive coliniare. Fiecare piesă atinge două frontiere și câștigă două laturi. Rotația păstrează congruența, deci P(r+1).",
            f"Proprietatea este adevărată pentru orice r≥0. Pentru r={r}, obținem {base}+2·{r}={answer} laturi pe piesă.")
    raise AssertionError((kind,text))


def build_questions():
    questions = []

    def add(section, kind, text, correct, wrong, explanation):
        values = list(map(str, [correct, *wrong]))
        assert len(values) == len(set(values)) == 4, (section, kind, text, values)
        position = len(questions) % 4
        values.insert(position, values.pop(0))
        questions.append({
            "text": text, "type": "multiple_choice", "format": "grid", "points": 10,
            "explanation": explanation,
            "options": [{"text": value, "is_correct": i == position} for i, value in enumerate(values)],
            "catalog": {"section": f"A1.{section}", "type": kind, "type_name": NAMES[section][kind-1],
                        "task_scope": (
                            "Construcție ghidată și pas inductiv; nu demonstrația integrală din sursă"
                            if section == "4.1" and kind in {25,26,30} else
                            "Caz particular sau pas al metodei; nu demonstrația integrală din sursă"
                            if section == "4.1" and kind in {1,11,12,13,14,16,17,18,21,23,24} else
                            "Formulă generală și justificarea inducției"
                            if section == "4.1" and kind in {2,10,15,20} else
                            "Aplicarea numerică a metodei"),
                        "origin": "Exercițiu nou după tipologia catalogului Burtea IX"},
        })

    def numeric(section, kind, text, answer, explanation, wrong=None):
        answer = F(answer)
        if wrong is None:
            wrong = []
            for v in [answer+1, answer-1, 2*answer, answer+2, answer/2, answer+3]:
                if v != answer and v not in wrong and (answer < 0 or v >= 0):
                    wrong.append(v)
                if len(wrong) == 3: break
        assert len(set(map(F, wrong)) | {answer}) == 4
        add(section, kind, text, number(answer), [number(v) for v in wrong], explanation)

    def induction(kind, *args, **kwargs): return numeric("4.1", kind, *args, **kwargs)
    def counting(kind, *args, **kwargs): return numeric("4.2", kind, *args, **kwargs)

    # Toate opțiunile trec testul n=1; cele false au contraexemple explicite.
    # Pentru opțiunea corectă demonstrăm condiția pentru toți indicii.
    for m in range(5):
        wrong = [F(m*m)+delta for delta in [F(1,4),F(1,2),F(3,4)]]
        witnesses = []
        for candidate in wrong:
            index = next(n for n in range(2,101) if isqrt((n*n*candidate).__floor__())**2 != (n*n*candidate).__floor__())
            floor_value = (index*index*candidate).__floor__()
            witnesses.append(f"x={number(candidate)} este exclus prin n={index}, deoarece ⌊n²x⌋={floor_value}, care nu este pătrat perfect")
        square_proof = (
            f"Pentru x={m*m}={m}², avem ⌊n²x⌋=({m}n)² pentru orice întreg n≥1. "
            + "; ".join(witnesses) + ". Toate opțiunile au partea întreagă egală cu "
            f"{m*m} la n=1, astfel încât acel test singur nu le distinge. "
            "Un singur contraexemplu infirmă condiția universală; verificarea unui număr finit de indici nu o demonstrează."
        )
        induction(1, f"Fie x ∈ [{m*m}; {m*m+1}) astfel încât ⌊n²x⌋ este pătrat perfect pentru orice întreg n ≥ 1. "
                  "Care dintre următoarele valori poate fi x? ⌊t⌋ este partea întreagă a lui t.",
                  m*m, square_proof, wrong)

    sum_formulas = [
        "n(n+1)/2", "n(n+1)(2n+1)/6", "n²(n+1)²/4",
        "n(n+1)(2n+1)(3n²+3n−1)/30", "n²(n+1)²(2n²+2n−1)/12",
    ]
    for power, formula in enumerate(sum_formulas,1):
        wrong = ["Sₙ = "+other for other in sum_formulas if other != formula][:3]
        add("4.1",2,f"Ce formulă se demonstrează prin inducție pentru Sₙ = ∑ₖ₌₁ⁿ k^{power}, n ≥ 1?",
            "Sₙ = "+formula, wrong,
            f"Punem F(n)={formula}. Baza este F(1)=1. Dezvoltând expresiile, "
            f"F(n+1)−F(n)=(n+1)^{power}, exact termenul adăugat sumei. "
            "Astfel Sₙ=F(n) implică Sₙ₊₁=F(n)+(n+1)^"+str(power)+"=F(n+1).")

    for n in range(4,9):
        answer=sum((-1)**(k+1)*k*k for k in range(1,n+1))
        assert answer == (-1)**(n+1)*n*(n+1)//2
        induction(3,f"Calculați ∑ₖ₌₁^{n} (−1)^(k+1)k², folosind formula demonstrabilă prin inducție.",answer,
                  f"Formula este Sₙ = (−1)^(n+1)n(n+1)/2. Baza n=1 dă 1. La pasul următor adăugăm "
                  f"(−1)^(n+2)(n+1)² și obținem (−1)^(n+2)(n+1)(n+2)/2. Pentru n={n}: {answer}.")
        nested=sum(sum(range(1,k+1)) for k in range(1,n+1))
        assert nested==n*(n+1)*(n+2)//6
        induction(4,f"Calculați (1)+(1+2)+⋯+(1+2+⋯+{n}).",nested,
                  f"Sₙ = n(n+1)(n+2)/6. În pasul inductiv adăugăm (n+1)(n+2)/2 și factorizăm, "
                  f"obținând (n+1)(n+2)(n+3)/6. Pentru n={n}, suma este {nested}.")

    for c,n in zip(range(1,6),range(4,9)):
        answer=sum(k*(c*k+1) for k in range(1,n+1))
        induction(5,f"Calculați ∑ₖ₌₁^{n} k({c}k+1).",answer,
                  f"Separăm suma în {c}∑k² + ∑k, folosind formulele dovedite prin inducție. "
                  f"Rezultă {c}·{n}·{n+1}·{2*n+1}/6 + {n}·{n+1}/2 = {answer}.")

    for n in range(3,8):
        answer=sum((F(1,k*(k+1)) for k in range(1,n+1)),F(0))
        assert answer==F(n,n+1)
        induction(6,f"Calculați ∑ₖ₌₁^{n} 1/[k(k+1)].",answer,
                  f"1/[k(k+1)] = 1/k − 1/(k+1). Termenii se reduc succesiv: Sₙ = 1 − 1/(n+1). "
                  f"Același rezultat se verifică inductiv prin adăugarea termenului nou. Pentru n={n}: {number(answer)}.")
        answer=sum((F(1,k*(k+1)*(k+2)) for k in range(1,n+1)),F(0))
        assert answer==F(1,4)-F(1,2*(n+1)*(n+2))
        induction(7,f"Calculați ∑ₖ₌₁^{n} 1/[k(k+1)(k+2)].",answer,
                  "Folosim 1/[k(k+1)(k+2)] = (1/2)(1/[k(k+1)] − 1/[(k+1)(k+2)]). "
                  f"Suma telescopică este 1/4 − 1/[2(n+1)(n+2)] = {number(answer)}; adăugarea termenului nou confirmă pasul inductiv.")
        answer=prod(F(k*k-1,k*k) for k in range(2,n+1))
        assert answer==F(n+1,2*n)
        induction(8,f"Calculați ∏ₖ₌₂^{n} (1 − 1/k²).",answer,
                  f"Fiecare factor este ((k−1)/k)((k+1)/k). Produsul se reduce la (n+1)/(2n). "
                  f"Baza n=2 este 3/4; înmulțirea cu 1−1/(n+1)² dă formula următoare. Rezultatul este {number(answer)}.")

    for a,n in [(2,1),(2,2),(3,1),(3,2),(4,1)]:
        answer=prod(1+a**(2**k) for k in range(n+1))
        assert (a-1)*answer==a**(2**(n+1))-1
        factors = "·".join(f"(1+{a}^{2**k})" for k in range(n+1))
        induction(9,f"Calculați produsul {factors}.",answer,
                  f"Înmulțind produsul cu {a}−1 și aplicând repetat diferența de pătrate obținem "
                  f"{a}^(2^({n}+1))−1. Așadar produsul este ({a}^(2^({n}+1))−1)/({a}−1) = {answer}.")

    for base,power in [(2,2),(2,3),(3,3),(2,4),(3,4)]:
        failures=[n for n in range(1,201) if base**n<=n**power]
        threshold=max(failures)+1
        assert base*threshold**power >= (threshold+1)**power
        induction(10,f"Care este cel mai mic întreg N ≥ 1 astfel încât {base}ⁿ > n^{power} pentru orice n ≥ N?",threshold,
                  f"La n={threshold-1}, avem {base}ⁿ={base**(threshold-1)} ≤ n^{power}={(threshold-1)**power}; "
                  f"la n={threshold}, inegalitatea este strictă. Pentru n≥{threshold}, "
                  f"(1+1/n)^{power} ≤ (1+1/{threshold})^{power} ≤ {base}. Astfel "
                  f"{base}^(n+1) > {base}n^{power} ≥ (n+1)^{power}, deci inducția închide demonstrația.")

    for c,n in [(1,4),(2,5),(3,6),(4,7),(5,8)]:
        bound=c*(F(2)-F(1,n))
        induction(11,f"Pentru Sₙ = ∑ₖ₌₁ⁿ {c}/k² folosim, la k≥2, 1/k² < 1/[k(k−1)]. "
                  f"Ce valoare are majorantul telescopic {c}·(1+∑ₖ₌₂^{n} 1/[k(k−1)])?",bound,
                  f"Suma de comparație se reduce la {c}(2−1/{n}) = {number(bound)}. "
                  "Inductiv, noul termen 1/(n+1)² este mai mic decât diferența 1/n−1/(n+1). "
                  "Pentru n≥2, majorarea sumei inițiale este strictă.")

    for m in range(2,7):
        n=m*m-1
        induction(12,f"Din 1/√k > 2(√(k+1)−√k), k≥1, se obține prin însumare de la 1 la {n} "
                  f"o bornă inferioară strictă pentru ∑ₖ₌₁^{n} 1/√k. Care este valoarea exactă a acestei borne telescopice?",
                  2*(m-1),f"2(√(k+1)−√k) = 2/(√(k+1)+√k) < 1/√k. "
                  f"Prin însumare, termenii intermediari se reduc: 2(√({n}+1)−1) = {2*(m-1)}. "
                  "Adăugarea următorului termen păstrează estimarea, ceea ce furnizează și demonstrația inductivă.")

    for n in range(2,7):
        induction(13,f"Pentru 0 ≤ x₁ ≤ ⋯ ≤ x_{n}, care este cea mai mică constantă C astfel încât "
                  f"∑ₖ₌₁^{n} (2k−1)xₖ² ≤ C·x_{n}² pentru toate aceste șiruri?",n*n,
                  f"Înlocuim fiecare xₖ² cu x_{n}²; suma coeficienților impari este {n}²={n*n}, "
                  "identitate dovedită inductiv prin adăugarea lui 2n+1. Constanta este optimă: luăm toate valorile xₖ=1.")

    for n in [10,20,30,40,50]:
        bound=1+F(n,100)
        induction(14,f"Ce bornă inferioară dă inegalitatea lui Bernoulli pentru (1+1/100)^{n}? "
                  "Se cere exact expresia 1+nx din această inegalitate, nu o bornă mai slabă.",bound,
                  f"Bernoulli: (1+x)ⁿ ≥ 1+nx pentru x≥−1 și n întreg pozitiv. "
                  f"Aici x=1/100 și n={n}, deci rezultă {number(bound)}. În pasul inductiv, "
                  "(1+nx)(1+x)=1+(n+1)x+nx² ≥ 1+(n+1)x.")

    for c in range(1,6):
        add("4.1",15,f"Pentru f(n)={c}(n³−n), n≥1, ce identitate justifică pasul inductiv în demonstrația 6 | f(n)?",
            f"f(n+1)−f(n) = {3*c}n(n+1)",
            [f"f(n+1)−f(n) = {3*c}n²",f"f(n+1)−f(n) = {c}n(n+1)",f"f(n+1)−f(n) = {3*c}(n+1)"],
            f"Prin dezvoltare, diferența este {3*c}n(n+1), multiplu de 6 deoarece n(n+1) este par. "
            "Baza f(1)=0 și ipoteza 6|f(n) implică 6|f(n+1).")

    for a in range(3,8):
        induction(16,f"Pentru a={a}, inducția pentru (a−1) | (aⁿ−1) folosește "
                  "a^(n+1)−1 = a(aⁿ−1)+r. Ce valoare are r?",a-1,
                  f"a(aⁿ−1)=a^(n+1)−a, deci r=a−1={a-1}. Atât primul termen, prin ipoteza inductivă, "
                  "cât și restul sunt divizibili cu a−1; baza n=1 este imediată.")

    for divisors in [(2,3,5),(3,4,5),(4,5,7),(5,7,9),(7,8,9)]:
        assert all(gcd(a,b)==1 for a,b in combinations(divisors,2))
        answer=prod(divisors)
        induction(17,f"Numărul întreg N este divizibil cu fiecare dintre {divisors[0]}, {divisors[1]}, {divisors[2]}. "
                  "Care este cel mai mare întreg pozitiv D despre care aceste condiții garantează că divide N?",
                  answer,f"Divizorii sunt primi între ei două câte două. Lema lui Euclid, aplicată succesiv, "
                  f"arată că produsul {answer} divide N. Nu se poate garanta mai mult, deoarece N poate fi chiar {answer}.")

    for m in range(2,7):
        a=m*(m-1)
        induction(18,f"Fie u₁=√{a} și uₙ₊₁=√({a}+uₙ), n≥1. "
                  "Care este cel mai mic întreg M pentru care uₙ < M pentru orice n≥1?",m,
                  f"Avem {m-1} < √{a} < {m}. Dacă uₙ<{m}, atunci {a}+uₙ<{a+m}={m}², "
                  f"deci uₙ₊₁<{m}. Inducția demonstrează afirmația, iar orice întreg mai mic este deja exclus de u₁>{m-1}.")

    for t in range(3,8):
        s=[2,t]
        for _ in range(3): s.append(t*s[-1]-s[-2])
        induction(19,f"Fie x>0 cu x+1/x={t}. Calculați x⁴+1/x⁴ folosind recurența sumelor simetrice.",s[4],
                  f"Pentru Sₙ=xⁿ+x^(−n), S₀=2, S₁={t}, iar Sₙ₊₁={t}Sₙ−Sₙ₋₁. "
                  f"Prin urmare S₂={s[2]}, S₃={s[3]}, S₄={s[4]}. Recurența dovedește inductiv și integritatea tuturor termenilor.")

    for b in range(2,7):
        add("4.1",20,f"Șirul este dat prin a₀=0, aₙ₊₁={b}aₙ+{b-1}. Care formulă pentru n≥0 se verifică prin inducție?",
            f"aₙ={b}ⁿ−1",[f"aₙ={b}ⁿ+1",f"aₙ={b}n",f"aₙ={b}^(n+1)−1"],
            f"La n=0 formula dă 0. Dacă aₙ={b}ⁿ−1, atunci aₙ₊₁={b}({b}ⁿ−1)+{b-1}={b}^(n+1)−1.")

    for m in range(2,7):
        induction(21,f"Șirul u₁=1, uₙ₊₁=(uₙ+{m})/2 este mărginit superior. "
                  "Care este cea mai mică bornă superioară reală valabilă pentru toți termenii?",m,
                  f"Inductiv 1≤uₙ<{m}, deoarece media a două numere cel mult {m} rămâne cel mult {m}. "
                  f"Mai precis uₙ={m}−({m-1})/2^(n−1), verificabil prin inducție. Termenii se apropie de {m}, "
                  "deci nicio bornă mai mică nu este valabilă pentru toți n.")

    for n in range(3,8):
        answer=sum(valuation(k*(k+1),2) for k in range(1,n+1))
        assert answer==factorial_valuation(n,2)+factorial_valuation(n+1,2)
        induction(22,f"Care este exponentul lui 2 în descompunerea în factori primi a produsului ∏ₖ₌₁^{n} k(k+1)?",answer,
                  f"Produsul este {n}!·{n+1}!. Exponenții se adună, deci v₂(P)="
                  f"v₂({n}!)+v₂({n+1}!)={answer}. Inductiv, noul factor (n+1)(n+2) adaugă exact v₂(n+1)+v₂(n+2).")

    for a in range(1,6):
        first_u,first_v=2*a-1,a+2
        u,v=first_u-2*first_v,2*first_u+first_v
        fmt=lambda x,y:f"({x}; {y})"
        assert u*u+v*v==(a*a+1)*25
        add("4.1",23,f"Identitatea (a²+b²)(c²+d²)=(ac−bd)²+(ad+bc)² se folosește inductiv pentru produse de sume de pătrate. "
            f"Aplicăm identitatea succesiv produsului ({a}²+1²)(2²+1²)(1²+2²), păstrând ordinea factorilor. "
            "Ce pereche de baze ale pătratelor obținem? La fiecare pas folosim exact (ac−bd; ad+bc).",fmt(u,v),
            [fmt(u+1,v),fmt(u,v+1),fmt(u+1,v+1)],
            f"După primii doi factori obținem ({first_u}; {first_v}). La adăugarea factorului 1²+2², "
            f"noua pereche este ({first_u}−2·{first_v}; 2·{first_u}+{first_v})=({u}; {v}). "
            f"Suma pătratelor este {(a*a+1)*25}. Acesta este pasul iterabil pentru oricâți factori.")

    for n in range(3,6):
        target=sum(k*k for k in range(1,n))-n*n
        def signed(signs): return " ".join(("+" if s>0 else "−")+f"{k}²" for k,s in enumerate(signs,1))
        correct=[1]*(n-1)+[-1]
        wrong=[]; wrong_values=set()
        for signs in product([1,-1],repeat=n):
            value=sum(s*k*k for k,s in enumerate(signs,1))
            if value!=target and value not in wrong_values:
                wrong.append(signed(signs)); wrong_values.add(value)
            if len(wrong)==3: break
        add("4.1",24,f"Care alegere a semnelor reprezintă întregul {target} folosind exact pătratele 1²,…,{n}², o singură dată fiecare?",
            signed(correct),wrong,
            f"Pornim de la suma tuturor pătratelor pozitive, {sum(k*k for k in range(1,n+1))}. "
            f"Schimbarea semnului lui {n}² scade suma cu {2*n*n}, rezultând {target}. "
            "Acest tip de modificare controlată este pasul constructiv folosit în reprezentări cu semne.")

    for n in [6,7]:
        def block(signs):
            return " ".join(("+" if sign>0 else "−")+f"{n+i}²" for i,sign in enumerate(signs,1))
        correct=[1,-1,-1,1]
        wrong=[]
        for signs in product([1,-1],repeat=4):
            if sum(sign*(n+i)**2 for i,sign in enumerate(signs,1))!=4:
                wrong.append(block(signs))
            if len(wrong)==3: break
        add("4.1",24,f"Avem o reprezentare a unui întreg k folosind exact pătratele 1²,…,{n}² cu semne ±. "
            f"Ce bloc adăugat produce o reprezentare a lui k+4, folosind exact pătratele 1²,…,{n+4}²?",
            block(correct),wrong,
            "Identitatea (n+1)²−(n+2)²−(n+3)²+(n+4)²=4 rezultă prin dezvoltare. "
            "Blocul extinde reprezentarea și crește valoarea cu 4. Baze pentru toate resturile modulo 4: "
            "0=1²+2²−3²+4²−5²−6²+7²; 1=1²; 2=−1²−2²−3²+4²; "
            "3=−1²+2²−3²−4²+5². Repetând pasul obținem orice întreg nenegativ; "
            "inversarea tuturor semnelor dă și întregii negativi.")

    for target,base in [(9,6),(10,7),(11,8),(17,8),(23,8)]:
        steps=(target-base)//3
        add("4.1",25,f"Avem construcții inițiale ale unui pătrat în 6, 7 sau 8 pătrate, posibil de mărimi diferite. "
            "Un rafinament înlocuiește o singură piesă cu patru pătrate egale. "
            f"Ce pereche (număr inițial de piese; număr de rafinamente) produce exact {target} pătrate?",
            f"({base}; {steps})",[f"({base}; {steps+1})",f"({base-1}; {steps})",f"({base+1}; {steps})"],
            "Baza 6: împărțim un pătrat de latură 3 într-un pătrat 2×2 și cinci pătrate 1×1. "
            "Baza 7: rafinăm o piesă din partiția în patru sferturi. Baza 8: într-un pătrat de latură 4, "
            "luăm un pătrat 3×3 și șapte pătrate 1×1. Fiecare rafinament crește numărul cu 3. "
            f"Aici {base}+3·{steps}={target}. Cele trei baze acoperă toate resturile modulo 3, deci metoda construiește orice ordin ≥6.")

    for r,corner in [(1,True),(1,False),(2,True),(2,False),(3,True)]:
        endpoints = "două vârfuri opuse" if corner else "mijloacele a două laturi opuse"
        outer = 2 if corner else 3
        induction(26,f"O linie frântă simplă, invariantă la rotația de 180° în jurul centrului pătratului, "
                  f"unește {endpoints} și are {2*r} vârfuri intermediare strict în interior. "
                  "Nu există trei vârfuri consecutive coliniare și nu atinge altfel conturul. "
                  "Câte laturi are fiecare dintre cele două poligoane congruente obținute?",2*r+1+outer,
                  f"Fiecare contur folosește {outer} segmente ale marginii pătratului și {2*r+1} segmente ale tăieturii, "
                  f"în total {2*r+1+outer}. Rotația de 180° schimbă cele două piese între ele; inserarea unei noi perechi "
                  "de vârfuri simetrice mărește numărul laturilor fiecărei piese cu 2. Plecând de la diagonală "
                  "obținem ordine impare, iar plecând de la segmentul dintre mijloace, ordine pare.")

    for c,n in zip(range(1,6),range(2,7)):
        answer=c*c*(2*n-1)**2
        induction(27,f"Numerele aₙ sunt nenegative și satisfac √a₁+⋯+√aₙ={c}n² pentru fiecare n≥1. "
                  f"Cât este a_{n}?",answer,
                  f"Scădem relația pentru n−1 din cea pentru n: √aₙ={c}(n²−(n−1)²)={c}(2n−1). "
                  f"Pentru n={n}, aₙ=({c}·{2*n-1})²={answer}. Formula reface sumele prin telescopare.")

    for d in [3,5,7,9,11]:
        induction(28,f"Avem oricâte monede de 2 lei și de {d} lei. Care este cel mai mic întreg N≥0 astfel încât "
                  "orice sumă întreagă de cel puțin N lei poate fi plătită exact?",d-1,
                  f"Orice sumă pară se plătește cu monede de 2 lei. Orice sumă impară ≥{d} se plătește cu "
                  f"o monedă de {d} și restul cu monede de 2. Baze consecutive: {d-1} și {d}; "
                  f"pasul adaugă 2. Suma {d-2}, impară și mai mică decât {d}, este imposibilă, deci pragul este minim.")

    for n in range(2,7):
        induction(29,f"Fiecare latură a unui triunghi echilateral este împărțită în {n} segmente egale. "
                  "Prin punctele de diviziune trasăm paralelele la laturi care formează rețeaua triunghiulară. "
                  "Câte triunghiuri echilaterale mici, toate congruente, formează partiția?",n*n,
                  f"Rândurile conțin 1,3,…,2n−1 triunghiuri. Suma este n², dovedită inductiv prin adăugarea "
                  f"unui rând cu 2n+1 piese. Pentru n={n}, rezultă {n*n}. Numărăm numai piesele mici ale partiției.")

    for r,corner in [(1,True),(1,False),(2,True),(2,False),(3,True)]:
        base=3 if corner else 4
        endpoints="vârfurile" if corner else "mijloacele laturilor"
        shape="triunghiuri" if corner else "patrulatere"
        outer=1 if corner else 2
        induction(30,f"Un triunghi echilateral este împărțit în trei {shape} congruente unind centrul cu {endpoints}. "
                  f"Înlocuim fiecare dintre cele trei frontiere interioare cu o linie frântă cu {r} vârfuri intermediare. "
                  "Cele trei linii se obțin prin rotații de 120°, nu se intersectează în puncte noi și nu produc laturi consecutive coliniare. "
                  "Câte laturi are fiecare piesă nouă?",base+2*r,
                  f"Fiecare piesă are {outer} laturi pe conturul triunghiului și două frontiere interioare. Fiecare frontieră "
                  f"are acum {r+1} segmente, deci numărul laturilor este {outer}+2·{r+1}={base+2*r}. "
                  "Simetria de rotație păstrează congruența; o etapă suplimentară adaugă două laturi fiecărei piese. "
                  "Baza cu trei triunghiuri produce ordine impare, iar baza cu trei patrulatere, ordine pare. "
                  "Îndoiturile pot fi alese suficient de mici în vecinătăți disjuncte ale frontierelor, pentru a păstra o partiție simplă.")

    # 4.2. Numărări exacte; convențiile de ordine, repetiție și distinctibilitate sunt explicite.
    for i in range(5):
        a,b,overlap=12+i,9+2*i,3+i
        union=a+b-overlap
        counting(1,f"Mulțimile finite A și B satisfac |A|={a}, |A∩B|={overlap}, |A∪B|={union}. Cât este |B|?",b,
                 f"|A∪B|=|A|+|B|−|A∩B|, deci |B|={union}−{a}+{overlap}={b}.")
    for n in range(4,9):
        counting(2,f"O mulțime finită are {2**n} submulțimi, incluzând ∅ și mulțimea însăși. Câte elemente are?",n,
                 f"Fiecare element poate fi inclus sau exclus independent; sunt 2^n submulțimi. Din 2^n={2**n}, rezultă n={n}.")
    for i in range(5):
        total,a,b,both=30+2*i,14+i,12+i,5+i
        answer=total-(a+b-both)
        counting(3,f"Din {total} elevi, {a} joacă șah, {b} tenis, iar {both} practică ambele activități. "
                 "Câți nu practică niciuna dintre cele două?",answer,
                 f"Cel puțin o activitate: {a}+{b}−{both}={a+b-both}. Niciuna: {total}−{a+b-both}={answer}.")
    for i in range(5):
        # Disjoint Venn atoms ensure that every declared cardinal is feasible.
        only_a,only_b,only_c,ab,ac,bc,abc=4+i,5+i,6+i,2,3,4,1+i
        a=only_a+ab+ac+abc; b=only_b+ab+bc+abc; c=only_c+ac+bc+abc
        answer=only_a+only_b+only_c+ab+ac+bc+abc
        counting(4,f"Pentru mulțimi finite, |A|={a}, |B|={b}, |C|={c}, |A∩B|={ab+abc}, "
                 f"|A∩C|={ac+abc}, |B∩C|={bc+abc}, |A∩B∩C|={abc}. "
                 "Intersecțiile câte două includ și intersecția triplă. Cât este |A∪B∪C|?",answer,
                 f"Incluziune–excluziune: {a}+{b}+{c}−{ab+abc}−{ac+abc}−{bc+abc}+{abc}={answer}.")
    for left,right,d in [(10,100,7),(25,250,9),(100,999,13),(1,500,11),(50,600,17)]:
        answer=right//d-(left-1)//d
        assert answer==sum(x%d==0 for x in range(left,right+1))
        counting(5,f"Câți întregi din intervalul închis [{left}; {right}] sunt divizibili cu {d}?",answer,
                 f"Numărul multiplilor este ⌊{right}/{d}⌋−⌊{left-1}/{d}⌋={answer}. Scădem multiplii până la {left-1}, pentru a include capătul stâng {left}.")
    for n,a,b in [(100,4,6),(300,6,8),(500,9,12),(1000,10,15),(750,14,21)]:
        common=lcm(a,b); answer=n//common
        assert answer==sum(x%a==x%b==0 for x in range(1,n+1))
        counting(6,f"Câți întregi din {{1,…,{n}}} sunt divizibili simultan cu {a} și {b}?",answer,
                 f"Multiplii comuni sunt multiplii lui cmmmc({a},{b})={common}. Sunt ⌊{n}/{common}⌋={answer}.")
    for n,a,b in [(100,4,6),(200,3,5),(300,6,10),(500,8,12),(1000,7,11)]:
        answer=n//a+n//b-n//lcm(a,b)
        assert answer==sum(x%a==0 or x%b==0 for x in range(1,n+1))
        counting(7,f"Câți întregi din {{1,…,{n}}} sunt divizibili cu {a} sau cu {b}, inclusiv cu ambele?",answer,
                 f"Adunăm multiplii fiecărui divizor și scădem multiplii comuni: "
                 f"⌊{n}/{a}⌋+⌊{n}/{b}⌋−⌊{n}/{lcm(a,b)}⌋={answer}.")
    for n in [12,18,30,40,60]:
        answer=sum(gcd(x,n)==1 for x in range(1,n+1))
        primes=[p for p in range(2,n+1) if n%p==0 and all(p%d for d in range(2,isqrt(p)+1))]
        formula=F(n)*prod(F(p-1,p) for p in primes)
        assert answer==formula
        counting(8,f"Câți întregi x, 1≤x≤{n}, sunt primi cu {n} (adică au cmmdc(x,{n})=1)?",answer,
                 f"Excludem prin incluziune–excluziune multiplii factorilor primi distincți {primes}. "
                 f"Numărul este {n}·∏(1−1/p)={answer}. A fi «prime cu {n}» nu înseamnă că x însuși trebuie să fie prim.")
    for n in range(5,10):
        add("4.2",9,f"La o întâlnire cu {n} persoane, fiecare pereche își strânge mâna o singură dată, "
            "apoi fiecare persoană oferă câte o fotografie fiecărei alte persoane. "
            "Care sunt numerele de strângeri de mână și, respectiv, de fotografii oferite?",
            f"({comb(n,2)}; {n*(n-1)})",[f"({n*(n-1)}; {comb(n,2)})",f"({n*n}; {n*n})",f"({comb(n,2)}; {comb(n,2)})"],
            f"Perechile neordonate sunt {n}·{n-1}/2={comb(n,2)}. Oferirile sunt direcționate: "
            f"{n} expeditori cu câte {n-1} destinatari, deci {n*(n-1)} fotografii.")
    for c,limit in [(10,100),(5,150),(12,200),(20,300),(7,500)]:
        answer=isqrt(limit-c)+1
        assert answer==len({c+k*k for k in range(limit+1) if c+k*k<=limit})
        counting(10,f"Câte valori distincte are mulțimea {{{c}+k² | k întreg, k≥0 și {c}+k²≤{limit}}}?",answer,
                 f"Avem 0≤k≤⌊√({limit}−{c})⌋={answer-1}. Sunt {answer} indici. Formula este strict crescătoare pe k≥0, deci valorile sunt distincte.")
    for length in range(3,8):
        counting(11,f"Câte numere naturale în baza 10 au exact {length} cifre, prima cifră 4 și ultima 0? "
                 "Repetarea cifrelor este permisă.",10**(length-2),
                 f"Prima și ultima poziție sunt fixate. Fiecare dintre cele {length-2} poziții interioare are 10 alegeri independente: 10^{length-2}.")
    for m in range(3,8):
        repeated=m**3; distinct=m*(m-1)*(m-2)
        add("4.2",12,f"Din cifrele 1,…,{m} formăm numere de trei cifre. Câte obținem dacă repetarea este permisă și, "
            "respectiv, dacă toate cele trei cifre trebuie să fie distincte?",
            f"({repeated}; {distinct})",[f"({distinct}; {repeated})",f"({repeated}; {repeated})",f"({repeated}; {comb(m,3)})"],
            f"Cu repetare avem {m} alegeri la fiecare poziție: {repeated}. Fără repetare, alegerile succesive "
            f"sunt {m}, {m-1}, {m-2}: {distinct}. C({m},3) ar număra selecții fără ordine; pozițiile cifrelor contează.")
    for white,black,red in [(2,3,4),(3,4,5),(4,2,6),(5,3,2),(6,4,3)]:
        counting(13,f"O urnă conține {white} bile albe, {black} negre și {red} roșii, toate etichetate distinct. "
                 "Extragem succesiv trei bile fără reintroducere, în ordinea albă–neagră–roșie. Câte rezultate ordonate sunt posibile?",
                 white*black*red,f"Alegem o bilă din fiecare culoare, în ordinea impusă: {white}·{black}·{red}={white*black*red}. "
                 "Culorile sunt diferite, deci prima extragere nu reduce numărul de alegeri pentru următoarea culoare.")
    for n in range(4,9):
        answer=n*(n-1)*(n-2)
        assert answer==len(list(permutations(range(n),3)))
        counting(14,f"Dintr-o urnă cu {n} bile etichetate distinct extragem succesiv trei bile fără reintroducere. "
                 "Ordinea contează. Câte rezultate sunt posibile?",answer,
                 f"Prima extragere are {n} alegeri, a doua {n-1}, a treia {n-2}; produsul este {answer}.")
    for n in range(3,8):
        counting(15,f"Distribuim {n} calculatoare distincte la două școli distincte. Fiecare calculator este dat exact unei școli; "
                 "o școală poate să nu primească nimic. Câte repartizări există?",2**n,
                 f"Fiecare dintre cele {n} calculatoare are două destinații independente. Rezultă 2^{n}={2**n}; ordinea livrării nu contează.")
    for n in range(3,8):
        answer=3**n-3*2**n+3
        assert answer==sum(len(set(destinations))==3 for destinations in product(range(3),repeat=n))
        counting(16,f"Distribuim {n} obiecte distincte la trei persoane distincte, fiecare obiect unei singure persoane. "
                 "Fiecare persoană trebuie să primească cel puțin un obiect. Câte repartizări există?",answer,
                 f"Incluziune–excluziune pe persoanele care nu primesc nimic: 3^{n}−3·2^{n}+3·1^{n}={answer}. "
                 "Repartizarea tuturor obiectelor la zero persoane nu este posibilă, deoarece n>0.",
                 wrong=[3**n,3**n-3*2**n,comb(n-1,2)])
    for colors,positions in [(2,3),(3,4),(4,3),(5,3),(3,5)]:
        counting(17,f"Avem {positions} panouri distincte și {colors} culori. Fiecare panou se colorează cu o singură culoare, "
                 "iar culorile se pot repeta. Câte colorări există?",colors**positions,
                 f"Fiecare poziție are {colors} alegeri independente. Nu identificăm colorările prin rotație sau reflexie: {colors}^{positions}={colors**positions}.")
    concatenation="".join(map(str,range(1,3001)))
    for rank in [15,100,190,500,2026]:
        remaining=rank; width=1; block_start=1
        while remaining>9*block_start*width:
            remaining-=9*block_start*width; width+=1; block_start*=10
        containing=block_start+(remaining-1)//width; offset=(remaining-1)%width
        answer=int(str(containing)[offset])
        assert answer==int(concatenation[rank-1])
        digit_candidates=[int(concatenation[rank-2]),int(concatenation[rank]),*range(10)]
        wrong=list(dict.fromkeys(d for d in digit_candidates if d!=answer))[:3]
        counting(18,f"În șirul de cifre 123456789101112… obținut concatenând întregii pozitivi, "
                 f"care este cifra de pe poziția {rank}? Prima cifră are poziția 1.",answer,
                 f"Eliminăm blocurile complete de numere cu mai puține cifre. Rămâne poziția {remaining} în blocul "
                 f"numerelor de {width} cifre. Numărul este {containing}, iar cifra cerută este a {offset+1}-a din el: {answer}.",wrong=wrong)
    for pages in [85,120,250,500,1000]:
        digits=sum(len(str(k)) for k in range(1,pages+1))
        counting(19,f"Numerotând toate paginile unei cărți de la 1 până la ultima pagină, fără zerouri inițiale, "
                 f"folosim {digits} cifre. Câte pagini are cartea?",pages,
                 "Primele 9 pagini consumă 9 cifre; paginile 10–99 consumă 180; paginile 100–999 consumă 2700. "
                 f"Scădem blocurile complete și împărțim restul la numărul de cifre al paginilor din ultimul bloc. Rezultă {pages} pagini.")
    for n,p in [(10,2),(20,3),(30,5),(50,2),(100,3)]:
        answer=factorial_valuation(n,p)
        assert answer==valuation(factorial(n),p)
        counting(20,f"Care este exponentul numărului prim {p} în descompunerea lui {n}! în factori primi?",answer,
                 f"Numărăm multiplii lui {p}, apoi factorii suplimentari de la multiplii lui {p}², {p}³ etc.: "
                 f"v_{p}({n}!)=⌊{n}/{p}⌋+⌊{n}/{p*p}⌋+⋯={answer}.")
    for n in [25,50,75,100,125]:
        answer=factorial_valuation(n,5)
        assert answer==len(str(factorial(n)))-len(str(factorial(n)).rstrip('0'))
        counting(21,f"În câte zerouri se termină scrierea în baza 10 a lui {n}! ?",answer,
                 f"Fiecare zero cere un factor 10=2·5. Factorii 2 sunt mai numeroși; numărăm factorii 5: "
                 f"⌊{n}/5⌋+⌊{n}/25⌋+⌊{n}/125⌋+⋯={answer}.")
    for n in [12,30,60,210,420]:
        prime_count=sum(n%p==0 and all(p%d for d in range(2,isqrt(p)+1)) for p in range(2,n+1))
        answer=2**prime_count
        assert answer==sum(n%a==0 and gcd(a,n//a)==1 for a in range(1,n+1))
        counting(22,f"Câte perechi ordonate (a,b) de întregi pozitivi satisfac ab={n} și cmmdc(a,b)=1?",answer,
                 f"Fiecare dintre cele {prime_count} blocuri de puteri prime trebuie dat integral lui a sau lui b; "
                 f"altfel factorii nu ar fi coprimi. Sunt 2^{prime_count}={answer} perechi ordonate, incluzând (1,{n}) și ({n},1).")
    for n in range(5,10):
        counting(23,f"Câte diagonale are un poligon convex cu {n} vârfuri?",n*(n-3)//2,
                 f"Din cele {comb(n,2)} perechi de vârfuri scădem cele {n} laturi: {comb(n,2)}−{n}={n*(n-3)//2}.")
    for n in range(4,9):
        counting(24,f"Câte diagonale spațiale are o prismă dreaptă cu baza un poligon convex cu {n} laturi? "
                 "Prin diagonală spațială înțelegem un segment între două vârfuri care nu sunt pe aceeași față.",n*(n-3),
                 f"Din fiecare vârf al bazei de jos, în baza de sus excludem vârful corespunzător și cele două vecine: "
                 f"rămân {n-3} alegeri. Sunt {n} vârfuri jos, deci {n*(n-3)} segmente; fiecare este numărat o singură dată.")
    for n in range(2,7):
        counting(25,f"În câte regiuni este împărțit planul de {n} drepte distincte care trec toate prin același punct?",2*n,
                 f"Prima dreaptă produce 2 regiuni. Fiecare dreaptă nouă prin același punct adaugă exact 2: în total 2·{n}={2*n}.")
    for n in range(4,9):
        counting(26,f"Câte drepte distincte determină {n} puncte din plan dacă oricare trei sunt necoliniare?",comb(n,2),
                 f"Fiecare pereche neordonată determină o dreaptă unică. Nicio dreaptă nu conține trei puncte, deci sunt {n}·{n-1}/2={comb(n,2)}.")
    for steps in range(1,6):
        counting(27,f"Pornim cu un pătrat. La fiecare etapă, fiecare piesă existentă este împărțită în patru pătrate egale. "
                 f"Câte piese sunt după {steps} etape?",4**steps,
                 f"N₀=1 și Nₖ₊₁=4Nₖ. Inductiv Nₖ=4ᵏ, deci după {steps} etape avem {4**steps} piese. "
                 "Aici se împart toate piesele, nu doar una.")
    for n in [20,50,99,120,200]:
        answer=isqrt(n)
        assert answer==sum(isqrt(k)**2==k for k in range(1,n+1))
        counting(28,f"Câte dintre numerele √1,√2,…,√{n} sunt raționale?",answer,
                 f"Pentru k întreg pozitiv, √k este rațional exact când k este pătrat perfect. "
                 f"Pătratele sunt 1²,…,{answer}², deci sunt ⌊√{n}⌋={answer}.")
    for n,k in [(7,2),(8,3),(9,4),(10,3),(12,5)]:
        add("4.2",29,f"O mulțime A are {n} elemente. Comparăm numărul submulțimilor cu {k} elemente cu numărul "
            f"submulțimilor cu {n-k} elemente. Care afirmație este corectă?",
            "Numerele sunt egale; complementarea B↦A∖B este o bijecție.",
            ["Primul număr este de două ori mai mare.","Al doilea număr este de două ori mai mare.","Nu există nicio corespondență bijectivă între cele două familii."],
            f"Complementul unei submulțimi cu {k} elemente are {n-k} elemente, iar complementarea aplicată de două ori "
            f"întoarce mulțimea inițială. Prin urmare ambele numere sunt C({n},{k})={comb(n,k)}.")
    for a,b in [(2,1),(3,2),(4,1),(2,3),(3,3)]:
        n=2**a*3**b; answer=a*(b+1)
        assert answer==sum(n%d==0 and d%2==0 for d in range(1,n+1))
        counting(30,f"Câți divizori pozitivi ai numărului 2^{a}·3^{b} sunt divizibili cu 2?",answer,
                 f"Divizorul este 2ⁱ3ʲ. Cerem 1≤i≤{a} și 0≤j≤{b}: {a}·{b+1}={answer} alegeri.")
    for limit in [30,50,80,100,150]:
        def prime(p): return p>=2 and all(p%d for d in range(2,isqrt(p)+1))
        cubes=[p**3 for p in range(2,limit+1) if prime(p) and p**3<=limit]
        pairs=[p*q for p in range(2,limit+1) for q in range(p+1,limit+1) if p*q<=limit and prime(p) and prime(q)]
        answer=len(cubes)+len(pairs)
        assert answer==sum(sum(n%d==0 for d in range(1,n+1))==4 for n in range(1,limit+1))
        counting(31,f"Câte numere întregi din intervalul [1; {limit}] au exact patru divizori pozitivi?",answer,
                 "Sunt exact numerele p³ și pq, unde p,q sunt primi distincți, p<q. "
                 f"Până la {limit}, găsim {len(cubes)} cuburi de prime și {len(pairs)} produse de două prime distincte, "
                 f"fără suprapuneri; total {answer}.")
    for size in range(1,6):
        a=set(range(1,size+1)); b=set(range(1,size+4)); answer=2**size
        a_text="{"+"; ".join(map(str,sorted(a)))+"}"
        b_text="{"+"; ".join(map(str,sorted(b)))+"}"
        counting(32,f"Fie A={a_text} și B={b_text}. Câte mulțimi X satisfac A∪X=B?",answer,
                 f"Toate elementele din B∖A sunt obligatorii în X, niciun element din afara lui B nu este permis, "
                 f"iar fiecare dintre cele {size} elemente din A poate fi ales independent. Sunt 2^{size}={answer} soluții.")
    for total in [23,31,41,53,73]:
        solutions=[(x,y) for x in range(total//3+1) for y in range(total//5+1) if 3*x+5*y==total]
        answer=len(solutions)
        counting(33,f"Câte perechi ordonate (x,y) de întregi nenegativi satisfac 3x+5y={total}? "
                 "Valoarea zero este admisă pentru fiecare necunoscută.",answer,
                 f"Pentru 0≤y≤⌊{total}/5⌋, avem x=({total}−5y)/3. Păstrăm valorile pentru care numărătorul "
                 f"este divizibil cu 3. Perechile sunt {solutions}, deci sunt {answer} soluții.")

    expected={(f"A1.{s}",kind):5 for s,names in NAMES.items() for kind in range(1,len(names)+1)}
    assert Counter((q["catalog"]["section"],q["catalog"]["type"]) for q in questions)==expected
    assert len({q["text"] for q in questions})==len(questions)==315
    for question in questions:
        if question["catalog"]["section"] == "A1.4.1":
            question["explanation"] = induction_explanation(question)
    return questions


def main():
    path=Path(__file__).resolve().parents[1]/"clasa_9"/"clasa_9_u01_l05_rationamente_logice_inductia_matematica_si_probleme_de_numarare.json"
    payload={"title":"Raționamente logice. Inducția matematică și probleme de numărare",
             "description":"Clasa a 9-a · Mulțimi și logică matematică",
             "difficulty":"hard","questions":build_questions()}
    path.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(f"Scrise {len(payload['questions'])} grile: {path.name}")


if __name__=="__main__": main()
