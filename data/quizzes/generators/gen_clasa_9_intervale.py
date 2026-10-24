"""80 de grile originale pentru A1 §1.6, toate cele 21 de tipuri."""
from fractions import Fraction as F
from catalog_grid_utils import GridBank


TYPE_NAMES = [
    "Apartenență la interval", "Traducerea intervalului în inegalități", "Reuniuni de intervale",
    "Intersecții de intervale", "Întregi într-un interval", "Reconstrucție din reuniune",
    "Reconstrucție din intersecție", "Diferență de intervale", "Complement relativ",
    "Legile lui De Morgan pe intervale", "Operații cu parametru", "Capete date de medii",
    "Familii de intervale indexate", "Un singur natural în interval", "Comparații cu inverse pozitive",
    "Operații inverse combinate", "Capete cu puteri", "Capete raționale cu parametru",
    "Mulțimi definite prin module", "Intervale reconstruite din egalități algebrice",
    "Cardinal prescris pentru intersecția cu Z",
]


def build_interval_questions():
    bank=GridBank("A1.1.6",TYPE_NAMES)
    add,num=bank.add,bank.numeric

    for interval,correct,wrong,proof in [
        ("(−5; 5)","0",["−5","5","6"],"0 este strict între −5 și 5. Ambele capete sunt excluse."),
        ("[−2; 3)","−2",["3","−3","4"],"Capătul −2 este inclus, iar capătul 3 este exclus."),
        ("(1; 4]","4",["1","0","5"],"Capătul 4 este inclus. 1 este exclus, iar 0 și 5 sunt în afara intervalului."),
        ("(−∞; 2)","−3",["2","3","4"],"Intervalul conține exact numerele strict mai mici decât 2."),
    ]:
        add(1,f"Care dintre numerele de mai jos aparține intervalului {interval}?",correct,wrong,proof)

    for interval,correct,wrong,proof in [
        ("[−2; 3)","−2≤x<3",["−2<x≤3","−2<x<3","−2≤x≤3"],"Paranteza pătrată include −2, iar cea rotundă exclude 3."),
        ("(−1; 4]","−1<x≤4",["−1≤x<4","−1<x<4","−1≤x≤4"],"Capătul −1 este exclus și capătul 4 este inclus."),
        ("(−∞; 5]","x≤5",["x<5","x≥5","x>5"],"Sunt admise toate numerele cel mult egale cu 5."),
        ("[2; +∞)","x≥2",["x>2","x≤2","x<2"],"Sunt admise toate numerele mai mari sau egale cu 2."),
    ]:
        add(2,f"Scrieți condiția x∈{interval} prin inegalități.",correct,wrong,proof)

    rows=[
        ("[−2; 3] ∪ (1; 5)","[−2; 5)",["(−2; 5)","[−2; 5]","(1; 3]"],"Intervalele se suprapun. −2 este inclus, iar 5 nu aparține niciunuia."),
        ("(−2; 0) ∪ (0; 3)","(−2; 0) ∪ (0; 3)",["(−2; 3)","[−2; 3]","{0}"],"0 lipsește din ambele intervale, deci reuniunea nu poate fi contopită într-un singur interval."),
        ("[−1; 2) ∪ [2; 4]","[−1; 4]",["[−1; 4)","(−1; 4]","[−1; 2) ∪ (2; 4]"],"Punctul 2 este inclus în al doilea interval. Nu rămâne niciun gol între −1 și 4."),
        ("(−∞; −1] ∪ (−1; +∞)","R",["R∖{−1}","(−∞; −1)","{−1}"],"Primul interval conține și −1; al doilea conține toate numerele mai mari. Împreună acoperă R."),
    ]
    for expr,correct,wrong,proof in rows:
        add(3,f"Determinați reuniunea {expr}.",correct,wrong,proof)

    for expr,correct,wrong,proof in [
        ("[−2; 3] ∩ (1; 5)","(1; 3]",["[1; 3]","(1; 3)","[−2; 5)"],"Punctele comune verifică x>1 și x≤3. 1 este exclus, 3 este inclus."),
        ("[−1; 2] ∩ [2; 4]","{2}",["∅","[−1; 4]","(−1; 4)"],"Singurul punct comun este 2, inclus în ambele intervale."),
        ("(−1; 2) ∩ [2; 4]","∅",["{2}","(−1; 4]","[2; 4]"],"Primul interval cere x<2, iar al doilea x≥2; condițiile sunt incompatibile."),
        ("(−∞; 3] ∩ [−2; +∞)","[−2; 3]",["(−2; 3)","R","∅"],"Trebuie îndeplinite simultan x≤3 și x≥−2."),
    ]:
        add(4,f"Determinați intersecția {expr}.",correct,wrong,proof)

    for interval,answer,proof in [
        ("(−√10; 5/2]",6,"−4<−√10<−3 și 2<5/2<3. Întregii admiși sunt −3,−2,−1,0,1,2, în total 6."),
        ("[−2; 3)",5,"Întregii sunt −2,−1,0,1,2. Capătul 3 este exclus."),
        ("(−1; 1)",1,"Singurul întreg strict între −1 și 1 este 0."),
        ("[1/3; 10/3]",3,"Întregii sunt 1,2,3; nici 0, nici 4 nu se află în interval."),
    ]:
        num(5,f"Câte numere întregi se află în intervalul {interval}?",answer,proof)

    for t in [0,1,2,-1]:
        lo,hi=t-3,t+4
        add(6,f"Știind că x<{t}<y și [x; {t}]∪[{t}; y]=[{lo}; {hi}], determinați perechea (x;y).",
            f"({lo}; {hi})",[f"({lo+1}; {hi})",f"({lo}; {hi-1})",f"({lo+1}; {hi-1})"],
            f"Cele două intervale se ating în {t}. Reuniunea este [x;y], deci compararea extremităților dă x={lo}, y={hi}.")

    for t in [0,1,-2,3]:
        add(7,f"Intervalele [x; {t+4}] și [{t-3}; y] sunt nevide și au intersecția [{t+1}; {t+2}]. Determinați (x;y).",
            f"({t+1}; {t+2})",[f"({t-3}; {t+4})",f"({t+2}; {t+1})",f"({t}; {t+3})"],
            f"Capătul stâng este max(x,{t-3})={t+1}, deci x={t+1}. Capătul drept este min({t+4},y)={t+2}, deci y={t+2}.")

    for expr,correct,wrong,proof in [
        ("[−2; 5]∖(0; 3]","[−2; 0] ∪ (3; 5]",["[−2; 0) ∪ [3; 5]","[−2; 3]","(0; 3]"],"Eliminăm punctele 0<x≤3. Punctul 0 rămâne, iar 3 este eliminat."),
        ("(0; 4)∖[1; 3]","(0; 1) ∪ (3; 4)",["(0; 1] ∪ [3; 4)","[0; 1) ∪ (3; 4]","[1; 3]"],"Punctele 1 și 3 sunt eliminate împreună cu segmentul dintre ele; 0 și 4 erau deja excluse."),
        ("[−1; 2]∖[−1; 2]","∅",["{−1; 2}","[−1; 2]","R"],"Diferența unei mulțimi cu ea însăși este vidă."),
        ("R∖(−1; 1)","(−∞; −1] ∪ [1; +∞)",["(−∞; −1) ∪ (1; +∞)","[−1; 1]","∅"],"Eliminăm exact punctele strict între −1 și 1. Cele două capete rămân."),
    ]:
        add(8,f"Calculați diferența de mulțimi {expr}.",correct,wrong,proof)

    for universe,subset,correct,wrong,proof in [
        ("[−3; 4]","(0; 2]","[−3; 0] ∪ (2; 4]",["(−∞; 0] ∪ (2; +∞)","[−3; 0) ∪ [2; 4]","(0; 2]"],"Din universul [−3,4] eliminăm 0<x≤2; nu includem puncte din afara universului."),
        ("(−2; 5)","[−1; 3)","(−2; −1) ∪ [3; 5)",["(−2; −1] ∪ (3; 5)","[−2; −1) ∪ [3; 5]","[−1; 3)"],"−1 este eliminat, iar 3 rămâne. Capetele universului −2 și 5 rămân excluse."),
        ("[0; 2]","{1}","[0; 1) ∪ (1; 2]",["[0; 2]","(0; 1) ∪ (1; 2)","{0; 2}"],"Eliminăm numai punctul 1; toate celelalte puncte din [0,2] rămân."),
        ("[1; 3]","[1; 3)","{3}",["∅","{1}","[1; 3]"],"Submulțimea eliminată conține toate punctele universului, mai puțin 3."),
    ]:
        add(9,f"În universul U={universe}, calculați complementul relativ U∖A pentru A={subset}.",correct,wrong,proof)

    for a,b,operation,correct,wrong,proof in [
        ("[−2; 2]","[0; 4]","reuniunii A∪B","(−∞; −2) ∪ (4; +∞)",["[−2; 4]","(−∞; 0) ∪ (2; +∞)","(−∞; −2] ∪ [4; +∞)"],"A∪B=[−2,4]. Complementul este C(A)∩C(B), cu −2 și 4 excluse."),
        ("[−2; 2]","[0; 4]","intersecției A∩B","(−∞; 0) ∪ (2; +∞)",["[0; 2]","(−∞; −2) ∪ (4; +∞)","(−∞; 0] ∪ [2; +∞)"],"A∩B=[0,2]. Complementul este C(A)∪C(B), cu 0 și 2 excluse."),
        ("(−∞; 1)","(2; +∞)","reuniunii A∪B","[1; 2]",["(1; 2)","(−∞; 1] ∪ [2; +∞)","∅"],"C(A)=[1,+∞), C(B)=(−∞,2]. Intersecția lor este [1,2]."),
        ("(−∞; 1]","[1; +∞)","intersecției A∩B","(−∞; 1) ∪ (1; +∞)",["R","{1}","∅"],"A∩B={1}, deci complementul este R fără 1, egal cu C(A)∪C(B)."),
    ]:
        add(10,f"Fie A={a}, B={b}. Folosind legile lui De Morgan, determinați complementul în R al {operation}.",correct,wrong,proof)

    for condition,correct,wrong,proof in [
        ("a=0","{0}",["∅","[−1; 1]","{1}"],"I={0} și J=[−1,1], deci intersecția este {0}."),
        ("0<a<1","[0; a]",["[a−1; a]","[0; a+1]","∅"],"a−1<0 și a<a+1, deci I este inclus în J."),
        ("a=1","[0; 1]",["{1}","(0; 1)","[0; 2]"],"I=[0,1], J=[0,2], deci partea comună este [0,1]."),
        ("a>1","[a−1; a]",["[0; a]","[a; a+1]","∅"],"a−1>0. Capătul stâng comun este a−1, iar cel drept este a."),
    ]:
        add(11,f"Fie I=[0;a], J=[a−1;a+1]. Pentru {condition}, calculați I∩J.",correct,wrong,proof)

    for operation,condition,correct,wrong,proof in [
        ("I∩J","a≠b","{G}",["[H; A]","[H; G)","∅"],"Din H<G<A, intervalele se ating doar în capătul comun G, inclus în ambele."),
        ("I∪J","a≠b","[H; A]",["(H; A)","{G}","[H; G) ∪ (G; A]"],"H<G<A, iar G aparține ambelor intervale, deci reuniunea este întregul segment [H,A]."),
        ("I∖J","a≠b","[H; G)",["[H; G]","(G; A]","∅"],"G este inclus în J și se elimină din I; H rămâne."),
        ("I∪J","a=b=2","{2}",["∅","(0; 2)","[0; 2]"],"În cazul egalității, H=G=A=2. Ambele intervale se reduc la {2}."),
    ]:
        add(12,f"Pentru a,b>0, notăm H=2ab/(a+b), G=√(ab), A=(a+b)/2, I=[H;G], J=[G;A]. Dacă {condition}, calculați {operation}.",correct,wrong,proof)

    add(13,"Fie Iₙ=[n/(n+1); (n+2)/(n+1)] pentru n∈N*. Determinați I₂.","[2/3; 4/3]",
        ["[1/2; 3/2]","[2; 4]","(2/3; 4/3)"],"Înlocuim n=2: capetele sunt 2/3 și 4/3, ambele incluse.")
    add(13,"Fie Iₙ=[n/(n+1); (n+2)/(n+1)] pentru n∈N*. Determinați Iₙ∩Z.","{1}",
        ["{0; 1}","{1; 2}","∅"],"0<n/(n+1)<1<(n+2)/(n+1)≤3/2<2. Singurul întreg admis este 1.")
    add(13,"Fie Iₙ=[n/(n+1); (n+2)/(n+1)] pentru n∈N*. Determinați intersecția tuturor intervalelor Iₙ.","{1}",
        ["[1/2; 3/2]","∅","(0; 2)"],"Toate intervalele îl conțin pe 1. Capetele sunt 1±1/(n+1); orice punct diferit de 1 este exclus pentru n suficient de mare.")
    add(13,"Fie Iₙ=[n/(n+1); (n+2)/(n+1)] pentru n∈N*. Determinați reuniunea tuturor intervalelor Iₙ.","[1/2; 3/2]",
        ["(1/2; 3/2)","{1}","[0; 2]"],"Intervalele sunt incluse succesiv unul în altul: Iₙ₊₁⊂Iₙ. Cel mai mare este I₁=[1/2,3/2], deci el este reuniunea.")

    for expr,correct,wrong,proof in [
        ("[a;a+1)∩N={3}","(2; 3]",["[2; 3)","(2; 3)","[2; 3]"],"Intervalul semiînchis de lungime 1 conține exact un întreg. Pentru ca acesta să fie 3, cerem a≤3<a+1, adică 2<a≤3."),
        ("(a;a+1]∩N={3}","[2; 3)",["(2; 3]","(2; 3)","[2; 3]"],"Condiția este a<3≤a+1, adică 2≤a<3."),
        ("[a;a+1]∩N={3}","(2; 3)",["[2; 3]","(2; 3]","[2; 3)"],"Pentru a∈[2,3], punctul 3 este inclus. La a=2 apare și 2, iar la a=3 apare și 4. Excludem ambele capete."),
        ("(a;a²]∩N={3}","∅",["[√3; 2)","[2; 3)","{2}"],"Pentru a-l include pe 3 trebuie a<3≤a². Ca să excludem 2, trebuie a≥2; ca să excludem 4, trebuie a²<4, deci a<2 deoarece a≥0. Contradicție."),
    ]:
        add(14,f"În convenția N={{0,1,2,…}}, determinați mulțimea parametrilor a≥0 pentru care {expr}.",correct,wrong,proof)

    for condition,correct,wrong,proof in [
        ("0<a<b<1","∅",["[a; b]","[1/b; 1/a]","{1}"],"Primul interval este strict sub 1; al doilea este strict deasupra lui 1."),
        ("1<a<b","∅",["[a; b]","[1/b; 1/a]","{1}"],"Primul interval este strict peste 1, iar cel al inverselor strict sub 1."),
        ("0<a<1<b și ab=1","[a; b]",["{1}","∅","(a; b)"],"Din ab=1 rezultă 1/b=a și 1/a=b. Cele două intervale coincid."),
        ("0<a<1<b și ab>1","[a; 1/a]",["[1/b; b]","[a; b]","∅"],"ab>1 implică 1/b<a și 1/a<b. Așadar maximul capetelor stângi este a, iar minimul celor drepte este 1/a; a<1<1/a."),
    ]:
        add(15,f"Dacă {condition}, determinați [a;b]∩[1/b;1/a].",correct,wrong,proof)

    for t in [0,1,-1,3]:
        add(16,f"Intervalul [x;y] verifică [x;y]∖[{t+1};{t+3}]=[{t-2};{t+1})∪({t+3};{t+5}]. Determinați (x;y).",
            f"({t-2}; {t+5})",[f"({t+1}; {t+3})",f"({t-1}; {t+4})",f"({t-2}; {t+4})"],
            f"Diferența conține ambele bucăți exterioare, deci extremitățile intervalului inițial sunt x={t-2} și y={t+5}. Eliminarea segmentului central verifică egalitatea.")

    for condition,operation,correct,wrong,proof in [
        ("0<x<1","intersecția","[−x²; x²]",["[−x; x]","∅","{0}"],"0<x²<x; intervalul cu raza x² este inclus în cel cu raza x."),
        ("x=1","intersecția","[−1; 1]",["{−1; 1}","{0}","(−1; 1)"],"Cele două intervale coincid cu [−1,1]."),
        ("x>1","intersecția","[−x; x]",["[−x²; x²]","∅","{0}"],"0<x<x²; intervalul cu raza x este cel mai mic."),
        ("0<x<1","reuniunea","[−x; x]",["[−x²; x²]","[−x; −x²] ∪ [x²; x]","∅"],"Intervalele sunt concentrice și cel cu raza x îl conține pe cel cu raza x²."),
    ]:
        add(17,f"Pentru {condition}, determinați {operation} intervalelor [−x;x] și [−x²;x²].",correct,wrong,proof)

    add(18,"Pentru x>1, notăm r=(x+1)/(x−1). Determinați [0;r]∩[0;1].","[0; 1]",
        ["[0; r]","∅","{1}"],"x−1>0 și r=1+2/(x−1)>1. Intervalul [0,1] este inclus în [0,r].")
    add(18,"Pentru x<−1, notăm r=(x+1)/(x−1). Determinați [0;r]∩[0;1].","[0; r]",
        ["[0; 1]","∅","{0}"],"Numărătorul și numitorul sunt negative, deci r>0. Din r=1+2/(x−1) și x−1<−2 rezultă r<1; primul interval este inclus în al doilea.")
    add(18,"Pentru 0<x<1, notăm r=(x+1)/(x−1). Determinați [r;0]∩[−1;1].","[−1; 0]",
        ["[r; 0]","[0; 1]","∅"],"Numitorul este negativ. Din r+1=2x/(x−1)<0 rezultă r<−1. Partea comună este [−1,0].")

    for expr,correct,wrong,proof in [
        ("I={x∈R:|x|≤2}, J={x∈R:|x+1|≥3}; calculați I∩J","{2}",["∅","[−2; 2]","{−2; 2}"],"I=[−2,2], iar J=(−∞,−4]∪[2,+∞). Punctul comun este numai 2."),
        ("I={x∈R:|x−1|<2}, J={x∈R:|x|>1}; calculați I∩J","(1; 3)",["[1; 3]","(−1; 3)","(−1; 1)"],"I=(−1,3), iar J=(−∞,−1)∪(1,+∞). Partea comună este (1,3)."),
        ("I={x∈R:|x|≤3}, J={x∈R:|x−1|<1}; calculați I∖J","[−3; 0] ∪ [2; 3]",["[−3; 0) ∪ (2; 3]","(0; 2)","[−3; 3]"],"I=[−3,3], J=(0,2). Eliminarea intervalului deschis păstrează capetele 0 și 2."),
    ]:
        add(19,f"Fie {expr}.",correct,wrong,proof)

    for a,b in [(F(1,4),F(3,4)),(F(5,4),F(7,4)),(F(-3,4),F(-1,4))]:
        left,right=str(a).replace('-','−'),str(b).replace('-','−')
        add(20,f"a≤b și (a−({a}))²+(b−({b}))²=0. Determinați I=[a;b] și intersecția sa cu Z.",
            f"I=[{left}; {right}], I∩Z=∅",
            [f"I=[{left}; {right}], I∩Z={{0}}",f"I=[{left}; {right}], I∩Z={{1}}","I=∅, I∩Z=∅"],
            f"Ambii pătrați trebuie să fie zero, deci a={a} și b={b}. Segmentul se află strict între doi întregi consecutivi, deci nu conține întregi.")

    add(21,"Fie a∈[0;7], I(a)=[a;a+3], J=[0;10]. Pentru ce valori ale lui a mulțimea I(a)∩J∩Z are exact 4 elemente?",
        "a∈{0;1;2;3;4;5;6;7}",["a∈[0;7]∖Z","a∈[0;7]","a=7"],
        "I(a) este inclus în J. Un segment închis de lungime 3 conține 4 întregi dacă a este întreg; altfel conține 3. Rezultă exact cele opt valori întregi din [0,7].")
    add(21,"Fie a∈[0;7], I(a)=(a;a+3), J=[0;10]. Pentru ce valori ale lui a mulțimea I(a)∩J∩Z are exact 3 elemente?",
        "a∈[0;7]∖Z",["a∈{0;1;2;3;4;5;6;7}","a∈[0;7]","Nu există valori."],
        "I(a) este inclus în J. Dacă a este întreg, capetele deschise lasă doar a+1 și a+2. Dacă a nu este întreg, între a și a+3 sunt exact 3 întregi.")
    add(21,"Pentru a≥1, determinați mulțimea valorilor lui a pentru care [0;a]∩[1;10]∩Z are exact 3 elemente.","[3; 4)",
        ["(3; 4]","{3}","[2; 3)"],"Primii trei întregi sunt 1,2,3. Ca să fie incluși și 4 să fie exclus, trebuie 3≤a<4. Pentru a≥10 ar fi incluși zece întregi, deci nu apar alte soluții.")

    return bank.finish({i:4 if i<=17 else 3 for i in range(1,22)})
