"""Generează structura JSON goală pentru programa clasei a VI-a."""

import json
import re
import unicodedata
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "chapters.json"

CHAPTERS = [
    (
        "multimi-numere-naturale",
        "Mulțimi și numere naturale",
        [
            "Mulțimi: descriere, notații și reprezentări",
            "Relații între mulțimi",
            "Mulțimi finite și infinite. Cardinalul unei mulțimi",
            "Operații cu mulțimi: reuniune, intersecție, diferență",
            "Descompunerea numerelor naturale în factori primi",
            "CMMDC și CMMMC. Numere prime între ele",
            "Proprietăți ale divizibilității în N",
        ],
    ),
    (
        "rapoarte-proportii",
        "Rapoarte și proporții",
        [
            "Rapoarte",
            "Proporții. Proprietatea fundamentală",
            "Proporții derivate",
            "Șir de rapoarte egale",
            "Mărimi direct proporționale",
            "Mărimi invers proporționale",
            "Regula de trei simplă",
            "Organizarea și reprezentarea datelor",
            "Probabilități",
        ],
    ),
    (
        "numere-intregi",
        "Numere întregi",
        [
            "Mulțimea numerelor întregi. Opusul și modulul. Compararea și ordonarea",
            "Adunarea numerelor întregi. Proprietăți",
            "Scăderea numerelor întregi",
            "Înmulțirea numerelor întregi. Proprietăți",
            "Împărțirea numerelor întregi",
            "Puterea cu exponent natural a unui număr întreg nenul",
            "Ordinea efectuării operațiilor și folosirea parantezelor",
            "Ecuații în mulțimea numerelor întregi",
            "Inecuații în mulțimea numerelor întregi",
            "Probleme cu ecuații și inecuații în numere întregi",
        ],
    ),
    (
        "numere-rationale",
        "Numere raționale",
        [
            "Mulțimea numerelor raționale. Opus, modul, comparare și ordonare",
            "Adunarea și scăderea numerelor raționale",
            "Înmulțirea numerelor raționale. Proprietăți",
            "Împărțirea numerelor raționale",
            "Puterea cu exponent întreg a unui număr rațional nenul",
            "Ordinea efectuării operațiilor și folosirea parantezelor",
            "Ecuații în mulțimea numerelor raționale",
            "Probleme care se rezolvă folosind ecuații",
        ],
    ),
    (
        "geometrie-fundamentala",
        "Geometrie fundamentală",
        [
            "Unghiuri opuse la vârf. Unghiuri în jurul unui punct. Unghiuri complementare și suplementare",
            "Unghiuri adiacente. Bisectoarea unui unghi",
            "Drepte paralele. Criterii de paralelism",
            "Drepte perpendiculare. Distanța de la un punct la o dreaptă. Mediatoarea unui segment",
            "Cercul: definiție, elemente, construcție și unghi la centru",
            "Pozițiile unei drepte față de un cerc. Pozițiile relative a două cercuri",
        ],
    ),
    (
        "triunghiuri",
        "Triunghiuri",
        [
            "Triunghiul: definiție, elemente, clasificare, perimetru și suma unghiurilor",
            "Construcția triunghiurilor. Inegalități între elementele triunghiului",
            "Linii importante în triunghi",
            "Congruența triunghiurilor. Criterii de congruență",
            "Metoda triunghiurilor congruente",
            "Proprietăți ale triunghiului isoscel",
            "Proprietăți ale triunghiului echilateral",
            "Proprietăți ale triunghiului dreptunghic",
        ],
    ),
]


def slugify(value: str) -> str:
    value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode()
    value = re.sub(r"[^a-zA-Z0-9]+", "_", value).strip("_").lower()
    return value[:70]


def main() -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    manifest = [chapter for chapter in manifest if chapter.get("class_level") != 6]

    for chapter_order, (chapter_slug, chapter_title, lessons) in enumerate(CHAPTERS, 1):
        filenames = []
        for lesson_order, lesson_title in enumerate(lessons, 1):
            filename = f"clasa_6_u{chapter_order:02d}_l{lesson_order:02d}_{slugify(lesson_title)}.json"
            filenames.append(filename)
            path = ROOT / filename
            if not path.exists():
                payload = {
                    "title": lesson_title,
                    "description": f"Clasa a 6-a · {chapter_title}",
                    "difficulty": "easy",
                    "questions": [],
                }
                path.write_text(
                    json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
                    encoding="utf-8",
                )

        manifest.append(
            {
                "class_level": 6,
                "slug": chapter_slug,
                "title": chapter_title,
                "order": chapter_order,
                "topics": filenames,
            }
        )

    MANIFEST.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
