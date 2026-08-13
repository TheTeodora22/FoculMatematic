"""Generează structura JSON goală pentru programa clasei a IX-a."""

import json
import re
import unicodedata
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "chapters.json"

CHAPTERS = [
    (
        "multimi-logica-matematica",
        "Mulțimi și logică matematică",
        [
            "Mulțimea numerelor reale. Operații, ordonare, modul și aproximări",
            "Puteri, radicali și operații cu intervale de numere reale",
            "Propoziții, predicate și cuantificatori",
            "Operații logice elementare și legi de calcul",
            "Raționamente logice. Inducția matematică și probleme de numărare",
        ],
    ),
    (
        "functii",
        "Funcții",
        [
            "Șiruri de numere reale. Notația și termenul general",
            "Progresii aritmetice și geometrice. Aplicații",
            "Funcții. Reper cartezian, produs cartezian și reprezentare grafică",
            "Noțiunea, imaginea și preimaginea unei funcții",
            "Graficul, restricțiile și prelungirile unei funcții. Funcții numerice",
            "Proprietăți generale ale funcțiilor: mărginire, paritate, periodicitate și monotonie",
            "Compunerea funcțiilor",
        ],
    ),
    (
        "functia-gradul-intai",
        "Funcția de gradul I",
        [
            "Funcția de gradul I. Definiție și reprezentare grafică",
            "Interpretarea grafică a proprietăților algebrice. Monotonie și semn",
            "Inecuații de forma ax + b ≤ 0 și studiul lor pe R",
            "Poziția relativă a două drepte",
            "Sisteme de ecuații și sisteme de inecuații de gradul I",
        ],
    ),
    (
        "functia-gradul-doi",
        "Funcția de gradul al II-lea",
        [
            "Funcția de gradul al II-lea. Forma canonică, maximul și minimul",
            "Graficul funcției de gradul al II-lea. Simetrie și intersecții cu axele",
            "Reprezentarea grafică și imaginea funcției de gradul al II-lea",
            "Relațiile lui Viète",
            "Interpretarea geometrică a proprietăților algebrice. Monotonie și semn",
            "Poziția relativă a unei drepte față de o parabolă",
            "Sisteme de ecuații cu ecuații de gradul al II-lea",
        ],
    ),
    (
        "vectori-plan",
        "Vectori în plan",
        [
            "Segmente orientate. Relația de echipolență",
            "Vectorul de poziție al unui punct. Vectorul lui Thales",
            "Operații cu vectori în plan. Adunarea și înmulțirea cu scalari",
            "Descompunerea unui vector după doi vectori necoliniari",
        ],
    ),
    (
        "coliniaritate-concurenta-paralelism",
        "Coliniaritate, concurență și paralelism",
        [
            "Vectorul de poziție al unui punct în plan",
            "Teorema lui Thales",
            "Vectorul de poziție al centrului de greutate al unui triunghi",
            "Teorema bisectoarei. Relația lui Sylvester",
            "Teorema lui Menelau",
        ],
    ),
    (
        "trigonometrie",
        "Elemente de trigonometrie",
        [
            "Unghiuri și arce. Măsura unghiurilor și arcelor",
            "Generalizarea noțiunii de unghi",
            "Funcții trigonometrice. Sinus, cosinus, tangentă și cotangentă",
            "Semnul funcțiilor trigonometrice",
            "Formule de reducere la primul cadran",
            "Paritatea și imparitatea funcțiilor trigonometrice",
            "Relații între funcțiile trigonometrice ale aceluiași unghi",
            "Funcțiile trigonometrice ale unei sume și diferențe de unghiuri",
            "Transformarea sumelor în produs și a produselor în sume",
        ],
    ),
    (
        "aplicatii-trigonometrie-geometrie",
        "Aplicații ale trigonometriei în geometrie",
        [
            "Produsul scalar a doi vectori. Unghiul a doi vectori și teorema cosinusului",
            "Aplicații vectoriale în geometria plană. Coliniaritate și relația lui Leibniz",
            "Rezolvarea triunghiurilor. Raza cercului circumscris și înscris. Formule pentru arie",
        ],
    ),
]


def slugify(value: str) -> str:
    value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode()
    value = re.sub(r"[^a-zA-Z0-9]+", "_", value).strip("_").lower()
    return value[:70]


def main() -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    manifest = [chapter for chapter in manifest if chapter.get("class_level") != 9]

    for chapter_order, (chapter_slug, chapter_title, lessons) in enumerate(CHAPTERS, 1):
        filenames = []
        for lesson_order, lesson_title in enumerate(lessons, 1):
            filename = f"clasa_9_u{chapter_order:02d}_l{lesson_order:02d}_{slugify(lesson_title)}.json"
            filenames.append(filename)
            path = ROOT / filename
            if not path.exists():
                payload = {
                    "title": lesson_title,
                    "description": f"Clasa a 9-a · {chapter_title}",
                    "difficulty": "easy",
                    "questions": [],
                }
                path.write_text(
                    json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
                    encoding="utf-8",
                )

        manifest.append(
            {
                "class_level": 9,
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
