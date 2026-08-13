"""Generează structura JSON goală pentru programa clasei a VII-a."""

import json
import re
import unicodedata
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "chapters.json"

CHAPTERS = [
    (
        "numere-reale",
        "Numere reale",
        [
            "Rădăcina pătrată a pătratului unui număr natural. Estimarea rădăcinii pătrate",
            "Mulțimea numerelor reale",
            "Reguli de calcul cu radicali",
            "Adunarea și scăderea numerelor reale",
            "Înmulțirea și împărțirea numerelor reale",
            "Puterea cu exponent întreg a unui număr real. Ordinea operațiilor",
            "Raționalizarea numitorului unei fracții",
            "Media aritmetică ponderată și media geometrică",
            "Ecuația de forma x² = a, unde a este număr real",
        ],
    ),
    (
        "ecuatii-sisteme-liniare",
        "Ecuații și sisteme liniare",
        [
            "Transformarea unei egalități într-o egalitate echivalentă. Identități",
            "Ecuații de forma ax + b = 0. Mulțimea soluțiilor. Ecuații echivalente",
            "Sisteme de două ecuații liniare cu două necunoscute",
            "Probleme rezolvate cu ecuații sau sisteme de ecuații liniare",
        ],
    ),
    (
        "organizarea-datelor",
        "Organizarea datelor",
        [
            "Produsul cartezian. Sisteme de axe ortogonale. Reprezentarea punctelor și distanța în plan",
            "Reprezentarea și interpretarea dependențelor funcționale. Poligonul frecvențelor",
        ],
    ),
    (
        "patrulatere",
        "Patrulatere",
        [
            "Patrulaterul convex. Suma măsurilor unghiurilor",
            "Paralelogramul. Proprietăți",
            "Aplicații ale paralelogramului în geometria triunghiului. Linia mijlocie și centrul de greutate",
            "Dreptunghiul. Proprietăți",
            "Rombul. Proprietăți",
            "Pătratul. Proprietăți",
            "Trapezul: clasificare și proprietăți. Linia mijlocie",
            "Perimetre și arii",
        ],
    ),
    (
        "cercul",
        "Cercul",
        [
            "Cercul. Coarde și arce în cerc. Proprietăți",
            "Unghiuri înscrise în cerc",
            "Tangente la cerc",
            "Poligoane regulate înscrise într-un cerc",
            "Lungimea cercului și aria discului",
        ],
    ),
    (
        "asemanarea-triunghiurilor",
        "Asemănarea triunghiurilor",
        [
            "Segmente proporționale. Teorema paralelelor echidistante",
            "Teorema lui Thales",
            "Triunghiuri asemenea. Teorema fundamentală a asemănării",
            "Criterii de asemănare. Aproximarea distanțelor folosind asemănarea",
        ],
    ),
    (
        "relatii-metrice-triunghi-dreptunghic",
        "Relații metrice în triunghiul dreptunghic",
        [
            "Proiecții ortogonale pe o dreaptă. Teorema înălțimii",
            "Teorema catetei",
            "Teorema lui Pitagora",
            "Noțiuni de trigonometrie în triunghiul dreptunghic",
            "Rezolvarea triunghiului dreptunghic și calculul elementelor în poligoane regulate",
        ],
    ),
]


def slugify(value: str) -> str:
    value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode()
    value = re.sub(r"[^a-zA-Z0-9]+", "_", value).strip("_").lower()
    return value[:70]


def main() -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    manifest = [chapter for chapter in manifest if chapter.get("class_level") != 7]

    for chapter_order, (chapter_slug, chapter_title, lessons) in enumerate(CHAPTERS, 1):
        filenames = []
        for lesson_order, lesson_title in enumerate(lessons, 1):
            filename = f"clasa_7_u{chapter_order:02d}_l{lesson_order:02d}_{slugify(lesson_title)}.json"
            filenames.append(filename)
            path = ROOT / filename
            if not path.exists():
                payload = {
                    "title": lesson_title,
                    "description": f"Clasa a 7-a · {chapter_title}",
                    "difficulty": "easy",
                    "questions": [],
                }
                path.write_text(
                    json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
                    encoding="utf-8",
                )

        manifest.append(
            {
                "class_level": 7,
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
