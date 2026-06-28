#!/usr/bin/env python3
"""Django's command-line utility for administrative tasks."""
import os
import sys
from pathlib import Path


def main():
    """Run administrative tasks."""
    project_root = Path(__file__).resolve().parent
    venv_python = project_root / ".venv" / "bin" / "python"
    try:
        import allauth  # noqa: F401
    except ModuleNotFoundError:
        if venv_python.is_file():
            sys.stderr.write(
                "[Focul Matematic] Lipsește pachetul django-allauth pentru interpretul curent.\n"
                f"  Acum folosești: {sys.executable}\n"
                "  Pornește Django cu mediul virtual al proiectului, de exemplu:\n"
                f"    {venv_python} manage.py runserver\n"
                "  sau:  source .venv/bin/activate && python manage.py runserver\n"
            )
            sys.exit(1)
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'FoculMatematicProiect.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
