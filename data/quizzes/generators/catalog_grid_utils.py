"""Format comun pentru grilele catalogului; calculele rămân în fiecare modul."""
from collections import Counter
from fractions import Fraction


class GridBank:
    def __init__(self, section, names, notation=""):
        self.section, self.names, self.notation = section, names, notation
        self.questions = []
        self.counts = Counter()

    def add(self, kind, text, correct, wrong, explanation):
        values = [str(correct), *map(str, wrong)]
        assert len(values) == len(set(values)) == 4, (kind, text, values)
        position = len(self.questions) % 4
        values.insert(position, values.pop(0))
        self.counts[kind] += 1
        self.questions.append({
            "text": text + self.notation, "type": "multiple_choice", "format": "grid", "points": 10,
            "explanation": explanation,
            "options": [{"text": v, "is_correct": i == position} for i, v in enumerate(values)],
            "catalog": {"section": self.section, "type": kind, "type_name": self.names[kind-1],
                        "variant": self.counts[kind],
                        "origin": "Exercițiu nou după tipologia catalogului Burtea IX"},
        })

    def numeric(self, kind, text, answer, explanation, wrong=None):
        answer = Fraction(answer)
        if wrong is None:
            wrong = [answer-1, answer+1, answer+2]
        wrong = list(map(Fraction, wrong))
        assert len(set([answer, *wrong])) == 4
        self.add(kind, text, answer, wrong, explanation)

    def finish(self, counts):
        assert self.counts == counts, self.counts
        assert len({q['text'] for q in self.questions}) == len(self.questions)
        return self.questions


def number_set(values):
    return "{" + "; ".join(str(Fraction(v)).replace("-", "−") for v in sorted(set(values))) + "}"
