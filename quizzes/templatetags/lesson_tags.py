from django import template

from quizzes.lesson_tags import build_lesson_tags

register = template.Library()


@register.inclusion_tag("quizzes/includes/lesson_tags.html")
def render_lesson_tags(topic):
    return {"tags": build_lesson_tags(topic)}
