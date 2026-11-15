"""Rebuild the three existing trigonometry application lessons, without seeding."""
import json
from pathlib import Path

from gen_clasa_9_g4_scalar_cosinus import update_file as update_scalar
from gen_clasa_9_g4_vectoriale import update_file as update_vectors
from gen_clasa_9_g4_triunghiuri import update_file as update_triangles


def main():
    files=sorted((Path(__file__).resolve().parents[1]/'clasa_9').glob('clasa_9_u08_l*.json'))
    assert len(files)==3
    def preserved():
        return {p.name:[q for q in json.loads(p.read_text(encoding='utf-8'))['questions']
                        if q.get('type')!='multiple_choice'] for p in files}
    original=preserved()
    update_scalar()
    update_vectors()
    update_triangles()
    assert preserved()==original
    counts=[len(json.loads(p.read_text(encoding='utf-8'))['questions']) for p in files]
    assert counts==[230,115,200],counts
    print(f'G4: {counts}, {sum(counts)} original grids; no database changes.')


if __name__=='__main__':main()
