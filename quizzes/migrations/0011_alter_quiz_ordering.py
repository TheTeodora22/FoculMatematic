from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("quizzes", "0010_quiz_order"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="quiz",
            options={"ordering": ["chapter__order", "order", "title"]},
        ),
    ]
