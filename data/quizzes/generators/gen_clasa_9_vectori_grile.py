"""Rebuild the four vector banks, preserving their original interactive items."""
import json
from pathlib import Path

from gen_clasa_9_vectori_operatii import update_file as update_operations
from gen_clasa_9_vectori_pozitie import update_file as update_position
from gen_clasa_9_vectori_segmente_baze import update_files as update_segments_bases


def main():
    directory = Path(__file__).resolve().parents[1] / 'clasa_9'
    files = sorted(directory.glob('clasa_9_u05_l*.json'))
    def interactive():
        return {p.name: [q for q in json.loads(p.read_text(encoding='utf-8'))['questions']
                         if q.get('type') == 'vector_workbench'] for p in files}
    before = interactive()
    update_segments_bases()
    update_position()
    update_operations()
    assert before == interactive(), 'An existing interactive question changed.'
    counts = [len(json.loads(p.read_text(encoding='utf-8'))['questions']) for p in files]
    assert counts == [33, 28, 243, 33], counts
    print(f'Vectori: {counts}; total {sum(counts)} = 325 grids + 12 preserved interactive questions.')


if __name__ == '__main__':
    main()
