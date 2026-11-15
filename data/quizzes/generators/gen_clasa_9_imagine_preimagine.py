"""Imagine și preimagine: 6 tipuri A2 §3.3, cinci variante fiecare."""
import json
from collections import Counter
from pathlib import Path
from catalog_grid_utils import GridBank, number_set

TITLE = 'Imaginea și preimaginea unei funcții'
FILENAME = 'clasa_9_u02_l04_notiunea_imaginea_si_preimaginea_unei_functii.json'
NAMES = ['Imagine din diagramă', 'Preimagine din diagramă',
 'Imaginea intervalului prin funcție afină',
 'Preimaginea intervalului prin funcție afină',
 'Recuperarea funcției din imaginea unui interval',
 'Recuperarea funcției din preimagine']


def build():
    bank=GridBank('A2.3.3',NAMES)
    for j in range(1,6):
        values=[j,j+1,j,j+2]
        arrows=', '.join(f'{k}↦{v}' for k,v in enumerate(values,1))
        bank.add(1, f'Funcția f:{{1;2;3;4}}→{{{j};{j+1};{j+2}}} este dată prin săgețile {arrows}. Determinați f({{1;2;3}}).',
            number_set([j,j+1]),
            [number_set([j,j+1,j+2]),number_set([1,2,3,4]),number_set([j+1,j+2])],
            f'Urmărim săgețile: f(1)={j}, f(2)={j+1}, f(3)={j}. Imaginea este mulțimea {number_set([j,j+1])}; valoarea {j} se scrie o singură dată. f(4) nu intervine deoarece 4 nu este în submulțimea dată.')
        bank.add(2, f'Funcția f:{{1;2;3;4}}→{{{j};{j+1};{j+2}}} este dată prin {arrows}. Aflați preimaginea f⁻¹({{{j};{j+2}}}).',
            number_set([1,3,4]),[number_set([1,3]),number_set([1,2,3,4]),number_set([2,4])],
            f'Căutăm TOATE argumentele x din domeniu pentru care f(x)∈{{{j};{j+2}}}. Argumentele 1 și 3 au imaginea {j}, iar 4 are imaginea {j+2}. Argumentul 2 are imaginea {j+1}, deci este exclus. Preimaginea este {{1;3;4}}. Notația f⁻¹ desemnează preimaginea unei mulțimi și nu presupune existența unei funcții inverse.')
        q=j+1
        lo=-q*(j+2)+j;hi=q+j
        bank.add(3, f'Fie f:ℝ→ℝ, f(x)=−{q}x+{j}. Determinați imaginea intervalului [−1, {j+2}).',
            f'({lo}, {hi}]',[f'[{lo}, {hi}]',f'[{lo}, {hi})',f'({lo}, {hi})'],
            f'Panta −{q} este negativă, deci f este strict descrescătoare. Capătul −1 este inclus și are imaginea {hi}; capătul {j+2} este exclus și ar avea imaginea {lo}. Prin urmare imaginea este ({lo},{hi}], cu ordinea și tipul capetelor inversate.')
        bound=2*j+1
        bank.add(4, f'Fie f:ℝ→ℝ, f(x)=−{q}x+{j}. Aflați f⁻¹((−∞, {j-q*bound}]).',
            f'[{bound}, +∞)',[f'({bound}, +∞)',f'(−∞, {bound}]',f'(−∞, {bound})'],
            f'Condiția este −{q}x+{j}≤{j-q*bound}, adică −{q}x≤{-q*bound}. Împărțirea la −{q}<0 inversează sensul: x≥{bound}. Egalitatea este admisă; preimaginea este [{bound},+∞).')
        offset=j-2
        left=q*j+offset;right=q*(j+2)+offset
        bank.add(5, f'O funcție afină f:ℝ→ℝ este strict crescătoare și f([{j}, {j+2}])=[{left}, {right}]. Determinați perechea (a; b) din f(x)=ax+b.',
            f'({q}; {offset})',[f'({-q}; {offset})',f'({q}; {offset+1})',f'({q+1}; {offset})'],
            f'Din creștere, f({j})={left}, f({j+2})={right}. Scăzând ecuațiile obținem 2a={right-left}, deci a={q}>0. Apoi b={left}−{q}·{j}={offset}. Aceste valori trimit exact capetele în capetele cerute.')
        # O preimagine de interval mărginit exclude panta nulă.
        low=offset-q*(j+2);high=offset-q*j
        bank.add(6, f'O funcție afină f:ℝ→ℝ este strict descrescătoare și f⁻¹([{low}, {high}))=({j}, {j+2}]. Determinați (a; b), unde f(x)=ax+b.',
            f'({-q}; {offset})',[f'({q}; {offset})',f'({-q}; {offset+1})',f'({-q-1}; {offset})'],
            f'Pentru o funcție afină strict descrescătoare, f({j})={high} este capătul exclus al intervalului țintă, iar f({j+2})={low} este capătul inclus. Scăderea dă 2a={low-high}, deci a=−{q}; apoi b={high}−(−{q})·{j}={offset}. Verificarea {low}≤−{q}x+{offset}<{high} dă exact {j}<x≤{j+2}.')
    return bank.finish(Counter({i:5 for i in range(1,7)}))


if __name__=='__main__':
    path=Path(__file__).resolve().parents[1]/'clasa_9'/FILENAME
    data=json.loads(path.read_text(encoding='utf-8'))
    data.update(title=TITLE,difficulty='medium',questions=build())
    path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('30 grile generate')
