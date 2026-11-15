"""80 de grile originale după cele 16 tipuri din A2, §1.1, p. 63–66."""
import json
import re
from collections import Counter
from fractions import Fraction as F
from pathlib import Path
from catalog_grid_utils import GridBank

NAMES = [
    'Termeni din formulă explicită', 'Termeni din recurență',
    'Formula unui șir descris prin termeni', 'Apartenența la un șir',
    'Șir produs cumulativ', 'Șirul diferențelor consecutive',
    'Recurență aditivă cu indice', 'Recurență liniară de ordin doi',
    'Recurență pe indici din două în două',
    'Recurență multiplicativă cu coeficient de rang',
    'Recuperarea termenului din suma parțială', 'Periodicitate recurentă',
    'Sume ale numerelor Fibonacci', 'Pătrate și produse Fibonacci',
    'Subșiruri și identități Fibonacci', 'Șir determinat de identități de produse',
]


def build():
    b = GridBank('A2.1.1', NAMES)
    def add(t, text, correct, wrong, explanation):
        b.add(t, text, correct, wrong, explanation)
    def num(t, text, value, explanation):
        b.numeric(t, text, value, explanation)
    fib = [0, 1]
    for _ in range(30):
        fib.append(sum(fib[-2:]))
    for j in range(1, 6):
        n = j + 2
        num(1, f'Fie aₙ=n(n+{j}), n≥1. Calculați a_{n}.', n*(n+j),
            f'Înlocuim n={n}: a_{n}={n}·({n}+{j})={n*(n+j)}.')
        q = j+1
        num(2, f'Dacă xₙ₊₁={q}xₙ+{j}, n≥1, și x₁=1, calculați x₄.',
            q**3+j*(q*q+q+1),
            f'x₂={q+j}, x₃={q*(q+j)+j}, x₄={q**3+j*(q*q+q+1)}. Aplicăm relația de trei ori.')
        add(3, f'Al n-lea termen este numărul cu exact n cifre, toate egale cu {j}, n≥1. Care este formula lui aₙ?',
            rf'\({j}(10^n-1)/9\)',
            [rf'\({j}10^n\)', rf'\({j}(10^n+1)/9\)', rf'\({j}(10^{{n-1}}-1)/9\)'],
            f'aₙ={j}(1+10+⋯+10ⁿ⁻¹). Suma geometrică este (10ⁿ−1)/9. Descrierea prin cifre fixează regula pentru orice n.')
        c = n*(n+j)
        num(4, f'Pentru aₙ=n(n+{j}), n≥1, determinați rangul termenului egal cu {c}.', n,
            f'Ecuația n²+{j}n−{c}=0 are rădăcinile {n} și {-(n+j)}. Numai {n} este indice natural pozitiv.')
        add(5, rf'Fie aₖ=(k+{j})/(k+{j+1}), k≥1. Determinați \(b_n=\prod_{{k=1}}^n a_k\).',
            rf'\({j+1}/(n+{j+1})\)',
            [rf'\(1/(n+{j+1})\)', rf'\((n+{j+1})/{j+1}\)', rf'\({j+1}/(n+{j})\)'],
            f'Produsul este ({j+1}/{j+2})·({j+2}/{j+3})·⋯·((n+{j})/(n+{j+1})). Se reduc factorii intermediari și rămâne {j+1}/(n+{j+1}).')
        num(6, rf'Fie aₖ=k²+{j}, k≥1. Calculați \(\sum_{{k=1}}^{{{n}}}(a_{{k+1}}-a_k)\).', (n+1)**2-1,
            f'aₖ₊₁−aₖ=2k+1. Suma telescopică este a_{n+1}−a₁=({(n+1)**2}+{j})−(1+{j})={(n+1)**2-1}.')
        add(7, f'Fie a₁={j}, aₙ₊₁=aₙ+2n, n≥1. Care este termenul general?',
            rf'\(a_n={j}+n(n-1)\)',
            [rf'\(a_n={j}+n(n+1)\)', rf'\(a_n={j}+2n\)', rf'\(a_n={j}+n^2\)'],
            f'Însumăm aₖ₊₁−aₖ=2k pentru k=1,…,n−1: aₙ−{j}=2·n(n−1)/2=n(n−1). Formula este valabilă și la n=1.')
        add(8, f'Fie a₀=2, a₁={q+1}, aₙ₊₂={q+1}aₙ₊₁−{q}aₙ, n≥0. Care formulă este corectă pentru orice n≥0?',
            rf'\(a_n={q}^n+1\)',
            [rf'\(a_n={q}^n-1\)', rf'\(a_n={q}^n+n\)', rf'\(a_n=2\cdot {q}^n\)'],
            f'La n=0 obținem 2, iar la n=1 obținem {q+1}. Dacă formula este adevărată la n și n+1, recurența dă ({q+1})({q}ⁿ⁺¹+1)−{q}({q}ⁿ+1)={q}ⁿ⁺²+1. Inducția cu două baze demonstrează formula.')
        m = j+2
        num(9, f'Fie a₁={j}, a₂={j+1}, aₙ₊₂=aₙ+{q}, n≥1. Calculați a_{2*m+1}.', j+m*q,
            f'Indicii impari formează șirul a₂ᵣ₊₁={j}+{q}r, deoarece fiecare salt de două ranguri adaugă {q}. Pentru r={m}, rezultatul este {j+m*q}.')
        add(10, f'Fie a₁={j}, (n+1)aₙ₊₁=naₙ pentru n≥1. Determinați aₙ.',
            rf'\(a_n={j}/n\)',
            [rf'\(a_n={j}n\)', rf'\(a_n={j}/(n+1)\)', rf'\(a_n={j}(n+1)\)'],
            f'aₙ₊₁/aₙ=n/(n+1). Înmulțind rapoartele de la 1 la n−1, obținem aₙ/a₁=1/n. Deci aₙ={j}/n, inclusiv pentru n=1.')
        add(11, f'Suma primilor n termeni este Sₙ=n²+{j}n, n≥1. Determinați aₙ pentru orice n≥1.',
            rf'\(a_n=2n+{j-1}\)',
            [rf'\(a_n=2n+{j}\)', rf'\(a_n=n+{j}\)', rf'\(a_n=2n+{j+1}\)'],
            f'Pentru n≥2, aₙ=Sₙ−Sₙ₋₁=n²−(n−1)²+{j}=2n+{j-1}. La n=1, a₁=S₁={j+1}, în acord cu formula.')
        num(12, f'Fie x₁={j+2}, xₙ₊₁=1/xₙ, n≥1. Calculați x_{2*j+3}.', j+2,
            f'Termenii sunt nenuli, iar xₙ₊₂=1/(1/xₙ)=xₙ. Toți termenii de rang impar sunt x₁={j+2}; rangul {2*j+3} este impar.')
        pre = 'Fie f₀=0, f₁=1 și fₙ₊₂=fₙ₊₁+fₙ pentru n≥0. '
        num(13, pre+rf'Calculați \(\sum_{{k=1}}^{{{n}}} f_k\).', sum(fib[1:n+1]),
            f'fₖ=fₖ₊₂−fₖ₊₁. Suma se reduce la f_{n+2}−f₂={fib[n+2]}−1={fib[n+2]-1}.')
        num(14, pre+rf'Calculați \(\sum_{{k=1}}^{{{n}}} f_k^2\).', sum(x*x for x in fib[1:n+1]),
            f'Identitatea este Σfₖ²=fₙfₙ₊₁: la n=1 este 1=1·1; adăugarea lui fₙ₊₁² transformă fₙfₙ₊₁ în fₙ₊₁(fₙ+fₙ₊₁)=fₙ₊₁fₙ₊₂. Aici rezultă {fib[n]}·{fib[n+1]}={fib[n]*fib[n+1]}.')
        num(15, pre+rf'Calculați \(\sum_{{k=1}}^{{{n}}}f_{{2k-1}}\).', sum(fib[2*k-1] for k in range(1,n+1)),
            f'f₂ₖ₋₁=f₂ₖ−f₂ₖ₋₂. Prin telescopare suma este f_{2*n}−f₀={fib[2*n]}.')
        add(16, rf'Un șir pozitiv satisface \(\prod_{{k=1}}^n x_k=(n+{j})/{j}\) pentru orice n≥1. Determinați xₙ pentru n≥2.',
            rf'\(x_n=(n+{j})/(n+{j-1})\)',
            [rf'\(x_n=(n+{j-1})/(n+{j})\)', rf'\(x_n=1/{j}\)', rf'\(x_n=(n+{j})/{j}\)'],
            f'Notăm produsul cu Pₙ. Pentru n≥2, xₙ=Pₙ/Pₙ₋₁=((n+{j})/{j})/((n+{j-1})/{j})=(n+{j})/(n+{j-1}). Numitorul este pozitiv. Separat, x₁=({j+1})/{j}.')
    return b.finish(Counter({i: 5 for i in range(1,17)}))


if __name__ == '__main__':
    path = Path(__file__).resolve().parents[1] / 'clasa_9/clasa_9_u02_l01_siruri_de_numere_reale_notatia_si_termenul_general.json'
    data = json.loads(path.read_text(encoding='utf-8'))
    data['questions'] = build()
    data['difficulty'] = 'medium'
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(f'{len(data["questions"])} grile scrise.')
