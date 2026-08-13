"""Generează structura JSON goală pentru programa clasei a X-a."""

import json
import re
import unicodedata
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "chapters.json"

CHAPTERS = [
    (
        "multimi-de-numere",
        "Mulțimi de numere",
        [
            "Mulțimea numerelor reale. Puteri și radicali",
            "Radicali de ordin n. Proprietăți și operații",
            "Raționalizarea numitorilor",
            "Puteri cu exponent rațional și real",
            "Logaritmi. Proprietăți ale logaritmilor",
            "Mulțimea numerelor complexe. Forma algebrică și operații",
            "Numere complexe conjugate și modulul unui număr complex",
            "Interpretarea geometrică a numerelor complexe",
            "Ecuații de gradul al II-lea cu coeficienți reali. Relațiile lui Viète",
            "Numere complexe în formă trigonometrică. Operații și radicali",
        ],
    ),
    (
        "functii-ecuatii",
        "Funcții și ecuații",
        [
            "Funcții injective, surjective și bijective",
            "Funcții inversabile. Inversa unei funcții",
            "Funcția putere cu exponent natural",
            "Funcția radical",
            "Funcția exponențială",
            "Funcția logaritmică",
            "Funcții trigonometrice directe și inverse",
            "Ecuații iraționale",
            "Ecuații exponențiale",
            "Ecuații logaritmice",
            "Ecuații trigonometrice fundamentale",
            "Ecuații trigonometrice reductibile la ecuații fundamentale",
            "Ecuații trigonometrice liniare în sin x și cos x",
        ],
    ),
    (
        "metode-de-numarare",
        "Metode de numărare",
        [
            "Metoda inducției matematice",
            "Mulțimi finite ordonate",
            "Permutările unei mulțimi finite. Calculul lui n!",
            "Numărul funcțiilor bijective între două mulțimi finite",
            "Combinări și aranjamente. Definiții și formule",
            "Drumuri de lungime minimă într-o rețea. Formula lui Pascal",
            "Numărul funcțiilor injective între două mulțimi finite",
            "Binomul lui Newton. Formula și aplicații",
        ],
    ),
    (
        "matematici-financiare-statistica-probabilitati",
        "Matematici financiare, statistică și probabilități",
        [
            "Procente. Dobândă simplă și dobândă compusă",
            "Taxa pe valoarea adăugată și alte elemente de calcul financiar",
            "Date statistice. Culegerea, înregistrarea și clasificarea datelor",
            "Serii statistice și frecvențe",
            "Reprezentarea grafică și interpretarea datelor statistice",
            "Experimente și evenimente aleatoare. Operații cu evenimente",
            "Probabilitatea unui eveniment și probabilități condiționate",
            "Evenimente independente. Scheme clasice de probabilitate",
            "Variabile aleatoare",
        ],
    ),
    (
        "geometrie-analitica",
        "Geometrie analitică",
        [
            "Reper cartezian în plan. Coordonatele unui vector",
            "Coordonatele unei sume vectoriale. Distanța dintre două puncte",
            "Dreapta în plan. Ecuația determinată de un punct și o direcție",
            "Ecuația dreptei determinate de două puncte",
            "Condiții de paralelism și perpendicularitate a două drepte",
            "Distanța de la un punct la o dreaptă și distanța dintre două drepte paralele",
            "Aria unui triunghi și aria unei suprafețe poligonale convexe",
        ],
    ),
]


def slugify(value: str) -> str:
    value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode()
    value = re.sub(r"[^a-zA-Z0-9]+", "_", value).strip("_").lower()
    return value[:70]


def main() -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    manifest = [chapter for chapter in manifest if chapter.get("class_level") != 10]

    for chapter_order, (chapter_slug, chapter_title, lessons) in enumerate(CHAPTERS, 1):
        filenames = []
        for lesson_order, lesson_title in enumerate(lessons, 1):
            filename = f"clasa_10_u{chapter_order:02d}_l{lesson_order:02d}_{slugify(lesson_title)}.json"
            filenames.append(filename)
            path = ROOT / filename
            if not path.exists():
                payload = {
                    "title": lesson_title,
                    "description": f"Clasa a 10-a · {chapter_title}",
                    "difficulty": "easy",
                    "questions": [],
                }
                path.write_text(
                    json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
                    encoding="utf-8",
                )

        manifest.append(
            {
                "class_level": 10,
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
