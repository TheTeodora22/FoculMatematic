"""Generează lecția „Metoda figurativă” pentru clasa a V-a."""
import json
from pathlib import Path
import figurative_factory as f


def grid(text, correct, wrong, explanation):
    values = [str(correct), *map(str, wrong)]
    assert len(values) == 4 and len(set(values)) == 4
    return {"text": text, "format": "grid", "points": 10, "explanation": explanation,
            "options": [{"text": value, "is_correct": index == 0} for index, value in enumerate(values)]}


def build_questions():
    S = f.scheme
    questions = [
        grid("Suma a două numere este 27, iar diferența este 19. Cât reprezintă cele două părți egale?", 8, [4, 19, 46], "Eliminăm diferența: 27 − 19 = 8."),
        grid("Două părți egale însumează 8. Cât reprezintă o parte?", 4, [2, 6, 8], "8 : 2 = 4."),
        grid("Suma a două numere este 36, iar primul este de 3 ori al doilea. Câte părți avem?", 4, [2, 3, 6], "Primul are 3 părți și al doilea o parte."),
        grid("Suma este 36 și raportul este 3. Care este numărul mai mic?", 9, [3, 12, 27], "36 : 4 = 9."),
        grid("Diferența dintre vârste este 28, iar tatăl va avea de 3 ori vârsta fiului. Câte părți reprezintă diferența?", 2, [1, 3, 28], "3 părți − 1 parte = 2 părți."),
        grid("Două părți valorează 28. Cât valorează o parte?", 14, [7, 26, 42], "28 : 2 = 14."),
        grid("Perimetrul unui dreptunghi este 444 m, iar lățimea este cu 12 m mai mică. Ce calcul facem întâi?", "444 : 2", ["444 − 12", "444 : 4", "444 + 12"], "Semiperimetrul este suma lungimii și lățimii."),
        grid("Suma a două numere este 206. Adăugând cifra 1 în stânga unuia obținem celălalt număr. Diferența este:", 100, [1, 10, 206], "Cifra 1 adăugată în stânga unui număr de două cifre mărește numărul cu 100."),
        grid("Un număr este de 4 ori altul, iar suma lor este 60. Numărul mic este:", 12, [4, 15, 48], "Avem 5 părți: 60 : 5 = 12."),
        grid("Doi frați cântăresc împreună cu părinții 238 kg. Copiii au câte 40 kg, iar tatăl are cu 14 kg mai mult decât mama. Mama are:", 72, [58, 76, 86], "Părinții au 158 kg; eliminăm diferența 14 și împărțim la 2."),
        grid("37 de copii au participat la concurs, iar cei cu punctaj mic sunt de 3 ori mai mulți. Ce observăm?", "date incompatibile", ["9 copii", "12 copii", "28 copii"], "37 nu se împarte exact în 4, deci datele nu conduc la numere naturale."),
        grid("Împărțind un număr la altul obținem câtul 5 și restul 14. Restul trebuie să fie:", "mai mic decât împărțitorul", ["egal cu împărțitorul", "mai mare decât împărțitorul", "întotdeauna zero"], "În împărțirea cu rest, restul este mai mic decât împărțitorul."),
        grid("16 elevi ar mai încăpea câte doi în bancă, folosind încă 3 bănci. Câte locuri reprezintă cele 3 bănci?", 6, [3, 8, 16], "3 · 2 = 6 locuri."),
        grid("Pe un desen, bara mare are 4 părți, iar bara mică una. Câtul este:", 4, [3, 5, 8], "Bara mare este de patru ori bara mică."),
        grid("Dacă suma minus diferența este impară, problema cu două numere naturale:", "nu are soluție", ["are mereu soluție", "are două soluții", "are numere egale"], "Rezultatul trebuie împărțit la 2 și trebuie să fie natural."),
        grid("Verificarea pentru numerele 4 și 23, cu suma 27 și diferența 19, este:", "4 + 23 = 27 și 23 − 4 = 19", ["4 · 23 = 27", "27 − 19 = 4", "23 : 4 = 19"], "Verificăm atât suma, cât și diferența."),
    ]

    schemes_27 = [S(1,1,19,27), S(1,2,19,27), S(2,2,19,27), S(1,3,0,27)]
    schemes_36 = [S(1,3,0,36), S(1,2,3,36), S(2,3,0,36), S(1,4,0,36)]
    schemes_age = [S(1,3,28,None,"fiul","tatăl"), S(1,2,28,None,"fiul","tatăl"), S(2,3,28,None,"fiul","tatăl")]

    questions += [
        f.choose_scheme("Alege desenul pentru suma 27 și diferența 19.", schemes_27, 0, "Ambele bare au câte o parte comună, iar bara mare are încă 19."),
        f.choose_scheme("Alege desenul pentru suma 36 și câtul 3.", schemes_36, 0, "Numărul mare are 3 părți, iar cel mic una."),
        f.choose_scheme("Alege desenul pentru diferența 28 și câtul 3.", schemes_age, 0, "Diferența dintre 3 părți și o parte este 28."),
        f.build_segments("Construiește schema: suma 60, numărul mare este de 4 ori numărul mic.", S(1,4,0,60), {"small_parts":1,"large_parts":4,"difference":0}, "Schema are 1 parte și 4 părți."),
        f.build_segments("Construiește schema: suma 48, numărul mare este de 3 ori numărul mic.", S(1,3,0,48), {"small_parts":1,"large_parts":3,"difference":0}, "Schema are în total 4 părți."),
        f.build_segments("Construiește schema pentru 27 și diferența 19.", S(1,1,19,27), {"small_parts":1,"large_parts":1,"difference":19}, "Cele două bare au o parte comună."),
        f.divide_segments("Împarte bara sumei 36 în numărul corect de părți.", S(1,3,0,36), 4, "1 + 3 = 4 părți."),
        f.divide_segments("Împarte bara sumei 60 pentru raportul 4.", S(1,4,0,60), 5, "1 + 4 = 5 părți."),
        f.divide_segments("Împarte diferența de vârstă în părți egale.", S(1,3,28,None,"fiul","tatăl"), 2, "3 − 1 = 2 părți."),
        f.order_steps("Pune în ordine rezolvarea sumei 27 și diferenței 19.", S(1,1,19,27), ["27 − 19 = 8", "8 : 2 = 4", "4 + 19 = 23", "4 + 23 = 27"], "Întâi eliminăm diferența, apoi aflăm o parte."),
        f.order_steps("Pune în ordine rezolvarea sumei 36 și câtului 3.", S(1,3,0,36), ["3 + 1 = 4 părți", "36 : 4 = 9", "9 · 3 = 27", "9 + 27 = 36"], "Numărăm părțile înainte de împărțire."),
        f.order_steps("Pune în ordine problema de vârstă.", S(1,3,28,None,"fiul","tatăl"), ["3 − 1 = 2 părți", "28 : 2 = 14", "14 · 3 = 42", "scădem cei 2 ani"], "Diferența corespunde la două părți."),
        f.animate_difference("Elimină diferența 19 din suma 27.", S(1,1,19,27), 8, "După eliminare rămân două părți egale cu suma 8."),
        f.animate_difference("Elimină diferența 14 din totalul de 158 kg al părinților.", S(1,1,14,158,"mama","tata"), 144, "158 − 14 = 144."),
        f.animate_difference("Elimină diferența 12 din semiperimetrul 222.", S(1,1,12,222,"lățimea","lungimea"), 210, "222 − 12 = 210."),
        f.repair_scheme("Repară desenul pentru suma 36 și câtul 3.", S(1,2,0,36), [2,3,4], 3, "Bara mare trebuie să aibă trei părți."),
        f.repair_scheme("Repară diferența din schema sumei 27.", S(1,1,17,27), [17,19,21], 19, "Diferența corectă este 19."),
        f.repair_scheme("Repară desenul vârstelor.", S(1,4,28,None,"fiul","tatăl"), [2,3,4], 3, "Tatăl va avea de trei ori vârsta fiului."),
        f.true_false("Citește desenul cu suma 36.", S(1,3,0,36), "Numărul mare este de trei ori numărul mic.", True, "Bara mare are trei părți egale."),
        f.true_false("Citește desenul cu suma 27.", S(1,1,19,27), "Diferența dintre numere este 27.", False, "27 este suma; diferența este 19."),
        f.true_false("Citește desenul vârstelor.", S(1,3,28,None,"fiul","tatăl"), "Diferența reprezintă două părți.", True, "3 − 1 = 2 părți."),
        f.remainder_slider("Alege restul pentru o împărțire cu câtul 3 și suma numerelor 36.", S(1,3,0,36), 8, 0, "36 se împarte exact la 4, deci restul este 0."),
        f.remainder_slider("Alege restul pentru soluția 28 = 8 · 3 + r.", S(1,3,4,36), 7, 4, "28 = 24 + 4."),
        f.remainder_slider("Alege restul pentru soluția 27 = 9 · 3 + r.", S(1,3,0,36), 5, 0, "27 = 9 · 3."),
        f.no_solution("Suma este 24 și diferența 19. Există două numere naturale?", S(1,1,19,24), False, "(24 − 19) : 2 = 2,5, deci nu obținem numere naturale."),
        f.no_solution("Suma este 27 și diferența 19. Există soluție?", S(1,1,19,27), True, "(27 − 19) : 2 = 4."),
        f.no_solution("Suma este 36 și câtul 3. Există soluție naturală?", S(1,3,0,36), True, "36 : 4 = 9."),
        f.benches("Mută elevii pe bănci și află situația inițială.", 34, 4, 5, {"bănci":38,"elevi":170}, "34 bănci ocupate și 4 libere: 38 bănci; 34 · 5 = 170 elevi."),
        f.benches("Calculează pentru 20 de bănci ocupate, 3 libere și câte 4 elevi.", 20, 3, 4, {"bănci":23,"elevi":80}, "Sunt 23 de bănci și 80 de elevi."),
        f.benches("Calculează pentru 12 bănci ocupate, 2 libere și câte 3 elevi.", 12, 2, 3, {"bănci":14,"elevi":36}, "Sunt 14 bănci și 36 de elevi."),
        f.equivalent_schemes("Alege cele două desene echivalente pentru suma 36 și câtul 3.", [S(1,3,0,36),S(2,6,0,72),S(1,2,12,36),S(1,3,0,40)], 0, 1, "A doua schemă este prima scalată de două ori."),
        f.equivalent_schemes("Alege schemele echivalente pentru diferența 28 și câtul 3.", [S(1,3,28),S(2,6,56),S(1,2,28),S(1,4,28)], 0, 1, "Ambele rapoarte sunt 1 la 3 și diferențele sunt scalate identic."),
        f.equivalent_schemes("Alege desenele echivalente pentru suma 60 și câtul 4.", [S(1,4,0,60),S(2,8,0,120),S(1,3,0,60),S(1,4,5,60)], 0, 1, "Raportul și totalul sunt dublate împreună."),
        f.full_puzzle("Rezolvă complet desenul: suma 27, diferența 19.", S(1,1,19,27), {"parts":2,"one_part":4,"small":4,"large":23}, "27 − 19 = 8; 8 : 2 = 4; numerele sunt 4 și 23."),
        f.full_puzzle("Rezolvă complet desenul: suma 36, câtul 3.", S(1,3,0,36), {"parts":4,"one_part":9,"small":9,"large":27}, "36 : 4 = 9; numerele sunt 9 și 27."),
        f.full_puzzle("Rezolvă desenul vârstelor: diferența 28, câtul 3.", S(1,3,28), {"parts":2,"one_part":14,"small":14,"large":42}, "28 : 2 = 14; vârstele din momentul comparat sunt 14 și 42."),
    ]
    assert len(questions) == 52, len(questions)
    assert len({q["text"] for q in questions}) == 52
    return questions


def main():
    output = Path(__file__).resolve().parent.parent / "clasa_5_metoda_figurativa.json"
    payload = {"title":"Metoda figurativă", "description":"Clasa a 5-a · Metode aritmetice de rezolvare a problemelor",
               "difficulty":"medium", "questions":build_questions()}
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Scrise {len(payload['questions'])} exerciții în {output.name}")


if __name__ == "__main__":
    main()
