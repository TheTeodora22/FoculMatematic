from django.db.utils import OperationalError

from .models import QuizTag


def quiz_navigation(request):
    try:
        class_tags = list(
            QuizTag.objects.filter(kind=QuizTag.KIND_CLASS).order_by(
                "sort_order", "slug"
            )
        )
        exam_tags = list(
            QuizTag.objects.filter(kind=QuizTag.KIND_EXAM).order_by(
                "sort_order", "slug"
            )
        )
    except OperationalError:
        class_tags = []
        exam_tags = []
    return {
        "nav_quiz_class_tags": class_tags,
        "nav_quiz_exam_tags": exam_tags,
    }
