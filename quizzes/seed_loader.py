"""
Încarcă capitole și subiecte din data/quizzes/.

După migrate sau reset DB rulezi:
    python manage.py seed_quizzes
"""

import json
from pathlib import Path

from django.conf import settings
from django.db import transaction

from quizzes.lesson_tags import normalize_class_levels, normalize_exam_slugs
from quizzes.models import AnswerOption, Chapter, Question, Quiz

DIFFICULTIES = {"easy", "medium", "hard"}
CHAPTERS_MANIFEST = "chapters.json"


class SeedValidationError(Exception):
    pass


def quizzes_data_dir() -> Path:
    return Path(settings.BASE_DIR) / "data" / "quizzes"


def _validate_quiz_payload(data: dict, source: str) -> None:
    if not isinstance(data, dict):
        raise SeedValidationError(f"{source}: rădăcina trebuie să fie un obiect JSON.")

    for field in ("title", "difficulty", "questions"):
        if field not in data:
            raise SeedValidationError(f"{source}: lipsește câmpul '{field}'.")

    if data["difficulty"] not in DIFFICULTIES:
        raise SeedValidationError(
            f"{source}: difficulty trebuie să fie easy, medium sau hard."
        )

    if not isinstance(data["questions"], list):
        raise SeedValidationError(f"{source}: 'questions' trebuie să fie o listă.")

    if not data["questions"]:
        return

    for i, question in enumerate(data["questions"], start=1):
        if not question.get("text"):
            raise SeedValidationError(f"{source}: întrebarea {i} nu are text.")
        options = question.get("options", [])
        if len(options) < 2:
            raise SeedValidationError(
                f"{source}: întrebarea {i} trebuie să aibă minim 2 opțiuni."
            )
        correct = [o for o in options if o.get("is_correct")]
        if len(correct) != 1:
            raise SeedValidationError(
                f"{source}: întrebarea {i} trebuie să aibă exact o opțiune corectă."
            )
        for j, opt in enumerate(options, start=1):
            if not opt.get("text"):
                raise SeedValidationError(
                    f"{source}: întrebarea {i}, opțiunea {j} nu are text."
                )


def _validate_chapters_manifest(data: list, source: str) -> None:
    if not isinstance(data, list):
        raise SeedValidationError(f"{source}: manifestul trebuie să fie o listă.")
    for i, chapter in enumerate(data, start=1):
        for field in ("class_level", "slug", "title", "topics"):
            if field not in chapter:
                raise SeedValidationError(f"{source}: capitolul {i} lipsește '{field}'.")
        if not isinstance(chapter["topics"], list):
            raise SeedValidationError(f"{source}: capitolul {i} — topics trebuie listă.")


def _sync_options(question: Question, options_data: list) -> None:
    seen_texts = set()
    for opt in options_data:
        text = opt["text"].strip()
        seen_texts.add(text)
        option, created = AnswerOption.objects.get_or_create(
            question=question,
            text=text,
            defaults={"is_correct": bool(opt.get("is_correct"))},
        )
        if not created and option.is_correct != bool(opt.get("is_correct")):
            option.is_correct = bool(opt.get("is_correct"))
            option.save(update_fields=["is_correct"])

    question.options.exclude(text__in=seen_texts).delete()


def _sync_question(quiz: Quiz, question_data: dict) -> Question:
    text = question_data["text"].strip()
    points = int(question_data.get("points", 10))
    explanation = question_data.get("explanation", "").strip()
    question, created = Question.objects.get_or_create(
        quiz=quiz,
        text=text,
        defaults={"points": points, "explanation": explanation},
    )
    updated_fields = []
    if not created and question.points != points:
        question.points = points
        updated_fields.append("points")
    if not created and question.explanation != explanation:
        question.explanation = explanation
        updated_fields.append("explanation")
    if updated_fields:
        question.save(update_fields=updated_fields)
    _sync_options(question, question_data["options"])
    return question


def sync_quiz_from_dict(
    data: dict,
    *,
    chapter: Chapter | None = None,
    source_file: str = "",
) -> tuple[Quiz, bool]:
    title = data["title"].strip()
    class_levels = normalize_class_levels(data, chapter)
    exam_slugs = normalize_exam_slugs(data, chapter)
    defaults = {
        "title": title,
        "description": data.get("description", ""),
        "difficulty": data["difficulty"],
        "chapter": chapter,
        "class_levels": class_levels,
        "exam_slugs": exam_slugs,
    }
    if source_file:
        quiz, created = Quiz.objects.update_or_create(
            source_file=source_file,
            defaults=defaults,
        )
    else:
        quiz, created = Quiz.objects.get_or_create(title=title, defaults=defaults)

    seen_question_texts = set()
    for question_data in data["questions"]:
        question = _sync_question(quiz, question_data)
        seen_question_texts.add(question.text)

    quiz.questions.exclude(text__in=seen_question_texts).delete()
    return quiz, created


@transaction.atomic
def load_chapters_manifest(data_dir: Path | None = None) -> dict[str, Chapter]:
    directory = data_dir or quizzes_data_dir()
    manifest_path = directory / CHAPTERS_MANIFEST
    if not manifest_path.exists():
        return {}

    with manifest_path.open(encoding="utf-8") as f:
        data = json.load(f)
    _validate_chapters_manifest(data, CHAPTERS_MANIFEST)

    file_to_chapter: dict[str, Chapter] = {}
    for chapter_data in data:
        chapter, _ = Chapter.objects.update_or_create(
            class_level=int(chapter_data["class_level"]),
            slug=chapter_data["slug"].strip(),
            defaults={
                "title": chapter_data["title"].strip(),
                "order": int(chapter_data.get("order", 0)),
                "exam_slug": chapter_data.get("exam_slug", "").strip(),
            },
        )
        for filename in chapter_data["topics"]:
            file_to_chapter[filename] = chapter

    return file_to_chapter


@transaction.atomic
def load_quiz_file(path: Path, chapter: Chapter | None = None) -> tuple[Quiz, bool]:
    with path.open(encoding="utf-8") as f:
        data = json.load(f)
    _validate_quiz_payload(data, path.name)
    return sync_quiz_from_dict(data, chapter=chapter, source_file=path.name)


@transaction.atomic
def load_all_quizzes(
    data_dir: Path | None = None,
    only_file: str | None = None,
) -> list[tuple[Quiz, bool, str]]:
    directory = data_dir or quizzes_data_dir()
    if not directory.exists():
        return []

    file_to_chapter = load_chapters_manifest(directory)
    if only_file:
        paths = [directory / only_file]
    else:
        if file_to_chapter:
            paths = [directory / name for name in sorted(file_to_chapter.keys())]
        else:
            paths = sorted(
                p for p in directory.glob("*.json") if p.name != CHAPTERS_MANIFEST
            )

    results = []
    for path in paths:
        if not path.exists():
            continue
        if path.name.startswith("_") or path.name == CHAPTERS_MANIFEST:
            continue
        chapter = file_to_chapter.get(path.name)
        quiz, created = load_quiz_file(path, chapter=chapter)
        results.append((quiz, created, path.name))
    return results
