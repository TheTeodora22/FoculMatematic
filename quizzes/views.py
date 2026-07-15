from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Prefetch
from django.http import Http404, HttpResponseBadRequest, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from .models import (
    Chapter,
    GeneratedQuizSession,
    GeneratedQuizSessionQuestion,
    Question,
    Quiz,
    QuizAttempt,
    QuizAttemptAnswer,
    UserQuestionProgress,
)
from .exams import get_exam
from .lesson_tags import topics_for_exam
from .mode_services import (
    TopicModeError,
    build_training_payload,
    complete_generated_session,
    get_in_progress_session,
    get_training_questions,
    get_training_states,
    reset_training_progress,
    session_is_complete,
    start_or_resume_generated_session,
    submit_generated_answer,
    submit_training_answer,
)
from .services import QuizSubmitError, submit_quiz_attempt

VALID_CLASS_LEVELS = range(5, 13)


def _quiz_with_questions():
    return Quiz.objects.prefetch_related(
        Prefetch(
            "questions",
            queryset=Question.objects.order_by("id").prefetch_related("options"),
        )
    )


def quiz_list(request):
    return render(
        request,
        "quizzes/quiz_list.html",
        {"class_levels": list(VALID_CLASS_LEVELS)},
    )


def _get_quiz_for_take(pk):
    return get_object_or_404(_quiz_with_questions(), pk=pk)


def quiz_take(request, pk):
    quiz = _get_quiz_for_take(pk)
    questions = list(quiz.questions.all())
    can_submit = all(q.options.all() for q in questions)

    if request.method == "POST":
        if not request.user.is_authenticated:
            login_url = reverse("login")
            return redirect(f"{login_url}?next={request.path}")

        answers = {}
        for q in questions:
            raw = request.POST.get(f"q_{q.id}")
            if raw:
                try:
                    answers[q.id] = int(raw)
                except (TypeError, ValueError):
                    return HttpResponseBadRequest("Răspuns invalid.")

        try:
            result = submit_quiz_attempt(request.user, quiz, answers)
        except QuizSubmitError as exc:
            return HttpResponseBadRequest(exc.message)

        if result["xp_gained"]:
            messages.success(request, f"Ai câștigat {result['xp_gained']} XP!")
        if result["leveled_up"]:
            messages.success(
                request,
                f"Felicitări! Ai ajuns la nivelul {result['new_level']}!",
            )
            for reward_name in result["new_rewards"]:
                messages.success(
                    request, f"Recompensă nouă deblocată: {reward_name}!"
                )

        attempt = result["attempt"]
        return redirect("quiz_result", pk=quiz.pk, attempt_id=attempt.pk)

    return render(
        request,
        "quizzes/quiz_take.html",
        {"quiz": quiz, "questions": questions, "can_submit": can_submit},
    )


@login_required
def quiz_result(request, pk, attempt_id):
    attempt = get_object_or_404(
        QuizAttempt.objects.select_related("quiz").prefetch_related(
            Prefetch(
                "answers",
                queryset=QuizAttemptAnswer.objects.select_related(
                    "question", "selected_option"
                ).prefetch_related("question__options"),
            )
        ),
        pk=attempt_id,
        quiz_id=pk,
        user=request.user,
    )
    return render(
        request,
        "quizzes/quiz_result.html",
        {"attempt": attempt, "quiz": attempt.quiz},
    )


@login_required
def class_chapters(request, class_level):
    if class_level not in VALID_CLASS_LEVELS:
        return HttpResponseBadRequest("Clasă invalidă.")
    chapters = (
        Chapter.objects.filter(class_level=class_level, exam_slug="")
        .order_by("order", "title")
    )
    return render(
        request,
        "quizzes/class_chapters.html",
        {"class_level": class_level, "chapters": chapters},
    )


@login_required
def chapter_topics(request, class_level, slug):
    if class_level not in VALID_CLASS_LEVELS:
        return HttpResponseBadRequest("Clasă invalidă.")
    chapter = get_object_or_404(Chapter, class_level=class_level, slug=slug)
    topics = chapter.topics.order_by("title")
    return render(
        request,
        "quizzes/chapter_topics.html",
        {"class_level": class_level, "chapter": chapter, "topics": topics},
    )


@login_required
def exam_detail(request, slug):
    exam = get_exam(slug)
    if exam is None:
        raise Http404
    chapters = Chapter.objects.filter(exam_slug=slug).order_by("order", "title")
    topics = topics_for_exam(slug)
    return render(
        request,
        "quizzes/exam_detail.html",
        {"exam": exam, "chapters": chapters, "topics": topics},
    )


@login_required
def exam_chapter_topics(request, exam_slug, chapter_slug):
    exam = get_exam(exam_slug)
    if exam is None:
        raise Http404
    chapter = get_object_or_404(Chapter, exam_slug=exam_slug, slug=chapter_slug)
    topics = chapter.topics.order_by("title")
    return render(
        request,
        "quizzes/exam_chapter_topics.html",
        {"exam": exam, "chapter": chapter, "topics": topics},
    )


@login_required
def topic_detail(request, pk):
    topic = get_object_or_404(Quiz.objects.select_related("chapter"), pk=pk)
    in_progress = get_in_progress_session(request.user, topic)
    question_count = topic.questions.count()
    return render(
        request,
        "quizzes/topic_detail.html",
        {
            "topic": topic,
            "in_progress": in_progress,
            "question_count": question_count,
        },
    )


def _get_topic(pk):
    return get_object_or_404(Quiz.objects.select_related("chapter"), pk=pk)


@login_required
def generated_quiz(request, pk):
    topic = _get_topic(pk)

    if request.method == "POST":
        try:
            session = start_or_resume_generated_session(request.user, topic)
        except TopicModeError as exc:
            messages.error(request, exc.message)
            return redirect("topic_detail", pk=pk)

        if session.status == GeneratedQuizSession.STATUS_COMPLETED:
            return redirect("generated_quiz_result", pk=pk)

        try:
            item_id = int(request.POST.get("item_id", ""))
            option_id = int(request.POST.get("option_id", ""))
        except (TypeError, ValueError):
            return HttpResponseBadRequest("Răspuns invalid.")

        item = session.items.filter(pk=item_id).first()
        if item is None:
            return HttpResponseBadRequest("Întrebare invalidă.")

        try:
            submit_generated_answer(session, item, option_id)
        except TopicModeError as exc:
            messages.error(request, exc.message)
            return redirect("generated_quiz", pk=pk)

        if session_is_complete(session):
            return redirect("generated_quiz_result", pk=pk)
        return redirect("generated_quiz", pk=pk)

    try:
        session = start_or_resume_generated_session(request.user, topic)
    except TopicModeError as exc:
        messages.error(request, exc.message)
        return redirect("topic_detail", pk=pk)

    if session.status == GeneratedQuizSession.STATUS_COMPLETED:
        return redirect("generated_quiz_result", pk=pk)

    item = (
        session.items.filter(selected_option__isnull=True)
        .select_related("question")
        .prefetch_related("question__options")
        .order_by("order")
        .first()
    )
    if item is None:
        return redirect("generated_quiz_result", pk=pk)

    answered_count = session.items.filter(selected_option__isnull=False).count()
    total_count = session.items.count()

    return render(
        request,
        "quizzes/generated_quiz.html",
        {
            "topic": topic,
            "session": session,
            "item": item,
            "answered_count": answered_count,
            "total_count": total_count,
            "question_number": item.order + 1,
        },
    )


@login_required
def generated_quiz_result(request, pk):
    topic = _get_topic(pk)
    session = (
        GeneratedQuizSession.objects.filter(user=request.user, topic=topic)
        .prefetch_related(
            Prefetch(
                "items",
                queryset=GeneratedQuizSessionQuestion.objects.select_related(
                    "question", "selected_option"
                ).order_by("order"),
            )
        )
        .order_by("-updated_at")
        .first()
    )

    if session is None:
        return redirect("topic_detail", pk=pk)

    result = None
    if session.status != GeneratedQuizSession.STATUS_COMPLETED:
        if not session_is_complete(session):
            return redirect("generated_quiz", pk=pk)
        result = complete_generated_session(session)
        if result["xp_gained"]:
            messages.success(request, f"Ai câștigat {result['xp_gained']} XP!")
        if result["leveled_up"]:
            messages.success(
                request,
                f"Felicitări! Ai ajuns la nivelul {result['new_level']}!",
            )
            for reward_name in result["new_rewards"]:
                messages.success(
                    request, f"Recompensă nouă deblocată: {reward_name}!"
                )
        session.refresh_from_db()
    else:
        correct_count = session.items.filter(is_correct=True).count()
        total_count = session.items.count()
        result = {
            "correct_count": correct_count,
            "total_count": total_count,
            "xp_gained": 0,
        }

    wrong_items = list(
        session.items.filter(is_correct=False).select_related("question")
    )

    return render(
        request,
        "quizzes/generated_quiz_result.html",
        {
            "topic": topic,
            "session": session,
            "result": result,
            "wrong_items": wrong_items,
        },
    )


@login_required
def training(request, pk, index=None):
    topic = _get_topic(pk)
    questions = get_training_questions(topic)
    if not questions:
        messages.error(request, "Acest subiect nu are întrebări.")
        return redirect("topic_detail", pk=pk)

    states = get_training_states(request.user, topic)

    if index is None:
        index = 0
        for i, state in enumerate(states):
            if state["status"] == "unanswered":
                index = i
                break

    try:
        index = int(index)
    except (TypeError, ValueError):
        return HttpResponseBadRequest("Index invalid.")

    if index < 0 or index >= len(questions):
        return HttpResponseBadRequest("Index invalid.")

    current = questions[index]
    current_state = states[index]
    feedback = None
    training_solved = current_state["status"] == UserQuestionProgress.TRAINING_CORRECT

    if request.method == "POST":
        if training_solved:
            return redirect("training_index", pk=pk, index=index)

        try:
            option_id = int(request.POST.get("option_id", ""))
        except (TypeError, ValueError):
            return HttpResponseBadRequest("Răspuns invalid.")
        try:
            feedback = submit_training_answer(request.user, current, option_id)
            states = get_training_states(request.user, topic)
            current_state = states[index]
            training_solved = current_state["status"] == UserQuestionProgress.TRAINING_CORRECT
        except TopicModeError as exc:
            messages.error(request, exc.message)

    selected_option_id = feedback["selected_option_id"] if feedback else None
    training_payload = build_training_payload(
        request.user,
        topic,
        index,
        reverse("training_submit", args=[pk]),
    )

    return render(
        request,
        "quizzes/training.html",
        {
            "topic": topic,
            "questions": questions,
            "states": states,
            "index": index,
            "current": current,
            "current_state": current_state,
            "feedback": feedback,
            "training_solved": training_solved,
            "selected_option_id": selected_option_id,
            "training_payload": training_payload,
            "has_prev": index > 0,
            "has_next": index < len(questions) - 1,
            "prev_index": index - 1,
            "next_index": index + 1,
        },
    )


@login_required
@require_POST
def training_submit(request, pk):
    topic = _get_topic(pk)
    try:
        question_id = int(request.POST.get("question_id", ""))
        option_id = int(request.POST.get("option_id", ""))
    except (TypeError, ValueError):
        return JsonResponse({"error": "Date invalide."}, status=400)

    question = get_object_or_404(Question, pk=question_id, quiz=topic)
    try:
        result = submit_training_answer(request.user, question, option_id)
    except TopicModeError as exc:
        return JsonResponse({"error": exc.message}, status=400)

    return JsonResponse(result)


@login_required
@require_POST
def training_reset(request, pk):
    topic = _get_topic(pk)
    reset_training_progress(request.user, topic)
    messages.success(request, "Progresul de antrenare a fost resetat.")
    return redirect("topic_detail", pk=pk)
