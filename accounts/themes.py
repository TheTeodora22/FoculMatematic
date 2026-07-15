THEMES = {
    "light": {
        "--bg": "#f5f7fa",
        "--surface": "#ffffff",
        "--text": "#1a2332",
        "--muted": "#5c6b7f",
        "--accent": "#e85d04",
        "--accent-hover": "#c44d03",
        "--border": "#d8dee9",
    },
    "dark_theme_1": {
        "--bg": "#0f1419",
        "--surface": "#1a2332",
        "--text": "#e7ecf3",
        "--muted": "#8b9cb3",
        "--accent": "#e85d04",
        "--accent-hover": "#f48c06",
        "--border": "#2d3a4d",
    },
    "fire_theme": {
        "--bg": "#1a0a00",
        "--surface": "#2d1408",
        "--text": "#fff0e6",
        "--muted": "#c9a08a",
        "--accent": "#ff6b35",
        "--accent-hover": "#ff8c5a",
        "--border": "#4a2010",
    },
}

DEFAULT_THEME = "dark_theme_1"


def get_theme_vars(theme_key: str) -> dict:
    return THEMES.get(theme_key, THEMES[DEFAULT_THEME])


def theme_css_vars(theme_key: str) -> str:
    vars_dict = get_theme_vars(theme_key)
    return "; ".join(f"{k}: {v}" for k, v in vars_dict.items())
