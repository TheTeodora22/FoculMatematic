from django.contrib.auth.decorators import login_required
from django.db.models import Prefetch
from django.http import HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render

from .models import AnswerOption, Question, Quiz, QuizAttempt


def _quiz_with_questions():
    return Quiz.objects.prefetch_related(
        Prefetch(
            "questions",
            queryset=Question.objects.order_by("id").prefetch_related("options"),
        )
    )


def quiz_list(request):
    quizzes = Quiz.objects.order_by("title")
    return render(request, "quizzes/quiz_list.html", {"quizzes": quizzes})


def _get_quiz_for_take(pk):
    return get_object_or_404(_quiz_with_questions(), pk=pk)


@login_required
def quiz_take(request, pk):
    quiz = _get_quiz_for_take(pk)
    questions = list(quiz.questions.all())

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
