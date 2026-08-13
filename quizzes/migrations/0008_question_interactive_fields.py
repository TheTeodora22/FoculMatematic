from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("quizzes", "0007_quiz_class_levels_quiz_exam_slugs"),
    ]

    operations = [
        migrations.AddField(
            model_name="question",
            name="question_type",
            field=models.CharField(
                choices=[
                    ("multiple_choice", "Grilă"),
                    ("parentheses_drag", "Plasează parantezele"),
                ],
                default="multiple_choice",
                max_length=30,
            ),
        ),
        migrations.AddField(
            model_name="question",
            name="interactive_data",
            field=models.JSONField(blank=True, default=dict),
        ),
    ]
