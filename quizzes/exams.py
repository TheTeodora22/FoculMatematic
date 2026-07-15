EXAM_DEFINITIONS = {
    "evaluare-nationala": {
        "title": "Evaluarea Națională",
        "description": (
            "Pregătire pentru Evaluarea Națională la matematică — subiecte, "
            "antrenament și chestionare pentru clasa a VIII-a."
        ),
        "fallback_class": 8,
    },
    "bacalaureat": {
        "title": "Bacalaureat",
        "description": (
            "Pregătire pentru examenul de Bacalaureat la matematică — subiecte, "
            "antrenament și chestionare pentru clasa a XII-a."
        ),
        "fallback_class": 12,
    },
}


def get_exam(slug: str) -> dict | None:
    exam = EXAM_DEFINITIONS.get(slug)
    if exam is None:
        return None
    return {"slug": slug, **exam}
