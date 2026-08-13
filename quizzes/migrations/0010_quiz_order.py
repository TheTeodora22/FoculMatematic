from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("quizzes", "0009_alter_question_question_type"),
    ]

    operations = [
        migrations.AddField(
            model_name="quiz",
            name="order",
            field=models.PositiveIntegerField(default=0),
        ),
    ]
