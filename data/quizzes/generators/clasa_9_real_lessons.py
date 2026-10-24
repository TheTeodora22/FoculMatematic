"""Structura secțiunii Mulțimea numerelor reale, conform cuprinsului Burtea."""
LESSONS = [
    ("1.1", "Operații algebrice cu numere reale", "clasa_9_numere_reale_1_1_operatii_algebrice.json"),
    ("1.2", "Ordonarea numerelor reale", "clasa_9_numere_reale_1_2_ordonare.json"),
    ("1.3", "Modulul unui număr real", "clasa_9_numere_reale_1_3_modul.json"),
    ("1.4", "Aproximări prin lipsă sau prin adaos", "clasa_9_numere_reale_1_4_aproximari.json"),
    ("1.5", "Parte întreagă. Parte fracționară", "clasa_9_numere_reale_1_5_parte_intreaga_fractionara.json"),
    ("1.6", "Operații cu intervale de numere reale", "clasa_9_numere_reale_1_6_intervale.json"),
]


def configure_manifest(manifest):
    manifest = [c for c in manifest if not (c.get("class_level") == 9 and c["slug"] == "multimea-numerelor-reale")]
    first = next(i for i,c in enumerate(manifest) if c.get("class_level") == 9)
    chapter = {
        "class_level": 9, "slug": "multimea-numerelor-reale", "title": "Mulțimea numerelor reale", "order": 1,
        "topics": [f"clasa_9/{filename}" for _,_,filename in LESSONS],
    }
    manifest.insert(first, chapter)
    for c in manifest:
        if c.get("class_level") == 9 and c["slug"] == "multimi-logica-matematica":
            c["topics"] = [p for p in c["topics"] if not p.startswith(("clasa_9/clasa_9_u01_l01_", "clasa_9/clasa_9_u01_l02_"))]
    for order,c in enumerate((c for c in manifest if c.get("class_level") == 9),1):
        c["order"] = order
    return manifest
