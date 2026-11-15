"""55 de grile originale: A2 §3.3 tipurile 7–11 și §3.4 tipurile 1–6."""
import json
from collections import Counter
from pathlib import Path
from catalog_grid_utils import GridBank, number_set

FILENAME='clasa_9_u02_l05_graficul_restrictiile_si_prelungirile_unei_functii_functii_numerice.json'
GRAPH_NAMES=['Imagine din diagramă','Preimagine din diagramă',
 'Imaginea intervalului prin funcție afină','Preimaginea intervalului prin funcție afină',
 'Recuperarea funcției din imaginea unui interval','Recuperarea funcției din preimagine',
 'Graficul ca mulțime de perechi','Reconstrucția funcției din grafic finit',
 'Apartenența unui punct la grafic','Restricția unei funcții','Extensia unei funcții']
NUMERIC_NAMES=['Grafic de funcție constantă','Grafic constant pe ramuri',
 'Intersecții cu axele','Funcție afină din interceptări',
 'Funcție parametrizată din interceptări','Numărul intersecțiilor cu Ox']

def pairs(points):
    return '{'+'; '.join(f'({x}, {y})' for x,y in sorted(points))+'}'

def build():
    graph=GridBank('A2.3.3',GRAPH_NAMES)
    numeric=GridBank('A2.3.4',NUMERIC_NAMES)
    for j in range(1,6):
        q=j+1
        d={-1,0,2}
        points={(x,q*x+j) for x in d}
        graph.add(7,f'Fie f:{{−1;0;2}}→ℝ, f(x)={q}x+{j}. Care este graficul G_f?',
            pairs(points),[pairs({(y,x) for x,y in points}),pairs({(x,q*x) for x in d}),pairs({(x,q*x+j) for x in {0,1,2}})],
            f'Graficul este mulțimea perechilor (x,f(x)) cu x în domeniu. Calculăm f(−1)=−1, f(0)={j}, f(2)={2*q+j}; rezultă {pairs(points)}. Nu includem alte abscise și nu inversăm coordonatele.')
        finite={(1,j),(2,j),(3,j+2)}
        graph.add(8,f'Graficul unei funcții este G={pairs(finite)}. Care sunt domeniul D și cel mai mic codomeniu posibil C?',
            f'D={{1;2;3}}, C={{{j};{j+2}}}',
            [f'D={{{j};{j+2}}}, C={{1;2;3}}',f'D={{1;2;3}}, C={{{j}}}',f'D={{1;2}}, C={{{j};{j+2}}}'],
            f'Prima proiecție a graficului este domeniul {{1;2;3}}. A doua proiecție este imaginea {{{j};{j+2}}}, care este cel mai mic codomeniu posibil. Alte codomenii pot fi orice supramulțimi ale imaginii; codomeniul nu se determină unic doar din grafic.')
        target=q*(j+2)+j
        graph.numeric(9,f'Fie f:ℝ→ℝ, f(x)={q}x+{j}. Pentru ce m punctul (m, {target}) aparține lui G_f?',j+2,
            f'Condiția este {target}=f(m)={q}m+{j}. Rezultă m=({target}−{j})/{q}={j+2}. Domeniul este ℝ, deci soluția este admisă.')
        subset={1,3,5}
        graph.add(10,f'Fie f:ℝ→ℝ, f(x)=x²+{j}. Care este graficul restricției lui f la A={{1;3;5}}?',
            pairs({(x,x*x+j) for x in subset}),
            [pairs({(x,x+j) for x in subset}),pairs({(x,x*x+j) for x in {0,1,2}}),pairs({(x*x+j,x) for x in subset})],
            f'Restricția păstrează valorile și codomeniul lui f, dar are domeniul A. Valorile sunt {1+j}, {9+j}, {25+j}; graficul conține exact cele trei perechi corespunzătoare.')
        graph.add(11,f'Fie f:[0,{j}]→ℝ, f(x)=x+{j}. Care funcție g:ℝ→ℝ este o prelungire a lui f?',
            rf'\(g(x)=\begin{{cases}}x+{j},&x\ge0\\x^2,&x<0\end{{cases}}\)',
            [f'g(x)=x+{j+1} pentru orice x',f'g(x)=−x+{j} pentru orice x',f'g(x)=x+{j} dacă x<0 și g(x)=x+{j+1} dacă x≥0'],
            f'O prelungire are domeniu mai mare și coincide cu f pe ÎNTREGUL domeniu inițial. Varianta corectă dă x+{j} pentru orice x∈[0,{j}], inclusiv 0 și {j}; valorile pentru x<0 pot fi alese liber. Prima și ultima variantă eșuează la 0, iar g(x)=−x+{j} eșuează la x={j}>0. Prelungirea nu este unică.')
        numeric.add(1,f'Fie f:[−{j},{j+2})→ℝ, f(x)={q}. Care este graficul său?',
            f'Segment orizontal y={q}, −{j}≤x<{j+2}',
            [f'Dreapta orizontală y={q}',f'Segment vertical x={q}, −{j}≤y<{j+2}',f'Segment orizontal y={q}, −{j}<x≤{j+2}'],
            f'Toate punctele au ordonata {q}, dar abscisele parcurg numai [−{j},{j+2}). Graficul este segmentul orizontal cu extremitatea stângă inclusă și cea dreaptă exclusă. Nu este dreapta întreagă, deoarece domeniul este limitat.')
        correct=f'{{(x,−{j}) | x<0}} ∪ {{(x,{q}) | 0≤x<2}} ∪ {{(x,0) | x≥2}}'
        numeric.add(2,rf'Funcția f:ℝ→ℝ este definită prin \(f(x)=\begin{{cases}}-{j},&x<0\\{q},&0\le x<2\\0,&x\ge2\end{{cases}}\). Care mulțime reprezintă graficul ei?',
            correct,
            [f'{{(x,−{j}) | x≤0}} ∪ {{(x,{q}) | 0<x<2}} ∪ {{(x,0) | x≥2}}',
             f'{{(x,−{j}) | x<0}} ∪ {{(x,{q}) | 0≤x≤2}} ∪ {{(x,0) | x>2}}',
             f'{{(x,{j}) | x<0}} ∪ {{(x,{q}) | 0≤x<2}} ∪ {{(x,0) | x≥2}}'],
            f'Fiecărei ramuri îi corespunde o porțiune orizontală. La x=0 se aplică ramura mediană, deci (0,{q}) este inclus, iar (0,−{j}) este exclus. La x=2 se aplică ultima ramură: (2,0) este inclus și (2,{q}) exclus. Pentru x<0 ordonata este −{j}, nu {j}.')
        intercept=j+2;beta=q*intercept
        numeric.add(3,f'Fie f:ℝ→ℝ, f(x)=−{q}x+{beta}. Care sunt intersecțiile graficului cu Ox, respectiv Oy?',
            f'({intercept}, 0), (0, {beta})',
            [f'(0, {intercept}), ({beta}, 0)',f'({-intercept}, 0), (0, {beta})',f'({intercept}, 0), (0, {-beta})'],
            f'Pe Ox avem y=0: −{q}x+{beta}=0, deci x={intercept}. Pe Oy avem x=0: y=f(0)={beta}. Rezultă ({intercept},0), respectiv (0,{beta}).')
        numeric.add(4,f'Graficul funcției afine f:ℝ→ℝ intersectează Ox în ({intercept},0) și Oy în (0,{beta}). Aflați (a;b) pentru f(x)=ax+b.',
            f'({-q};{beta})',[f'({q};{beta})',f'({-q};{-beta})',f'({-q-1};{beta})'],
            f'Din f(0)={beta} rezultă b={beta}. Apoi f({intercept})=0 dă {intercept}a+{beta}=0, deci a=−{q}. Ambele intersecții sunt astfel verificate.')
        numeric.numeric(5,f'Fie f_m:ℝ→ℝ, f_m(x)=(m−1)x+{q}. Graficul trece prin (0,{q}) și intersectează Ox în (−1,0). Aflați m.',q+1,
            f'Condiția f_m(0)={q} este automată. Din f_m(−1)=0 obținem −(m−1)+{q}=0, deci m={q+1}. Panta m−1={q}≠0, astfel intersecția cu Ox este unică.')
        numeric.add(6,f'Pentru ce valori reale ale lui m graficul lui f_m(x)=(m−{j})x²+2x+1, x∈ℝ, intersectează Ox în exact un punct?',
            number_set([j,j+1]),[number_set([j]),number_set([j+1]),number_set([j-1,j])],
            f'Dacă m={j}, termenul de grad doi dispare: 2x+1=0 are o singură soluție. Dacă m≠{j}, ecuația este de grad doi și are o singură rădăcină reală distinctă exact când Δ=4−4(m−{j})=0, adică m={j+1}. Ambele cazuri sunt necesare: mulțimea cerută este {{{j};{j+1}}}.')
    result=graph.finish(Counter({i:5 for i in range(7,12)}))+numeric.finish(Counter({i:5 for i in range(1,7)}))
    assert len({q['text'] for q in result})==55
    return result

if __name__=='__main__':
    path=Path(__file__).resolve().parents[1]/'clasa_9'/FILENAME
    payload=json.loads(path.read_text(encoding='utf-8'))
    payload.update(difficulty='medium',questions=build())
    path.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('55 grile generate')
