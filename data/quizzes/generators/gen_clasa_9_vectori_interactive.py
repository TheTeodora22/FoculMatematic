"""Build the 12 approved vector workshop examples without replacing other content."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from quizzes.vector_workbench import MODE_KEYS, validate_config

FILES = [
    'clasa_9_u05_l01_segmente_orientate_relatia_de_echipolenta.json',
    'clasa_9_u05_l02_vectorul_de_pozitie_al_unui_punct_vectorul_lui_thales.json',
    'clasa_9_u05_l03_operatii_cu_vectori_in_plan_adunarea_si_inmultirea_cu_scalari.json',
    'clasa_9_u05_l04_descompunerea_unui_vector_dupa_doi_vectori_necoliniari.json',
]
EXPLANATIONS = {
    'V01': 'AB deplasează 3 unități la dreapta și 2 în sus. CD=(1−(−2),3−1)=(3,2), deci este echipolent cu AB. DC și EF au deplasarea (−3,−2), opusă lui AB.',
    'V02': 'AB=(3,2), iar EF=(1−4,2−4)=(−3,−2)=−AB. Vectorii au același modul și aceeași direcție, dar sensuri opuse; nu sunt egali.',
    'V03': 'AB=(4−1,3−1)=(3,2). Condiția CD=AB impune D=C+AB=(−2,0)+(3,2)=(1,2). Verificare: D−C=(3,2).',
    'V04': 'Vectorul de poziție al lui A față de O este OA=A−O=(4−1,3−(−2))=(3,5). Originea vectorului este O, iar vârful este A.',
    'V05': 'PA=A−P=(4−(−1),3−1)=(5,2). Echivalent: OA=(3,5), OP=(−2,3), iar PA=OA−OP=(5,2). Punctul A rămâne fix când schimbăm originea.',
    'V06': 'Mijlocul lui AB este M=((0+6)/2,(0+4)/2)=(3,2). Pentru orice origine O, OM=(OA+OB)/2; relația nu depinde de alegerea originii.',
    'V07': 'Transportăm v la vârful lui u, deci coada copiei lui v este în (3,1). Vârful acestei copii este (3,1)+(−1,2)=(2,3). Rezultanta unește originea lui u cu acest vârf și are componentele (2,3).',
    'V08': 'Înmulțim fiecare componentă a lui u cu −2: −2u=(−2·3,−2·1)=(−6,−2). Semnul minus schimbă sensul, iar modulul scalarului dublează lungimea.',
    'V09': 'u+v=(2−1,1+3)=(1,4). Pentru închiderea poligonului trebuie w=−(u+v)=(−1,−4). Verificare: (2,1)+(−1,3)+(−1,−4)=(0,0).',
    'V10': 'Ecuația au+bv=w devine (2a+b,2b)=(5,6). Din 2b=6 obținem b=3, apoi 2a+3=5, deci a=1. Determinantul bazei este 4, nenul: descompunerea este unică.',
    'V11': 'Deoarece M este mijlocul lui BC, AM=(AB+AC)/2=(2,3). Coeficienții după AB și AC sunt amândoi 1/2. Aceștia sunt coeficienți în baza laturilor, nu lungimi de proiecții ortogonale.',
    'V12': 'M=(6,3) și N=(3,6), deci AM=(6,3), AN=(3,6). Sistemul 6a+3b=6, 3a+6b=0 dă a=4/3 și b=−2/3. Verificare: (4/3)(6,3)−(2/3)(3,6)=(6,0)=AB; determinantul bazei este 27, nenul.',
}


def build_questions():
    examples = json.loads((ROOT/'docs/vectori_in_plan_interactive.examples.json').read_text(encoding='utf-8'))['examples']
    result = {name: [] for name in FILES}
    for example in examples:
        mode = example['mode']
        config = {key: example[key] for key in MODE_KEYS[mode] | {'mode'}}
        validate_config(config)
        question = {
            'text': example['prompt'], 'type':'vector_workbench', 'format':'interactive',
            'points':10, 'explanation':EXPLANATIONS[example['id']], 'interactive':config,
            'workshop': {'id':example['id'], 'origin':'Exercițiu original; lot interactiv introductiv',
                         'reference':example['catalog']},
        }
        result[FILES[example['lesson']-1]].append(question)
    return result


def main():
    for filename, questions in build_questions().items():
        path = ROOT/'data/quizzes/clasa_9'/filename
        data = json.loads(path.read_text(encoding='utf-8'))
        by_id = {q.get('workshop',{}).get('id'):q for q in questions}
        existing = []
        inserted = set()
        for question in data['questions']:
            key = question.get('workshop',{}).get('id')
            if key in by_id:
                existing.append(by_id[key]); inserted.add(key)
            else:
                existing.append(question)
        existing.extend(q for q in questions if q['workshop']['id'] not in inserted)
        assert len({q['text'] for q in existing}) == len(existing), filename
        data['questions'] = existing
        data['difficulty'] = 'medium'
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n',encoding='utf-8')
        print(f'{filename}: {len(questions)} vector workshops; {len(existing)} total questions.')


if __name__ == '__main__':
    main()
