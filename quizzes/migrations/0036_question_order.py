from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("quizzes", "0035_alter_question_question_type")]

    operations = [
        migrations.AddField(
            model_name="question",
            name="order",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterModelOptions(
            name="question",
            options={"ordering": ["order", "id"]},
        ),
    ]
