"""Generează lecția „Metoda comparației” pentru clasa a V-a."""

import json
from pathlib import Path

import comparison_factory as comparison


def item(count, name, icon):
    return {"count": count, "name": name, "icon": icon}


def row(total, *items):
    return {"items": list(items), "total": total}


def grid(text, correct, wrong, explanation):
    correct, wrong = str(correct), [str(value) for value in wrong]
    assert len(wrong) == 3 and correct not in wrong and len(set(wrong)) == 3
    return {"text": text, "format": "grid", "points": 10, "explanation": explanation, "options": [
        {"text": wrong[0], "is_correct": False}, {"text": correct, "is_correct": True},
        {"text": wrong[1], "is_correct": False}, {"text": wrong[2], "is_correct": False},
    ]}


def build_questions():
    questions = [
        grid("Două caiete și un pix costă 24 lei, iar două caiete și două pixuri costă 40 lei. Cât costă un pix?", "16 lei", ["8 lei", "12 lei", "20 lei"], "Scădem situațiile: un pix costă 40 − 24 = 16 lei."),
        grid("6 coli și 8 carioci costă 58 lei, iar 6 coli și 12 carioci costă 78 lei. Cât costă o cariocă?", "5 lei", ["3 lei", "4 lei", "20 lei"], "Diferența de 4 carioci costă 20 lei, deci o cariocă costă 5 lei."),
        grid("În problema cu 6 coli și 8 carioci, respectiv 6 coli și 12 carioci, termenul comun este:", "6 coli", ["8 carioci", "12 carioci", "58 lei"], "Cele două situații au același număr de coli."),
        grid("2 coli și 7 carioci costă 41 lei, iar 7 coli și 2 carioci costă 31 lei. Ce trebuie făcut mai întâi pentru eliminare prin scădere?", "Egalizăm numărul unuia dintre obiecte", ["Adunăm totalurile direct", "Ignorăm cariocile", "Împărțim ambele totaluri la 2"], "Nu există inițial un termen de comparație egal."),
        grid("7 containere de maculatură cântăresc cât 6 containere de plastic, iar împreună cu încă 5 containere de maculatură cântăresc 720 kg. Cât cântărește un container de maculatură?", "60 kg", ["50 kg", "72 kg", "120 kg"], "Înlocuim cele 6 containere de plastic cu 7 de maculatură și obținem 12 containere = 720 kg."),
        grid("3 pixuri și 3 creioane costă 41 lei, iar 8 pixuri și 6 creioane costă 82 lei. Ce observăm?", "Datele sunt contradictorii", ["Un pix costă 5 lei", "Un creion costă 8 lei", "Ambele obiecte sunt gratuite"], "Dublând prima situație obținem 6 pixuri și 6 creioane = 82 lei, nu 8 pixuri și 6 creioane."),
        grid("3 cărți și 4 caiete costă 62 lei, iar 3 cărți și 6 caiete costă 30 lei. Problema:", "nu are soluție cu prețuri naturale pozitive", ["are soluția carte = 10 lei", "are soluția caiet = 16 lei", "are întotdeauna două soluții"], "Mai multe caiete nu pot produce un total mai mic dacă prețurile sunt pozitive."),
        grid("5 pungi de mălai și 7 pungi de făină cântăresc 31 kg, iar 7 pungi de mălai și 7 de făină cântăresc 35 kg. Cât cântărește o pungă de mălai?", "2 kg", ["1 kg", "4 kg", "7 kg"], "Două pungi de mălai cântăresc 4 kg, deci una cântărește 2 kg."),
        grid("5 trandafiri și 6 garoafe costă 42 lei. Un trandafir costă cât 3 garoafe. Cât costă o garoafă?", "2 lei", ["1 leu", "3 lei", "6 lei"], "Înlocuim 5 trandafiri cu 15 garoafe; 21 de garoafe costă 42 lei."),
        grid("4 băieți și 6 fete confecționează 26 de mărțișoare, iar 5 băieți și 3 fete confecționează 19. Câte confecționează un băiat și o fată împreună?", 5, [3, 7, 9], "Prin egalizare și eliminare se obține băiat = 2, fată = 3, împreună 5."),
        grid("3 robinete și 2 pompe au debitul total 31 hl/oră, iar 3 robinete și 8 pompe au 79 hl/oră. Care este debitul unei pompe?", "8 hl/oră", ["6 hl/oră", "10 hl/oră", "16 hl/oră"], "6 pompe în plus dau 48 hl/oră, deci o pompă are 8 hl/oră."),
        grid("2 cocoși cântăresc cât 3 găini, iar 8 cocoși și 9 găini cântăresc 42 kg. Cât cântărește o găină?", "2 kg", ["1 kg", "3 kg", "4 kg"], "8 cocoși echivalează cu 12 găini; în total sunt echivalentul a 21 găini = 42 kg."),
        grid("Pe o balanță, două cuburi cântăresc cât o piramidă și o bilă. Dacă un cub cântărește cât 11 bile, ce putem face?", "Înlocuim fiecare cub cu 11 bile", ["Eliminăm toate bilele", "Adunăm 11 la total", "Împărțim piramida la cub"], "Folosim echivalența pentru substituție."),
        grid("Ogarul face 7 sărituri în timpul în care vulpea face 8. Pentru o perioadă comună de 5 asemenea intervale, ogarul face:", "35 sărituri", ["13 sărituri", "40 sărituri", "56 sărituri"], "7 · 5 = 35 sărituri."),
        grid("Dacă la 35 de sărituri ale ogarului, vulpea face 40, iar 5 sărituri de ogar măsoară cât 6 de vulpe, avantajul ogarului este echivalent cu:", "6 sărituri de vulpe", ["2 sărituri de vulpe", "5 sărituri de vulpe", "12 sărituri de vulpe"], "35 sărituri de ogar măsoară cât 42 de vulpe; diferența față de 40 este 2 la fiecare perioadă și duce la calculul urmăririi."),
        grid("Patru dansatori și 6 dansatoare execută dansul în 5 minute. În cât timp îl execută 8 dansatori și 12 dansatoare, în aceleași condiții?", "5 minute", ["2 minute", "10 minute", "20 minute"], "Formația s-a dublat în aceeași proporție; fiecare execută același dans în 5 minute."),
        grid("Când înmulțim un rând al comparației cu 3, trebuie să:", "înmulțim cu 3 toate cantitățile și totalul", ["înmulțim doar primul obiect", "păstrăm totalul", "împărțim al doilea obiect"], "Întreaga situație trebuie scalată cu același factor."),
        grid("După eliminarea termenului comun obținem 4 carioci = 20 lei. Pasul următor este:", "20 : 4 = 5 lei pentru o cariocă", ["20 · 4", "20 − 4", "4 : 20"], "Reducem la unitate împărțind totalul la numărul de obiecte."),
        grid("Care verificare este corectă dacă o coală costă 3 lei și o cariocă 5 lei?", "6 · 3 + 8 · 5 = 58", ["6 + 3 + 8 + 5 = 22", "6 · 5 + 8 · 3 = 54", "58 : 3 = 5"], "Înlocuim prețurile în prima situație."),
        grid("Pentru a elimina prin scădere o necunoscută, cele două situații trebuie să aibă:", "același termen de comparație", ["același total", "numai numere pare", "exact două obiecte în total"], "Scădem cantități egale ale aceleiași necunoscute."),
    ]

    r_carioci = [row(58, item(6,"coli","📄"), item(8,"carioci","🖍️")), row(78, item(6,"coli","📄"), item(12,"carioci","🖍️"))]
    r_pixuri = [row(24, item(2,"caiete","📘"), item(1,"pix","🖊️")), row(40, item(2,"caiete","📘"), item(2,"pixuri","🖊️"))]
    r_faina = [row(31, item(5,"mălai","🌽"), item(7,"făină","🌾")), row(35, item(7,"mălai","🌽"), item(7,"făină","🌾"))]

    # 1, 2, 3: balanță, eliminare și aliniere.
    for n, rows, answers, explanation in [
        ("coli și carioci", r_carioci, {"diferență_obiecte":4,"diferență_total":20,"preț_unitar":5}, "Eliminăm cele 6 coli; 4 carioci costă 20 lei."),
        ("caiete și pixuri", r_pixuri, {"diferență_obiecte":1,"diferență_total":16,"preț_unitar":16}, "Eliminăm cele 2 caiete; un pix costă 16 lei."),
        ("mălai și făină", r_faina, {"diferență_obiecte":2,"diferență_total":4,"preț_unitar":2}, "Eliminăm cele 7 pungi de făină; 2 pungi de mălai cântăresc 4 kg."),
    ]: questions.append(comparison.two_rows(f"Folosește balanța pentru comparația cu {n}.","balance",rows,answers,explanation))
    for n, rows, answers, explanation in [
        ("coli",r_carioci,{"termeni_eliminați":6,"rest_obiecte":4,"rest_total":20},"Tăiem 6 coli din ambele situații."),
        ("caiete",r_pixuri,{"termeni_eliminați":2,"rest_obiecte":1,"rest_total":16},"Tăiem 2 caiete din ambele situații."),
        ("făină",r_faina,{"termeni_eliminați":7,"rest_obiecte":2,"rest_total":4},"Tăiem 7 pungi de făină din ambele situații."),
    ]: questions.append(comparison.two_rows(f"Elimină termenii comuni: {n}.","cancel_common",rows,answers,explanation))
    questions.extend([
        comparison.two_rows("Aliniază situațiile pentru comparația colilor.","align_rows",r_carioci,{"coloană_comună":6,"diferență":20},"Termenul comun este 6 coli."),
        comparison.two_rows("Aliniază situațiile pentru comparația făinii.","align_rows",r_faina,{"coloană_comună":7,"diferență":4},"Termenul comun este 7 pungi de făină."),
    ])

    # 4: egalizare.
    unequal = [row(41,item(2,"coli","📄"),item(7,"carioci","🖍️")),row(31,item(7,"coli","📄"),item(2,"carioci","🖍️"))]
    questions.extend([
        comparison.two_rows("Alege multiplicatorul pentru a egaliza cele 2 coli cu 14 coli.","equalize",unequal,{"multiplier":7,"total_nou":287},"Înmulțim primul rând cu 7.",multiplier_choices=[2,5,7]),
        comparison.two_rows("Egalizează 3 robinete din ambele situații.","equalize",[row(31,item(3,"robinete","🚰"),item(2,"pompe","⚙️")),row(79,item(3,"robinete","🚰"),item(8,"pompe","⚙️"))],{"multiplier":1,"diferență_total":48},"Robinetele sunt deja egalizate.",multiplier_choices=[1,2,3]),
        comparison.two_rows("Egalizează numărul fetelor: 6 și 3.","equalize",[row(26,item(4,"băieți","🕺"),item(6,"fete","💃")),row(19,item(5,"băieți","🕺"),item(3,"fete","💃"))],{"multiplier":2,"total_nou":38},"Înmulțim al doilea rând cu 2.",multiplier_choices=[2,3,6]),
    ])

    # 5: alegerea metodei.
    questions.extend([
        comparison.choose_method("Alege metoda pentru două situații care au deja 6 coli în comun.","6 coli + 8 carioci = 58; 6 coli + 12 carioci = 78","subtract","Eliminăm colile prin scădere."),
        comparison.choose_method("Alege metoda când un trandafir costă cât 3 garoafe.","5 trandafiri + 6 garoafe = 42; 1 trandafir = 3 garoafe","substitute","Înlocuim trandafirii cu garoafe."),
        comparison.choose_method("Alege metoda când coeficienții aceleiași necunoscute au semne opuse.","3A + 2B = 31; 3A − 4B = 7","add","Adunarea elimină termenii opuși."),
    ])

    # 8: tabelul comparației.
    for text, rows, answers, explanation in [
        ("Completează tabelul colilor și cariocilor.",r_carioci,{"diferență_obiecte":4,"diferență_total":20,"cariocă":5},"4 carioci costă 20 lei."),
        ("Completează tabelul robinetelor și pompelor.",[row(31,item(3,"robinete","🚰"),item(2,"pompe","⚙️")),row(79,item(3,"robinete","🚰"),item(8,"pompe","⚙️"))],{"diferență_pompe":6,"diferență_debit":48,"debit_pompă":8},"6 pompe au debitul 48 hl/oră."),
        ("Completează tabelul pungilor de mălai și făină.",r_faina,{"diferență_mălai":2,"diferență_greutate":4,"mălai":2},"Două pungi de mălai cântăresc 4 kg."),
    ]: questions.append(comparison.two_rows(text,"comparison_table",rows,answers,explanation))

    # 10: substituție.
    questions.extend([
        comparison.substitution("Înlocuiește containerele de plastic cu maculatură.",{"items":[item(6,"plastic","♻️")]},{"items":[item(7,"maculatură","📦")]},{"items":[item(5,"maculatură","📦"),item(6,"plastic","♻️")],"total":720},{"items":[item(12,"maculatură","📦")],"total":720},{"maculatură":60,"plastic":70},"12 containere de maculatură cântăresc 720 kg."),
        comparison.substitution("Înlocuiește trandafirii cu garoafe.",{"items":[item(1,"trandafir","🌹")]},{"items":[item(3,"garoafe","🌸")]},{"items":[item(5,"trandafiri","🌹"),item(6,"garoafe","🌸")],"total":42},{"items":[item(21,"garoafe","🌸")],"total":42},{"garoafă":2,"trandafir":6},"21 de garoafe costă 42 lei."),
        comparison.substitution("Înlocuiește cocoșii cu găini.",{"items":[item(2,"cocoși","🐓")]},{"items":[item(3,"găini","🐔")]},{"items":[item(8,"cocoși","🐓"),item(9,"găini","🐔")],"total":42},{"items":[item(21,"găini","🐔")],"total":42},{"găină":2,"cocoș":3},"8 cocoși echivalează cu 12 găini; totalul echivalează cu 21 găini."),
    ])

    # 12: detectivul greșelilor.
    questions.extend([
        comparison.error_detective("Găsește primul pas greșit în comparația colilor.",["6 coli + 8 carioci = 58","6 coli + 12 carioci = 78","Scădem: 4 carioci = 136","O cariocă = 5 lei"],2,"Diferența totalurilor este 20, nu 136."),
        comparison.error_detective("Găsește primul pas greșit la multiplicarea unui rând.",["2 coli + 7 carioci = 41","Înmulțim rândul cu 7","14 coli + 49 carioci = 41","Totalul corect ar fi 287"],2,"Și totalul trebuie înmulțit cu 7."),
        comparison.error_detective("Găsește primul pas greșit în substituție.",["1 trandafir = 3 garoafe","5 trandafiri = 15 garoafe","15 + 6 = 20 garoafe","O garoafă costă 2 lei"],2,"15 + 6 = 21, nu 20."),
    ])

    # 16, 17: cursa și dansatorii.
    questions.extend([
        comparison.animal_race("Compară săriturile ogarului și vulpii.",{"name":"Ogar","icon":"🐕","jumps":7,"distance":5},{"name":"Vulpe","icon":"🦊","jumps":8,"distance":6},35,2,{"perioade":6,"sărituri_ogar":42},"După 6 perioade, ogarul ajunge vulpea."),
        comparison.animal_race("Compară două broscuțe care sar în același timp.",{"name":"Verde","icon":"🐸","jumps":4,"distance":12},{"name":"Roșie","icon":"🐸","jumps":6,"distance":12},12,2,{"diferență_sărituri":2,"perioade":5},"În fiecare perioadă apar 2 sărituri diferență."),
        comparison.dancers("Completează formația dublă de dansatori.",4,6,5,8,12,5,"Formația s-a dublat în aceeași proporție; timpul dansului rămâne 5 minute."),
        comparison.dancers("Completează o formație de trei ori mai mare.",3,5,4,9,15,4,"Numărul fiecărui tip de dansator s-a triplat; timpul coregrafiei rămâne 4 minute."),
    ])

    # 21: potrivire triplă.
    questions.extend([
        comparison.triple_match("Potrivește problema cu comparația și răspunsul.",[
            {"problem":"6 coli + 8 carioci = 58; 6 coli + 12 carioci = 78","scheme":"(78 − 58) : (12 − 8)","answer":"cariocă = 5 lei"},
            {"problem":"5 mălai + 7 făină = 31; 7 mălai + 7 făină = 35","scheme":"(35 − 31) : (7 − 5)","answer":"mălai = 2 kg"},
            {"problem":"3 robinete + 2 pompe = 31; 3 robinete + 8 pompe = 79","scheme":"(79 − 31) : (8 − 2)","answer":"pompă = 8 hl/oră"},
        ],"Eliminăm termenul comun și reducem diferența la unitate."),
        comparison.triple_match("Potrivește substituțiile corecte.",[
            {"problem":"1 trandafir = 3 garoafe; total 42 lei","scheme":"5 · 3 + 6 = 21 garoafe","answer":"garoafă = 2 lei"},
            {"problem":"2 cocoși = 3 găini; total 42 kg","scheme":"8 cocoși = 12 găini; 12 + 9 = 21","answer":"găină = 2 kg"},
            {"problem":"6 plastic = 7 maculatură; total 720 kg","scheme":"7 + 5 = 12 containere maculatură","answer":"maculatură = 60 kg"},
        ],"Înlocuim grupul echivalent și apoi reducem la unitate."),
    ])

    # 23: adevărat/fals.
    questions.extend([
        comparison.visual_true_false("Multiplicarea unui rând – adevărat sau fals.","Dacă înmulțim cantitățile unui rând cu 3, trebuie să înmulțim și totalul cu 3.",True,"✖️","Întregul rând descrie de trei ori aceeași cumpărătură.","Afirmația este adevărată."),
        comparison.visual_true_false("Eliminarea termenului comun – adevărat sau fals.","Putem elimina 6 coli dintr-un rând și 7 coli din celălalt ca și cum ar fi același termen.",False,"✂️","Cantitățile eliminate trebuie să fie egale.","Nu putem scădea cantități diferite ale necunoscutei."),
        comparison.visual_true_false("Substituția – adevărat sau fals.","Dacă 2 cocoși cântăresc cât 3 găini, putem înlocui 8 cocoși cu 12 găini.",True,"⚖️","Echivalența inițială este folosită de patru ori.","2 · 4 = 8 cocoși și 3 · 4 = 12 găini."),
    ])

    assert len(questions) == 52, len(questions)
    assert len({q["text"] for q in questions}) == len(questions)
    return questions


def main():
    output = Path(__file__).resolve().parent.parent / "clasa_5_metoda_comparatiei.json"
    payload = {"title":"Metoda comparației","description":"Clasa a 5-a · Metode aritmetice de rezolvare a problemelor","difficulty":"medium","questions":build_questions()}
    output.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(f"Scrise {len(payload['questions'])} exerciții în {output.name}")


if __name__ == "__main__": main()
