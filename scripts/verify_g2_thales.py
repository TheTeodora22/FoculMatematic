"""Independent exact audit; no generator import, eval or application writes."""
import json
import re
from collections import Counter
from fractions import Fraction as F
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
FILE=next((ROOT/'data/quizzes/clasa_9').glob('clasa_9_u06_l02_*.json'))
BANK='g2_thales_original_v1'
PAIR=re.compile(r'\((-?\d+(?:/\d+)?);\s*(-?\d+(?:/\d+)?)\)')


def vec(raw):return tuple(F(c) for c in raw)
def diff(a,b):return tuple(x-y for x,y in zip(a,b))
def determinant(a,b):return a[0]*b[1]-a[1]*b[0]


def verify(question):
    scope=question['practice_scope'];family=scope['family'];g=question['verification']
    assert scope['catalog'] is None and question['explanation']
    if family in (2,3,5):
        pts={key:vec(value) for key,value in g.items() if key in ('A','B','C','D','M')}
        a,b,c=[pts[key] for key in ('A','B','C')]
        assert determinant(diff(b,a),diff(c,a))!=0
        shown={name:vec((x,y)) for name,x,y in re.findall(r'\b([ABCM])\s*=?\s*\((-?\d+(?:/\d+)?);\s*(-?\d+(?:/\d+)?)\)',question['text'])}
        for name,value in shown.items():assert pts[name]==value
    if family==1:
        assert 0<g['AM']<g['AB'] and g['AC']>0
        assert f"AB={g['AB']} cm" in question['text'] and f"AC={g['AC']} cm" in question['text'] and f"AM={g['AM']} cm" in question['text']
    if family==4:
        assert all(value>0 for value in g.values())
        assert f"AB={g['AB']} cm" in question['text'] and f"BC={g['BC']} cm" in question['text'] and f"A′B′={g['ApBp']} cm" in question['text']
    options=question['options'];assert len(options)==4
    values=[]
    for option in options:
        match=PAIR.fullmatch(option['text'])
        values.append(vec(match.groups()) if match else F(option['text']))
    assert len(set(values))==4
    def satisfies(value):
        if family==1:return g['AB']*value==g['AC']*g['AM']
        if family==2:
            n=tuple(a[i]+value*(c[i]-a[i]) for i in range(2))
            return n!=pts['M'] and determinant(diff(n,pts['M']),diff(c,b))==0
        if family==3:
            assert F(g['k'])<0 and f"({g['k']})AB" in question['text']
            assert diff(pts['M'],a)==tuple(F(g['k'])*(b[i]-a[i]) for i in range(2))
            # N must be on AC and MN parallel to BC; solve by testing geometry.
            return determinant(diff(value,a),diff(c,a))==0 and determinant(diff(value,pts['M']),diff(c,b))==0
        if family==4:return value*g['AB']==g['BC']*g['ApBp']
        if family==5:
            d=pts['D'];assert determinant(diff(b,a),diff(c,d))==0
            # Candidate ratio r implies O=(A+r C)/(1+r) on AC.
            if value<=0:return False
            o=tuple((a[i]+value*c[i])/(1+value) for i in range(2))
            return determinant(diff(o,b),diff(d,b))==0
        raise AssertionError(family)
    truth=[satisfies(value) for value in values]
    assert truth==[o['is_correct'] for o in options] and sum(truth)==1,scope
    answer=values[truth.index(True)]
    formatted='('+'; '.join(map(str,answer))+')' if isinstance(answer,tuple) else str(answer)
    assert f'Rezultatul este {formatted}.' in question['explanation']


def main():
    data=json.loads(FILE.read_text(encoding='utf-8'))
    questions=[q for q in data['questions'] if q.get('practice_scope',{}).get('bank')==BANK]
    assert len(questions)==len({q['text'] for q in questions})==25
    assert Counter(q['practice_scope']['family'] for q in questions)==Counter({i:5 for i in range(1,6)})
    for q in questions:verify(q)
    print('Thales: 25 grids, 100 options; exact proportions, oriented extensions and geometric determinants verified.')


if __name__=='__main__':main()
