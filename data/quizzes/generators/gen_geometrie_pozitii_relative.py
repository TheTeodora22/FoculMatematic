"""Generează lecția despre puncte coliniare și pozițiile relative ale dreptelor."""
import json
from pathlib import Path
import geometry_factory as g


def build_questions():
    E,F,P=g.exercise,g.figure,g.point
    q=[]
    def add(text,mode,answers,explanation,**data): q.append(E(text,mode,answers,explanation,**data))
    membership_line=F("point_line",label="d",points=[P("A",120,90),P("B",250,90),P("C",350,45)])
    collinear_line=F("point_line",label="d",points=[P("A",100,90),P("B",220,90),P("C",340,90),P("D",300,42)])
    pairs={r:F("line_pair",label=r,relation=r) for r in ("parallel","concurrent","identical")}

    # Punct față de dreaptă și coliniaritate.
    add("Mută punctul M pe dreapta d.","point_on_line",{"membership":"on"},"Un punct aparține dreptei când centrul lui este pe linie.",points=[P("M",180,45)],figures=[F("line",label="d")],line={"a":0,"b":1,"c":-90},draggable=True)
    add("Mută punctul N în exteriorul dreptei d.","point_on_line",{"membership":"off"},"Punctul exterior nu se află pe dreaptă.",points=[P("N",230,90)],figures=[F("line",label="d")],line={"a":0,"b":1,"c":-90},draggable=True)
    for name,value in (("M","on"),("N","off")):
        point_y=90 if value=="on" else 45
        named_figure=F("point_line",label="d",points=[P(name,220,point_y)])
        add(f"Stabilește poziția punctului {name} față de dreapta d.","membership_choice",{"membership":value},"Alegem «aparține» numai dacă centrul punctului se află pe dreaptă.",figures=[named_figure],choice_key="membership",choices=["on","off"])
        add(f"Completează simbolul pentru punctul {name} și dreapta d.","membership_symbol",{"symbol":"∈" if value=="on" else "∉"},"Folosim ∈ pentru apartenență și ∉ pentru neapartenență.",figures=[named_figure],choice_key="symbol",choices=["∈","∉"])
    add("Colorează punctele care aparțin dreptei d.","color_membership",{"selected":"0,1"},"A și B sunt pe dreaptă, C este în exterior.",figures=[membership_line],choice_key="selected",choices=["0","1","2"],labels=["A","B","C"],multi=True)
    add("Repară desenul mutând punctul A pe dreapta d.","repair_membership",{"membership":"on"},"A trebuie mutat până când centrul lui ajunge pe dreaptă.",points=[P("A",160,45)],figures=[F("line",label="d")],line={"a":0,"b":1,"c":-90},draggable=True)
    add("Repară desenul mutând punctul B în exteriorul dreptei d.","repair_membership",{"membership":"off"},"B trebuie scos de pe dreaptă.",points=[P("B",260,90)],figures=[F("line",label="d")],line={"a":0,"b":1,"c":-90},draggable=True)
    add("Adevărat sau fals: punctul C aparține dreptei d.","visual_true_false",{"answer":"false"},"C este desenat deasupra dreptei.",figures=[membership_line],statement="C ∈ d",format_tag="true_false")
    add("Adevărat sau fals: punctele A și B sunt coliniare.","visual_true_false",{"answer":"true"},"Punctele A și B se află pe aceeași dreaptă.",figures=[membership_line],statement="A și B sunt coliniare.",format_tag="true_false")
    add("Mută A, B și C astfel încât să fie coliniare.","place_collinear",{"relation":"collinear"},"Toate cele trei puncte trebuie să se afle pe aceeași dreaptă.",points=[P("A",100,50),P("B",240,105),P("C",370,55)],draggable=True)
    add("Mută A, B și C astfel încât să fie necoliniare.","place_noncollinear",{"relation":"noncollinear"},"Cel puțin un punct trebuie să fie în afara dreptei celorlalte două.",points=[P("A",100,90),P("B",240,90),P("C",370,90)],draggable=True)
    add("Selectează punctul care strică alinierea.","odd_point",{"point":"D"},"A, B și C sunt coliniare; D este exterior.",figures=[F("point_line",points=[P("A",90,90),P("B",190,90),P("C",300,90),P("D",360,45)])],choice_key="point",choices=list("ABCD"))
    add("Găsește punctul necoliniar din al doilea desen.","odd_point",{"point":"P"},"M și N se află pe dreaptă, P este în exterior.",figures=[F("point_line",points=[P("M",100,90),P("N",280,90),P("P",350,130)])],choice_key="point",choices=["M","N","P"])
    add("Mută punctul C pe dreapta determinată de A și B.","move_to_collinear",{"membership":"on"},"A, B și C devin coliniare.",points=[P("C",320,40)],figures=[F("line",label="AB")],line={"a":0,"b":1,"c":-90},draggable=True)
    add("Așază punctul P pe dreapta MN.","move_to_collinear",{"membership":"on"},"P trebuie să ajungă pe dreapta MN.",points=[P("P",300,135)],figures=[F("line",label="MN")],line={"a":0,"b":1,"c":-90},draggable=True)
    for i,(side,text) in enumerate((("same","A și B de aceeași parte a lui C"),("opposite","A și C de părți diferite ale lui B"))):
        add(f"Alege configurația în care {text}.","same_side",{"side":side},"Comparam ordinea punctelor pe dreaptă.",figures=[F("point_line",points=[P("A",100,90),P("B",180,90),P("C",310,90)])],choice_key="side",choices=["same","opposite"])
    add("Alege tripletul de puncte coliniare.","choose_collinear",{"triple":"A,B,C"},"A, B și C se află pe aceeași dreaptă.",figures=[collinear_line],choice_key="triple",choices=["A,B,C","A,C,D","B,C,D"])
    add("Alege al doilea triplet coliniar.","choose_collinear",{"triple":"M,N,P"},"M, N și P aparțin aceleiași drepte.",figures=[F("point_line",points=[P("M",90,90),P("N",220,90),P("P",350,90),P("R",250,40)])],choice_key="triple",choices=["M,N,R","M,N,P","N,P,R"])
    add("Selectează toate tripletele coliniare.","select_collinear",{"selected":"0,2"},"A, B, C sunt pe prima dreaptă, iar M, N, P sunt pe a doua.",figures=[F("two_point_lines",points=[P("A",90,55),P("B",210,55),P("C",340,55),P("M",80,115),P("N",220,115),P("P",360,115),P("D",285,148)])],choice_key="selected",choices=["0","1","2","3"],multi=True,labels=["A, B, C","A, C, D","M, N, P","B, D, P"])

    # Axioma dreptei și construcții cu rigla.
    tool=lambda **answers:{"answers":answers,"tool_limits":{"angle":[0,175,5],"x":[40,360,10],"y":[30,150,10]}}
    add("Poziționează rigla prin punctele A și B, apoi trasează dreapta.","ruler_line",{"ruler_angle":0,"ruler_x":220,"ruler_y":90,"line_angle":0},"Marginea riglei trebuie să treacă prin ambele puncte.",points=[P("A",100,90),P("B",340,90)],tool_limits=tool()["tool_limits"],show_ruler=True)
    add("Trasează cu rigla dreapta oblică MN.","ruler_line",{"ruler_angle":25,"ruler_x":220,"ruler_y":90,"line_angle":25},"Rotim rigla până când trece prin M și N.",points=[P("M",110,140),P("N",330,40)],tool_limits=tool()["tool_limits"],show_ruler=True)
    add("Așază rigla exact peste punctele A și B.","position_ruler",{"ruler_angle":0,"ruler_x":220,"ruler_y":90},"Rigla este aliniată când ambele puncte ating aceeași margine.",points=[P("A",100,90),P("B",340,90)],tool_limits=tool()["tool_limits"],show_ruler=True)
    add("Rotește rigla la 45° prin punctul O.","position_ruler",{"ruler_angle":45,"ruler_x":220,"ruler_y":90},"Centrul riglei rămâne în O și unghiul devine 45°.",points=[P("O",220,90)],tool_limits=tool()["tool_limits"],show_ruler=True)
    add("Câte drepte distincte sunt desenate prin punctul O?","many_lines_point",{"count":3},"Prin punctul O sunt desenate trei drepte distincte.",figures=[F("spokes",count=3)],choice_key="count",choices=[1,2,3,4])
    add("Câte drepte distincte trec prin două puncte distincte A și B?","unique_line",{"count":1},"Două puncte distincte determină o dreaptă și numai una.",figures=[F("point_line",points=[P("A",120,90),P("B",320,90)])],choice_key="count",choices=[0,1,2,"infinit"])
    add("Câte drepte pot trece prin două puncte coincidente?","coincident_lines",{"count":"infinit"},"Două puncte coincidente se comportă ca un singur punct.",figures=[F("spokes",count=5)],choice_key="count",choices=[0,1,5,"infinit"])
    add("Alege desenul care respectă axioma dreptei.","choose_figure",{"figure":1},"Prin două puncte distincte trece o singură dreaptă.",figures=[F("spokes",count=3),F("point_line",points=[P("A",120,90),P("B",320,90)]),F("parallel")])
    add("Completează axioma dreptei.","axiom_fill",{"first":"două","second":"distincte","third":"una"},"Două puncte distincte determină o dreaptă și numai una.",fields=["first","second","third"])

    # Poziții relative ale dreptelor.
    for relation,label in (("parallel","paralele"),("concurrent","concurente"),("identical","identice")):
        add(f"Identifică dreptele {label}.","line_relation",{"relation":relation},"Analizăm numărul punctelor comune.",figures=[pairs[relation]],choice_key="relation",choices=["parallel","concurrent","identical"])
    add("Selectează punctul de intersecție al dreptelor a și b.","intersection_point",{"point":"O"},"Dreptele concurente au un singur punct comun.",figures=[F("line_pair",relation="concurrent",points=[P("O",220,80)])],choice_key="point",choices=["A","O","B"])
    add("Care este punctul comun al dreptelor CD și EF?","intersection_point",{"point":"P"},"P este centrul intersecției.",figures=[F("line_pair",relation="concurrent",points=[P("C",100,115),P("D",340,45),P("E",100,45),P("F",340,115),P("P",220,80)])],choice_key="point",choices=["C","D","P","F"])
    add("Rotește dreapta b până devine concurentă cu a.","make_concurrent",{"relation":"concurrent"},"Dreptele trebuie să aibă exact un punct comun.",figures=[pairs["parallel"]],choice_key="relation",choices=["parallel","concurrent","identical"])
    add("Transformă două drepte paralele în drepte concurente.","make_concurrent",{"relation":"concurrent"},"Rotirea uneia dintre drepte creează un punct de intersecție.",figures=[pairs["parallel"]],choice_key="relation",choices=["parallel","concurrent"])
    add("Deplasează dreapta b până devine paralelă cu a.","make_parallel",{"relation":"parallel"},"Dreptele au aceeași direcție și nu coincid.",figures=[pairs["concurrent"]],choice_key="relation",choices=["parallel","concurrent","identical"])
    add("Transformă configurația în două drepte paralele distincte.","make_parallel",{"relation":"parallel"},"Păstrăm direcția și schimbăm poziția.",figures=[pairs["identical"]],choice_key="relation",choices=["parallel","identical"])
    add("Suprapune dreptele a și b.","make_identical",{"relation":"identical"},"Dreptele identice au toate punctele comune.",figures=[pairs["parallel"]],choice_key="relation",choices=["parallel","concurrent","identical"])
    relation_names={"parallel":"paralele","concurrent":"concurente","identical":"identice"}
    for target,start in (("parallel","concurrent"),("concurrent","parallel")):
        add(f"Transformă dreptele {relation_names[start]} în drepte {relation_names[target]}.","transform_relation",{"relation":target},"Schimbăm poziția sau direcția uneia dintre drepte.",figures=[pairs[start]])
    add("Repară configurația astfel încât dreptele să fie paralele.","repair_relation",{"relation":"parallel"},"Dreptele paralele au aceeași direcție și niciun punct comun.",figures=[pairs["concurrent"]],choice_key="relation",choices=["parallel","concurrent","identical"])
    add("Asociază relația cu notația corectă.","match_relation_notation",{"match:0":"a∥b","match:1":"a∩b={O}","match:2":"a=b"},"Fiecare poziție are o notație specifică.",figures=list(pairs.values()),relations=["parallel","concurrent","identical"],notations=["a∥b","a∩b={O}","a=b"])
    add("Completează simbolul dintre dreptele a și b.","complete_relation",{"symbol":"∥"},"Dreptele din desen sunt paralele.",figures=[pairs["parallel"]],choice_key="symbol",choices=["∥","=","∩"])
    add("Completează notația dreptelor identice.","complete_relation",{"symbol":"="},"Dreptele coincidente se notează a = b.",figures=[pairs["identical"]],choice_key="symbol",choices=["∥","=","∈"])
    add("Selectează toate perechile de drepte concurente.","select_concurrent_pairs",{"selected":"0,2"},"Perechile selectate au câte un punct comun.",figures=[pairs["concurrent"],pairs["parallel"],pairs["concurrent"]],choice_key="selected",choices=["0","1","2"],multi=True)
    add("Selectează toate perechile de drepte paralele.","select_parallel_pairs",{"selected":"1,3"},"Perechile selectate nu au puncte comune.",figures=[pairs["concurrent"],pairs["parallel"],pairs["identical"],pairs["parallel"]],choice_key="selected",choices=["0","1","2","3"],multi=True)
    add("Grupează relațiile în identice, concurente și paralele.","sort_relations",{"match:0":"parallel","match:1":"concurrent","match:2":"identical"},"Clasificăm după numărul punctelor comune.",figures=[pairs["parallel"],pairs["concurrent"],pairs["identical"]],labels=["parallel","concurrent","identical"])

    # Riglă și echer SVG.
    limits={"angle":[0,175,5],"x":[40,360,10],"y":[30,150,10]}
    tool_cases=[
        ("ruler_set_square_parallel","Construiește o paralelă la d folosind rigla și echerul.",{"ruler_angle":0,"ruler_x":220,"ruler_y":120,"square_angle":0,"square_x":220,"square_y":70,"line_angle":0}),
        ("ruler_set_square_parallel","Construiește paralela oblică folosind ambele instrumente.",{"ruler_angle":30,"ruler_x":220,"ruler_y":120,"square_angle":30,"square_x":220,"square_y":65,"line_angle":30}),
        ("place_set_square","Așază echerul cu o latură pe dreapta d.",{"square_angle":0,"square_x":220,"square_y":90}),
        ("place_set_square","Rotește echerul la 45° pe dreapta dată.",{"square_angle":45,"square_x":220,"square_y":90}),
        ("slide_set_square","Glisează echerul până la punctul O fără să-l rotești.",{"square_angle":0,"square_x":300,"square_y":60}),
        ("slide_set_square","Glisează echerul oblic până la punctul P.",{"square_angle":25,"square_x":300,"square_y":55}),
        ("parallel_through_point","Trasează prin O paralela la d.",{"ruler_angle":0,"ruler_x":220,"ruler_y":120,"square_angle":0,"square_x":280,"square_y":60,"line_angle":0,"through":"O"}),
        ("parallel_through_point","Trasează prin P paralela oblică la a.",{"ruler_angle":30,"ruler_x":220,"ruler_y":125,"square_angle":30,"square_x":290,"square_y":60,"line_angle":30,"through":"P"}),
        ("continue_construction","Continuă construcția începută și trasează paralela.",{"square_angle":0,"square_x":280,"square_y":60,"line_angle":0}),
        ("repair_tools","Corectează poziția instrumentelor pentru o paralelă.",{"ruler_angle":0,"ruler_x":220,"ruler_y":120,"square_angle":0,"square_x":280,"square_y":60}),
        ("draw_concurrent","Trasează două drepte concurente în O.",{"line_angle":45,"through":"O"}),
        ("draw_concurrent","Trasează o dreaptă care intersectează d în P.",{"line_angle":90,"through":"P"}),
        ("draw_parallel","Trasează o dreaptă paralelă cu d.",{"line_angle":0,"through":"free"}),
        ("draw_parallel","Trasează o paralelă la dreapta oblică a.",{"line_angle":30,"through":"free"}),
        ("draw_identical","Trasează o dreaptă identică cu d.",{"line_angle":0,"through":"A"}),
    ]
    for mode,text,answers in tool_cases:
        base_angle=0 if mode=="draw_concurrent" else answers.get("line_angle",answers.get("square_angle",0))
        add(text,mode,answers,"Poziția și unghiul instrumentelor sunt verificate geometric.",points=[P(answers.get("through","O"),280,60)] if answers.get("through") not in (None,"free") else [],figures=[F("line",label="d",angle=base_angle)],tool_limits=limits,show_ruler=mode not in {"place_set_square","slide_set_square","draw_concurrent","draw_parallel","draw_identical"},show_square=mode not in {"draw_concurrent","draw_parallel","draw_identical"})
    steps=["așază echerul pe dreapta dată","fixează rigla lângă echer","glisează echerul până la punct","trasează paralela"]
    for i in range(2): add(f"Ordonează etapele construcției cu rigla și echerul – setul {i+1}.","order_tool_steps",{f"position:{j}":j for j in range(4)},"Ordinea păstrează direcția echerului în timpul glisării.",steps=steps,display_order=[2,0,3,1],figures=[F("line")])

    # Configurații, numărare și explorare.
    for n,result in ((5,10),(8,28)):
        add(f"Câte drepte determină maxim {n} puncte, oricare trei necoliniare?","line_count",{"count":result},f"Numărăm perechile: {n}·{n-1}:2 = {result}.",figures=[F("points",count=n)],choice_key="count",choices=[result,n,result-1,result+1])
    add("Unește fiecare pereche de puncte o singură dată.","line_counter",{"edges":"AB,AC,AD,BC,BD,CD"},"Patru puncte fără trei coliniare determină 6 drepte.",points=[P("A",100,45),P("B",330,45),P("C",100,140),P("D",330,140)])
    add("Aranjează 6 puncte pentru a obține numărul minim de drepte.","min_lines",{"arrangement":"all_collinear","count":1},"Toate punctele pe aceeași dreaptă determină o singură dreaptă.",points=[P("A",70,45),P("B",150,125),P("C",230,55),P("D",310,135),P("E",380,50),P("F",390,145)],draggable=True)
    add("Aranjează 6 puncte pentru numărul maxim de drepte.","max_lines",{"arrangement":"no_three_collinear","count":15},"Nici trei puncte nu trebuie să fie coliniare.",points=[P("A",60,90),P("B",125,90),P("C",190,90),P("D",255,90),P("E",320,90),P("F",385,90)],draggable=True)
    for count,arrangement in ((1,"all_collinear"),(4,"three_collinear"),(6,"no_three_collinear")):
        start=[P("A",80,55),P("B",190,115),P("C",300,50),P("D",370,135)]
        add(f"Aranjează patru puncte astfel încât să determine {count} {'dreaptă' if count==1 else 'drepte'}.","arrange_line_count",{"arrangement":arrangement},"Poziția punctelor schimbă numărul dreptelor distincte.",points=start,draggable=True)
    three_cases=[F("three_lines",case="all_parallel"),F("three_lines",case="all_concurrent"),F("three_lines",case="pairwise"),F("three_lines",case="two_parallel_one_secant")]
    add("Alege desenul cu trei drepte care au un singur punct de intersecție.","choose_figure",{"figure":1},"Cele trei drepte sunt concurente în același punct.",figures=three_cases[:3])
    add("Alege desenul cu trei puncte distincte de intersecție.","choose_figure",{"figure":2},"Fiecare pereche de drepte se intersectează într-un alt punct.",figures=three_cases[:3])
    add("Alege desenul în care cele trei drepte nu au puncte comune.","choose_figure",{"figure":0},"Cele trei drepte sunt paralele distincte.",figures=three_cases[:3])
    add("Alege desenul cu două drepte paralele și o secantă.","choose_figure",{"figure":1},"Secanta intersectează ambele drepte paralele.",figures=[three_cases[0],three_cases[3],three_cases[2]])
    add("Reconstituie configurația cu trei puncte coliniare și unul exterior.","reconstruct_model",{"A":"100,90","B":"220,90","C":"340,90","D":"280,45"},"A, B și C sunt pe aceeași dreaptă, D este exterior.",points=[P("A",100,90),P("B",220,90),P("C",340,90),P("D",280,45)],draggable=True)
    add("Rezolvă puzzle-ul complet: punct O exterior și paralelă prin O.","full_geometry_puzzle",{"O":"300,50","A":"120,90","tool":"line","notation":"a∥d"},"Plasăm O, folosim instrumentele și notăm relația.",points=[P("O",300,50),P("A",120,90)],figures=[F("line",label="d")],tools=["line","ray","segment"],draggable=True)
    add("Rezolvă puzzle-ul complet cu două drepte concurente în P.","full_geometry_puzzle",{"P":"220,90","A":"100,140","tool":"line","notation":"a∩b={P}"},"P este punctul comun al celor două drepte.",points=[P("P",220,90),P("A",100,140)],figures=[F("line_pair",relation="concurrent")],tools=["line","ray","segment"],draggable=True)

    assert 65 <= len(q) <= 90, len(q)
    assert len({item["text"] for item in q})==len(q)
    return q


def main():
    output=Path(__file__).resolve().parent.parent/"clasa_5_geometrie_pozitii_relative_punct_dreapta.json"
    payload={"title":"Pozițiile relative ale unui punct față de o dreaptă. Puncte coliniare. Pozițiile relative a două drepte: drepte concurente, drepte paralele","description":"Clasa a 5-a · Elemente de geometrie și unități de măsură","difficulty":"easy","questions":build_questions()}
    output.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(f"Scrise {len(payload['questions'])} exercitii in {output.name}")


if __name__=="__main__": main()
