"""Generează lecția despre c.m.m.d.c., amplificare și simplificare."""
import json, math
from pathlib import Path

def grid(text, correct, wrong, explanation):
    values=[str(correct),*[str(x) for x in wrong]]; order=[2,0,3,1]
    return {"text":text,"type":"multiple_choice","format":"grid","points":10,"explanation":explanation,"options":[{"text":values[i],"is_correct":i==0} for i in order]}
def tf(text, answer, explanation):
    return {"text":text,"type":"multiple_choice","format":"true_false","points":10,"explanation":explanation,"options":[{"text":x,"is_correct":x==answer} for x in ("Adevărat","Fals")]}
def iq(text, kind, data, explanation): return {"text":text,"type":kind,"format":"interactive","points":10,"explanation":explanation,"interactive":data}
def divisors(n): return [x for x in range(1,n+1) if n%x==0]
def csv(values): return ",".join(map(str,values))

def gcd_table(a,b):
    da,db=divisors(a),divisors(b); common=sorted(set(da)&set(db)); g=max(common)
    return iq(f"Completează tabelul divizorilor pentru {a} și {b}.","gcd_workbench",{"mode":"table","a":a,"b":b,"answers":{"divisors_a":csv(da),"divisors_b":csv(db),"common":csv(common),"gcd":g}},f"Divizorii comuni sunt {csv(common)}, iar cel mai mare este {g}.")
def gcd_select(a,b,candidates):
    common=[x for x in candidates if a%x==0 and b%x==0]; g=math.gcd(a,b)
    return iq(f"Găsește divizorii comuni ai numerelor {a} și {b}.","gcd_workbench",{"mode":"select","a":a,"b":b,"candidates":candidates,"answers":{"common":csv(common),"gcd":g}},f"Divizorii comuni sunt {csv(common)}; c.m.m.d.c. este {g}.")
def packing(a,b,label):
    g=math.gcd(a,b)
    return iq(label,"gcd_workbench",{"mode":"packing","a":a,"b":b,"answers":{"groups":g,"per_a":a//g,"per_b":b//g}},f"Putem forma cel mult {g} grupe, fiecare cu {a//g} și {b//g} obiecte.")
def scale(n,d,f,mode="amplify"):
    if mode=="amplify": ans={"factor":f,"result_numerator":n*f,"result_denominator":d*f}; text=f"Amplifică fracția {n}/{d} cu {f}."; exp=f"Înmulțim ambii termeni cu {f}."
    elif mode=="simplify": ans={"factor":f,"result_numerator":n//f,"result_denominator":d//f}; text=f"Simplifică fracția {n}/{d} cu {f}."; exp=f"Împărțim ambii termeni la {f}."
    elif mode=="missing_factor": ans={"factor":f,"result_numerator":n*f,"result_denominator":d*f}; text=f"Completează factorul și fracția echivalentă pornind de la {n}/{d}."; exp=f"Factorul comun este {f}."
    else: ans={"factor":f,"numerator":n,"denominator":d}; text=f"Refă fracția inițială știind că prin amplificare cu {f} s-a obținut {n*f}/{d*f}."; exp=f"Împărțim termenii rezultatului la {f}."
    data={"mode":mode,"numerator":n,"denominator":d,"factor":f,"result_numerator":n*f,"result_denominator":d*f,"answers":ans}
    return iq(text,"fraction_scale",data,exp)
def path(n,d,factors):
    steps=[]; a,b=n,d
    for f in factors: a//=f;b//=f;steps.append({"factor":f,"numerator":a,"denominator":b})
    return iq(f"Simplifică succesiv fracția {n}/{d} până la forma ireductibilă.","fraction_reduce_path",{"numerator":n,"denominator":d,"steps":steps},f"Forma ireductibilă este {a}/{b}.")

def build_questions():
    q=[
      grid("Care este c.m.m.d.c. al numerelor 18 și 24?",6,[2,3,12],"Cel mai mare divizor comun este 6."),
      grid("Care este c.m.m.d.c. al numerelor 35 și 42?",7,[1,5,6],"Divizorii comuni sunt 1 și 7."),
      grid("Numerele 13 și 30 sunt prime între ele deoarece c.m.m.d.c. este:",1,[13,30,390],"Au doar divizorul comun 1."),
      grid("Amplificând 3/5 cu 4 obținem:","12/20",["7/9","12/5","3/20"],"Înmulțim numărătorul și numitorul cu 4."),
      grid("Cu ce număr a fost amplificată fracția 2/7 pentru a obține 10/35?",5,[3,7,10],"2·5=10 și 7·5=35."),
      grid("Simplificând 24/36 cu 6 obținem:","4/6",["18/30","6/4","4/30"],"24:6=4 și 36:6=6."),
      grid("Forma ireductibilă a fracției 50/75 este:","2/3",["10/15","25/50","3/2"],"c.m.m.d.c.(50,75)=25."),
      grid("Care fracție este ireductibilă?","8/11",["6/18","12/10","49/64"],"8 și 11 au c.m.m.d.c. egal cu 1."),
      grid("Prin care număr se poate simplifica fracția 35/70?",5,[2,6,8],"5 divide atât 35, cât și 70."),
      grid("Ce numitor obținem amplificând 3/4 pentru a avea numărătorul 12?",16,[8,12,20],"Factorul este 4, deci 4·4=16."),
      grid("Care fracție NU este echivalentă cu 6/9?","12/15",["2/3","18/27","24/36"],"12/15=4/5, nu 2/3."),
      grid("Câte grupe identice, cel mult, se pot forma din 24 de mere și 36 de pere?",12,[6,18,24],"Numărul maxim de grupe este c.m.m.d.c.(24,36)=12."),
      grid("O fracție este ireductibilă dacă:","numărătorul și numitorul sunt prime între ele",["numărătorul este mai mic","numitorul este par","ambii termeni sunt compuși"],"C.m.m.d.c. al termenilor trebuie să fie 1."),
      grid("Simplificarea unei fracții înseamnă:","împărțirea ambilor termeni la același divizor comun",["scăderea aceluiași număr","împărțirea doar a numărătorului","adunarea termenilor"],"Valoarea fracției trebuie păstrată."),
      tf("Amplificarea păstrează valoarea fracției.","Adevărat","Se înmulțesc ambii termeni cu același număr nenul."),
      tf("Fracția 9/15 este ireductibilă.","Fals","Se poate simplifica prin 3."),
      tf("Două numere naturale consecutive sunt prime între ele.","Adevărat","Divizorul lor comun poate fi doar 1."),
      tf("La simplificare putem împărți numărătorul și numitorul prin numere diferite.","Fals","Trebuie folosit același divizor comun."),
    ]
    q += [gcd_table(18,24),gcd_table(15,30),gcd_select(24,36,[1,2,3,4,6,8,9,12]),gcd_select(14,25,[1,2,5,7,10,14,25]),packing(18,24,"Împarte sandvișurile în cât mai multe platouri identice."),packing(28,42,"Formează cât mai multe pachete identice din cele două colecții."),packing(32,48,"Așază obiectele în numărul maxim de cutii identice.")]
    q += [scale(1,3,4),scale(4,7,6),scale(5,12,7),scale(24,36,6,"simplify"),scale(42,49,7,"simplify"),scale(3,5,4,"missing_factor"),scale(7,9,3,"missing_factor"),scale(5,8,6,"restore"),scale(2,11,5,"restore"),scale(35,50,5,"simplify")]
    q += [path(36,96,[3,4]),path(50,75,[5,5]),path(84,126,[2,3,7]),path(64,200,[4,2]),path(90,150,[3,10])]
    assert len(q)==40
    return q
def main():
    target=Path(__file__).resolve().parents[1]/"clasa_5_fractii_ordinare_cmmdc_amplificarea_si_simplificarea.json"
    payload={"title":"Cel mai mare divizor comun a două numere naturale. Amplificarea și simplificarea fracțiilor. Fracții ireductibile","description":"Clasa a 5-a · Fracții ordinare","difficulty":"easy","questions":build_questions()}
    target.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");print(f"Am scris {len(payload['questions'])} întrebări în {target}.")
if __name__=="__main__": main()
