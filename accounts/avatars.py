"""Avatare predefinite (cheie → etichetă + emoji pentru UI)."""

AVATAR_CHOICES = [
    ("ember", "Flacără"),
    ("spark", "Scânteie"),
    ("compass", "Compas"),
    ("sigma", "Sigma"),
    ("infinity", "Infinit"),
    ("graph", "Grafic"),
    ("star", "Stea"),
    ("rocket", "Rachetă"),
    ("brain", "Logică"),
    ("trophy", "Trofeu"),
]

AVATAR_EMOJI = {
    "ember": "🔥",
    "spark": "✨",
    "compass": "🧭",
    "sigma": "∑",
    "infinity": "∞",
    "graph": "📈",
    "star": "⭐",
    "rocket": "🚀",
    "brain": "🧠",
    "trophy": "🏆",
}

DEFAULT_AVATAR = "ember"


def avatar_label(key: str) -> str:
    return dict(AVATAR_CHOICES).get(key, key)


def avatar_emoji(key: str) -> str:
    return AVATAR_EMOJI.get(key, "⭐")
