from django.contrib.auth.decorators import login_required
from django.db.models import Prefetch
from django.http import HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render

from .models import AnswerOption, Question, Quiz, QuizAttempt, QuizQuestion, QuizTag


def _quiz_for_take(pk):
    return get_object_or_404(
        Quiz.objects.prefetch_related(
            Prefetch(
                "question_links",
                queryset=QuizQuestion.objects.select_related("question")
                .prefetch_related(
                    Prefetch(
                        "question__options",
                        queryset=AnswerOption.objects.order_by("pk"),
                    )
                )
                .order_by("order", "pk"),
            )
        ),
        pk=pk,
    )


def _ordered_questions(quiz):
    return [link.question for link in quiz.question_links.all()]


def quiz_list(request):
    quizzes = Quiz.objects.prefetch_related("tags").order_by("title")
    return render(
        request,
        "quizzes/quiz_list.html",
        {"quizzes": quizzes, "current_tag": None},
    )


def quiz_list_by_tag(request, tag_slug):
    tag = get_object_or_404(QuizTag, slug=tag_slug)
    quizzes = (
        Quiz.objects.filter(tags=tag)
        .prefetch_related("tags")
        .distinct()
        .order_by("title")
    )
    return render(
        request,
        "quizzes/quiz_list.html",
        {"quizzes": quizzes, "current_tag": tag},
    )


def class_hub(request):
    tags = QuizTag.objects.filter(kind=QuizTag.KIND_CLASS).order_by("sort_order", "slug")
    return render(request, "quizzes/class_hub.html", {"class_tags": tags})


def exam_hub(request):
    tags = QuizTag.objects.filter(kind=QuizTag.KIND_EXAM).order_by("sort_order", "slug")
    return render(request, "quizzes/exam_hub.html", {"exam_tags": tags})


@login_required
def quiz_take(request, pk):
    quiz = _quiz_for_take(pk)
    questions = _ordered_questions(quiz)

    if request.method == "POST":
        valid_option_ids_by_question = {
            q.id: {opt.id for opt in q.options.all()} for q in questions
        }
        score = 0
        max_score = sum(q.points for q in questions)

        for q in questions:
            raw = request.POST.get(f"q_{q.id}")
            if not raw:
                continue
            try:
                option_id = int(raw)
            except (TypeError, ValueError):
                return HttpResponseBadRequest("Răspuns invalid.")
            allowed = valid_option_ids_by_question.get(q.id, set())
            if option_id not in allowed:
                return HttpResponseBadRequest("Răspuns invalid.")
            if AnswerOption.objects.filter(
                id=option_id, question_id=q.id, is_correct=True
            ).exists():
                score += q.points

        attempt = QuizAttempt.objects.create(
            user=request.user,
            quiz=quiz,
            score=score,
            max_score=max_score,
        )
        return redirect("quiz_result", pk=quiz.pk, attempt_id=attempt.pk)

    return render(
        request,
        "quizzes/quiz_take.html",
        {"quiz": quiz, "questions": questions},
    )


@login_required
def quiz_result(request, pk, attempt_id):
    attempt = get_object_or_404(
        QuizAttempt.objects.select_related("quiz"),
        pk=attempt_id,
        quiz_id=pk,
        user=request.user,
    )
    return render(
        request,
        "quizzes/quiz_result.html",
        {"attempt": attempt, "quiz": attempt.quiz},
    )
