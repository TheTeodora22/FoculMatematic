"""Lecția mixtă: metode aritmetice cu fracții și unități de măsură."""
import json
from pathlib import Path

import comparison_factory as comparison
import false_hypothesis_factory as hypothesis
import figurative_factory as figurative
import reverse_factory as reverse
import unit_reduction_factory as unit
from gen_metoda_comparatiei import build_questions as comparison_bank


def grid(text, correct, wrong, explanation):
    values = [str(correct), *map(str, wrong)]
    assert len(values) == 4 and len(set(values)) == 4
    order = [1, 3, 0, 2]
    return {"text": text, "type": "multiple_choice", "format": "grid", "points": 10,
            "explanation": explanation,
            "options": [{"text": values[i], "is_correct": i == 0} for i in order]}


def missing(text, expression, fields, answers, explanation):
    return {"text": text, "type": "decimal_workbench", "format": "interactive", "points": 10,
            "explanation": explanation,
            "interactive": {"mode": "missing", "expression": expression,
                            "fields": [{"key": key, "label": label} for key, label in fields],
                            "answers": answers}}


def item(count, name, icon):
    return {"count": count, "name": name, "icon": icon}


def row(total, *items):
    return {"items": list(items), "total": total}


def pick_modes(bank, modes):
    result = []
    for mode in modes:
        result.append(next(question for question in bank if question.get("interactive", {}).get("mode") == mode))
    return result


def build_questions():
    questions = [
        unit.visual_scale("Pentru 14 m² de gard s-au folosit 3 500 g de vopsea. Reglează cantitatea pentru 35 m².",
                          14, 3500, 35, "m²", "🎨", "Un metru pătrat cere 250 g, deci 35 m² cer 8 750 g."),
        unit.unit_path("Opt metri de material costă 120 lei. Construiește drumul printr-un metru pentru 13 m.",
                       8, 120, 13, "lei", "120 : 8 = 15 lei/m, iar 13 m costă 195 lei."),
        unit.balance("Douăzeci și patru de plăci acoperă 6 m². Câte plăci sunt necesare pentru 15 m²?",
                     6, 24, 15, unit.DIRECT, ["suprafață", "plăci"], "O suprafață mai mare cere proporțional mai multe plăci: 60."),
        unit.balance("Douăsprezece robinete umplu piscina în 13 ore și 20 de minute, adică 800 de minute. Află timpul pentru 32 de robinete.",
                     12, 800, 32, unit.INVERSE, ["robinete", "minute"], "Produsul robinete · timp rămâne constant; rezultă 300 minute."),
        unit.faucets("Opt pompe golesc un bazin în 18 ore. În cât timp îl golesc 12 pompe identice?",
                     8, 18, 12, "⚙️", "Mai multe pompe înseamnă mai puțin timp: 8 · 18 : 12 = 12 ore."),
        unit.dependency_direction("Cantitatea cumpărată crește; prețul total, la același preț unitar, ce face?",
                                  "cantitatea crește", "prețul total crește", unit.DIRECT,
                                  "Cele două mărimi cresc în același raport."),
        unit.dependency_direction("Numărul robinetelor deschise crește; timpul de umplere ce face?",
                                  "numărul robinetelor crește", "timpul scade", unit.INVERSE,
                                  "Debitul total crește, deci timpul necesar scade."),
        unit.unit_table("Completează tabelul preț–cantitate prin reducere la unitate.",
                        [{"cantitate": 6, "cost": 30, "missing": "cost"},
                         {"cantitate": 1, "cost": 5, "missing": "cost"},
                         {"cantitate": 14, "cost": 70, "missing": "cost"}],
                        ["cantitate", "cost"], "Un kilogram costă 5 lei; 14 kg costă 70 lei."),
        unit.operation_drop("Așază operațiile pe traseul 40% din suprafață → 1% → întreaga suprafață.",
                            [40, 1, 100], [": 40", "× 100"], ["× 40", ": 100"],
                            "Împărțim valoarea cunoscută la 40, apoi înmulțim cu 100."),
        unit.triple_match("Potrivește fiecare problemă cu schema și răspunsul ei.", [
            {"problem": "8 m costă 120 lei; 13 m costă ?", "scheme": "120 : 8 · 13", "answer": "195 lei"},
            {"problem": "24 plăci acoperă 6 m²; pentru 15 m²?", "scheme": "24 : 6 · 15", "answer": "60 plăci"},
            {"problem": "8 pompe în 18 h; 12 pompe în ?", "scheme": "8 · 18 : 12", "answer": "12 ore"},
        ], "Reducerea la unitate poate descrie atât dependențe directe, cât și inverse."),
    ]

    # Comparația: folosim componentele deja verificate și adăugăm un caz monetar din lecție.
    questions += pick_modes(comparison_bank(),
                            ["balance", "cancel_common", "equalize", "choose_method", "comparison_error", "comparison_match"])

    trail = figurative.scheme(4, 7, 3, 11, "traseu rămas", "traseu parcurs")
    schemes = [trail, figurative.scheme(4, 5, 3, 11), figurative.scheme(3, 7, 4, 11)]
    questions += [
        figurative.choose_scheme("Alege schema în care 7/11 din traseu au fost parcurși, iar 4/11 au rămas.",
                                 schemes, 0, "Barele reprezintă 7 părți parcurse și 4 părți rămase din același întreg."),
        figurative.animate_difference("Elimină diferența dintre cele 7 părți parcurse și cele 4 părți rămase.",
                                      trail, 8,
                                      "Eliminăm 3 părți din bara mare și rămân două bare egale de câte 4 părți."),
        figurative.order_steps("Ordonează aflarea traseului dacă 4/11 înseamnă 5,6 km.", trail,
                               ["5,6 : 4 = 1,4 km", "1,4 · 11 = 15,4 km", "verificăm cele 11 părți"],
                               "Aflăm mai întâi o parte, apoi întregul."),
        figurative.divide_segments("Împarte traseul în numărul corect de părți egale.", trail, 11,
                                   "Numitorul comun este 11, deci întregul are 11 părți."),
        figurative.true_false("Citește schema traseului.", trail,
                              "Distanța rămasă după cele două porțiuni reprezintă 4/11 din traseu.", True,
                              "1 − 5/11 − 2/11 = 4/11."),
        figurative.full_puzzle("Rezolvă schema în hectometri dacă ultimele 4 părți măsoară 56 hm.", trail,
                               {"parts": 11, "one_part": 14, "small": 56, "large": 98},
                               "O parte măsoară 14 hm; restul măsoară 56 hm, iar partea parcursă 98 hm."),
    ]

    money = reverse.chain(96, [reverse.op("/", 8), reverse.op("*", 2), reverse.op("+", 4)])
    simple = reverse.chain(120, [reverse.op("/", 3), reverse.op("-", 10), reverse.op("/", 2)])
    questions += [
        reverse.exercise("Construiește drumul invers al unui calcul care pornește de la 96 lei.", "build_reverse_path",
                         reverse.values_for_reverse(money), "Pornim de la rezultat și aplicăm operațiile inverse.", **money),
        reverse.exercise("Așază operațiile inverse pentru traseul 120 → :3 → −10 → :2.", "drag_inverse_ops",
                         reverse.operations_for_reverse(simple), "Aplicăm ×2, +10 și ×3, în această ordine.", **simple,
                         operation_pool=["×2", "+10", "×3"]),
        reverse.exercise("Reconstituie suma: după ultima cumpărătură rămân 40 lei, înainte erau 60, apoi 84, iar inițial 96.",
                         "reverse_table", {"stage:1": 60, "stage:2": 84, "stage:3": 96},
                         "Tabelul se completează de la restul final spre suma inițială.",
                         stages=[{"label": "rest final", "value": 40}, {"label": "restul al doilea", "value": 60},
                                 {"label": "primul rest", "value": 84}, {"label": "suma inițială", "value": 96}]),
        reverse.exercise("Găsește primul pas invers greșit pentru traseul 120 → :3 → −10 → :2.", "reverse_error",
                         {"step": 1}, "După ×2 trebuie adunat 10, nu scăzut.", **simple,
                         shown_steps=["×2", "−10", "×3"]),
        reverse.exercise("Rezolvă puzzle-ul complet pentru traseul care începe cu 120.", "full_reverse_puzzle",
                         {**reverse.operations_for_reverse(simple), **reverse.values_for_reverse(simple), "start": 120},
                         "Drumul invers reface valoarea inițială 120.", **simple),
        reverse.exercise("Verifică traseul dus–întors care pornește de la 96.", "round_trip",
                         {"initial": 96, "final": money["end"], "verified": "yes"},
                         "Parcurgerea directă și cea inversă ajung la aceleași capete.", **money),
    ]

    vessels = hypothesis.scenario("vase cu apă", 12, 3, 7, 68,
                                  "vase de 1,5 l", "vase de 3,5 l", "jumătăți de litru", ("🥛", "🫙"))
    baskets = hypothesis.scenario("coșuri cu fructe", 20, 3, 7, 92,
                                  "coșuri mici", "coșuri mari", "fructe", ("🧺", "🍎"))
    questions += [
        hypothesis.exercise("Alege ipoteza de pornire pentru cele 12 vase.", "choose_hypothesis", vessels,
                            {"hypothesis": "low"}, "Presupunem mai întâi că toate vasele au 1,5 l.", choices=["low", "high"]),
        hypothesis.exercise("Simulează situația în care toate cele 12 vase au câte 1,5 l.", "all_same_simulator", vessels,
                            {"assumed_total": 36}, "În jumătăți de litru, totalul presupus este 12 · 3 = 36.", maximum=12),
        hypothesis.exercise("Măsoară diferența dintre totalul real și ipoteza vaselor mici.", "mismatch_meter", vessels,
                            {"mismatch": 32}, "Diferența este 68 − 36 = 32 jumătăți de litru."),
        hypothesis.exercise("Află câte vase mici trebuie înlocuite cu vase mari.", "replacement_count", vessels,
                            {"unit_difference": 4, "replacements": 8}, "O înlocuire adaugă 4 jumătăți de litru; 32 : 4 = 8."),
        hypothesis.exercise("Completează tabelul falsei ipoteze pentru vase.", "hypothesis_table", vessels,
                            {"assumed_total": 36, "mismatch": 32, "replacements": 8},
                            "Ipoteză 36, diferență 32, opt înlocuiri."),
        hypothesis.exercise("Rezolvă puzzle-ul complet al coșurilor cu fructe.", "full_hypothesis_puzzle", baskets,
                            hypothesis.core_answers(baskets), "Rezultă 12 coșuri mici și 8 coșuri mari."),
    ]

    questions += [
        missing("Gresia pentru 40% dintr-o podea costă 279,50 lei. Cât costă gresia pentru întreaga podea?",
                "40% → 279,50 lei; 100% → ?",
                [("one", "Costul pentru 1%"), ("total", "Costul total")],
                {"one": "6,9875", "total": "698,75"}, "279,50 : 40 = 6,9875 lei, apoi înmulțim cu 100."),
        missing("Din 3 600 t de cereale, 60% este grâu, 10% orz, iar restul porumb. Completează cantitățile.",
                "3 600 t = 60% grâu + 10% orz + 30% porumb",
                [("wheat", "Grâu (t)"), ("barley", "Orz (t)"), ("corn", "Porumb (t)")],
                {"wheat": "2160", "barley": "360", "corn": "1080"}, "Calculăm 60%, 10% și 30% din 3 600."),
        missing("O minge urcă la jumătate din înălțimea precedentă, apoi la jumătate, iar ultima dată la o treime și ajunge la 80 cm. Reconstituie înălțimea inițială.",
                "80 cm ← ×3 ← ×2 ← ×2",
                [("before3", "Înaintea ultimei urcări"), ("before2", "Înaintea celei de-a doua"), ("start", "Înălțimea inițială")],
                {"before3": "240", "before2": "480", "start": "960"}, "Mergem invers: 80 · 3 · 2 · 2 = 960 cm."),
        missing("Un elev are masa de 60 kg și înălțimea de 1,50 m. Calculează IMC = masă : înălțime².",
                "60 : (1,5 · 1,5)", [("square", "Înălțimea la pătrat"), ("imc", "IMC, rotunjit la sutimi")],
                {"square": "2,25", "imc": "26,67"}, "60 : 2,25 = 26,666..., deci aproximativ 26,67."),
        missing("Un test are 20 de întrebări. Un răspuns corect valorează 5 puncte, unul greșit −1,5 puncte. Un elev obține 87 de puncte. Câte răspunsuri corecte are?",
                "5 · corecte − 1,5 · greșite = 87",
                [("correct", "Răspunsuri corecte"), ("wrong", "Răspunsuri greșite")],
                {"correct": "18", "wrong": "2"}, "18 · 5 − 2 · 1,5 = 90 − 3 = 87."),
        missing("Douăsprezece vase de 1,5 l și 3,5 l conțin împreună 34 l. Câte sunt din fiecare fel?",
                "12 vase; total 34 l",
                [("small", "Vase de 1,5 l"), ("large", "Vase de 3,5 l")],
                {"small": "4", "large": "8"}, "Dacă toate erau mici aveam 18 l; diferența 16 l înseamnă 8 înlocuiri de câte 2 l."),
        missing("Patru robinete și cinci pompe umplu 105 hl într-o oră. O pompă are debit cât două robinete. Află debitele.",
                "4 robinete + 5 pompe; 1 pompă = 2 robinete",
                [("tap", "Un robinet (hl/oră)"), ("pump", "O pompă (hl/oră)")],
                {"tap": "7,5", "pump": "15"}, "Cele 5 pompe echivalează cu 10 robinete; 105 : 14 = 7,5 hl/oră pentru un robinet."),
        missing("La începutul unei excursii, 4/11 din traseu au rămas după două porțiuni și măsoară 5,6 km. Află traseul întreg.",
                "4/11 din traseu = 5,6 km",
                [("part", "O parte din 11 (km)"), ("total", "Traseul total (km)")],
                {"part": "1,4", "total": "15,4"}, "5,6 : 4 = 1,4 km pentru o parte; 1,4 · 11 = 15,4 km."),
        grid("Ce metodă este potrivită când ultima informație cunoscută este rezultatul final?", "Mersul invers",
             ["Falsa ipoteză", "Comparația", "Reducerea la unitate"], "Pornim de la final și refacem operațiile în ordine inversă."),
        grid("Ce metodă folosește un desen cu segmente pentru părți din același întreg?", "Metoda figurativă",
             ["Metoda comparației", "Falsa ipoteză", "Reducerea la unitate"], "Segmentele fac vizibile fracțiile și restul din întreg."),
        grid("Ce metodă presupune temporar că toate obiectele sunt de același tip?", "Falsa ipoteză",
             ["Mersul invers", "Metoda figurativă", "Comparația"], "Diferența față de total arată câte înlocuiri sunt necesare."),
    ]

    assert len(questions) == 45, len(questions)
    assert len({question["text"] for question in questions}) == len(questions)
    return questions


def main():
    output = Path(__file__).resolve().parents[1] / "clasa_5_metode_aritmetice_si_unitati_de_masura.json"
    payload = {"title": "Metode aritmetice pentru rezolvarea problemelor cu fracții în care intervin și unități de măsură pentru lungime, arie, volum, capacitate, masă, timp și unități monetare",
               "description": "Clasa a 5-a · Fracții zecimale", "difficulty": "medium",
               "questions": build_questions()}
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Scrise {len(payload['questions'])} exerciții în {output.name}")


if __name__ == "__main__":
    main()
