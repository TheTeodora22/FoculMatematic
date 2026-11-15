"""25 original Thales exercises for the existing separate lesson.

G2 has no dedicated Thales section: these are original foundation families,
without invented catalog attribution. No database writes.
"""
import json
from fractions import Fraction as F
from pathlib import Path

TARGET = next((Path(__file__).resolve().parents[1] / 'clasa_9').glob('clasa_9_u06_l02_*.json'))
BANK = 'g2_thales_original_v1'
NAMES = ['Thales direct: lungime necunoscută', 'Reciproca lui Thales: parametru pentru paralelism',
         'Paralele pe prelungiri și rapoarte orientate', 'Trei paralele și două transversale',
         'Raportul diagonalelor într-un trapez']


def add(a,b): return tuple(F(x)+F(y) for x,y in zip(a,b))
def sub(a,b): return tuple(F(x)-F(y) for x,y in zip(a,b))
def mul(k,a): return tuple(F(k)*F(x) for x in a)
def pair(a): return '('+'; '.join(str(F(x)) for x in a)+')'
def serial(a): return [str(F(x)) for x in a]


def build_questions():
    result=[]
    def emit(family,j,text,answer,reason,givens):
        if isinstance(answer,tuple):
            values=[pair(answer),pair(add(answer,(1,0))),pair(add(answer,(0,-1))),pair(add(answer,(-1,1)))]
            formatted=pair(answer)
        else:
            values=[str(F(answer)+k) for k in (0,1,-1,2)]
            formatted=str(answer)
        assert len(values)==len(set(values))==4
        correct=len(result)%4
        values.insert(correct,values.pop(0))
        result.append({'text':text,'type':'multiple_choice','format':'grid','points':10,
            'explanation':reason+f' Rezultatul este {formatted}.',
            'options':[{'text':value,'is_correct':i==correct} for i,value in enumerate(values)],
            'practice_scope':{'bank':BANK,'family':family,'family_name':NAMES[family-1],
                'variant':j,'catalog':None,'adaptation':'Exercițiu original de consolidare; fără atribuire de tip G2.'},
            'verification':givens})
    for j in range(1,6):
        ab,ac,am=3*j+6,4*j+8,j+1
        emit(1,j,f'În triunghiul ABC, AB={ab} cm și AC={ac} cm. M este interior segmentului AB, AM={am} cm, iar paralela prin M la BC intersectează AC în N. Calculați AN, în cm.',
            F(am*ac,ab),'Din MN∥BC, triunghiurile AMN și ABC sunt asemenea. Avem AM/AB=AN/AC; înmulțim raportul AM/AB cu AC. Originea comună A și ordinea interioară a punctelor justifică rapoartele de lungimi pozitive.',
            {'AB':ab,'AC':ac,'AM':am})

        a,b,c=(j,-j),(j+2,2*j+1),(-2*j-3,j+4)
        ratio=F(j+1,j+3)
        m=add(a,mul(ratio,sub(b,a)))
        emit(2,j,f'În reperul cartezian sunt A{pair(a)}, B{pair(b)}, C{pair(c)} și M{pair(m)}. Punctul N are poziția N=A+t(C−A), cu t real. Pentru ce t este dreapta MN paralelă cu BC?',
            ratio,'Vectorii AB și AC sunt necoliniari. Dacă AM=r·AB și AN=t·AC, atunci MN=t·AC−r·AB. Paralelismul cu BC=AC−AB impune t=r prin egalarea coeficienților în baza (AB,AC). Raportul r se obține din coordonatele lui M.',
            {'A':serial(a),'B':serial(b),'C':serial(c),'M':serial(m)})

        k=-F(j,2);m=add(a,mul(k,sub(b,a)));n=add(a,mul(k,sub(c,a)))
        emit(3,j,f'A{pair(a)}, B{pair(b)}, C{pair(c)} determină un triunghi. Punctul M este pe semidreapta opusă lui AB și AM=({k})AB ca vectori. Paralela prin M la BC intersectează dreapta AC în N. Aflați coordonatele lui N.',
            n,f'Forma orientată a lui Thales păstrează coeficientul k={k}: AN=k·AC. Prin urmare N=A+k(C−A). Coeficientul negativ pune N pe semidreapta opusă lui AC; nu se înlocuiește cu valoarea absolută. Vectorul MN=k·BC este nenul și paralel cu BC.',
            {'A':serial(a),'B':serial(b),'C':serial(c),'k':str(k),'M':serial(m)})

        lengths={'AB':j+1,'BC':2*j+3,'ApBp':j+2}
        emit(4,j,f'Trei drepte distincte paralele taie două transversale în A,B,C și A′,B′,C′, în această ordine pe fiecare transversală. AB={j+1} cm, BC={2*j+3} cm, A′B′={j+2} cm. Calculați B′C′, în cm.',
            F((2*j+3)*(j+2),j+1),'Teorema lui Thales pentru trei paralele dă AB/BC=A′B′/B′C′. Segmentele sunt consecutive și în ordine corespunzătoare. Rezolvăm produsul în cruce AB·B′C′=BC·A′B′; AB este strict pozitiv.', lengths)

        p,q,h=3*j+4,j+2,j+3
        emit(5,j,f'Trapezul convex ABCD are A=(0;0), B=({p};0), D=({j};{h}), C=({j+q};{h}). Diagonalele AC și BD se intersectează în O. Care este raportul lungimilor AO/OC?',
            F(p,q),'AB și DC sunt paralele. Triunghiurile AOB și COD sunt asemenea, deci AO/OC=AB/DC. Bazele au lungimile pozitive p și q; intersecția este interioară ambelor diagonale. Echivalent, pe AC parametrul lui O este p/(p+q), astfel AO/OC=[p/(p+q)]/[q/(p+q)].',
            {'A':['0','0'],'B':[str(p),'0'],'C':[str(j+q),str(h)],'D':[str(j),str(h)]})
    assert len(result)==25 and len({q['text'] for q in result})==25
    return result


def update_file():
    data=json.loads(TARGET.read_text(encoding='utf-8'))
    retained=[q for q in data['questions'] if q.get('practice_scope',{}).get('bank')!=BANK]
    data['questions']=retained+build_questions()
    data['difficulty']='medium'
    TARGET.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return len(data['questions'])


if __name__=='__main__':
    print(f'Thales: {update_file()} questions; 25 original grids.')
