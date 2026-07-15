from accounts.services import award_quiz_xp
from accounts.utils import get_or_create_profile
from battlepass.services import grant_tier_rewards

from .models import QuizAttempt, QuizAttemptAnswer


class QuizSubmitError(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


def submit_quiz_attempt(user, quiz, answers_by_question_id: dict):
    """
    Validează și salvează o încercare quiz.
    answers_by_question_id: {question_id (int): option_id (int)}
  Returns dict cu attempt, xp_gained, leveled_up, new_rewards.
    """
    questions = list(quiz.questions.prefetch_related("options").order_by("id"))
    if not questions:
        raise QuizSubmitError("Acest chestionar nu are întrebări.")

    valid_option_ids_by_question = {
        q.id: {opt.id for opt in q.options.all()} for q in questions
    }

    score = 0
    max_score = sum(q.points for q in questions)
    pending_answers = []

    for q in questions:
        if not valid_option_ids_by_question.get(q.id):
            raise QuizSubmitError("Unele întrebări nu au opțiuni de răspuns.")

        raw = answers_by_question_id.get(q.id)
        if raw is None:
            raise QuizSubmitError("Răspunde la toate întrebările.")

        try:
            option_id = int(raw)
        except (TypeError, ValueError):
            raise QuizSubmitError("Răspuns invalid.")

        allowed = valid_option_ids_by_question.get(q.id, set())
        if option_id not in allowed:
            raise QuizSubmitError("Răspuns invalid.")

        correct_ids = {opt.id for opt in q.options.all() if opt.is_correct}
        is_correct = option_id in correct_ids
        if is_correct:
            score += q.points
        pending_answers.append((q, option_id, is_correct))

    attempt = QuizAttempt.objects.create(
        user=user,
        quiz=quiz,
        score=score,
        max_score=max_score,
    )
    QuizAttemptAnswer.objects.bulk_create(
        [
            QuizAttemptAnswer(
                attempt=attempt,
                question=q,
                selected_option_id=option_id,
                is_correct=is_correct,
            )
            for q, option_id, is_correct in pending_answers
        ]
    )

    profile = get_or_create_profile(user)
    xp_gained, leveled_up = award_quiz_xp(profile, score)
    new_rewards = []
    if leveled_up:
        new_rewards = grant_tier_rewards(user, profile.level)

    return {
        "attempt": attempt,
        "xp_gained": xp_gained,
        "leveled_up": leveled_up,
        "new_level": profile.level if leveled_up else None,
        "new_rewards": new_rewards,
    }
