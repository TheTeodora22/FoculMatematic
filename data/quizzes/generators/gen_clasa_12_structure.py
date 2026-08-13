"""Generează structura JSON goală pentru programa clasei a XII-a."""

import json
import re
import unicodedata
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "chapters.json"

CHAPTERS = [
    (
        "grupuri",
        "Grupuri",
        [
            "Legi de compoziție pe o mulțime. Definiții și exemple",
            "Operații modulo n și partea stabilă",
            "Tabla unei legi de compoziție",
            "Proprietățile legilor de compoziție: comutativitate și asociativitate",
            "Element neutru și elemente simetrizabile",
            "Noțiunea de grup. Exemple de grupuri",
            "Grupul aditiv al resturilor modulo n și grupul claselor de resturi modulo n",
            "Grupul permutărilor și grupul simetric",
            "Grupuri de matrice și grupul rădăcinilor de ordin n ale unității",
            "Reguli de calcul într-un grup",
            "Morfisme de grupuri",
            "Subgrupuri",
            "Grupuri finite. Ordinul unui element și teoreme remarcabile",
        ],
    ),
    (
        "inele-corpuri",
        "Inele și corpuri",
        [
            "Inele. Definiții și exemple",
            "Inelul claselor de resturi modulo n și inele de matrice pătratice",
            "Inele de funcții reale",
            "Reguli de calcul într-un inel",
            "Corpuri",
            "Morfisme de inele și corpuri",
        ],
    ),
    (
        "inele-de-polinoame",
        "Inele de polinoame",
        [
            "Mulțimea polinoamelor cu coeficienți într-un corp comutativ",
            "Șiruri de elemente și operații cu șiruri într-un corp",
            "Forma algebrică a polinoamelor. Monoame și polinoame",
            "Valoarea unui polinom și funcții polinomiale",
            "Operații cu polinoame scrise sub formă algebrică",
            "Împărțirea polinoamelor. Schema lui Horner",
            "Divizibilitatea polinoamelor. Relația și proprietățile divizibilității",
            "Cel mai mare divizor comun al polinoamelor",
            "Rădăcinile unui polinom și rădăcini multiple",
            "Ecuații algebrice și polinoame reductibile în factori ireductibili",
            "Descompunerea polinoamelor în factori ireductibili",
            "Relațiile lui Viète",
            "Ecuații algebrice cu coeficienți întregi, raționali sau reali",
            "Ecuații algebrice de grad superior cu coeficienți complecși",
            "Ecuații bipătrate, binome și reciproce",
        ],
    ),
    (
        "primitive",
        "Primitive",
        [
            "Probleme care conduc la noțiunea de integrală",
            "Primitivele unei funcții. Integrala nedefinită",
            "Proprietăți ale integralei nedefinite",
            "Primitive uzuale deduse din derivatele funcțiilor elementare",
            "Primitive deduse din derivarea funcțiilor compuse",
            "Primitive deduse din formula de derivare a produsului a două funcții",
        ],
    ),
    (
        "integrala-definita",
        "Integrala definită",
        [
            "Diviziuni ale unui interval și sume Riemann",
            "Integrabilitatea unei funcții pe un interval",
            "Integrabilitatea funcțiilor continue",
            "Formula lui Leibniz–Newton",
            "Proprietăți ale integralei definite",
            "Integrarea funcțiilor continue",
            "Metoda integrării prin părți",
            "Metoda schimbării de variabilă",
            "Calculul integralelor funcțiilor raționale",
        ],
    ),
    (
        "aplicatii-integrala-definita",
        "Aplicații ale integralei definite",
        [
            "Aria unei suprafețe plane",
            "Volumul corpurilor de rotație",
            "Calculul unor limite de șiruri folosind integrala definită",
        ],
    ),
]


def slugify(value: str) -> str:
    value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode()
    value = re.sub(r"[^a-zA-Z0-9]+", "_", value).strip("_").lower()
    return value[:70]


def main() -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    manifest = [chapter for chapter in manifest if chapter.get("class_level") != 12]

    for chapter_order, (chapter_slug, chapter_title, lessons) in enumerate(CHAPTERS, 1):
        filenames = []
        for lesson_order, lesson_title in enumerate(lessons, 1):
            filename = f"clasa_12_u{chapter_order:02d}_l{lesson_order:02d}_{slugify(lesson_title)}.json"
            filenames.append(filename)
            path = ROOT / filename
            if not path.exists():
                payload = {
                    "title": lesson_title,
                    "description": f"Clasa a 12-a · {chapter_title}",
                    "difficulty": "easy",
                    "questions": [],
                }
                path.write_text(
                    json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
                    encoding="utf-8",
                )

        manifest.append(
            {
                "class_level": 12,
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
