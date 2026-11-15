"""Repeatable frontend checks. Run with the project's virtual-environment Python."""
from pathlib import Path
import shutil
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
PYTHON = [sys.executable, "-X", "utf8"]
DJANGO_TESTS = (
    "quizzes.tests.TrainingTests", "quizzes.tests.NavigationTests",
    "quizzes.tests.QuizFlowTests", "quizzes.tests.GeneratedSessionTests",
    "quizzes.tests.ExamTests", "quizzes.test_ui_states", "quizzes.test_page_experience",
    "accounts.test_ui_components", "accounts.test_accessibility",
    "accounts.tests.ProfileViewTests", "feedback.tests.ErrorReportFormTests",
    "analytics.tests", "FoculMatematic.test_math_demo",
)


def run(label, command):
    print(f"\n{label}", flush=True)
    subprocess.run(command, cwd=ROOT, check=True)


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    node = shutil.which("node")
    git = shutil.which("git")
    if not node or not git:
        print("Node.js și Git trebuie să fie disponibile în PATH.", file=sys.stderr)
        return 1
    run("Django: verificarea configurației", [*PYTHON, "manage.py", "check"])
    run("Django: compilarea tuturor șabloanelor", [*PYTHON, "manage.py", "shell", "-c",
        "from pathlib import Path; from django.template.loader import get_template; "
        "files=list(Path('templates').rglob('*.html')); "
        "[get_template(p.relative_to('templates').as_posix()) for p in files]; "
        "print(f'{len(files)} șabloane compilate.')"])
    scripts = sorted((ROOT / "static/core/js").glob("*.js"))
    print(f"\nJavaScript: verificarea sintaxei pentru {len(scripts)} fișiere", flush=True)
    for script in scripts:
        subprocess.run([node, "--check", str(script)], cwd=ROOT, check=True)
    tests = sorted((ROOT / "scripts").glob("test_*.cjs"))
    run("JavaScript: teste automate", [node, "--test", *(str(p) for p in tests)])
    run("Django: regresii pentru interfață și fluxurile existente",
        [*PYTHON, "manage.py", "test", *DJANGO_TESTS, "--verbosity", "1"])
    run("Git: verificarea diferențelor", [git, "diff", "--check"])
    print("\nVerificările automate au trecut. Verificările în browser se fac separat.", flush=True)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except subprocess.CalledProcessError as error:
        print(f"\nVerificare eșuată (cod {error.returncode}).", file=sys.stderr)
        raise SystemExit(error.returncode)
