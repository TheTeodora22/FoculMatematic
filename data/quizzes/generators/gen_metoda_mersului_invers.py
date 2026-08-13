"""Generează lecția „Metoda mersului invers” pentru clasa a V-a."""
import json
from pathlib import Path
import reverse_factory as r


def grid(text, correct, wrong, explanation):
    values = [str(correct), *map(str, wrong)]
    assert len(values) == 4 and len(set(values)) == 4
    return {"text":text, "format":"grid", "points":10, "explanation":explanation,
            "options":[{"text":value,"is_correct":index == 0} for index,value in enumerate(values)]}


def symbol(operation):
    return f'{operation["op"]}{operation["value"]}'.replace("*", "×").replace("/", ":")


def build_questions():
    questions = [
        grid("Operația inversă înmulțirii cu 5 este:", "împărțirea la 5", ["adunarea cu 5","scăderea cu 5","înmulțirea cu 5"], "Înmulțirea și împărțirea cu același număr se anulează."),
        grid("Operația inversă scăderii lui 9 este:", "adunarea lui 9", ["împărțirea la 9","scăderea lui 9","înmulțirea cu 9"], "Adunăm ceea ce a fost scăzut."),
        grid("Din 11 refacem operația «împărțire la 5». Primul pas invers este:", "11 × 5", ["11 : 5","11 + 5","11 − 5"], "Inversa împărțirii la 5 este înmulțirea cu 5."),
        grid("Ioana obține 11 după ce împarte la 5. Numărul dinaintea împărțirii este:", 55, [6,16,50], "11 × 5 = 55."),
        grid("După ce scădem 5 obținem 50. Numărul anterior este:", 55, [45,10,250], "50 + 5 = 55."),
        grid("După înmulțirea cu 5 obținem 50. Numărul inițial este:", 10, [5,45,250], "50 : 5 = 10."),
        grid("Un număr este împărțit la 8 și se obține 251. Numărul anterior este:", 2008, [243,259,2016], "251 × 8 = 2008."),
        grid("După ce adunăm 5 obținem 256. Valoarea anterioară este:", 251, [261,51,1280], "256 − 5 = 251."),
        grid("O operație dus–întors corectă este:", "×7 urmat de :7", ["+7 urmat de ×7","−7 urmat de :7","×7 urmat de −7"], "Operațiile inverse readuc valoarea inițială."),
        grid("Tudor ia jumătate din 12 bomboane. Câte rămân?", 6, [3,12,24], "12 : 2 = 6."),
        grid("După ce Ioana ia jumătate, rămân 3 bomboane. Înainte erau:", 6, [1,3,9], "Refacem înjumătățirea prin înmulțire cu 2."),
        grid("Într-un tabel al mersului invers, completăm valorile:", "de la rezultat spre început", ["aleatoriu","numai de la stânga","fără operații inverse"], "Pornim de la ultima valoare cunoscută."),
        grid("Pentru verificare, după aflarea numărului inițial:", "refacem drumul direct", ["schimbăm rezultatul final","ștergem operațiile","adunăm toate valorile"], "Drumul direct trebuie să producă rezultatul din enunț."),
        grid("Dacă rezultatul final este 8 și ultima operație a fost împărțirea la 10, mergând invers obținem:", 80, [2,10,18], "8 × 10 = 80."),
        grid("Un lanț invers trebuie să folosească operațiile:", "în ordine inversă apariției", ["în aceeași ordine","în ordine alfabetică","doar înmulțiri"], "Începem cu ultima operație a drumului direct."),
    ]

    cases = [
        ("Ioana", r.chain(10,[r.op("*",5),r.op("+",5),r.op("/",5)]), "Numărul inițial este 10."),
        ("Mara", r.chain(18,[r.op("/",3),r.op("+",7),r.op("*",2)]), "Numărul inițial este 18."),
        ("Radu", r.chain(25,[r.op("-",5),r.op("*",4),r.op("/",10)]), "Numărul inițial este 25."),
    ]

    # 1. Construiește drumul invers.
    for name,c,explanation in cases:
        questions.append(r.exercise(f"Construiește drumul invers pentru lanțul lui {name}.","build_reverse_path",r.values_for_reverse(c),explanation,**c))
    # 2. Trage/alege operațiile inverse.
    for name,c,explanation in cases:
        questions.append(r.exercise(f"Așază operațiile inverse pentru traseul lui {name}.","drag_inverse_ops",r.operations_for_reverse(c),explanation,**c,
                                    operation_pool=[symbol(op) for op in reversed(c["inverse_operations"])]))
    # 3. Întoarce săgețile.
    for name,c,explanation in cases:
        answers={"direction":"reverse",**r.operations_for_reverse(c)}
        questions.append(r.exercise(f"Întoarce săgețile și completează operațiile pentru {name}.","reverse_arrows",answers,explanation,**c))
    # 7. Perechi de operații inverse.
    pairs_sets = [
        [("+5","-5"),("×5",":5"),("+9","-9")],
        [(":3","×3"),("+7","-7"),("×2",":2")],
        [("-5","+5"),("×4",":4"),(":10","×10")],
    ]
    for index,pairs in enumerate(pairs_sets):
        answers={f"pair:{i}":right for i,(_,right) in enumerate(pairs)}
        questions.append(r.exercise(f"Potrivește perechile de operații inverse – setul {index+1}.","pair_inverse",answers,"Fiecare operație este anulată de inversa ei.",pairs=[{"left":a,"right":b} for a,b in pairs],right_order=[1,2,0]))
    # 8. Ordonează pașii invers.
    for name,c,explanation in cases:
        answers={f"position:{i}":i for i in range(len(c["inverse_operations"]))}
        questions.append(r.exercise(f"Ordonează pașii invers pentru {name}.","order_reverse",answers,explanation,**c,
                                    steps=[symbol(op) for op in c["inverse_operations"]],display_order=[2,0,1]))
    # 9. Detectivul drumului greșit.
    for index,(name,c,_) in enumerate(cases):
        shown=[symbol(op) for op in c["inverse_operations"]]; shown[1] = ["+99","×99",":99"][index]
        questions.append(r.exercise(f"Găsește primul pas invers greșit în traseul lui {name}.","reverse_error",{"step":1},"Al doilea cartonaș nu este inversa operației corespunzătoare.",**c,shown_steps=shown))
    # 10. Repară lanțul.
    for name,c,explanation in cases:
        correct=symbol(c["inverse_operations"][1])
        questions.append(r.exercise(f"Repară operația din mijlocul lanțului lui {name}.","repair_chain",{"repair":correct},explanation,**c,
                                    choices=[correct,"+1",":2"]))
    # 11. Mașina timpului.
    for name,c,explanation in cases:
        questions.append(r.exercise(f"Pornește mașina timpului matematică pentru {name}.","time_machine",r.values_for_reverse(c),explanation,**c,icon="⏳"))
    # 16. Cursor pentru numărul inițial.
    for name,c,explanation in cases:
        questions.append(r.exercise(f"Reglează numărul inițial al lui {name} până obții {c['end']}.","start_slider",{"start":c["start"]},explanation,**c,maximum=max(40,c["start"]+10)))
    # 17. Bomboane.
    candy_cases=[(3,[6,12]),(5,[10,20]),(4,[8,16])]
    for final,reverse_values in candy_cases:
        stages=[{"label":"după al doilea copil","value":final},{"label":"înaintea celui de-al doilea","value":reverse_values[0]},{"label":"inițial","value":reverse_values[1]}]
        questions.append(r.exercise(f"După două înjumătățiri rămân {final} bomboane. Reconstituie grămada.","candies",{"stage:1":reverse_values[0],"stage:2":reverse_values[1]},f"Înmulțim de două ori cu 2: inițial erau {reverse_values[1]} bomboane.",stages=stages,icon="🍬"))
    # 18. Vase cu apă.
    water_cases=[(36,[18,27]),(48,[24,36]),(60,[30,45])]
    for final,values in water_cases:
        stages=[{"label":"egal în fiecare vas","value":final},{"label":"o parte","value":values[0]},{"label":"cantitatea inițială din A","value":values[1]}]
        questions.append(r.exercise(f"În două vase rămân câte {final} l. Completează refacerea transferurilor.","water_transfer",{"stage:1":values[0],"stage:2":values[1]},"Refacem pe rând ultimul și apoi primul transfer.",stages=stages,icons=["🛢️","🛢️"]))
    # 23. Tabel cronologic invers.
    table_cases=[("bomboane",[3,6,12]),("nuci",[4,8,16]),("mere",[5,10,20])]
    for label,values in table_cases:
        stages=[{"label":"final", "value":values[0]},{"label":"etapa a doua","value":values[1]},{"label":"inițial","value":values[2]}]
        questions.append(r.exercise(f"Completează tabelul invers pentru problema cu {label}.","reverse_table",{"stage:1":values[1],"stage:2":values[2]},"Tabelul se completează de jos în sus, dublând valorile.",stages=stages,columns=["Moment","Cantitate"]))
    # 25. Alege enunțul potrivit traseului.
    stories=[
        ["Înmulțesc cu 5, adun 5, împart la 5.","Adun 5 de trei ori.","Împart numai la 5."],
        ["Împart la 3, adun 7, înmulțesc cu 2.","Înmulțesc cu 3 și scad 7.","Adun 2 și împart la 7."],
        ["Scad 5, înmulțesc cu 4, împart la 10.","Adun 5 și împart la 4.","Înmulțesc numai cu 10."],
    ]
    for (name,c,explanation),choices in zip(cases,stories):
        questions.append(r.exercise(f"Alege enunțul reprezentat de traseul lui {name}.","choose_story",{"story":0},explanation,**c,stories=choices))
    # 27. Puzzle complet.
    for name,c,explanation in cases:
        answers={**r.operations_for_reverse(c),**r.values_for_reverse(c),"start":c["start"]}
        questions.append(r.exercise(f"Rezolvă puzzle-ul complet al mersului invers pentru {name}.","full_reverse_puzzle",answers,explanation,**c))
    # 28. Verificare dus–întors.
    for name,c,explanation in cases:
        questions.append(r.exercise(f"Verifică traseul dus–întors al lui {name}.","round_trip",{"initial":c["start"],"final":c["end"],"verified":"yes"},explanation,**c))

    assert len(questions) == 60, len(questions)
    assert len({q["text"] for q in questions}) == 60
    return questions


def main():
    output=Path(__file__).resolve().parent.parent/"clasa_5_metoda_mersului_invers.json"
    payload={"title":"Metoda mersului invers","description":"Clasa a 5-a · Metode aritmetice de rezolvare a problemelor","difficulty":"medium","questions":build_questions()}
    output.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(f"Scrise {len(payload['questions'])} exerciții în {output.name}")


if __name__ == "__main__": main()
