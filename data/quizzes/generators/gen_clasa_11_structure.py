"""Generează structura JSON goală pentru programa clasei a XI-a."""

import json
import re
import unicodedata
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "chapters.json"

CHAPTERS = [
    (
        "permutari",
        "Permutări",
        [
            "Noțiunea de permutare",
            "Operații cu permutări. Compunerea permutărilor de gradul n",
            "Proprietăți ale compunerii permutărilor",
            "Puterea unei permutări. Proprietăți ale transpozițiilor",
            "Inversiunile unei permutări. Semnul unei permutări",
        ],
    ),
    (
        "matrice",
        "Matrice",
        [
            "Tabel matriceal. Matrice. Mulțimi de matrice",
            "Adunarea matricelor și înmulțirea unei matrice cu un scalar",
            "Înmulțirea matricelor",
            "Puterea unei matrice pătratice",
            "Transpusa unei matrice",
        ],
    ),
    (
        "determinanti",
        "Determinanți",
        [
            "Determinantul de ordinul n. Proprietăți",
            "Determinanți de ordinul 2 și 3",
            "Dezvoltarea unui determinant după o linie sau o coloană",
            "Ecuația dreptei determinate de două puncte. Coliniaritatea a trei puncte",
            "Distanța de la un punct la o dreaptă",
            "Aria unei suprafețe triunghiulare",
        ],
    ),
    (
        "sisteme-ecuatii-liniare",
        "Sisteme de ecuații liniare",
        [
            "Matrice inversabile din Mₙ(C)",
            "Ecuații matriceale",
            "Sisteme de ecuații liniare cu trei sau patru necunoscute",
            "Sisteme de ecuații liniare de tip Cramer",
            "Rangul unei matrice",
            "Studiul compatibilității și rezolvarea sistemelor de ecuații liniare",
        ],
    ),
    (
        "limite-functii",
        "Limite de funcții",
        [
            "Structura de ordine a mulțimii numerelor reale. Intervale",
            "Mulțimi mărginite. Marginile unei mulțimi de numere reale",
            "Vecinătățile unui punct pe axa reală",
            "Funcții reale de variabilă reală",
            "Limite de șiruri. Șiruri cu limită finită și infinită",
            "Proprietăți ale șirurilor care au limită",
            "Criterii de existență a limitei unui șir",
            "Proprietatea lui Weierstrass și aplicații ale teoremei",
            "Operații cu șiruri care au limită",
            "Limita unei funcții într-un punct și limite laterale",
            "Proprietăți ale funcțiilor care au limită. Limitele funcțiilor elementare",
            "Operații cu limite de funcții. Limite de funcții compuse",
            "Asimptotele funcțiilor reale",
        ],
    ),
    (
        "functii-continue",
        "Funcții continue",
        [
            "Funcții continue într-un punct. Continuitate laterală",
            "Prelungirea prin continuitate. Puncte de discontinuitate",
            "Operații cu funcții continue. Continuitatea funcțiilor compuse",
            "Proprietăți ale funcțiilor continue pe un interval",
            "Existența soluțiilor unei ecuații. Studiul semnului unei funcții",
            "Proprietatea lui Darboux",
        ],
    ),
    (
        "functii-derivabile",
        "Funcții derivabile",
        [
            "Derivata unei funcții într-un punct. Derivabilitate și continuitate",
            "Derivate laterale și derivatele funcțiilor elementare",
            "Operații cu funcții derivabile. Derivata funcției compuse și inverse",
            "Derivate de ordinul al II-lea",
            "Aplicații ale derivatelor. Rădăcini multiple ale ecuațiilor polinomiale",
            "Funcții derivabile pe un interval. Teoremele lui Fermat și Rolle",
            "Teorema lui Lagrange și consecințe",
            "Regulile lui l’Hospital",
            "Rolul derivatei întâi în studiul funcțiilor",
            "Monotonie, puncte de extrem și demonstrarea inegalităților",
            "Rolul derivatei a doua. Convexitate, concavitate și puncte de inflexiune",
        ],
    ),
    (
        "reprezentarea-grafica-functiilor",
        "Reprezentarea grafică a funcțiilor",
        [
            "Etapele reprezentării grafice a funcțiilor",
            "Reprezentarea grafică a conicelor",
            "Rezolvarea grafică a ecuațiilor",
        ],
    ),
]


def slugify(value: str) -> str:
    value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode()
    value = re.sub(r"[^a-zA-Z0-9]+", "_", value).strip("_").lower()
    return value[:70]


def main() -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    manifest = [chapter for chapter in manifest if chapter.get("class_level") != 11]

    for chapter_order, (chapter_slug, chapter_title, lessons) in enumerate(CHAPTERS, 1):
        filenames = []
        for lesson_order, lesson_title in enumerate(lessons, 1):
            filename = f"clasa_11_u{chapter_order:02d}_l{lesson_order:02d}_{slugify(lesson_title)}.json"
            filenames.append(filename)
            path = ROOT / filename
            if not path.exists():
                payload = {
                    "title": lesson_title,
                    "description": f"Clasa a 11-a · {chapter_title}",
                    "difficulty": "easy",
                    "questions": [],
                }
                path.write_text(
                    json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
                    encoding="utf-8",
                )

        manifest.append(
            {
                "class_level": 11,
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
