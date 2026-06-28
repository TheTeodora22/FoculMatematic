from achievements.services import flash_new_achievements
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Count, Prefetch
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from accounts.xp_rewards import award_quiz_xp
from .http_errors import (
    issue_quiz_form_token,
    render_bad_request,
    verify_and_consume_quiz_form_token,
)
from quizzes.models import Quiz, QuizTag
from quizzes.models import QuizAttempt as LegacyQuizAttempt

from .models import Answer, Chapter, Choice, Lesson, Question, QuizAttempt, SchoolClass


def _quiz_tag_progress_rows(user, kind: str):
    """Rânduri total/done/% per QuizTag pentru chestionare (cel puțin o încercare per quiz)."""
    rows = []
    for tag in QuizTag.objects.filter(kind=kind).order_by("sort_order", "slug"):
        total = Quiz.objects.filter(tags=tag).distinct().count()
        if total == 0:
            rows.append({"tag": tag, "total": 0, "done": 0, "percent": None})
            continue
        done = (
            LegacyQuizAttempt.objects.filter(user=user, quiz__tags=tag)
            .values("quiz_id")
            .distinct()
            .count()
        )
        rows.append(
            {
                "tag": tag,
                "total": total,
                "done": done,
                "percent": round(100 * done / total),
            }
        )
    return rows


def index(request):
    return render(request, "index.html")


def school_class_list(request):
    classes = SchoolClass.objects.select_related("quiz_tag").order_by("order", "slug")
    return render(
        request,
        "FoculMatematic/class_list.html",
        {"school_classes": classes},
    )


def school_class_detail(request, slug):
    school_class = get_object_or_404(
        SchoolClass.objects.select_related("quiz_tag"),
        slug=slug,
    )
    chapters = school_class.chapters.prefetch_related(
        Prefetch(
            "lessons",
            queryset=Lesson.objects.order_by("order", "slug"),
        )
    ).order_by("order", "slug")
    return render(
        request,
        "FoculMatematic/class_detail.html",
        {"school_class": school_class, "chapters": chapters},
    )


def school_class_chapters(request, slug):
    return school_class_detail(request, slug)


def lesson_catalog(request):
    """Listă toate lecțiile cu filtre opționale după clasă (curriculum) și capitol."""
    clasa_slug = (request.GET.get("clasa") or "").strip()
    capitol_slug = (request.GET.get("capitol") or "").strip()

    school_classes = list(SchoolClass.objects.order_by("order", "slug"))
    current_class = None
    chapter_choices = []

    qs = Lesson.objects.select_related("chapter", "chapter__school_class").order_by(
        "chapter__school_class__order",
        "chapter__order",
        "order",
        "slug",
    )

    if clasa_slug:
        current_class = get_object_or_404(SchoolClass, slug=clasa_slug)
        qs = qs.filter(chapter__school_class=current_class)
        chapter_choices = list(
            Chapter.objects.filter(school_class=current_class).order_by("order", "slug")
        )
        if capitol_slug:
            qs = qs.filter(chapter__slug=capitol_slug)

    lessons = list(qs)
    return render(
        request,
        "FoculMatematic/lesson_catalog.html",
        {
            "lessons": lessons,
            "school_classes": school_classes,
            "current_class": current_class,
            "chapter_choices": chapter_choices,
            "current_chapter_slug": capitol_slug if current_class else "",
        },
    )


def _lesson_for_quiz(lesson_slug):
    return get_object_or_404(
        Lesson.objects.select_related("chapter", "chapter__school_class").prefetch_related(
            Prefetch(
                "questions",
                queryset=Question.objects.prefetch_related(
                    Prefetch(
                        "choices",
                        queryset=Choice.objects.order_by("pk"),
                    )
                ).order_by("order", "pk"),
            )
        ),
        slug=lesson_slug,
    )


def lesson_detail(request, lesson_slug):
    lesson = get_object_or_404(
        Lesson.objects.select_related("chapter", "chapter__school_class"),
        slug=lesson_slug,
    )
    has_questions = lesson.questions.exists()
    return render(
        request,
        "FoculMatematic/lesson_detail.html",
        {"lesson": lesson, "has_questions": has_questions},
    )


@login_required
def lesson_quiz(request, lesson_slug):
    lesson = _lesson_for_quiz(lesson_slug)
    questions = list(lesson.questions.all())

    if request.method == "POST":
        if not questions:
            return render_bad_request(
                request,
                "Nu există întrebări pentru acest quiz.",
                retry_url=reverse("lesson_detail", kwargs={"lesson_slug": lesson.slug}),
                retry_label="Înapoi la lecție",
            )
        posted = request.POST.get("fm_form_token", "")
        if not verify_and_consume_quiz_form_token(request, "lesson", lesson.pk, posted):
            return render_bad_request(
                request,
                "Formularul a expirat sau a fost deja trimis (de exemplu dublu-click). "
                "Deschide din nou pagina quiz-ului și trimite răspunsurile o singură dată.",
                retry_url=reverse("lesson_quiz", kwargs={"lesson_slug": lesson.slug}),
                retry_label="Deschide din nou quiz-ul",
            )
        valid_choice_ids_by_question = {
            q.id: {c.id for c in q.choices.all()} for q in questions
        }
        score = 0
        max_score = sum(q.points for q in questions)
        answer_rows = []
        choice_by_q_and_id = {}
        for q in questions:
            for c in q.choices.all():
                choice_by_q_and_id[(q.id, c.id)] = c

        retry_quiz = reverse("lesson_quiz", kwargs={"lesson_slug": lesson.slug})
        for q in questions:
            raw = request.POST.get(f"q_{q.id}")
            if not raw:
                return render_bad_request(
                    request,
                    "Răspuns lipsă. Te rugăm să răspunzi la toate întrebările, apoi trimite din nou.",
                    retry_url=retry_quiz,
                    retry_label="Înapoi la quiz",
                )
            try:
                choice_id = int(raw)
            except (TypeError, ValueError):
                return render_bad_request(
                    request,
                    "Un răspuns nu este valid. Reîncarcă quiz-ul și încearcă din nou.",
                    retry_url=retry_quiz,
                    retry_label="Înapoi la quiz",
                )
            allowed = valid_choice_ids_by_question.get(q.id, set())
            if choice_id not in allowed:
                return render_bad_request(
                    request,
                    "Un răspuns nu corespunde variantelor permise. Reîncarcă quiz-ul.",
                    retry_url=retry_quiz,
                    retry_label="Înapoi la quiz",
                )
            choice = choice_by_q_and_id.get((q.id, choice_id))
            if choice is None:
                return render_bad_request(
                    request,
                    "Un răspuns nu este valid. Reîncarcă quiz-ul.",
                    retry_url=retry_quiz,
                    retry_label="Înapoi la quiz",
                )
            answer_rows.append((q, choice))
            if choice.is_correct:
                score += q.points

        with transaction.atomic():
            attempt = QuizAttempt.objects.create(
                user=request.user,
                lesson=lesson,
                score=score,
                max_score=max_score,
            )
            Answer.objects.bulk_create(
                [
                    Answer(attempt=attempt, question=q, choice=c)
                    for q, c in answer_rows
                ]
            )
            xp_gain = award_quiz_xp(
                request.user, score, max_score, lesson.quiz_max_xp
            )

        flash_new_achievements(request, request.user)

        if xp_gain:
            messages.success(
                request,
                f"Ai câștigat {xp_gain} XP (din maxim {lesson.quiz_max_xp} pentru acest quiz).",
            )

        return redirect(
            "lesson_quiz_results",
            lesson_slug=lesson.slug,
            attempt_id=attempt.pk,
        )

    form_token = None
    if questions:
        form_token = issue_quiz_form_token(request, "lesson", lesson.pk)
    return render(
        request,
        "FoculMatematic/lesson_quiz.html",
        {"lesson": lesson, "questions": questions, "form_token": form_token},
    )


@login_required
def lesson_quiz_results(request, lesson_slug, attempt_id):
    attempt = get_object_or_404(
        QuizAttempt.objects.select_related("lesson", "lesson__chapter__school_class")
        .prefetch_related(
            Prefetch(
                "answers",
                queryset=Answer.objects.select_related(
                    "question",
                    "choice",
                ),
            )
        ),
        pk=attempt_id,
        lesson__slug=lesson_slug,
        user=request.user,
    )
    lesson = attempt.lesson
    questions = list(
        lesson.questions.prefetch_related(
            Prefetch("choices", queryset=Choice.objects.order_by("pk"))
        ).order_by("order", "pk")
    )
    answers_by_q = {a.question_id: a for a in attempt.answers.all()}
    detail_rows = []
    for q in questions:
        ans = answers_by_q.get(q.id)
        correct_choice = next((c for c in q.choices.all() if c.is_correct), None)
        picked = ans.choice if ans else None
        detail_rows.append(
            {
                "question": q,
                "picked": picked,
                "picked_ok": bool(picked and picked.is_correct),
                "correct_choice": correct_choice,
            }
        )
    return render(
        request,
        "FoculMatematic/lesson_results.html",
        {
            "attempt": attempt,
            "lesson": lesson,
            "detail_rows": detail_rows,
        },
    )


@login_required
def user_progress(request):
    user = request.user
    attempts = (
        QuizAttempt.objects.filter(user=user)
        .select_related("lesson", "lesson__chapter", "lesson__chapter__school_class")
        .order_by("-created_at")
    )
    total_quizzes = attempts.count()

    completed_lesson_ids = attempts.values("lesson_id").distinct()
    completed_count = completed_lesson_ids.count()

    class_rows = []
    for sc in SchoolClass.objects.order_by("order", "slug").annotate(
        lesson_total=Count("chapters__lessons", distinct=True),
    ):
        done_in_class = (
            QuizAttempt.objects.filter(
                user=user,
                lesson__chapter__school_class=sc,
            )
            .values("lesson_id")
            .distinct()
            .count()
        )
        total = sc.lesson_total or 0
        pct = round(100 * done_in_class / total) if total else 0
        class_rows.append(
            {
                "school_class": sc,
                "completed_lessons": done_in_class,
                "total_lessons": total,
                "percent": pct,
            }
        )

    recent = list(attempts[:15])

    completed_lessons = (
        Lesson.objects.filter(
            pk__in=attempts.values_list("lesson_id", flat=True).distinct()
        )
        .select_related("chapter", "chapter__school_class")
        .order_by("chapter__school_class__order", "chapter__order", "order")
    )

    quiz_tag_class_rows = _quiz_tag_progress_rows(user, QuizTag.KIND_CLASS)
    quiz_tag_exam_rows = _quiz_tag_progress_rows(user, QuizTag.KIND_EXAM)

    return render(
        request,
        "FoculMatematic/progress.html",
        {
            "total_quizzes": total_quizzes,
            "completed_lesson_count": completed_count,
            "class_rows": class_rows,
            "recent_attempts": recent,
            "completed_lessons": completed_lessons,
            "quiz_tag_class_rows": quiz_tag_class_rows,
            "quiz_tag_exam_rows": quiz_tag_exam_rows,
        },
    )


def handler404(request, exception):
    """Pagină 404 tematică (activă când DEBUG=False)."""
    return render(request, "404.html", status=404)


def handler500(request):
    """Pagină 500 minimală fără dependențe fragile la context processors."""
    return render(request, "500.html", status=500)
