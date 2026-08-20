"""Generează atelierul statistic SVG pentru clasa a V-a."""
import json
from collections import Counter
from pathlib import Path


def stat(text, mode, data, answers, explanation):
    return {"text": text, "type": "statistics_chart", "format": "interactive", "points": 10,
            "explanation": explanation, "interactive": {"mode": mode, **data, "answers": answers}}


def grid(text, correct, wrong, explanation):
    vals=[str(correct),*map(str,wrong)]; order=[1,3,0,2]
    return {"text":text,"type":"multiple_choice","format":"grid","points":10,"explanation":explanation,
            "options":[{"text":vals[i],"is_correct":i==0} for i in order]}


def chart(text, mode, labels, values, max_value, answer, explanation, **extra):
    return stat(text,mode,{"labels":labels,"values":values,"max_value":max_value,"step":extra.pop("step",5),**extra},answer,explanation)


def frequency(text, raw, categories, relative=False):
    counts=Counter(raw); answers={}
    for i,c in enumerate(categories):
        answers[f"frequency:{i}"]=counts[c]
        if relative: answers[f"percent:{i}"]=str(round(100*counts[c]/len(raw),2)).replace(".",",").rstrip("0").rstrip(",")
    return stat(text,"relative_frequency" if relative else "frequency_table",{"raw_values":raw,"categories":categories},answers,
                "Numărăm fiecare apariție; frecvența relativă este frecvența împărțită la total și exprimată procentual.")


def mean(text,dataset):
    total=sum(dataset); average=total/len(dataset)
    answer=str(round(average,2)).replace(".",",").rstrip("0").rstrip(",")
    return stat(text,"mean",{"dataset":dataset,"fields":[{"key":"sum","label":"Suma datelor"},{"key":"count","label":"Numărul datelor"},{"key":"mean","label":"Media"}]},
                {"sum":total,"count":len(dataset),"mean":answer},f"Suma este {total}, sunt {len(dataset)} valori, iar media este {answer}.")


def build_questions():
    q=[]
    bar_sets=[
        (["literatură","matematică","științe","tehnică","altele"],[20,30,10,15,5],35,1,"matematică"),
        (["Andrei","Ștefan","Mădălina","Mihnea","Dana","Cătălin"],[8,10,7,6,8,6],12,1,"Ștefan"),
        (["L","Ma","Mi","J","V","S","D"],[30,20,40,10,30,50,10],60,5,"S"),
        (["nota 5","nota 6","nota 7","nota 8","nota 9","nota 10"],[6,4,2,4,2,2],8,0,"nota 5"),
        (["fotbal","handbal","baschet"],[14,4,7],15,0,"fotbal"),
        (["a V-a","a VI-a","a VII-a","a VIII-a"],[25,20,30,25],35,2,"a VII-a"),
    ]
    for i,(labels,values,mx,idx,name) in enumerate(bar_sets):
        q.append(chart(f"Citește graficul cu bare – setul {i+1}. Apasă categoria cu valoarea cea mai mare.","read_bar",labels,values,mx,{"selected":idx},f"Valoarea maximă aparține categoriei {name}.",step=5))

    build_sets=[
        (["3","4","5","6","8","9","10"],[2,4,6,5,4,3,2],6),
        (["fotbal","handbal","baschet"],[14,4,7],15),
        (["L","Ma","Mi","J","V"],[5,15,20,15,25],25),
        (["A","B","C","D"],[8,12,6,10],12),
        (["ian","feb","mar","apr"],[20,30,25,40],40),
        (["mere","pere","prune","nuci"],[12,8,16,4],16),
    ]
    for i,(labels,values,mx) in enumerate(build_sets):
        q.append(chart(f"Construiește graficul cu bare din tabelul dat – setul {i+1}.","build_bar",labels,values,mx,{f"value:{j}":v for j,v in enumerate(values)},"Reglăm fiecare bară la frecvența din tabel.",step=1))

    for i,(labels,values,mx) in enumerate(build_sets[:4]):
        shown=values.copy(); shown[(i+1)%len(values)]=max(0,shown[(i+1)%len(values)]-2)
        q.append(chart(f"Repară graficul: una dintre bare are înălțimea greșită – setul {i+1}.","repair_bar",labels,values,mx,{f"value:{j}":v for j,v in enumerate(values)},"Graficul reparat trebuie să coincidă cu toate valorile tabelului.",step=1,shown_values=shown))

    line_sets=[
        (["luni","marți","miercuri","joi","vineri"],[5,15,20,15,25],30,4,"vineri"),
        (["L","Ma","Mi","J","V","S","D"],[20,30,10,20,20,40,50],60,6,"D"),
        (["ora 8","ora 10","ora 12","ora 14","ora 16"],[8,12,18,16,10],20,2,"ora 12"),
        (["ian","feb","mar","apr","mai"],[12,18,16,24,20],25,3,"apr"),
        (["1","2","3","4","5"],[4,9,7,13,11],15,3,"4"),
    ]
    for i,(labels,values,mx,idx,name) in enumerate(line_sets):
        q.append(chart(f"Citește graficul cu linii – setul {i+1}. Apasă punctul maxim.","read_line",labels,values,mx,{"selected":idx},f"Punctul maxim este la {name}.",step=5))
    for i,(labels,values,mx,_,_) in enumerate(line_sets[:4]):
        q.append(chart(f"Construiește graficul cu linii – setul {i+1}.","build_line",labels,values,mx,{f"value:{j}":v for j,v in enumerate(values)},"Așezăm fiecare punct la valoarea din tabel; segmentele se desenează automat.",step=1))

    q += [
        frequency("Completează frecvențele sporturilor preferate.",["fotbal"]*7+["handbal"]*4+["baschet"]*5,["fotbal","handbal","baschet"]),
        frequency("Completează tabelul notelor.",[5,6,5,7,8,6,5,9,7,8,5,10],[5,6,7,8,9,10]),
        frequency("Numără mijloacele de transport.",["mers"]*5+["autobuz"]*7+["bicicletă"]*3,["mers","autobuz","bicicletă"]),
        frequency("Completează frecvențele culorilor.",["roșu","albastru","roșu","verde","albastru","roșu","verde","roșu"],["roșu","albastru","verde"]),
        frequency("Completează tabelul numărului de cărți citite.",[1,2,2,3,1,4,2,3,2,1],[1,2,3,4]),
        frequency("Completează tabelul fructelor alese.",["mere","pere","mere","prune","mere","pere","mere","prune","pere"],["mere","pere","prune"]),
        frequency("Completează frecvența zilelor cu temperaturi date.",[18,20,18,22,20,18,24,22,20,18],[18,20,22,24]),
    ]
    q += [
        frequency("Completează frecvențele și procentele sporturilor.",["fotbal"]*14+["handbal"]*4+["baschet"]*7,["fotbal","handbal","baschet"],True),
        frequency("Completează frecvențele relative pentru 20 de elevi.",["A"]*8+["B"]*6+["C"]*4+["D"]*2,["A","B","C","D"],True),
        frequency("Transformă frecvențele culorilor în procente.",["roșu"]*5+["albastru"]*3+["verde"]*2,["roșu","albastru","verde"],True),
        frequency("Completează procentele mijloacelor de transport.",["mers"]*6+["autobuz"]*9+["bicicletă"]*5,["mers","autobuz","bicicletă"],True),
        frequency("Completează frecvențele relative ale notelor.",["5"]*2+["6"]*4+["7"]*6+["8"]*4+["9"]*3+["10"],["5","6","7","8","9","10"],True),
    ]
    q += [
        mean("Calculează media numărului de vizitatori.",[100,150,200,270,250,300,270]),
        mean("Calculează media albumelor vândute.",[5,15,20,15,25]),
        mean("Calculează media notelor.",[8,9,7,10,6,8,9,7]),
        mean("Calculează media temperaturilor.",[18,20,22,19,21]),
        mean("Calculează media intrărilor în parcare.",[30,20,40,10,30,50,10]),
        mean("Calculează media punctajelor.",[8,10,7,6,8,6]),
    ]
    q += [
        grid("Frecvența absolută arată:","numărul de apariții",["media datelor","valoarea maximă","procentul fără total"],"Numărăm de câte ori apare categoria."),
        grid("Un grafic cu linii este potrivit în special pentru:","evoluția în timp",["o singură valoare","desenarea unei figuri","scrierea fracțiilor"],"Punctele unite evidențiază creșterile și scăderile."),
    ]
    assert len(q)==45,len(q)
    assert len({x["text"] for x in q})==45
    return q


def main():
    out=Path(__file__).resolve().parents[1]/"clasa_5_organizarea_datelor_frecventa_grafice.json"
    payload={"title":"Probleme de organizare a datelor. Frecvență. Grafice cu bare. Grafice cu linii. Media unui set de date statistice","description":"Clasa a 5-a · Fracții zecimale","difficulty":"medium","questions":build_questions()}
    out.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(f"Scrise {len(payload['questions'])} exerciții în {out.name}")


if __name__=="__main__": main()
