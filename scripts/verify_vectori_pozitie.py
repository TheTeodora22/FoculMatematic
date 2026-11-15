"""Audit independent, read-only, pentru cele 25 de grile de poziție.

Nu importă generatorul/Django și nu folosește eval sau parsare simbolică.
Verifică opțiunile prin ecuațiile geometrice originale, cu fracții exacte,
și compară datele de audit cu coordonatele efectiv afișate în enunț.
"""
import json
import re
from collections import Counter
from fractions import Fraction as F
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / 'data/quizzes/clasa_9/clasa_9_u05_l02_vectorul_de_pozitie_al_unui_punct_vectorul_lui_thales.json'
BANK = 'vectori_pozitie_grile_v1'
PAIR = re.compile(r'\((-?\d+(?:/\d+)?); (-?\d+(?:/\d+)?)\)')


def vector(raw):
    assert len(raw) == 2
    return tuple(F(component) for component in raw)


def parsed_option(text):
    match = PAIR.fullmatch(text)
    assert match is not None, f'Opțiune necanonică: {text}'
    return vector(match.groups())


def verify_question(question):
    scope = question['practice_scope']
    family = scope['family']
    inputs = question['verification']
    assert question['type'] == 'multiple_choice' and question['format'] == 'grid'
    assert question['points'] == 10
    assert question['explanation'].strip()
    assert 'Fără atribuire' in scope['reference_status']
    assert 'catalog_type' not in scope
    keys = {1: ['origin', 'A'], 2: ['OA', 'OP'], 3: ['origin', 'A', 'B'],
            4: ['OA', 'OB'], 5: ['OA', 'OB', 'OC']}[family]
    displayed = [vector(pair) for pair in PAIR.findall(question['text'])]
    assert displayed == [vector(inputs[key]) for key in keys], 'Datele auditului diferă de enunț.'

    if family == 4:
        ratio = re.search(r'AM:MB=(\d+):(\d+)', question['text'])
        assert ratio and list(map(int, ratio.groups())) == inputs['AM_MB']
        p, q = map(F, inputs['AM_MB'])
        assert p > 0 and q > 0

    def satisfies(candidate):
        if family == 1:
            # O + OA = A, verificat pe fiecare coordonată.
            return all(F(inputs['origin'][i]) + candidate[i] == F(inputs['A'][i]) for i in range(2))
        if family == 2:
            # OP + PA = OA (noua origine P, punctul A fix).
            return all(F(inputs['OP'][i]) + candidate[i] == F(inputs['OA'][i]) for i in range(2))
        if family == 3:
            # M=O+OM și MA=-MB, fără a folosi direct formula generatorului.
            return all(2 * (F(inputs['origin'][i]) + candidate[i]) ==
                       F(inputs['A'][i]) + F(inputs['B'][i]) for i in range(2))
        if family == 4:
            # q AM = p MB; pozitivitatea lui p,q asigură împărțirea internă.
            return all(q * (candidate[i] - F(inputs['OA'][i])) ==
                       p * (F(inputs['OB'][i]) - candidate[i]) for i in range(2))
        if family == 5:
            # Suma vectorilor AB, BC, BC, CA, calculată din capete.
            vertices = {key: vector(inputs[key]) for key in ['OA', 'OB', 'OC']}
            edges = [('OA', 'OB'), ('OB', 'OC'), ('OB', 'OC'), ('OC', 'OA')]
            return all(candidate[i] == sum(vertices[tail_to][i] - vertices[tail_from][i]
                                          for tail_from, tail_to in edges) for i in range(2))
        raise AssertionError(f'Familie necunoscută: {family}')

    options = question['options']
    assert len(options) == 4
    values = [parsed_option(option['text']) for option in options]
    assert len(set(values)) == 4, 'Opțiuni matematic identice.'
    truth = [satisfies(value) for value in values]
    flags = [option['is_correct'] for option in options]
    assert all(type(flag) is bool for flag in flags)
    assert sum(truth) == sum(flags) == 1 and truth == flags, (family, scope['variant'], truth, flags)
    expected = values[truth.index(True)]
    formatted = '(' + '; '.join(str(value) for value in expected) + ')'
    assert formatted in question['explanation'], 'Explicația nu conține rezultatul corect.'


def main():
    data = json.loads(TARGET.read_text(encoding='utf-8'))
    questions = data['questions']
    assert len(questions) == 28
    assert all(question['type'] == 'vector_workbench' for question in questions[:3])
    grids = [question for question in questions if question.get('practice_scope', {}).get('bank') == BANK]
    assert len(grids) == 25
    assert len({question['text'] for question in grids}) == 25
    assert Counter(question['practice_scope']['family'] for question in grids) == Counter({i: 5 for i in range(1, 6)})
    assert {(question['practice_scope']['family'], question['practice_scope']['variant']) for question in grids} == {
        (family, variant) for family in range(1, 6) for variant in range(1, 6)}
    for question in grids:
        verify_question(question)
    positions = Counter(next(index for index, option in enumerate(question['options']) if option['is_correct']) for question in grids)
    assert max(positions.values()) - min(positions.values()) <= 1
    print('OK: 25 grids, 5 families x 5 variants; 100 options verified exactly; matching statements and explanations.')


if __name__ == '__main__':
    main()
