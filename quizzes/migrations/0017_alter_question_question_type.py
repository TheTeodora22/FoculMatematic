from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("quizzes", "0016_alter_question_question_type")]

    operations = [
        migrations.AlterField(
            model_name="question",
            name="question_type",
            field=models.CharField(
                choices=[
                    *[(value, label) for value, label in [
                        ("multiple_choice", "Grilă"), ("parentheses_drag", "Plasează parantezele"),
                        ("column_addition", "Adunare în coloană"), ("column_multiplication", "Înmulțire în coloană"),
                        ("column_division", "Împărțire în coloană"), ("column_subtraction", "Scădere în coloană"),
                        ("missing_digits", "Completează cifrele lipsă"), ("error_spotting", "Detectează greșeala"),
                        ("parentheses_target", "Paranteze pentru rezultat-țintă"), ("input_output", "Mașină intrare–ieșire"),
                        ("division_relation", "Relația împărțirii"), ("operation_chain", "Lanț de operații"),
                        ("division_table", "Tabelul împărțirii"), ("numeric_input", "Răspuns numeric"),
                        ("factor_builder", "Construiește factorizarea"), ("factor_error", "Detectează pasul greșit"),
                        ("factor_match", "Potrivește forme echivalente"), ("power_builder", "Construiește sau desfă puterea"),
                        ("power_match", "Potrivește formele unei puteri"), ("power_table", "Completează tabelul puterilor"),
                        ("power_cycle", "Ciclul ultimei cifre"), ("power_square", "Reprezentarea pătratului"),
                        ("power_rule_chain", "Lanț de reguli pentru puteri"), ("power_compare", "Compară două puteri"),
                        ("power_order", "Ordonează puteri"),
                    ]],
                ],
                default="multiple_choice",
                max_length=30,
            ),
        )
    ]
