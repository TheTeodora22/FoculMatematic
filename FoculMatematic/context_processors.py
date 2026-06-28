from django.db.utils import OperationalError

from .models import SchoolClass


def curriculum_navigation(request):
    try:
        nav_school_classes = list(
            SchoolClass.objects.select_related("quiz_tag").order_by("order", "slug")
        )
    except OperationalError:
        nav_school_classes = []
    return {"nav_school_classes": nav_school_classes}
