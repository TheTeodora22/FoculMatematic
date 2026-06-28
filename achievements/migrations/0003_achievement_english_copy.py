from django.db import migrations, models


def english_achievement_copy(apps, schema_editor):
    Achievement = apps.get_model("achievements", "Achievement")
    updates = {
        "prima-lectie": {
            "title": "First lesson",
            "description": "Completed your first lesson quiz in the curriculum.",
        },
        "perfect-lectie": {
            "title": "Perfection",
            "description": "Max score on a lesson quiz.",
        },
        "pion-concentrat": {
            "title": "Focused pawn",
            "description": "Completed 5 lesson quizzes.",
        },
        "maraton-lectii": {
            "title": "Lesson marathon",
            "description": "Completed 15 lesson quizzes.",
        },
        "urca-scara": {
            "title": "Climbing up",
            "description": "Reached at least level 5.",
        },
        "veteran-nivel": {
            "title": "Veteran",
            "description": "Reached at least level 10.",
        },
        "foc-xp": {
            "title": "XP on fire",
            "description": "Earned 500 total XP.",
        },
        "explorer-quiz": {
            "title": "Explorer",
            "description": "Completed your first quiz from the Quizzes section.",
        },
        "orice-10": {
            "title": "All-rounder",
            "description": "Completed 10 quizzes in total (lessons + classic).",
        },
        "battlepass-inceput": {
            "title": "Rewards trail",
            "description": "Claimed your first Battle Pass reward.",
        },
    }
    for slug, fields in updates.items():
        Achievement.objects.filter(slug=slug).update(**fields)


class Migration(migrations.Migration):

    dependencies = [
        ("achievements", "0002_seed_default_achievements"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="achievement",
            options={
                "ordering": ["sort_order", "slug"],
                "verbose_name": "Achievement",
                "verbose_name_plural": "Achievements",
            },
        ),
        migrations.AlterModelOptions(
            name="userachievement",
            options={
                "ordering": ["-unlocked_at"],
                "verbose_name": "Unlocked achievement",
                "verbose_name_plural": "Unlocked achievements",
            },
        ),
        migrations.AlterField(
            model_name="achievement",
            name="icon",
            field=models.CharField(
                default="🏅",
                help_text="Emoji shown as the badge icon.",
                max_length=8,
            ),
        ),
        migrations.AlterField(
            model_name="achievement",
            name="threshold",
            field=models.PositiveIntegerField(
                default=0,
                help_text="For counters, min level, or XP: target value. Use 0 when not applicable.",
            ),
        ),
        migrations.RunPython(english_achievement_copy, migrations.RunPython.noop),
    ]
