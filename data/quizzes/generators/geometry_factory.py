"""Fabrică de date pentru atelierul geometric SVG."""


def figure(kind, label="", points=None, notation="", **extra):
    return {"kind": kind, "label": label, "points": points or [], "notation": notation, **extra}


def point(name, x, y):
    return {"name": name, "x": x, "y": y}


def exercise(text, mode, answers, explanation, *, figures=None, points=None, format_tag="interactive", **data):
    interactive = {"mode": mode, "answers": answers, **data}
    if figures is not None:
        interactive["figures"] = figures
    if points is not None:
        interactive["points"] = points
    return {"text": text, "type": "geometry_canvas", "format": format_tag, "points": 10,
            "explanation": explanation, "interactive": interactive}


KINDS = ["point", "line", "segment", "ray", "plane", "halfplane"]


def standard_figures(labels=("A", "AB", "AB", "AB", "α", "ρ")):
    return [figure(kind, label=label, notation=label) for kind, label in zip(KINDS, labels)]
