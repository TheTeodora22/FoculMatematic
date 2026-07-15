from quizzes.exams import EXAM_DEFINITIONS, get_exam
from quizzes.models import Quiz


def normalize_class_levels(data: dict, chapter) -> list[int]:
    raw = data.get("class_levels")
    if raw is not None:
        return [int(level) for level in raw]
    if chapter:
        return [chapter.class_level]
    return []


def normalize_exam_slugs(data: dict, chapter) -> list[str]:
    raw = data.get("exam_slugs", [])
    slugs = [slug.strip() for slug in raw if isinstance(slug, str) and slug.strip()]
    if not slugs and chapter and chapter.exam_slug:
        slugs = [chapter.exam_slug]
    return [slug for slug in slugs if slug in EXAM_DEFINITIONS]


def build_lesson_tags(topic: Quiz) -> list[dict]:
    tags: list[dict] = []
    levels = topic.class_levels or []
    if not levels and topic.chapter_id:
        levels = [topic.chapter.class_level]

    seen_labels = set()
    for level in levels:
        label = f"Clasa a {level}-a"
        if label not in seen_labels:
            tags.append({"type": "class", "label": label})
            seen_labels.add(label)

    for slug in topic.exam_slugs or []:
        exam = get_exam(slug)
        if exam and exam["title"] not in seen_labels:
            tags.append({"type": "exam", "label": exam["title"], "slug": slug})
            seen_labels.add(exam["title"])

    return tags


def topics_for_exam(exam_slug: str):
    from django.db import connection
    from django.db.models import Q

    from quizzes.models import Quiz

    chapter_filter = Q(chapter__exam_slug=exam_slug)
    if connection.vendor == "postgresql":
        exam_filter = Q(exam_slugs__contains=[exam_slug])
    else:
        tagged_pks = [
            pk
            for pk, slugs in Quiz.objects.values_list("pk", "exam_slugs")
            if exam_slug in (slugs or [])
        ]
        exam_filter = Q(pk__in=tagged_pks)

    return (
        Quiz.objects.filter(exam_filter | chapter_filter)
        .select_related("chapter")
        .distinct()
        .order_by("title")
    )
