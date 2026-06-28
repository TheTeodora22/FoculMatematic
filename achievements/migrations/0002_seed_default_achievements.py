from django.db import migrations


def seed_achievements(apps, schema_editor):
    Achievement = apps.get_model("achievements", "Achievement")
    rows = [
        {
            "slug": "prima-lectie",
            "title": "First lesson",
            "description": "Completed your first lesson quiz in the curriculum.",
            "icon": "📘",
            "trigger": "first_lesson_quiz",
            "threshold": 0,
            "sort_order": 10,
        },
        {
            "slug": "perfect-lectie",
            "title": "Perfection",
            "description": "Max score on a lesson quiz.",
            "icon": "💯",
            "trigger": "perfect_lesson_quiz",
            "threshold": 0,
            "sort_order": 20,
        },
        {
            "slug": "pion-concentrat",
            "title": "Focused pawn",
            "description": "Completed 5 lesson quizzes.",
            "icon": "♟️",
            "trigger": "lesson_quiz_total",
            "threshold": 5,
            "sort_order": 30,
        },
        {
            "slug": "maraton-lectii",
            "title": "Lesson marathon",
            "description": "Completed 15 lesson quizzes.",
            "icon": "📚",
            "trigger": "lesson_quiz_total",
            "threshold": 15,
            "sort_order": 40,
        },
        {
            "slug": "urca-scara",
            "title": "Climbing up",
            "description": "Reached at least level 5.",
            "icon": "🪜",
            "trigger": "level_at_least",
            "threshold": 5,
            "sort_order": 50,
        },
        {
            "slug": "veteran-nivel",
            "title": "Veteran",
            "description": "Reached at least level 10.",
            "icon": "🛡️",
            "trigger": "level_at_least",
            "threshold": 10,
            "sort_order": 60,
        },
        {
            "slug": "foc-xp",
            "title": "XP on fire",
            "description": "Earned 500 total XP.",
            "icon": "🔥",
            "trigger": "xp_total",
            "threshold": 500,
            "sort_order": 70,
        },
        {
            "slug": "explorer-quiz",
            "title": "Explorer",
            "description": "Completed your first quiz from the Quizzes section.",
            "icon": "🧭",
            "trigger": "first_legacy_quiz",
            "threshold": 0,
            "sort_order": 80,
        },
        {
            "slug": "orice-10",
            "title": "All-rounder",
            "description": "Completed 10 quizzes in total (lessons + classic).",
            "icon": "🎯",
            "trigger": "any_quiz_total",
            "threshold": 10,
            "sort_order": 90,
        },
        {
            "slug": "battlepass-inceput",
            "title": "Rewards trail",
            "description": "Claimed your first Battle Pass reward.",
            "icon": "🎁",
            "trigger": "battlepass_claims",
            "threshold": 1,
            "sort_order": 100,
        },
    ]
    for row in rows:
        slug = row.pop("slug")
        Achievement.objects.update_or_create(slug=slug, defaults=row)


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("achievements", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed_achievements, noop_reverse),
    ]
