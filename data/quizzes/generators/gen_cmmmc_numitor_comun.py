"""Generează lecția despre c.m.m.m.c. și numitorul comun."""
import json, math
from pathlib import Path

def grid(text,correct,wrong,explanation):
    v=[str(correct),*[str(x) for x in wrong]]; order=[2,0,3,1]
    return {"text":text,"type":"multiple_choice","format":"grid","points":10,"explanation":explanation,"options":[{"text":v[i],"is_correct":i==0} for i in order]}
def tf(text,answer,explanation):
    return {"text":text,"type":"multiple_choice","format":"true_false","points":10,"explanation":explanation,"options":[{"text":x,"is_correct":x==answer} for x in ("Adevărat","Fals")]}
def iq(text,kind,data,explanation): return {"text":text,"type":kind,"format":"interactive","points":10,"explanation":explanation,"interactive":data}
def lcm(a,b): return a*b//math.gcd(a,b)
def csv(v): return ",".join(map(str,v))
def multiples(n,count=8): return [n*i for i in range(1,count+1)]

def lcm_lists(a,b):
    m=lcm(a,b); ma=[x for x in multiples(a,10) if x<=m*3]; mb=[x for x in multiples(b,10) if x<=m*3]; common=[m,2*m,3*m]
    return iq(f"Completează șirurile de multipli pentru {a} și {b}.","lcm_workbench",{"mode":"lists","a":a,"b":b,"answers":{"multiples_a":csv(ma),"multiples_b":csv(mb),"common":csv(common),"lcm":m}},f"Primul multiplu comun nenul este {m}.")
def lcm_select(a,b,candidates):
    common=[x for x in candidates if x%a==0 and x%b==0]; m=lcm(a,b)
    return iq(f"Selectează multiplii comuni ai numerelor {a} și {b}.","lcm_workbench",{"mode":"select","a":a,"b":b,"candidates":candidates,"answers":{"common":csv(common),"lcm":m}},f"Cel mai mic dintre multiplii comuni selectați este {m}.")
def common_den(left,right,wording=None):
    a,b=left;c,d=right; den=lcm(b,d); lf=den//b;rf=den//d
    text=wording or f"Adu fracțiile {a}/{b} și {c}/{d} la cel mai mic numitor comun."
    ans={"left_factor":lf,"right_factor":rf,"left_numerator":a*lf,"right_numerator":c*rf,"common_denominator":den}
    return iq(text,"common_denominator",{"mode":"build","left":[a,b],"right":[c,d],"answers":ans},f"c.m.m.m.c.({b},{d})={den}; factorii sunt {lf} și {rf}.")
def missing_value(left,known_value,answer,position):
    n,d=left
    shown=f"?/{known_value}" if position=="numerator" else f"{known_value}/?"
    return iq(f"Completează: {n}/{d} = {shown}.","common_denominator",{"mode":"missing","left":[n,d],"right":[answer,known_value] if position=="numerator" else [known_value,answer],"missing_position":position,"known_value":known_value,"answers":{"missing":answer}},f"Amplificăm ambii termeni cu același factor; valoarea lipsă este {answer}.")
def error_case(text,left,right,steps,error_index,explanation):
    return iq(text,"common_denominator",{"mode":"error","left":list(left),"right":list(right),"steps":steps,"answers":{"error_index":error_index}},explanation)

def build_questions():
    q=[
      grid("Care este c.m.m.m.c. al numerelor 6 și 8?",24,[12,36,48],"Primul multiplu comun nenul este 24."),
      grid("Care este c.m.m.m.c. al numerelor 4 și 9?",36,[18,13,72],"4 și 9 sunt prime între ele, deci produsul este 36."),
      grid("Alege cel mai mic multiplu comun al numerelor 12 și 18.",36,[6,24,72],"36 este primul număr divizibil cu 12 și cu 18."),
      grid("Dacă 5 divide 20, atunci c.m.m.m.c.(5,20) este:",20,[5,25,100],"Când un număr îl divide pe celălalt, c.m.m.m.c. este numărul mai mare."),
      grid("Două turnuri folosesc piese de 6 cm și 8 cm. Care este cea mai mică înălțime comună?","24 cm",["14 cm","36 cm","48 cm"],"Căutăm c.m.m.m.c.(6,8)=24."),
      grid("Cel mai mic numitor comun pentru 1/6 și 5/8 este:",24,[14,36,48],"Este c.m.m.m.c.(6,8)."),
      grid("Aducând 3/4 și 5/6 la numitorul 12 obținem:","9/12 și 10/12",["6/12 și 10/12","9/12 și 5/12","3/12 și 5/12"],"Amplificăm prima fracție cu 3 și a doua cu 2."),
      grid("Cu ce factor amplificăm 7/9 pentru a avea numitorul 36?",4,[3,9,27],"9·4=36."),
      grid("Cu ce factor amplificăm 5/12 pentru a avea numitorul 60?",5,[4,12,48],"12·5=60."),
      grid("Care pereche este adusă corect la același numitor?","2/3=8/12 și 3/4=9/12",["2/3=6/12 și 3/4=9/12","2/3=8/12 și 3/4=6/12","2/3=4/12 și 3/4=9/12"],"Factorii sunt 4 și 3."),
      grid("După aducerea la numitor comun, care este mai mare: 3/5 sau 4/7?","3/5",["4/7","Sunt egale","Nu se pot compara"],"3/5=21/35, iar 4/7=20/35."),
      grid("Ordinea crescătoare a fracțiilor 2/3, 3/5 și 5/6 este:","3/5, 2/3, 5/6",["2/3, 3/5, 5/6","5/6, 2/3, 3/5","3/5, 5/6, 2/3"],"La numitorul 30 obținem 18/30, 20/30 și 25/30."),
      grid("Dacă numitorii sunt 15 și 25, cel mai mic numitor comun este:",75,[5,40,375],"c.m.m.m.c.(15,25)=75."),
      grid("Relația dintre c.m.m.d.c. și c.m.m.m.c. pentru a și b este:","c.m.m.d.c. · c.m.m.m.c. = a · b",["c.m.m.d.c. + c.m.m.m.c. = a+b","c.m.m.m.c. = a+b","c.m.m.d.c. = a·b"],"Produsul celor două este egal cu produsul numerelor."),
      tf("Cel mai mic multiplu comun este întotdeauna diferit de zero.","Adevărat","Definiția cere cel mai mic multiplu comun nenul."),
      tf("Dacă două numere sunt prime între ele, c.m.m.m.c. este produsul lor.","Adevărat","C.m.m.d.c. este 1, deci c.m.m.m.c.=a·b."),
      tf("Pentru a aduce fracții la același numitor trebuie să le schimbăm valoarea.","Fals","Folosim fracții echivalente, deci valoarea se păstrează."),
      tf("Numitorul comun ales poate fi orice multiplu comun al numitorilor, dar de obicei îl folosim pe cel mai mic.","Adevărat","Cel mai mic numitor comun produce numere mai ușor de calculat."),
    ]
    q += [lcm_lists(3,5),lcm_lists(6,8),lcm_lists(12,18),lcm_select(4,6,[8,12,16,18,24,30,36,48]),lcm_select(5,7,[20,28,35,42,70,105])]
    pairs=[((1,2),(7,15)),((3,4),(16,25)),((3,14),(2,9)),((7,12),(8,5)),((1,6),(5,8)),((5,9),(2,3)),((7,18),(8,27)),((3,10),(7,15)),((5,12),(11,20)),((4,21),(5,14)),((9,20),(11,30)),((2,7),(3,5)),((5,16),(49,96)),((3,8),(5,12))]
    q += [common_den(a,b) for a,b in pairs[:11]]
    q += [
      missing_value((2,3),8,12,"denominator"),
      missing_value((5,12),60,25,"numerator"),
      missing_value((3,8),15,40,"denominator"),
      error_case("Identifică primul pas greșit în aducerea fracțiilor 2/3 și 5/8 la același numitor.",(2,3),(5,8),["c.m.m.m.c.(3, 8) = 24","24 : 3 = 8 și 24 : 8 = 3","2/3 = 18/24","5/8 = 15/24"],2,"La pasul 3, numărătorul corect este 2 · 8 = 16, nu 18."),
      error_case("Identifică primul pas greșit în aducerea fracțiilor 3/4 și 7/10 la același numitor.",(3,4),(7,10),["c.m.m.m.c.(4, 10) = 20","Factorii de amplificare sunt 5 și 2","3/4 = 15/20","7/10 = 7/20"],3,"Ultima transformare este greșită: 7/10 amplificată cu 2 este 14/20."),
      error_case("Identifică primul pas greșit în aducerea fracțiilor 5/6 și 3/14 la același numitor.",(5,6),(3,14),["c.m.m.m.c.(6, 14) = 84","Factorii sunt 14 și 6","5/6 = 70/84","3/14 = 18/84"],0,"Primul pas este greșit: c.m.m.m.c.(6,14)=42, nu 84."),
    ]
    assert len(q)==40
    return q
def main():
    target=Path(__file__).resolve().parents[1]/"clasa_5_fractii_ordinare_cmmmc_numitor_comun.json"
    payload={"title":"Cel mai mic multiplu comun a două numere naturale. Aducerea fracțiilor la un numitor comun","description":"Clasa a 5-a · Fracții ordinare","difficulty":"easy","questions":build_questions()}
    target.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");print(f"Am scris {len(payload['questions'])} întrebări în {target}.")
if __name__=="__main__":main()
