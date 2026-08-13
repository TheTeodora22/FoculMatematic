"""Generează lecția „Metoda falsei ipoteze” pentru clasa a V-a."""
import json
from pathlib import Path
import false_hypothesis_factory as f


def grid(text, correct, wrong, explanation):
    correct=str(correct); distractors=[]
    for value in wrong:
        value=str(value)
        if value!=correct and value not in distractors: distractors.append(value)
    fallback=1
    while len(distractors)<3:
        value=str(int(correct)+fallback) if correct.lstrip("-").isdigit() else f"alt rezultat {fallback}"
        if value!=correct and value not in distractors: distractors.append(value)
        fallback+=1
    values=[correct,*distractors[:3]]
    return {"text":text,"format":"grid","points":10,"explanation":explanation,
            "options":[{"text":value,"is_correct":i==0} for i,value in enumerate(values)]}


def build_questions():
    cases=[
        f.scenario("bidoane",10,3,10,72,"bidoane de 3 l","bidoane de 10 l","litri",("🫙","🛢️")),
        f.scenario("găini și iepuri",100,2,4,240,"găini","iepuri","picioare",("🐔","🐇")),
        f.scenario("apartamente",18,2,3,42,"apartamente cu 2 camere","apartamente cu 3 camere","camere",("🏠","🏢")),
        f.scenario("probleme de concurs",7,-1,4,18,"probleme greșite","probleme corecte","puncte",("✗","✓")),
        f.scenario("bancnote",9,5,10,65,"bancnote de 5 lei","bancnote de 10 lei","lei",("💵","💶")),
        f.scenario("albine",60,20,25,1310,"vizite la 20 de flori","vizite la 25 de flori","flori",("🐝","🌼")),
        f.scenario("acțiuni",18,12,25,346,"acțiuni de 12 euro","acțiuni de 25 euro","euro",("📄","📈")),
        f.scenario("păsări și vite",320,2,4,880,"păsări","vite","picioare",("🐦","🐄")),
        f.scenario("vase",7,3,20,89,"vase de 3 l","vase de 20 l","litri",("🥛","🫙")),
        f.scenario("săgeți",8,-3,10,54,"săgeți în afara cercului","săgeți în interior","puncte",("○","🎯")),
        f.scenario("probleme rezolvate",6,-2,10,48,"probleme greșite","probleme corecte","puncte",("✗","✓")),
        f.scenario("coșuri cu fructe",20,3,7,92,"coșuri mici","coșuri mari","fructe",("🧺","🍎")),
        f.scenario("bilete",50,8,12,460,"bilete de 8 lei","bilete de 12 lei","lei",("🎫","🎟️")),
        f.scenario("monede",30,2,5,99,"monede de 2 lei","monede de 5 lei","lei",("🪙","💰")),
        f.scenario("pachete de cărți",24,10,15,285,"pachete mici","pachete mari","cărți",("📘","📚")),
    ]
    questions=[]
    for c in cases:
        questions.append(grid(f"În problema cu {c['label']}, dacă presupunem că toate sunt «{c['low_name']}», ce total obținem?",c["assumed_total"],[c["total"],c["mismatch"],c["count"]*c["high"]],f"{c['count']} · {c['low']} = {c['assumed_total']}."))

    modes=["choose_hypothesis","all_same_simulator","mismatch_meter","replacement_count","heads_legs","score_cards","containers","money_notes","bees_flowers","shares","vases","hypothesis_error","hypothesis_table","full_hypothesis_puzzle","hypothesis_verify"]
    for mode_index,mode in enumerate(modes):
        for variant in range(3):
            c=cases[(mode_index*3+variant)%len(cases)]
            prefix=f"{mode.replace('_',' ')} – {c['label']}"
            if mode=="choose_hypothesis":
                answers={"hypothesis":"low"}; extra={"choices":["low","high"]}; explanation=f"Presupunem toate obiectele de tipul cu valoarea {c['low']}."
            elif mode=="all_same_simulator":
                answers={"assumed_total":c["assumed_total"]}; extra={"maximum":c["count"]}; explanation=f"Ipoteza produce totalul {c['assumed_total']}."
            elif mode=="mismatch_meter":
                answers={"mismatch":c["mismatch"]}; extra={}; explanation=f"Nepotrivirea este {c['total']} − {c['assumed_total']} = {c['mismatch']}."
            elif mode=="replacement_count":
                answers={"unit_difference":c["unit_difference"],"replacements":c["high_count"]}; extra={}; explanation=f"O înlocuire schimbă totalul cu {c['unit_difference']}; sunt necesare {c['high_count']} înlocuiri."
            elif mode in {"heads_legs","score_cards","containers","money_notes","bees_flowers","shares","vases"}:
                answers={"high_count":c["high_count"],"low_count":c["low_count"]}; extra={"theme":mode}; explanation=f"Rezultă {c['high_count']} «{c['high_name']}» și {c['low_count']} «{c['low_name']}»."
            elif mode=="hypothesis_error":
                answers={"step":2}; extra={"steps":[f"Presupunem toate: {c['low_name']}",f"Total ipotetic: {c['assumed_total']}",f"Nepotrivire: {abs(c['total']+c['assumed_total'])}",f"O înlocuire: {c['unit_difference']}"]}; explanation=f"Nepotrivirea corectă este {c['mismatch']}."
            elif mode=="hypothesis_table":
                answers={"assumed_total":c["assumed_total"],"mismatch":c["mismatch"],"replacements":c["high_count"]}; extra={}; explanation="Completăm tabelul în ordinea ipoteză, nepotrivire, înlocuiri."
            elif mode=="full_hypothesis_puzzle":
                answers=f.core_answers(c); extra={}; explanation=f"Soluția completă este {c['low_count']} și {c['high_count']}."
            else:
                answers={"high_count":c["high_count"],"low_count":c["low_count"],"verified_total":c["total"],"verified":"yes"}; extra={}; explanation=f"Verificare: {c['low_count']}·{c['low']} + {c['high_count']}·{c['high']} = {c['total']}."
            questions.append(f.exercise(prefix,mode,c,answers,explanation,**extra))
    assert len(questions)==60
    assert len({q["text"] for q in questions})==60
    return questions


def main():
    output=Path(__file__).resolve().parent.parent/"clasa_5_metoda_falsei_ipoteze.json"
    payload={"title":"Metoda falsei ipoteze","description":"Clasa a 5-a · Metode aritmetice de rezolvare a problemelor","difficulty":"medium","questions":build_questions()}
    output.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(f"Scrise {len(payload['questions'])} exerciții în {output.name}")


if __name__=="__main__": main()
