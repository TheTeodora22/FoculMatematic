"""40 de grile originale după catalogul Burtea IX, A1 §1.4, p. 23–24.

Câte cinci pentru toate cele opt tipuri. Calcule zecimale exacte prin Fraction;
Decimal la precizie mare doar pentru radicalii îndepărtați de pragurile grilei.
"""
from collections import Counter
from decimal import Decimal, localcontext
from fractions import Fraction as F


TYPE_NAMES = [
    "Aproximare zecimală prin lipsă", "Aproximare zecimală prin adaos",
    "Trunchiere de ordin dat", "Rotunjire la o zecimală dată",
    "Comparația procedeelor de aproximare", "Verificarea unei erori declarate",
    "Îmbunătățirea rațională a aproximării", "Iterația mediei pentru radical",
]
LOWER_CASES = [("3.141592",2),("-2.413256",3),("0.00987",3),("-0.00041",4),("12.999",1)]
TRUNC_CASES = [("-6.465248",3),("2.718281",2),("-0.00987",3),("0.99999",2),("-12.3409",2)]
ROUND_CASES = [("4.245982",3),("-2.718281",3),("9.995",2),("-1.245",2),("0.00045",4)]


def decimal_text(coefficient, places):
    sign = "−" if coefficient < 0 else ""
    if not places:
        return sign+str(abs(coefficient))
    whole, frac = divmod(abs(coefficient),10**places)
    return f"{sign}{whole},{frac:0{places}d}"


def given(text):
    return text.replace("-","−").replace(".",",")


def grid_values(x, places):
    scaled = F(x)*10**places
    lower = scaled.numerator // scaled.denominator
    upper = -((-scaled.numerator) // scaled.denominator)
    trunc = int(scaled)
    # La cea mai apropiată valoare; la distanțe egale alegem modulul mai mare.
    magnitude = abs(scaled)
    rounded = (2*magnitude.numerator+magnitude.denominator)//(2*magnitude.denominator)
    if scaled < 0:
        rounded = -rounded
    return lower,upper,trunc,rounded


def build_approximation_questions():
    questions=[]
    occurrences=Counter()

    def add(kind,text,correct,wrong,explanation):
        options=[str(correct),*map(str,wrong)]
        assert len(options)==len(set(options))==4,(kind,options)
        position=len(questions)%4
        options.insert(position,options.pop(0))
        occurrences[kind]+=1
        questions.append({
            "text":text,"type":"multiple_choice","format":"grid","points":10,
            "explanation":explanation,
            "options":[{"text":value,"is_correct":i==position} for i,value in enumerate(options)],
            "catalog":{"section":"A1.1.4","type":kind,"type_name":TYPE_NAMES[kind-1],
                       "variant":occurrences[kind],"origin":"Exercițiu nou după tipologia catalogului Burtea IX"},
        })

    def decimal_question(kind,text,x,n,mode):
        values=grid_values(x,n)
        result=values[mode]
        answer=decimal_text(result,n)
        wrong=[decimal_text(result+offset,n) for offset in (-1,1,2)]
        low,high,trunc,rounded=values
        if mode==0:
            proof=f"{decimal_text(low,n)}≤x<{decimal_text(low+1,n)}. Alegem capătul din stânga: {answer}."
        elif mode==1:
            if low==high:
                proof=f"Numărul aparține deja grilei cu {n} zecimale. Cel mai mic element al grilei care este ≥x este chiar {answer}; eroarea este zero."
            else:
                proof=f"{decimal_text(high-1,n)}<x≤{answer}. Alegem cel mai mic element al grilei care este ≥x, anume {answer}."
        elif mode==2:
            proof=f"Eliminăm cifrele de după a {n}-a zecimală și păstrăm semnul. Trunchierea este spre zero, deci obținem {answer}."
        else:
            proof=f"Pe grila cu {n} zecimale alegem valoarea cea mai apropiată. La distanțe egale alegem modulul mai mare. Rezultatul este {answer}."
        add(kind,text,answer,wrong,proof)

    for raw,n in LOWER_CASES:
        decimal_question(1,f"Aproximați prin lipsă x={given(raw)} la {n} zecimale: alegeți cel mai mare multiplu de 10^(−{n}) care este ≤x.",F(raw),n,0)

    with localcontext() as ctx:
        ctx.prec=60
        r2,r3,r5=Decimal(2).sqrt(),Decimal(3).sqrt(),Decimal(5).sqrt()
        upper_cases=[("√5",F(r5),3),("−√2",F(-r2),2),("−3,141592",F('-3.141592'),3),("0,00481",F('0.00481'),3),("2,5",F('2.5'),1)]
        compare_cases=[("√2=1,414213…",F(r2),2),("−√2=−1,414213…",F(-r2),2),
                       ("φ=(1+√5)/2=1,618033…",F((1+r5)/2),3),
                       ("√3=1,732050…",F(r3),3),("−√5=−2,236067…",F(-r5),2)]

    for label,x,n in upper_cases:
        decimal_question(2,f"Aproximați prin adaos x={label} la {n} zecimale: alegeți cel mai mic multiplu de 10^(−{n}) care este ≥x.",x,n,1)

    for raw,n in TRUNC_CASES:
        decimal_question(3,f"Trunchiați {given(raw)} la {n} zecimale, prin eliminarea cifrelor următoare (spre zero).",F(raw),n,2)

    for raw,n in ROUND_CASES:
        decimal_question(4,f"Rotunjiți {given(raw)} la {n} zecimale. La egalitate de distanțe, alegeți valoarea cu modul mai mare.",F(raw),n,3)

    for label,x,n in compare_cases:
        low,high,trunc,rounded=grid_values(x,n)
        def quartet(values):
            return "("+"; ".join(decimal_text(v,n) for v in values)+")"
        answer=quartet((low,high,trunc,rounded))
        wrong=[quartet((high,low,trunc,rounded)),
               quartet((low,high,high if trunc==low else low,rounded)),
               quartet((low,high,trunc,high if rounded==low else low))]
        add(5,f"Pentru x={label}, care este cvadruplul (aproximare prin lipsă; aproximare prin adaos; trunchiere spre zero; rotunjire la cea mai apropiată valoare), toate la {n} zecimale?",
            answer,wrong,f"Încadrarea pe grilă dă {decimal_text(low,n)}<x<{decimal_text(high,n)}. Trunchierea se face spre zero; rotunjirea ține cont de prima cifră eliminată. Cvadruplul este {answer}.")

    errors=[(F(100),F(10501,105),F(1,100)),(F(7,5),F(99,70),F(1,100)),
            (F(142,100),F(1413,1000),F(1,100)),(F(250,100),F(251,100),F(1,100)),
            (F(-242,100),F(-2413,1000),F(1,100))]
    for a,x,tolerance in errors:
        direction="lipsă" if a<x else "adaos"
        small=abs(a-x)<tolerance
        all_choices=[f"Prin {d}, cu eroare {'strict mai mică decât' if s else 'mai mare sau egală cu'} ε."
                     for d in ("lipsă","adaos") for s in (True,False)]
        answer=f"Prin {direction}, cu eroare {'strict mai mică decât' if small else 'mai mare sau egală cu'} ε."
        add(6,f"Pentru x={x}, a={a} și ε={tolerance}, caracterizați aproximația a după sens și după eroarea absolută |x−a|. O eroare egală cu ε nu este strict sub toleranță.",
            answer,[c for c in all_choices if c!=answer],
            f"Avem a{'<' if a<x else '>'}x, deci aproximarea este prin {direction}. Eroarea exactă este |x−a|={abs(x-a)}, {'<' if small else '≥'} ε={tolerance}.")

    add(7,"Pentru aproximarea lui √2, folosim T(a)=(a+2)/(a+1). Calculați T(3/2).","7/5",
        ["5/7","3/2","3/5"],"T(3/2)=[3/2+2]/[3/2+1]=(7/2)/(5/2)=7/5. Deoarece (7/5)²<2<(3/2)², noua valoare este de cealaltă parte a radicalului.")
    add(7,"Pentru aproximarea lui √3, folosim T(a)=(a+3)/(a+1). Calculați T(2).","5/3",
        ["3/5","3/2","2"],"T(2)=(2+3)/(2+1)=5/3. Eroarea se reduce: pentru r=√3, |T(a)−r|/|a−r|=(r−1)/(a+1)<1 la a=2.")
    add(7,"Fie d>1, r=√d, a>r și T(a)=(a+d)/(a+1). Care identitate exprimă corect eroarea cu semn T(a)−r?",
        "T(a)−r=(1−r)(a−r)/(a+1)",
        ["T(a)−r=(1+r)(a−r)/(a+1)","T(a)−r=(a−r)/(a+1)","T(a)−r=(1−r)(a+r)/(a+1)"],
        "Folosind d=r², numărătorul diferenței este a+r²−r(a+1)=(1−r)(a−r). Împărțim la a+1>0.")
    add(7,"Fie a>√2 și T(a)=(a+2)/(a+1). Care este ordinea strictă a celor trei numere?","T(a)<√2<a",
        ["√2<T(a)<a","a<T(a)<√2","T(a)<a<√2"],
        "T(a)−√2=(1−√2)(a−√2)/(a+1)<0. În plus, raportul erorilor absolute este (√2−1)/(a+1)<1, deci noua aproximație este mai apropiată.")
    add(7,"Fie a=7/5 și T(a)=(a+2)/(a+1)=17/12. Care afirmație despre aproximațiile lui √2 este corectă?",
        "17/12 este prin adaos și are eroare mai mică decât 7/5.",
        ["17/12 este prin lipsă și are eroare mai mică decât 7/5.","17/12 este prin adaos și are eroare mai mare decât 7/5.","Cele două erori sunt egale."],
        "(7/5)²=49/25<2, iar (17/12)²=289/144>2. Raportul erorilor este (√2−1)/(12/5)<1; valoarea 17/12 este deasupra radicalului și mai apropiată.")

    for d,a in [(2,F(2)),(3,F(2))]:
        result=(a+F(d)/a)/2
        add(8,f"Pentru a₀={a} și aₙ₊₁=(aₙ+{d}/aₙ)/2, calculați a₁.",str(result),
            [str(result+F(1,2)),str(result-F(1,2)),str(2*result)],
            f"Înlocuim în recurență: a₁=({a}+{F(d)/a})/2={result}.")
    add(8,"Pentru a₀=2 și aₙ₊₁=(aₙ+2/aₙ)/2, calculați a₂.","17/12",
        ["3/2","7/5","25/12"],"a₁=(2+1)/2=3/2, apoi a₂=(3/2+4/3)/2=(17/6)/2=17/12.")
    add(8,"Fie d>0, a₀>√d și aₙ₊₁=(aₙ+d/aₙ)/2. Care descriere este corectă?",
        "Șirul este strict descrescător, rămâne deasupra lui √d și converge la √d.",
        ["Șirul este strict crescător și converge la √d.","Termenii alternează strict sub și deasupra lui √d.","Șirul este constant pentru orice a₀>√d."],
        "Dacă a>√d, atunci (a+d/a)/2−√d=(a−√d)²/(2a)>0 și (a+d/a)/2−a=(d−a²)/(2a)<0. Șirul este descrescător și mărginit; limita pozitivă L satisface L=(L+d/L)/2, deci L=√d.")
    add(8,"Fie d>0, r=√d, a>0 și b=(a+d/a)/2. Care este identitatea exactă pentru noua eroare b−r?",
        "b−r=(a−r)²/(2a)",
        ["b−r=(a−r)/(2a)","b−r=−(a−r)²/(2a)","b−r=(a+r)²/(2a)"],
        "b−r=(a²+d−2ar)/(2a). Folosind d=r², numărătorul este (a−r)²; eroarea este nenegativă și se anulează numai pentru a=r.")

    assert occurrences=={i:5 for i in range(1,9)}
    assert len(questions)==len({q['text'] for q in questions})==40
    return questions
