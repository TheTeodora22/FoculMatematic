from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("quizzes", "0008_question_interactive_fields"),
    ]

    operations = [
        migrations.AlterField(
            model_name="question",
            name="question_type",
            field=models.CharField(
                choices=[
                    ("multiple_choice", "Grilă"),
                    ("parentheses_drag", "Plasează parantezele"),
                    ("column_subtraction", "Scădere în coloană"),
                    ("missing_digits", "Completează cifrele lipsă"),
                    ("error_spotting", "Detectează greșeala"),
                    ("parentheses_target", "Paranteze pentru rezultat-țintă"),
                    ("input_output", "Mașină intrare–ieșire"),
                ],
                default="multiple_choice",
                max_length=30,
            ),
        ),
    ]
