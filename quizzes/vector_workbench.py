"""Exact vector exercises. Public configurations contain givens, never answer keys."""
import copy
import math
import re
from fractions import Fraction


class VectorValidationError(ValueError):
    pass


MODE_KEYS = {
    'same_displacement': {'points', 'reference', 'candidates'},
    'classify_vector': {'points', 'reference', 'candidate'},
    'translate_endpoint': {'points', 'reference', 'anchor'},
    'position_from_origin': {'points', 'origin', 'target'},
    'change_origin': {'points', 'old_origin', 'new_origin', 'target'},
    'midpoint': {'points', 'segment'},
    'head_to_tail': {'u', 'v'},
    'scale_vector': {'u', 'scalar'},
    'close_polygon': {'u', 'v'},
    'basis_decomposition': {'u', 'v', 'w'},
}


def number(value):
    if isinstance(value, bool) or not isinstance(value, (int, float, str)):
        raise VectorValidationError('Valoare numerică invalidă.')
    if isinstance(value, float) and not math.isfinite(value):
        raise VectorValidationError('Valoarea trebuie să fie finită.')
    if isinstance(value, str) and len(value) > 64:
        raise VectorValidationError('Valoarea numerică este prea lungă.')
    raw = str(value).strip().replace('−', '-').replace(',', '.')
    numeric = r'[+-]?(?:\d+(?:\.\d+)?|\.\d+)'
    if len(raw) > 32 or not re.fullmatch(rf'{numeric}(?:\s*/\s*{numeric})?', raw):
        raise VectorValidationError('Folosește un număr sau o fracție de forma a/b.')
    try:
        pieces = raw.split('/')
        result = Fraction(pieces[0].strip())
        if len(pieces) == 2:
            result /= Fraction(pieces[1].strip())
    except (ValueError, ZeroDivisionError, OverflowError) as exc:
        raise VectorValidationError('Fracție invalidă.') from exc
    if abs(result) > 1_000_000 or result.denominator > 1_000_000:
        raise VectorValidationError('Valoarea depășește limitele exercițiului.')
    return result


def vector(value):
    if not isinstance(value, (list, tuple)) or len(value) != 2:
        raise VectorValidationError('Un vector are exact două componente.')
    return tuple(number(v) for v in value)


def add(a, b):
    return tuple(x + y for x, y in zip(a, b))


def subtract(a, b):
    return tuple(x - y for x, y in zip(a, b))


def scale(k, a):
    return tuple(k * x for x in a)


def determinant(a, b):
    return a[0] * b[1] - a[1] * b[0]


def _solve_config(config):
    if not isinstance(config, dict):
        raise VectorValidationError('Configurație vectorială invalidă.')
    mode = config.get('mode')
    if not isinstance(mode, str) or mode not in MODE_KEYS:
        raise VectorValidationError('Mod vectorial necunoscut.')
    if set(config) != MODE_KEYS[mode] | {'mode'}:
        raise VectorValidationError('Configurația are câmpuri lipsă sau suplimentare.')
    points = {}
    if 'points' in config:
        raw = config['points']
        if not isinstance(raw, dict) or not 2 <= len(raw) <= 16:
            raise VectorValidationError('Sunt necesare între 2 și 16 puncte.')
        for name, pair in raw.items():
            if not isinstance(name, str) or not re.fullmatch(r'[A-Z][A-Za-z0-9_]{0,11}', name):
                raise VectorValidationError('Nume de punct invalid.')
            points[name] = vector(pair)

    def point(name):
        if not isinstance(name, str) or name not in points:
            raise VectorValidationError('Punctul nu aparține configurației.')
        return points[name]

    def displacement(pair):
        if not isinstance(pair, list) or len(pair) != 2 or pair[0] == pair[1]:
            raise VectorValidationError('Un segment orientat cere două puncte distincte.')
        return subtract(point(pair[1]), point(pair[0]))

    if mode == 'same_displacement':
        reference = displacement(config['reference'])
        candidates = config['candidates']
        if not isinstance(candidates, list) or not 2 <= len(candidates) <= 12:
            raise VectorValidationError('Sunt necesare între 2 și 12 segmente candidate.')
        labels = []
        correct = []
        for pair in candidates:
            value = displacement(pair)
            label = ''.join(pair)
            labels.append(label)
            if value == reference:
                correct.append(label)
        if len(set(labels)) != len(labels) or not correct or len(correct) == len(labels):
            raise VectorValidationError('Selecția trebuie să aibă candidați distincți, corecți și greșiți.')
        return {'selected': correct}
    if mode == 'classify_vector':
        u, v = displacement(config['reference']), displacement(config['candidate'])
        if u == (0, 0) or v == (0, 0):
            raise VectorValidationError('Clasificarea direcției cere vectori nenuli.')
        result = ('equal' if u == v else 'opposite' if u == scale(-1, v)
                  else 'collinear' if determinant(u, v) == 0 else 'noncollinear')
        return {'relation': result}
    if mode == 'translate_endpoint':
        return {'endpoint': add(point(config['anchor']), displacement(config['reference']))}
    if mode == 'position_from_origin':
        return {'vector': subtract(point(config['target']), point(config['origin']))}
    if mode == 'change_origin':
        point(config['old_origin'])
        return {'vector': subtract(point(config['target']), point(config['new_origin']))}
    if mode == 'midpoint':
        displacement(config['segment'])
        a, b = (point(name) for name in config['segment'])
        return {'midpoint': scale(Fraction(1, 2), add(a, b))}
    u = vector(config['u'])
    if mode == 'scale_vector':
        return {'vector': scale(number(config['scalar']), u)}
    v = vector(config['v'])
    if mode == 'head_to_tail':
        return {'tail': u, 'vector': add(u, v)}
    if mode == 'close_polygon':
        return {'vector': scale(-1, add(u, v))}
    w = vector(config['w'])
    denominator = determinant(u, v)
    if denominator == 0:
        raise VectorValidationError('Vectorii bazei trebuie să fie necoliniari.')
    return {'coefficients': (determinant(w, v) / denominator, determinant(u, w) / denominator)}


def validate_config(config):
    expected = _solve_config(config)
    for value in expected.values():
        if isinstance(value, tuple) and any(abs(x) > 1_000_000 or x.denominator > 1_000_000 for x in value):
            raise VectorValidationError('Rezultatul depășește limitele atelierului.')
    return expected


def public_config(config):
    validate_config(config)
    mode = config['mode']
    return copy.deepcopy({key: config[key] for key in MODE_KEYS[mode] | {'mode'}})


def solved_values(config):
    """Only expose after a correct saved answer; callers enforce that condition."""
    expected = validate_config(config)
    return {key: [int(x) if x.denominator == 1 else str(x) for x in value]
            if isinstance(value, tuple) else copy.deepcopy(value)
            for key, value in expected.items()}


def check_answer(config, values):
    expected = validate_config(config)
    if not isinstance(values, dict) or set(values) != set(expected):
        raise VectorValidationError('Răspunsul are câmpuri lipsă sau suplimentare.')
    if 'selected' in expected:
        selected = values['selected']
        choices = {''.join(pair) for pair in config['candidates']}
        if (not isinstance(selected, list) or len(selected) > len(choices)
                or any(not isinstance(s, str) or s not in choices for s in selected)
                or len(selected) != len(set(selected))):
            raise VectorValidationError('Selecție de segmente invalidă.')
        return set(selected) == set(expected['selected'])
    if 'relation' in expected:
        relation = values['relation']
        if relation not in ('equal', 'opposite', 'collinear', 'noncollinear'):
            raise VectorValidationError('Relație vectorială invalidă.')
        return relation == expected['relation']
    return all(vector(values[key]) == answer for key, answer in expected.items())
