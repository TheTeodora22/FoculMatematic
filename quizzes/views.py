from achievements.services import flash_new_achievements
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Prefetch
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from accounts.xp_rewards import award_quiz_xp
from FoculMatematic.http_errors import (
    issue_quiz_form_token,
    render_bad_request,
    verify_and_consume_quiz_form_token,
)

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
    tag_slug = (request.GET.get("tag") or "").strip()
    current_tag = None
    qs = Quiz.objects.prefetch_related("tags")
    if tag_slug:
        current_tag = get_object_or_404(QuizTag, slug=tag_slug)
        qs = qs.filter(tags=current_tag).distinct()
    quizzes = qs.order_by("title")
    all_tags = list(QuizTag.objects.order_by("kind", "sort_order", "slug"))
    return render(
        request,
        "quizzes/quiz_list.html",
        {
            "quizzes": quizzes,
            "current_tag": current_tag,
            "all_tags": all_tags,
        },
    )


def quiz_list_by_tag(request, tag_slug):
    tag = get_object_or_404(QuizTag, slug=tag_slug)
    quizzes = (
        Quiz.objects.filter(tags=tag)
        .prefetch_related("tags")
        .distinct()
        .order_by("title")
    )
    all_tags = list(QuizTag.objects.order_by("kind", "sort_order", "slug"))
    return render(
        request,
        "quizzes/quiz_list.html",
        {"quizzes": quizzes, "current_tag": tag, "all_tags": all_tags},
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
        if not questions:
            return render_bad_request(
                request,
                "Nu există întrebări pentru acest chestionar.",
                retry_url=reverse("quiz_list"),
                retry_label="Înapoi la chestionare",
            )
        posted = request.POST.get("fm_form_token", "")
        if not verify_and_consume_quiz_form_token(request, "quiz", quiz.pk, posted):
            return render_bad_request(
                request,
                "Formularul a expirat sau a fost deja trimis (de exemplu dublu-click). "
                "Deschide din nou chestionarul și trimite răspunsurile o singură dată.",
                retry_url=reverse("quiz_take", kwargs={"pk": quiz.pk}),
                retry_label="Deschide din nou chestionarul",
            )
        valid_option_ids_by_question = {
            q.id: {opt.id for opt in q.options.all()} for q in questions
        }
        score = 0
        max_score = sum(q.points for q in questions)

        retry_take = reverse("quiz_take", kwargs={"pk": quiz.pk})
        for q in questions:
            raw = request.POST.get(f"q_{q.id}")
            if not raw:
                return render_bad_request(
                    request,
                    "Răspuns lipsă. Te rugăm să răspunzi la toate întrebările, apoi trimite din nou.",
                    retry_url=retry_take,
                    retry_label="Înapoi la chestionar",
                )
            try:
                option_id = int(raw)
            except (TypeError, ValueError):
                return render_bad_request(
                    request,
                    "Un răspuns nu este valid. Reîncarcă chestionarul și încearcă din nou.",
                    retry_url=retry_take,
                    retry_label="Înapoi la chestionar",
                )
            allowed = valid_option_ids_by_question.get(q.id, set())
            if option_id not in allowed:
                return render_bad_request(
                    request,
                    "Un răspuns nu corespunde variantelor permise. Reîncarcă chestionarul.",
                    retry_url=retry_take,
                    retry_label="Înapoi la chestionar",
                )
            if AnswerOption.objects.filter(
                id=option_id, question_id=q.id, is_correct=True
            ).exists():
                score += q.points

        with transaction.atomic():
            attempt = QuizAttempt.objects.create(
                user=request.user,
                quiz=quiz,
                score=score,
                max_score=max_score,
            )
            xp_gain = award_quiz_xp(
                request.user, score, max_score, quiz.max_xp
            )

        flash_new_achievements(request, request.user)

        if xp_gain:
            messages.success(
                request,
                f"Ai câștigat {xp_gain} XP (din maxim {quiz.max_xp} pentru acest chestionar).",
            )

        return redirect("quiz_result", pk=quiz.pk, attempt_id=attempt.pk)

    form_token = None
    if questions:
        form_token = issue_quiz_form_token(request, "quiz", quiz.pk)
    return render(
        request,
        "quizzes/quiz_take.html",
        {"quiz": quiz, "questions": questions, "form_token": form_token},
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
