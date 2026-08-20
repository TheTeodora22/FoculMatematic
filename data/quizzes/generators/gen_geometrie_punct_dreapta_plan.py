"""Generează prima lecție de geometrie pentru clasa a V-a."""
import json
from pathlib import Path
import geometry_factory as g


def build_questions():
    F, P, E = g.figure, g.point, g.exercise
    standard = g.standard_figures()
    questions = []

    # 1. Multe exerciții de alegere a figurii corecte.
    choose_cases = [
        ("Alege desenul care reprezintă punctul A.", "point", "Un punct este reprezentat printr-un semn mic și o literă mare."),
        ("Alege desenul dreptei AB.", "line", "Dreapta continuă nelimitat în ambele sensuri."),
        ("Alege desenul segmentului AB.", "segment", "Segmentul are două extremități."),
        ("Alege desenul semidreptei AB.", "ray", "A este originea, iar săgeata indică sensul spre B."),
        ("Alege desenul planului α.", "plane", "Planul este sugerat printr-un paralelogram."),
        ("Alege desenul unui semiplan.", "halfplane", "O dreaptă-frontieră separă cele două semiplane."),
        ("Care figură nu are extremități și se prelungește în ambele sensuri?", "line", "Aceasta este dreapta."),
        ("Care figură are exact două capete?", "segment", "Segmentul are două extremități."),
        ("Care figură are o origine și un singur sens?", "ray", "Aceasta este semidreapta."),
        ("Alege figura notată cu o literă grecească.", "plane", "Planurile se notează frecvent cu α, β sau γ."),
        ("Alege figura care poate fi notată AB sau BA fără să se schimbe.", "segment", "Ordinea extremităților nu schimbă segmentul."),
        ("Alege figura pentru care AB și BA au sensuri diferite.", "ray", "Originea semidreptei este prima literă."),
        ("Alege reprezentarea frontierei dintre două semiplane.", "halfplane", "Dreapta colorată sau marcată este frontiera."),
        ("Alege figura determinată de două puncte și cu prelungire nelimitată.", "line", "Două puncte distincte determină o dreaptă."),
        ("Alege porțiunea de dreaptă cuprinsă între A și B.", "segment", "Porțiunea dintre cele două puncte este segmentul AB."),
        ("Alege urma vârfului unui creion pe foaie.", "point", "Modelul geometric este punctul."),
        ("Alege modelul geometric al unei suprafețe plane.", "plane", "Suprafața este sugerată printr-un plan."),
        ("Alege traseul care pornește din A și trece prin B fără să se termine.", "ray", "Este semidreapta AB."),
    ]
    for index, (text, correct, explanation) in enumerate(choose_cases):
        order = [standard[(index + shift) % len(standard)] for shift in range(4)]
        if not any(item["kind"] == correct for item in order):
            order[-1] = next(item for item in standard if item["kind"] == correct)
        answer = next(i for i,item in enumerate(order) if item["kind"] == correct)
        questions.append(E(text, "choose_figure", {"figure": answer}, explanation, figures=order))

    point_sets = [[P("A",110,85),P("B",260,85),P("C",360,55)], [P("M",120,70),P("N",280,110),P("P",380,70)]]
    two = lambda mode, maker: [maker(i, point_sets[i]) for i in range(2)]

    questions += two("construct_figure", lambda i,pts:E(f"Construiește {['dreapta AB','semidreapta MN'][i]}.","construct_figure",{"tool":["line","ray"][i],"first":pts[0]["name"],"second":pts[1]["name"]},"Alegem instrumentul potrivit, apoi punctele în ordinea cerută; desenul apare imediat.",points=pts,tools=["line","segment","ray"]))
    questions += two("place_points", lambda i,pts:E(f"Plasează punctele în locurile marcate – configurația {i+1}.","place_points",{p["name"]:f'{p["x"]},{p["y"]}' for p in pts},"Fiecare punct trebuie așezat pe marcajul cu aceeași literă.",points=pts,draggable=True))
    questions += [
        E("Suprapune punctele A și B pentru a obține A = B.","coincidence",{"relation":"coincident"},"Punctele coincidente ocupă aceeași poziție.",points=[P("A",130,80),P("B",330,80)],draggable=True),
        E("Separă punctele M și N, care sunt inițial suprapuse.","coincidence",{"relation":"distinct"},"Mută unul dintre puncte suficient de departe pentru ca ele să devină distincte.",points=[P("M",220,90),P("N",220,90)],draggable=True),
    ]
    questions += two("complete_notation", lambda i,pts:E(f"Completează notația pentru {['segmentul cu extremitățile A și B','semidreapta cu originea M și punctul N'][i]}.","complete_notation",{"notation":["AB","MN"][i]},"Scriem literele punctelor; la semidreaptă originea este prima.",figures=[F(["segment","ray"][i],label=["AB","MN"][i])]))
    questions += two("identify_figure", lambda i,pts:E(f"Identifică tipul figurilor din cele trei desene – setul {i+1}.","identify_figure",{"kind":["line","halfplane"][i]},"Cele trei desene reprezintă același tip de figură, în poziții sau culori diferite.",figures=([F("line",label="d",angle=-12),F("line",label="a",angle=0),F("line",label="b",angle=18)] if i==0 else [F("halfplane",boundary_label="d"),F("halfplane",boundary_label="a"),F("halfplane",boundary_label="b")]),choices=g.KINDS))
    questions += two("match_figure", lambda i,pts:E(f"Asociază desenele cu denumirile – setul {i+1}.","match_figure",{f"match:{j}":kind for j,kind in enumerate((["point","segment","ray"] if i==0 else ["line","plane","halfplane"]))},"Fiecare desen are o singură denumire corectă.",figures=[F(kind,variant=j,angle=(-10+j*10 if kind in {"line","segment","ray"} else 0)) for j,kind in enumerate((["point","segment","ray"] if i==0 else ["line","plane","halfplane"]))],labels=g.KINDS))
    questions += two("repair_drawing", lambda i,pts:E(f"Repară desenul greșit al {['segmentului','semidreptei'][i]}.","repair_drawing",{"repair":["remove_arrows","keep_one_arrow"][i]},"Segmentul nu are săgeți; semidreapta are una singură.",figures=[F(["line","line"][i],label="AB")],choices=["remove_arrows","keep_one_arrow","add_two_arrows"]))
    questions += two("transform_figure", lambda i,pts:E(f"Trage marcajele potrivite pentru a transforma segmentul AB în {['dreaptă','semidreaptă AB'][i]}.","transform_figure",{"left":["arrow","origine"][i],"right":"arrow"},"Pentru dreaptă punem săgeți în ambele sensuri; pentru semidreaptă păstrăm originea și o singură săgeată.",figures=[F("segment",label="AB")],choices=["cap","origine","arrow"]))
    questions += two("choose_origin", lambda i,pts:E(f"Alege originea semidreptei {['AB','MN'][i]}.","choose_origin",{"origin":["A","M"][i]},"Prima literă este originea semidreptei.",figures=[F("ray",label=["AB","MN"][i])],choices=[p["name"] for p in pts[:2]]))
    questions += two("reverse_ray", lambda i,pts:E(f"Schimbă sensul semidreptei {['AB','MN'][i]}.","reverse_ray",{"notation":["BA","NM"][i]},"Inversăm ordinea literelor și mutăm originea.",figures=[F("ray",label=["AB","MN"][i])]))
    questions += two("label_endpoints", lambda i,pts:E(f"Așază etichetele la extremitățile segmentului {['AB','MN'][i]}.","label_endpoints",{"left":pts[0]["name"],"right":pts[1]["name"]},"Etichetele se așază la cele două capete.",figures=[F("segment")],labels=[p["name"] for p in pts[:2]]))
    questions += two("complete_markers", lambda i,pts:E(f"Completează marcajele pentru a obține {['segment','semidreaptă'][i]}.","complete_markers",{"left":["cap","origine"][i],"right":["cap","arrow"][i]},"Alegem capetele sau săgeata potrivită.",figures=[F("plain_line")],choices=["cap","origine","arrow"]))
    questions += two("point_membership", lambda i,pts:E(f"Stabilește poziția punctului {['C','P'][i]} față de dreapta d.","point_membership",{"membership":["on","off"][i]},"Punctul este pe dreaptă numai dacă centrul său se află pe linie.",figures=[F("line",label="d",points=[P(["C","P"][i],280,[80,38][i])])],choices=["on","off"]))
    questions += two("select_figures", lambda i,pts:E(f"Selectează toate {['segmentele','semidreptele'][i]} din desen.","select_figures",{"selected":["0,2","1,3"][i]},"Selectăm numai figurile de tipul cerut.",figures=[F("segment",label="AB"),F("ray",label="CD"),F("segment",label="MN"),F("ray",label="PQ")]))
    questions += two("enumerate_segments", lambda i,pts:E(f"Enumeră toate segmentele determinate de punctele {['A, B, C, D','M, N, P'][i]}.","enumerate_segments",{"segments":["AB,AC,AD,BC,BD,CD","MN,MP,NP"][i]},"Din n puncte distincte obținem câte un segment pentru fiecare pereche.",points=([P(x,90+j*100,85) for j,x in enumerate("ABCD")] if i==0 else [P(x,120+j*130,85) for j,x in enumerate("MNP")]),figures=[F("line")]))
    questions += two("containing_segments", lambda i,pts:E(f"Selectează segmentele care conțin punctul {['B','N'][i]}.","containing_segments",{"segments":["AB,AC,AD,BC,BD","MN,MP,NP"][i]},"Un segment conține și punctele interioare dintre extremități.",points=([P(x,90+j*100,85) for j,x in enumerate("ABCD")] if i==0 else [P(x,120+j*130,85) for j,x in enumerate("MNP")]),figures=[F("line")]))
    questions += [E("Mută A, B și C astfel încât să fie necoliniare.","place_noncollinear",{"relation":"noncollinear"},"Cele trei puncte nu trebuie să aparțină aceleiași drepte.",points=[P("A",120,85),P("B",270,85),P("C",360,85)],draggable=True),E("Mută M, N și P astfel încât să fie necoliniare.","place_noncollinear",{"relation":"noncollinear"},"Unul dintre puncte trebuie scos vizibil de pe direcția celorlalte două.",points=[P("M",100,70),P("N",260,70),P("P",380,70)],draggable=True)]
    questions += [E("Mută A, B și C astfel încât să fie aproximativ pe aceeași dreaptă și să rămână distincte.","place_collinear",{"relation":"collinear"},"Centrele punctelor pot avea o mică abatere față de linia ideală.",points=[P("A",100,50),P("B",260,100),P("C",390,50)],draggable=True),E("Așază trei puncte distincte aproximativ pe aceeași dreaptă.","place_collinear",{"relation":"collinear"},"Exercițiul acceptă o mică marjă de poziționare.",points=[P("A",120,45),P("B",250,110),P("C",380,55)],draggable=True)]
    questions += two("build_triangle", lambda i,pts:E(f"Construiește triunghiul {['ABC','MNP'][i]} unind punctele.","build_triangle",{"edges":["AB,AC,BC","MN,MP,NP"][i]},"Un triunghi are trei laturi care unesc cele trei puncte necoliniare.",points=pts,tools=["segment"]))
    plane_sets=[[P("A",35,35),P("B",405,150)],[P("M",35,145),P("N",405,35)]]
    questions += two("plane_points", lambda i,pts:E(f"Trage punctul {['A','M'][i]} în planul α și punctul {['B','N'][i]} în afara planului.","plane_points",{"inside":["A","M"][i],"outside":["B","N"][i]},"Punctele sunt mutate direct pe desen: unul în paralelogram, celălalt în exterior.",points=plane_sets[i],figures=[F("plane",label="α")],draggable=True))
    questions += two("split_plane", lambda i,pts:E(f"Împarte planul în două semiplane cu o frontieră {['orizontală','oblică'][i]}.","split_plane",{"boundary":["horizontal","diagonal"][i]},"O dreaptă împarte planul în două semiplane.",figures=[F("plane",label="α")],choices=["horizontal","vertical","diagonal"]))
    questions += two("choose_halfplane", lambda i,pts:E(f"Colorează semiplanul {['deasupra','dedesubtul'][i]} dreptei d.","choose_halfplane",{"side":["upper","lower"][i]},"Alegem partea indicată a frontierei.",figures=[F("halfplane",label="d")],choices=["upper","lower"]))
    questions += two("move_boundary", lambda i,pts:E(f"Mută frontiera în poziția {['orizontală','verticală'][i]}.","move_boundary",{"boundary":["horizontal","vertical"][i]},"Frontiera rămâne o dreaptă și separă planul.",figures=[F("halfplane")],choices=["horizontal","vertical","diagonal"],initial_boundary=["diagonal","horizontal"][i]))
    questions += [E("Adevărat sau fals: dreapta are două extremități.","visual_true_false",{"answer":"false"},"Dreapta nu are extremități.",figures=[F("line")],format_tag="true_false",statement="Dreapta are două extremități."),E("Adevărat sau fals: segmentul AB este același cu segmentul BA.","visual_true_false",{"answer":"true"},"Ordinea extremităților nu schimbă segmentul.",figures=[F("segment",label="AB")],format_tag="true_false",statement="AB și BA reprezintă același segment.")]
    questions += two("notation_detective", lambda i,pts:E(f"Găsește notația greșită – setul {i+1}.","notation_detective",{"error":[1,2][i]},"Semidreapta ține cont de origine; planul se notează cu literă grecească.",notations=(["segment AB = BA","semidreapta AB = BA","dreapta AB = BA"] if i==0 else ["punct A","plan α","plan AB"])))
    questions += two("match_notation", lambda i,pts:E(f"Potrivește desenele cu notațiile – setul {i+1}.","match_notation",{f"match:{j}":notation for j,notation in enumerate((["A","AB","CD"] if i==0 else ["d","α","ρ"]))},"Folosim convenția de notare corespunzătoare fiecărei figuri.",figures=([F("point"),F("segment"),F("ray")] if i==0 else [F("line"),F("plane"),F("halfplane")]),notations=(["A","AB","CD"] if i==0 else ["d","α","ρ"])))
    questions += two("construction_checker", lambda i,pts:E((["Mută A pe dreapta d, B în afara ei și construiește segmentul AB.","Mută M în originea semidreptei, N pe semidreaptă și construiește semidreapta MN."][i]),"construction_checker",{"tool":["segment","ray"][i]},"Mută punctele în pozițiile cerute și alege figura pe care o construiești.",points=([P("A",150,45),P("B",300,90)] if i==0 else [P("M",180,45),P("N",300,130)]),figures=[F(["line","ray"][i],label=["d","MN"][i])],tools=[["segment","line"],["ray","segment"]][i],validation=["line_membership","ray_membership"][i]))
    questions += two("reconstruct_model", lambda i,pts:E(f"Reconstituie modelul geometric {i+1}.","reconstruct_model",{p["name"]:f'{p["x"]},{p["y"]}' for p in pts},"Punctele trebuie mutate aproape de marcajele modelului.",points=pts,model=pts,draggable=True))
    questions += two("full_geometry_puzzle", lambda i,pts:E(f"Rezolvă puzzle-ul geometric complet {i+1}.","full_geometry_puzzle",{**{p["name"]:f'{p["x"]},{p["y"]}' for p in pts[:2]},"tool":["segment","ray"][i],"notation":["AB","MN"][i]},"Plasăm punctele, alegem figura și scriem notația.",points=pts[:2],tools=["point","line","segment","ray"],draggable=True))

    assert len(questions) == 76, len(questions)
    assert len({q["text"] for q in questions}) == 76
    return questions


def main():
    output=Path(__file__).resolve().parent.parent/"clasa_5_elemente_de_geometrie_si_unitate_de_masura.json"
    payload={"title":"Punct, dreaptă, plan, semiplan, semidreaptă, segment de dreaptă","description":"Clasa a 5-a · Elemente de geometrie și unități de măsură","difficulty":"easy","questions":build_questions()}
    output.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(f"Scrise {len(payload['questions'])} exerciții în {output.name}")


if __name__=="__main__": main()
