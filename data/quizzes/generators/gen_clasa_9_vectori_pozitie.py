"""25 grile originale de consolidare: vectori de poziție, fără atribuire de catalog.

API pentru generatorul principal: build_questions() -> list[dict].
Pentru scriere folosiți update_file(): păstrează octeții obiectelor existente,
inclusiv CRLF, și înlocuiește numai grilele marcate cu BANK_ID.
Nu importă date în Django și nu modifică întrebările interactive.
"""
import hashlib
import json
import re
from collections import Counter
from fractions import Fraction as F
from pathlib import Path

BANK_ID = 'vectori_pozitie_grile_v1'
TARGET = Path(__file__).resolve().parents[1] / 'clasa_9' / 'clasa_9_u05_l02_vectorul_de_pozitie_al_unui_punct_vectorul_lui_thales.json'
FAMILIES = {
    1: 'Vector de poziție din coordonatele originii și punctului',
    2: 'Schimbarea originii unui vector de poziție',
    3: 'Vectorul de poziție al mijlocului unui segment',
    4: 'Împărțirea internă a segmentului într-un raport dat',
    5: 'Identități liniare între vectori exprimate prin vectori de poziție',
}


def pair(v):
    return '(' + '; '.join(str(F(x)) for x in v) + ')'


def add(u,v):return tuple(F(a)+F(b) for a,b in zip(u,v))
def sub(u,v):return tuple(F(a)-F(b) for a,b in zip(u,v))
def scale(k,v):return tuple(F(k)*F(a) for a in v)
def serial(v):return [str(F(x)) for x in v]


def build_questions():
    questions=[]
    def question(family,variant,text,answer,wrong,explanation,inputs):
        vectors=[tuple(map(F,v)) for v in [answer,*wrong]]
        assert len(vectors)==4==len(set(vectors)), (family,variant,vectors)
        correct_index=len(questions)%4
        vectors.insert(correct_index,vectors.pop(0))
        questions.append({
            'text':text,'type':'multiple_choice','format':'grid','points':10,
            'explanation':explanation,
            'options':[{'text':pair(v),'is_correct':index==correct_index} for index,v in enumerate(vectors)],
            'practice_scope':{
                'bank':BANK_ID,'family':family,'family_name':FAMILIES[family],'variant':variant,
                'origin':'Exercițiu original de consolidare a noțiunilor introductive despre vectori de poziție.',
                'reference_status':'Fără atribuire de tip din catalog; maparea denumirii «Vectorul lui Thales» rămâne de confirmat.',
            },
            'verification':inputs,
        })
    for j in range(1,6):
        origin=(j,-2*j);a=(3*j+1,j+2)
        answer=sub(a,origin)
        question(1,j,
            f'Într-un reper cartezian, O{pair(origin)} este originea aleasă pentru vectorii de poziție, iar A{pair(a)} este un punct fix. Determinați coordonatele vectorului '+r'\(\overrightarrow{OA}\).',
            answer,[sub(origin,a),add(a,origin),a],
            r'Vectorul \(\overrightarrow{OA}\) se obține scăzând coordonatele originii O din cele ale vârfului A: '
            +f'({a[0]}−({origin[0]}), {a[1]}−({origin[1]}))={pair(answer)}. Nu folosim direct coordonatele lui A deoarece originea aleasă O nu este (0;0).',
            {'origin':serial(origin),'A':serial(a)})

        oa=(j+2,2*j-1);op=(-j,j+1)
        answer=sub(oa,op)
        question(2,j,
            r'Față de aceeași origine O se cunosc '+rf'\(\overrightarrow{{OA}}={pair(oa)}\) și \(\overrightarrow{{OP}}={pair(op)}\). '
            +r'Punctul A rămâne fix, iar noua origine este P. Care sunt coordonatele lui \(\overrightarrow{PA}\)?',
            answer,[add(oa,op),sub(op,oa),oa],
            r'Relația lui Chasles dă \(\overrightarrow{OP}+\overrightarrow{PA}=\overrightarrow{OA}\). '
            +r'Prin urmare \(\overrightarrow{PA}=\overrightarrow{OA}-\overrightarrow{OP}\): '
            +f'({oa[0]}−({op[0]}), {oa[1]}−({op[1]}))={pair(answer)}. Schimbarea originii nu mută punctul A.',
            {'OA':serial(oa),'OP':serial(op)})

        origin=(j,-2*j);a=(-j,j+1);b=(2*j+1,-j+2)
        midpoint=scale(F(1,2),add(a,b));answer=sub(midpoint,origin)
        question(3,j,
            f'Într-un reper cartezian se dau O{pair(origin)}, A{pair(a)} și B{pair(b)}. Dacă M este mijlocul segmentului AB, determinați '+r'\(\overrightarrow{OM}\).',
            answer,[midpoint,sub(add(a,b),origin),scale(-1,answer)],
            f'Mijlocul are coordonatele M={pair(midpoint)}, obținute ca medii aritmetice ale coordonatelor lui A și B. '
            +r'Apoi \(\overrightarrow{OM}=M-O\) și rezultă '+pair(answer)+'. '
            +r'Echivalent, pentru orice origine O, \(2\overrightarrow{OM}=\overrightarrow{OA}+\overrightarrow{OB}\).',
            {'origin':serial(origin),'A':serial(a),'B':serial(b)})

        oa=(j,-j);ob=(3*j+1,j+2);p=j+1;q=j+2
        numerator=add(scale(q,oa),scale(p,ob))
        answer=scale(F(1,p+q),numerator)
        swapped=scale(F(1,p+q),add(scale(p,oa),scale(q,ob)))
        question(4,j,
            rf'Se cunosc \(\overrightarrow{{OA}}={pair(oa)}\), \(\overrightarrow{{OB}}={pair(ob)}\). '
            +f'Punctul M aparține segmentului AB și AM:MB={p}:{q}. Determinați '+r'\(\overrightarrow{OM}\).',
            answer,[swapped,scale(F(1,2),add(oa,ob)),numerator],
            f'Raportul {p}:{q} este pozitiv, deci M este interior segmentului. Din '
            +rf'\({q}\overrightarrow{{AM}}={p}\overrightarrow{{MB}}\) '
            +r'și din expresiile prin vectori de poziție obținem '
            +rf'\(({p}+{q})\overrightarrow{{OM}}={q}\overrightarrow{{OA}}+{p}\overrightarrow{{OB}}\). '
            +f'Suma ponderată din dreapta este {pair(numerator)}; împărțind la {p+q}>0, rezultă {pair(answer)}. Ponderile extremităților sunt în ordine inversă față de AM:MB.',
            {'OA':serial(oa),'OB':serial(ob),'AM_MB':[p,q]})

        oa=(j,-j);ob=(2*j+1,j+2);oc=(-j+3,3*j)
        ab=sub(ob,oa);bc=sub(oc,ob);ac=sub(oc,oa)
        answer=sub(add(ab,scale(2,bc)),ac)
        question(5,j,
            rf'Față de aceeași origine O, \(\overrightarrow{{OA}}={pair(oa)}\), \(\overrightarrow{{OB}}={pair(ob)}\), \(\overrightarrow{{OC}}={pair(oc)}\). '
            +r'Calculați \(\overrightarrow{AB}+2\overrightarrow{BC}-\overrightarrow{AC}\).',
            answer,[ab,ac,scale(-1,bc)],
            r'Prin Chasles, \(\overrightarrow{AB}+\overrightarrow{BC}=\overrightarrow{AC}\). '
            +r'Așadar expresia dată se reduce la \(\overrightarrow{BC}\), iar '
            +r'\(\overrightarrow{BC}=\overrightarrow{OC}-\overrightarrow{OB}\)='
            +f'({oc[0]}−({ob[0]}), {oc[1]}−({ob[1]}))={pair(answer)}. Identitatea nu depinde de alegerea originii O.',
            {'OA':serial(oa),'OB':serial(ob),'OC':serial(oc)})
    assert len(questions)==25
    assert len({q['text'] for q in questions})==25
    assert Counter(q['practice_scope']['family'] for q in questions)==Counter({i:5 for i in FAMILIES})
    return questions


def _question_spans(raw):
    """Return raw JSON-object spans, without reserializing retained questions."""
    match=re.search(r'"questions"\s*:\s*\[',raw)
    if not match:raise ValueError('Lipsește lista questions.')
    start=match.end();pos=start;decoder=json.JSONDecoder();items=[]
    while True:
        if raw[pos]==',':pos+=1
        leading=pos
        while raw[pos].isspace():pos+=1
        if raw[pos]==']':return start,pos,items
        item,end=decoder.raw_decode(raw,pos)
        items.append((item,raw[leading:pos],raw[pos:end]))
        pos=end


def update_file(path=TARGET):
    """Add/update our bank, preserving all other objects exactly and in order."""
    path=Path(path);raw=path.read_bytes().decode('utf-8')
    start,end,items=_question_spans(raw)
    if len(items)<3 or any(item[0].get('type')!='vector_workbench' for item in items[:3]):
        raise ValueError('Primele trei întrebări interactive trebuie păstrate.')
    original=[hashlib.sha256(item[2].encode('utf-8')).digest() for item in items[:3]]
    retained=[item for item in items if item[0].get('practice_scope',{}).get('bank')!=BANK_ID]
    newline='\r\n' if '\r\n' in raw else '\n'
    chunks=[leading+block for _,leading,block in retained]
    for item in build_questions():
        pretty=json.dumps(item,ensure_ascii=False,indent=2)
        block=newline.join('    '+line for line in pretty.splitlines())
        chunks.append(newline+block)
    updated=raw[:start]+','.join(chunks)+newline+'  '+raw[end:]
    _,_,after=_question_spans(updated)
    assert original==[hashlib.sha256(item[2].encode('utf-8')).digest() for item in after[:3]]
    json.loads(updated)
    path.write_bytes(updated.encode('utf-8'))
    return len(after)


if __name__=='__main__':
    print(f'{update_file()} questions; 25 original grids; existing objects preserved byte-for-byte.')
