"""Rebuild only the five banks of Coliniaritate, concurență și paralelism."""
import json
from pathlib import Path

from gen_clasa_9_g2_pozitie_centre import update_files as update_position_centres
from gen_clasa_9_g2_thales import update_file as update_thales
from gen_clasa_9_g2_bisectoare import update_file as update_bisectors
from gen_clasa_9_g2_menelau import update_file as update_menelaus


def main():
    directory=Path(__file__).resolve().parents[1]/'clasa_9'
    files=sorted(directory.glob('clasa_9_u06_l*.json'))
    def interactive():
        return {p.name:[q for q in json.loads(p.read_text(encoding='utf-8'))['questions']
                        if q.get('type')!='multiple_choice'] for p in files}
    preserved=interactive()
    update_position_centres()
    update_thales()
    update_bisectors()
    update_menelaus()
    assert interactive()==preserved
    counts=[len(json.loads(p.read_text(encoding='utf-8'))['questions']) for p in files]
    assert counts==[85,25,100,130,85],counts
    print(f'G2: {counts}, {sum(counts)} total grids. No database changes.')


if __name__=='__main__':main()
