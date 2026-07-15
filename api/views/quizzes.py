from django.db.models import Prefetch
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from api.serializers import (
    QuizAttemptSerializer,
    QuizDetailSerializer,
    QuizListSerializer,
    QuizSubmitSerializer,
)
from quizzes.models import Question, Quiz, QuizAttempt, QuizAttemptAnswer
from quizzes.services import QuizSubmitError, submit_quiz_attempt


class QuizListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        quizzes = Quiz.objects.order_by("title")
        return Response(QuizListSerializer(quizzes, many=True).data)


class QuizDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        quiz = get_object_or_404(
            Quiz.objects.prefetch_related(
                Prefetch(
                    "questions",
                    queryset=Question.objects.order_by("id").prefetch_related(
                        "options"
                    ),
                )
            ),
            pk=pk,
        )
        return Response(QuizDetailSerializer(quiz).data)


class QuizSubmitView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        quiz = get_object_or_404(Quiz, pk=pk)
        serializer = QuizSubmitSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        raw_answers = serializer.validated_data["answers"]
        answers = {int(k): v for k, v in raw_answers.items()}

        try:
            result = submit_quiz_attempt(request.user, quiz, answers)
        except QuizSubmitError as exc:
            return Response({"detail": exc.message}, status=status.HTTP_400_BAD_REQUEST)

        attempt_data = QuizAttemptSerializer(result["attempt"]).data
        return Response(
            {
                **attempt_data,
                "xp_gained": result["xp_gained"],
                "leveled_up": result["leveled_up"],
                "new_level": result["new_level"],
                "new_rewards": result["new_rewards"],
            },
            status=status.HTTP_201_CREATED,
        )


class AttemptDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        attempt = get_object_or_404(
            QuizAttempt.objects.select_related("quiz").prefetch_related(
                Prefetch(
                    "answers",
                    queryset=QuizAttemptAnswer.objects.select_related(
                        "question", "selected_option"
                    ).prefetch_related("question__options"),
                )
            ),
            pk=pk,
            user=request.user,
        )
        return Response(QuizAttemptSerializer(attempt).data)
