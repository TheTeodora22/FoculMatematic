"""Generează lecția „Metoda reducerii la unitate” pentru clasa a V-a."""

import json
from pathlib import Path

import unit_reduction_factory as unit


def fmt(value):
    return f"{value:,}".replace(",", " ") if isinstance(value, int) else str(value)


def grid(text, correct, wrong, explanation):
    correct = fmt(correct)
    wrong = [fmt(value) for value in wrong]
    assert len(wrong) == 3 and correct not in wrong and len(set(wrong)) == 3
    return {
        "text": text,
        "format": "grid",
        "points": 10,
        "explanation": explanation,
        "options": [
            {"text": wrong[0], "is_correct": False},
            {"text": correct, "is_correct": True},
            {"text": wrong[1], "is_correct": False},
            {"text": wrong[2], "is_correct": False},
        ],
    }


def build_questions():
    questions = [
        grid("8 kg de mere costă 24 de lei. Cât costă 5 kg de mere?", "15 lei", ["12 lei", "18 lei", "21 lei"], "Un kilogram costă 24 : 8 = 3 lei, iar 5 kg costă 5 · 3 = 15 lei."),
        grid("6 caiete identice costă 42 de lei. Cât costă 9 caiete?", "63 lei", ["54 lei", "56 lei", "72 lei"], "Un caiet costă 42 : 6 = 7 lei, deci 9 caiete costă 9 · 7 = 63 lei."),
        grid("2 litri de ulei costă 18 lei. Cât costă un litru?", "9 lei", ["8 lei", "16 lei", "36 lei"], "Reducem la unitate: 18 : 2 = 9 lei."),
        grid("5 metri de material costă 45 de lei. Cât costă 8 metri?", "72 lei", ["64 lei", "68 lei", "80 lei"], "Un metru costă 45 : 5 = 9 lei, iar 8 metri costă 8 · 9 = 72 lei."),
        grid("12 muncitori termină o lucrare în 5 zile. În câte zile o termină 20 de muncitori cu aceeași putere de muncă?", "3 zile", ["2 zile", "8 zile", "12 zile"], "Un muncitor ar termina în 12 · 5 = 60 de zile, iar 20 de muncitori în 60 : 20 = 3 zile."),
        grid("4 robinete identice umplu un bazin în 12 ore. În cât timp îl umplu 6 robinete?", "8 ore", ["6 ore", "16 ore", "18 ore"], "Un robinet ar avea nevoie de 4 · 12 = 48 de ore, iar 6 robinete de 48 : 6 = 8 ore."),
        grid("3 pompe identice golesc un rezervor în 8 ore. În cât timp îl golesc 4 pompe?", "6 ore", ["4 ore", "9 ore", "12 ore"], "O pompă ar lucra 3 · 8 = 24 de ore, iar 4 pompe 24 : 4 = 6 ore."),
        grid("30 de elevi plantează puieții în 4 ore. În cât timp ar termina 20 de elevi, lucrând la fel?", "6 ore", ["3 ore", "5 ore", "8 ore"], "Un elev ar lucra 30 · 4 = 120 de ore, iar 20 de elevi 120 : 20 = 6 ore."),
        grid("12 pixuri identice costă 60 de lei. Care este prețul unui pix?", "5 lei", ["4 lei", "6 lei", "12 lei"], "60 : 12 = 5 lei pentru un pix."),
        grid("6 robinete umplu piscina în 3 ore. În cât timp ar umple-o un singur robinet?", "18 ore", ["2 ore", "9 ore", "36 ore"], "Când numărul robinetelor scade de 6 ori, timpul crește de 6 ori: 3 · 6 = 18 ore."),
        grid("Care schemă arată corect reducerea la unitate pentru 8 kg care costă 24 lei și 5 kg cu preț necunoscut?", "8 kg → 1 kg → 5 kg; 24 : 8 · 5", ["8 kg → 5 kg; 24 : 5", "24 · 8 : 5", "24 + 8 + 5"], "Mai întâi aflăm prețul unui kilogram împărțind la 8, apoi înmulțim cu 5."),
        grid("Dacă numărul muncitorilor crește, iar lucrarea rămâne aceeași, timpul necesar:", "scade", ["crește", "rămâne mereu egal", "devine zero"], "Mai mulți muncitori împart aceeași lucrare, deci timpul scade."),
        grid("Un caiet costă 4 lei. Cât plătim pentru 7 caiete?", "28 lei", ["11 lei", "21 lei", "32 lei"], "7 · 4 = 28 lei."),
        grid("Un pătrat cu latura de 5 cm are perimetrul de 20 cm. Ce perimetru are un pătrat cu latura de 9 cm?", "36 cm", ["24 cm", "29 cm", "45 cm"], "Pentru 1 cm de latură corespund 4 cm de perimetru; 9 · 4 = 36 cm."),
        grid("Un pește parcurge 300 m în 6 secunde, cu viteză constantă. Câți metri parcurge într-o secundă?", "50 m", ["30 m", "60 m", "1 800 m"], "300 : 6 = 50 m într-o secundă."),
        grid("Clopotele bat de 3 ori în 12 secunde, considerând același timp pentru fiecare bătaie. În câte secunde bat de 12 ori?", "48 secunde", ["36 secunde", "40 secunde", "144 secunde"], "O bătaie corespunde la 12 : 3 = 4 secunde, iar 12 bătăi la 12 · 4 = 48 secunde."),
        grid("Din 200 litri de apă de mare se obțin 8 grame de sare. Câte grame se obțin din 400 litri?", "16 grame", ["4 grame", "8 grame", "32 grame"], "Cantitatea de apă se dublează, deci se dublează și sarea: 8 · 2 = 16 grame."),
        grid("O culegere este terminată în 25 de zile, dar nu știm câte probleme se rezolvă zilnic. Putem afla în câte zile se termină dacă se rezolvă 5 probleme pe zi?", "Nu, lipsește numărul inițial de probleme pe zi", ["Da, în 5 zile", "Da, în 20 de zile", "Da, în 125 de zile"], "Nu putem afla numărul total de probleme fără ritmul inițial de lucru."),
        grid("Dintr-o sârmă se fac 13 bucăți de câte 4 m. Ce lungime totală are sârma?", "52 m", ["48 m", "56 m", "64 m"], "13 · 4 = 52 m."),
        grid("Produsul a două numere este 60. Dacă primul număr devine 12, cât trebuie să fie al doilea pentru ca produsul să rămână 60?", 5, [4, 6, 12], "60 : 12 = 5."),
    ]

    # 1. Imagine care se mărește sau se micșorează.
    questions.extend([
        unit.visual_scale("Reglează imaginea pentru a arăta cât costă 5 kg de mere, dacă 8 kg costă 24 lei.", 8, 24, 5, "kg", "🍎", "Un kilogram costă 3 lei, deci 5 kg costă 15 lei."),
        unit.visual_scale("Reglează imaginea pentru 9 caiete, știind că 6 caiete costă 42 lei.", 6, 42, 9, "caiete", "📘", "Un caiet costă 7 lei, deci 9 caiete costă 63 lei."),
        unit.visual_scale("Reglează imaginea pentru 7 sticle, dacă 4 sticle conțin împreună 12 litri.", 4, 12, 7, "sticle", "🧴", "O sticlă conține 3 litri, iar 7 sticle conțin 21 litri."),
    ])

    # 2. Drumul prin unitate.
    questions.extend([
        unit.unit_path("Așază operațiile pe drumul 12 pixuri → 1 pix → 7 pixuri.", 12, 60, 7, "lei", "Împărțim 60 la 12 și înmulțim rezultatul cu 7: obținem 35 lei."),
        unit.unit_path("Așază operațiile pe drumul 9 bilete → 1 bilet → 5 bilete.", 9, 72, 5, "lei", "Un bilet costă 8 lei, iar 5 bilete costă 40 lei."),
        unit.unit_path("Așază operațiile pe drumul 6 metri → 1 metru → 4 metri.", 6, 54, 4, "lei", "Un metru costă 9 lei, iar 4 metri costă 36 lei."),
    ])

    # 3. Balanța mărimilor.
    questions.extend([
        unit.balance("Echilibrează latura și perimetrul pentru un pătrat cu latura de 9 cm.", 5, 20, 9, unit.DIRECT, ["Latură (cm)", "Perimetru (cm)"], "Perimetrul este de 4 ori latura: 9 · 4 = 36 cm."),
        unit.balance("Echilibrează numărul muncitorilor și timpul pentru 20 de muncitori.", 12, 5, 20, unit.INVERSE, ["Muncitori", "Zile"], "Produsul rămâne 60, deci 20 de muncitori lucrează 3 zile."),
        unit.balance("Echilibrează numărul pompelor și timpul pentru 8 pompe.", 4, 6, 8, unit.INVERSE, ["Pompe", "Ore"], "Produsul rămâne 24, deci 8 pompe lucrează 3 ore."),
    ])

    # 4. Coșul interactiv.
    questions.extend([
        unit.basket("Pune în coș 7 caiete și calculează totalul, dacă unul costă 3 lei.", 3, 7, "📘", "lei", "7 · 3 = 21 lei."),
        unit.basket("Pune în coș 6 sticle și calculează totalul, dacă una costă 5 lei.", 5, 6, "🧴", "lei", "6 · 5 = 30 lei."),
        unit.basket("Pune în coș 4 bilete și calculează totalul, dacă unul costă 8 lei.", 8, 4, "🎫", "lei", "4 · 8 = 32 lei."),
    ])

    # 6. Robineți și pompe.
    questions.extend([
        unit.faucets("Deschide 9 robinete și determină timpul, dacă 6 robinete umplu piscina în 3 ore.", 6, 3, 9, "🚰", "Un robinet ar lucra 18 ore; 9 robinete lucrează 2 ore."),
        unit.faucets("Deschide 6 robinete și determină timpul, dacă 4 robinete umplu bazinul în 12 ore.", 4, 12, 6, "🚰", "Un robinet ar lucra 48 de ore; 6 robinete lucrează 8 ore."),
        unit.faucets("Deschide 4 pompe și determină timpul, dacă 3 pompe golesc rezervorul în 8 ore.", 3, 8, 4, "⚙️", "O pompă ar lucra 24 de ore; 4 pompe lucrează 6 ore."),
    ])

    # 8. Sensul dependenței.
    questions.extend([
        unit.dependency_direction("Alege sensul dependenței dintre cantitatea cumpărată și prețul total.", "Mai multe kilograme", "Preț mai mare", unit.DIRECT, "Cantitatea și prețul total cresc împreună."),
        unit.dependency_direction("Alege sensul dependenței dintre muncitori și timpul aceleiași lucrări.", "Mai mulți muncitori", "Mai puține zile", unit.INVERSE, "O mărime crește, iar cealaltă scade."),
        unit.dependency_direction("Alege sensul dependenței dintre robinete și timpul de umplere.", "Mai puține robinete", "Mai mult timp", unit.INVERSE, "Când numărul robinetelor scade, timpul crește."),
    ])

    # 9. Tabele prin unitate.
    questions.extend([
        unit.unit_table("Completează tabelul cantitate–preț.", [{"Cantitate": 8, "Preț": 24, "missing": "Preț"}, {"Cantitate": 1, "Preț": 3, "missing": "Cantitate"}, {"Cantitate": 5, "Preț": 15, "missing": "Preț"}], ["Cantitate", "Preț"], "Prețul unei unități este 3 lei."),
        unit.unit_table("Completează tabelul muncitori–zile pentru aceeași lucrare.", [{"Muncitori": 12, "Zile": 5, "missing": "Zile"}, {"Muncitori": 1, "Zile": 60, "missing": "Muncitori"}, {"Muncitori": 20, "Zile": 3, "missing": "Zile"}], ["Muncitori", "Zile"], "Produsul dintre muncitori și zile este 60."),
        unit.unit_table("Completează tabelul latură–perimetru pentru pătrate.", [{"Latură": 5, "Perimetru": 20, "missing": "Perimetru"}, {"Latură": 1, "Perimetru": 4, "missing": "Latură"}, {"Latură": 9, "Perimetru": 36, "missing": "Perimetru"}], ["Latură", "Perimetru"], "Perimetrul pătratului este de 4 ori latura."),
    ])

    # 10. Operații trase pe săgeți.
    questions.extend([
        unit.operation_drop("Trage operațiile corecte între 8 kg, 1 kg și 5 kg.", ["8 kg", "1 kg", "5 kg"], [": 8", "× 5"], ["× 8", ": 5"], "Împărțim la 8, apoi înmulțim cu 5."),
        unit.operation_drop("Trage operațiile corecte între 12 pixuri, 1 pix și 7 pixuri.", ["12 pixuri", "1 pix", "7 pixuri"], [": 12", "× 7"], ["× 12", ": 7"], "Împărțim la 12, apoi înmulțim cu 7."),
        unit.operation_drop("Trage operațiile corecte între 6 robinete, 1 robinet și 9 robinete, urmărind timpul.", ["6 robinete", "1 robinet", "9 robinete"], ["× 6", ": 9"], [": 6", "× 9"], "Pentru un robinet timpul se mărește de 6 ori, apoi se împarte la 9."),
    ])

    # 16. Banda timpului.
    questions.extend([
        unit.timeline("Mută banda la timpul necesar pentru 6 muncitori, dacă 12 muncitori termină în 5 zile.", 1, 15, 1, 10, "12 muncitori: 5 zile", "6 muncitori: ? zile", "Un muncitor ar lucra 60 de zile, iar 6 muncitori 10 zile."),
        unit.timeline("Mută banda la timpul necesar pentru 8 robinete, dacă 4 robinete umplu bazinul în 12 ore.", 1, 15, 1, 6, "4 robinete: 12 ore", "8 robinete: ? ore", "Un robinet ar lucra 48 de ore, iar 8 robinete 6 ore."),
    ])

    # 17. Construirea problemei.
    questions.extend([
        unit.problem_builder("Construiește o problemă coerentă despre cumpărături.", ["8 kg de mere costă 24 lei.", "8 muncitori termină în 24 zile.", "8 robinete umplu în 24 ore."], ["Cât costă 5 kg?", "În cât timp lucrează 5 muncitori?", "Câte robinete sunt necesare?"], ["Cantitatea și prețul cresc sau scad împreună.", "Numărul și timpul variază invers.", "Datele nu au nicio legătură."], [0, 0, 0], "Problema corectă întreabă prețul unei alte cantități de mere."),
        unit.problem_builder("Construiește o problemă coerentă despre o lucrare.", ["12 caiete costă 60 lei.", "12 muncitori termină lucrarea în 5 zile.", "12 metri de material costă 5 lei."], ["În câte zile termină 20 de muncitori?", "Cât costă 20 de caiete?", "Câți metri sunt necesari?"], ["Mai mulți muncitori înseamnă mai puține zile.", "Mai mulți muncitori înseamnă mai multe zile.", "Timpul nu depinde de muncitori."], [1, 0, 0], "Pentru aceeași lucrare, numărul muncitorilor și timpul variază invers."),
    ])

    # 19. Simulatorul de viteză.
    questions.extend([
        unit.speed_simulator("Mută timpul până când peștele parcurge 300 m, știind că parcurge 50 m pe secundă.", 50, 300, 10, "🐟", "300 : 50 = 6 secunde."),
        unit.speed_simulator("Mută timpul până când mașina produce 320 de piese, dacă produce 40 de piese pe minut.", 40, 320, 12, "🏭", "320 : 40 = 8 minute."),
    ])

    # 21. Potrivire între problemă, schemă și răspuns.
    questions.extend([
        unit.triple_match("Potrivește fiecare problemă cu schema și răspunsul corect.", [
            {"problem": "8 kg costă 24 lei; 5 kg costă?", "scheme": "24 : 8 · 5", "answer": "15 lei"},
            {"problem": "12 muncitori, 5 zile; 20 muncitori?", "scheme": "12 · 5 : 20", "answer": "3 zile"},
            {"problem": "4 robinete, 12 ore; 6 robinete?", "scheme": "4 · 12 : 6", "answer": "8 ore"},
        ], "Fiecare schemă trece prin valoarea unei unități."),
        unit.triple_match("Potrivește noile probleme cu rezolvările lor.", [
            {"problem": "6 caiete costă 42 lei; 9 caiete?", "scheme": "42 : 6 · 9", "answer": "63 lei"},
            {"problem": "3 pompe, 8 ore; 4 pompe?", "scheme": "3 · 8 : 4", "answer": "6 ore"},
            {"problem": "Latura 5 cm dă P = 20 cm; latura 9 cm?", "scheme": "20 : 5 · 9", "answer": "36 cm"},
        ], "Identificăm dacă mărimile variază împreună sau invers."),
    ])

    # 22. Adevărat/fals vizual.
    questions.extend([
        unit.visual_true_false("Mere – decide dacă afirmația este corectă.", "Dacă 8 kg costă 24 lei, atunci 16 kg costă 48 lei.", True, "🍎", "Cantitatea s-a dublat.", "Prețul se dublează odată cu cantitatea."),
        unit.visual_true_false("Robinete – decide dacă afirmația este corectă.", "Dacă 6 robinete umplu bazinul în 3 ore, atunci 3 robinete îl umplu în 6 ore.", True, "🚰", "Numărul robinetelor s-a înjumătățit.", "Când robinetele se înjumătățesc, timpul se dublează."),
        unit.visual_true_false("Muncitori – decide dacă afirmația este corectă.", "Dacă 12 muncitori termină în 6 zile, atunci 24 de muncitori termină în 12 zile.", False, "👷", "Sunt de două ori mai mulți muncitori.", "Mai mulți muncitori au nevoie de mai puțin timp: 24 de muncitori termină în 3 zile, deci afirmația este falsă."),
        unit.visual_true_false("Pătrat – decide dacă afirmația este corectă.", "Dacă latura unui pătrat se dublează, atunci și perimetrul se dublează.", True, "⬜", "Perimetrul este de patru ori latura.", "P = 4 · l, deci latura și perimetrul cresc în același raport."),
    ])

    assert len(questions) == 56, len(questions)
    assert len({question["text"] for question in questions}) == len(questions)
    return questions


def main():
    output = Path(__file__).resolve().parent.parent / "clasa_5_metode_aritmetice_de_rezolvare_a_problemelor.json"
    payload = {
        "title": "Metoda reducerii la unitate",
        "description": "Clasa a 5-a · Metode aritmetice de rezolvare a problemelor",
        "difficulty": "medium",
        "questions": build_questions(),
    }
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Scrise {len(payload['questions'])} exerciții în {output.name}")


if __name__ == "__main__":
    main()
