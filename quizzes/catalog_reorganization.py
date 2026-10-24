"""Mutarea idempotentă a lecției vechi în subcapitole, păstrând ID-urile."""
import json
from pathlib import Path

from quizzes.models import Question, Quiz


OLD_SOURCE = "clasa_9_u01_l01_multimea_numerelor_reale_operatii_ordonare_modul_si_aproximari.json"
OLD_EMPTY = "clasa_9_u01_l02_puteri_radicali_si_operatii_cu_intervale_de_numere_reale.json"


def prepare_real_number_lessons(directory, manifest, validate, error_class):
    """Apelată în tranzacția seed-ului, înainte de sincronizarea întrebărilor."""
    legacy = list(Quiz.objects.filter(source_file__in=[OLD_SOURCE, OLD_EMPTY]))
    if not legacy:
        return
    targets = [(name,chapter,order) for name,(chapter,order) in manifest.items()
               if chapter.class_level == 9 and chapter.slug == "multimea-numerelor-reale"]
    if len(targets) != 6:
        return  # Alte manifesturi/fișiere de test nu declanșează reorganizarea.
    targets.sort(key=lambda item: item[2])
    payloads = []
    owners = {}
    for name,chapter,order in targets:
        path = directory / name
        payload = json.loads(path.read_text(encoding="utf-8"))
        validate(payload, name)
        for question in payload["questions"]:
            text = question["text"].strip()
            if text in owners:
                raise error_class("Reorganizare: un enunț apare în două subcapitole.")
            owners[text] = Path(name).name
        payloads.append((Path(name).name,chapter,order,payload))
    for quiz in legacy:
        if quiz.source_file == OLD_EMPTY and quiz.questions.exists():
            raise error_class("Lecția veche de intervale are conținut suplimentar; reorganizarea necesită maparea lui.")
        for text in quiz.questions.values_list("text",flat=True):
            if text not in owners:
                raise error_class(f"Reorganizare: întrebarea {text!r} nu are destinație; nu a fost mutată.")
    for quiz in legacy:
        destination = payloads[0][0] if quiz.source_file == OLD_SOURCE else payloads[-1][0]
        if Quiz.objects.filter(source_file=destination).exclude(pk=quiz.pk).exists():
            raise error_class("Există deja o lecție destinație; reorganizarea nu va suprascrie progresul.")
        quiz.source_file = destination
        quiz.save(update_fields=["source_file"])
    quizzes = {}
    for filename,chapter,order,payload in payloads:
        quiz,_ = Quiz.objects.update_or_create(source_file=filename,defaults={
            "title": payload["title"],"description":payload.get("description",""),
            "difficulty":payload["difficulty"],"chapter":chapter,"order":order,"class_levels":[9],
        })
        quizzes[filename] = quiz
    for quiz in legacy:
        moves = {}
        for question in quiz.questions.all():
            destination = quizzes[owners[question.text]]
            if destination.pk != quiz.pk:
                if destination.questions.filter(text=question.text).exists():
                    raise error_class("O întrebare există deja în destinație; mutarea a fost anulată.")
                moves.setdefault(destination.pk,[]).append(question.pk)
        for destination,ids in moves.items():
            Question.objects.filter(pk__in=ids).update(quiz_id=destination)
