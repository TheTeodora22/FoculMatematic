"""Generează structura JSON goală pentru programa clasei a VIII-a."""

import json
import re
import unicodedata
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "chapters.json"

CHAPTERS = [
    (
        "intervale-inecuatii",
        "Intervale și inecuații",
        [
            "Mulțimi definite printr-o proprietate comună a elementelor",
            "Intervale numerice și reprezentarea lor pe axă. Intersecția și reuniunea intervalelor",
            "Inecuații de forma ax + b ≥ 0 (≤, >, <), unde a și b sunt numere reale",
        ],
    ),
    (
        "calcul-algebric",
        "Calcul algebric",
        [
            "Operații cu numere reale reprezentate prin litere. Reducerea termenilor asemenea",
            "Formule de calcul prescurtat",
            "Descompuneri în factori utilizând reguli de calcul în R",
            "Fracții algebrice. Operații cu fracții algebrice",
            "Ecuația de forma ax² + bx + c = 0, unde a, b și c sunt numere reale, a ≠ 0",
        ],
    ),
    (
        "functii-statistica",
        "Funcții și statistică",
        [
            "Funcții definite pe mulțimi finite",
            "Funcția de forma f(x) = ax + b. Interpretarea geometrică. Lecturi grafice",
            "Elemente de statistică. Indicatorii tendinței centrale",
        ],
    ),
    (
        "geometrie-in-spatiu",
        "Geometrie în spațiu",
        [
            "Puncte, drepte și plane",
            "Corpuri geometrice: piramida, piramida regulată și tetraedrul regulat",
            "Corpuri geometrice: prisma dreaptă, paralelipipedul dreptunghic și cubul",
            "Corpuri geometrice: cilindrul circular drept și conul circular drept",
            "Drepte paralele. Unghiul a două drepte",
            "Dreaptă paralelă cu un plan",
            "Plane paralele",
            "Secțiuni paralele cu baza în corpurile geometrice studiate",
            "Dreaptă perpendiculară pe un plan. Distanța de la un punct la un plan",
            "Distanța dintre două plane paralele. Înălțimea prismei, cilindrului, piramidei și conului",
            "Plane perpendiculare. Secțiuni diagonale și secțiuni axiale",
            "Proiecții pe un plan. Unghiul dintre o dreaptă și un plan",
            "Unghi diedru. Unghiul plan corespunzător. Unghiul a două plane",
            "Teorema celor trei perpendiculare. Calculul distanțelor în spațiu",
        ],
    ),
    (
        "arii-volume",
        "Arii și volume",
        [
            "Distanțe și măsuri de unghiuri în corpuri geometrice",
            "Prisma dreaptă: arii și volum",
            "Piramida regulată: arii și volum",
            "Trunchiul de piramidă regulată: arii și volum",
            "Cilindrul circular drept: arii și volum",
            "Conul circular drept și trunchiul de con: arii și volume",
            "Sfera",
        ],
    ),
]


def slugify(value: str) -> str:
    value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode()
    value = re.sub(r"[^a-zA-Z0-9]+", "_", value).strip("_").lower()
    return value[:70]


def main() -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    manifest = [chapter for chapter in manifest if chapter.get("class_level") != 8]

    for chapter_order, (chapter_slug, chapter_title, lessons) in enumerate(CHAPTERS, 1):
        filenames = []
        for lesson_order, lesson_title in enumerate(lessons, 1):
            filename = f"clasa_8_u{chapter_order:02d}_l{lesson_order:02d}_{slugify(lesson_title)}.json"
            filenames.append(filename)
            path = ROOT / filename
            if not path.exists():
                payload = {
                    "title": lesson_title,
                    "description": f"Clasa a 8-a · {chapter_title}",
                    "difficulty": "easy",
                    "questions": [],
                }
                path.write_text(
                    json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
                    encoding="utf-8",
                )

        manifest.append(
            {
                "class_level": 8,
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
