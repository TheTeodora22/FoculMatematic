"""Mutarea idempotentă a lecției vechi în subcapitole, păstrând ID-urile."""
import json
from pathlib import Path

from quizzes.models import Question, Quiz


OLD_SOURCE = "clasa_9_u01_l01_multimea_numerelor_reale_operatii_ordonare_modul_si_aproximari.json"
OLD_EMPTY = "clasa_9_u01_l02_puteri_radicali_si_operatii_cu_intervale_de_numere_reale.json"

PROGRESSIONS_OLD = "clasa_9_u02_l02_progresii_aritmetice_si_geometrice_aplicatii.json"
PROGRESSIONS_FILES = [
    "clasa_9_u02_l02a_progresii_aritmetice.json",
    "clasa_9_u02_l02b_progresii_geometrice.json",
    "clasa_9_u02_l02c_aplicatii_progresii.json",
]


def prepare_progression_lessons(directory, manifest, validate, error_class):
    """Reutilizează lecția veche și mută întrebările fără schimbarea ID-urilor."""
    old = Quiz.objects.filter(source_file=PROGRESSIONS_OLD).first()
    if old is None:
        return
    targets = {Path(name).name: (name, chapter, order)
               for name, (chapter, order) in manifest.items()
               if Path(name).name in PROGRESSIONS_FILES}
    if len(targets) != 3:
        return
    payloads = {}
    owners = {}
    for filename in PROGRESSIONS_FILES:
        name, chapter, order = targets[filename]
        payload = json.loads((directory / name).read_text(encoding="utf-8"))
        validate(payload, name)
        payloads[filename] = payload
        for item in payload["questions"]:
            text = item["text"].strip()
            if text in owners:
                raise error_class("Progresii: enunț duplicat între destinații.")
            owners[text] = filename
    if any(text not in owners for text in old.questions.values_list("text", flat=True)):
        raise error_class("Progresii: există întrebări vechi fără destinație; mutarea a fost anulată.")
    if Quiz.objects.filter(source_file=PROGRESSIONS_FILES[0]).exists():
        raise error_class("Progresii: prima destinație există deja; mutarea a fost anulată.")
    old.source_file = PROGRESSIONS_FILES[0]
    old.save(update_fields=["source_file"])
    destinations = {}
    for filename in PROGRESSIONS_FILES:
        _, chapter, order = targets[filename]
        payload = payloads[filename]
        quiz, _ = Quiz.objects.update_or_create(source_file=filename, defaults={
            "title": payload["title"], "description": payload.get("description", ""),
            "difficulty": payload["difficulty"], "chapter": chapter,
            "order": order, "class_levels": [9],
        })
        destinations[filename] = quiz
    for question in old.questions.all():
        destination = destinations[owners[question.text]]
        if destination.pk != old.pk:
            if destination.questions.filter(text=question.text).exists():
                raise error_class("Progresii: întrebare deja prezentă în destinație.")
            Question.objects.filter(pk=question.pk).update(quiz=destination)
    chapter = destinations[PROGRESSIONS_FILES[0]].chapter
    for name, (topic_chapter, order) in manifest.items():
        if topic_chapter.pk == chapter.pk:
            Quiz.objects.filter(source_file=Path(name).name, chapter=chapter).update(order=order)


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
