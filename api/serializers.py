from django.contrib.auth.models import User
from rest_framework import serializers

from accounts.models import Profile
from accounts.services import xp_progress
from accounts.utils import get_or_create_profile
from battlepass.models import BattlePassSeason, BattlePassTier
from battlepass.services import get_battlepass_progress
from quizzes.models import AnswerOption, Question, Quiz, QuizAttempt, QuizAttemptAnswer


class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True, min_length=8)
    clasa = serializers.IntegerField(min_value=1, max_value=12)

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Acest nume de utilizator există deja.")
        return value

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data["username"],
            password=validated_data["password"],
        )
        profile = get_or_create_profile(user)
        profile.clasa = validated_data["clasa"]
        profile.save(update_fields=["clasa"])
        return user


class AnswerOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnswerOption
        fields = ("id", "text")


class QuestionSerializer(serializers.ModelSerializer):
    options = AnswerOptionSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = ("id", "text", "points", "options")


class QuizListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quiz
        fields = ("id", "title", "description", "difficulty")


class QuizDetailSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Quiz
        fields = ("id", "title", "description", "difficulty", "questions")


class QuizSubmitSerializer(serializers.Serializer):
    answers = serializers.DictField(
        child=serializers.IntegerField(),
        help_text="Map question_id -> option_id",
    )


class QuizAttemptAnswerSerializer(serializers.ModelSerializer):
    question_text = serializers.CharField(source="question.text", read_only=True)
    selected_text = serializers.CharField(source="selected_option.text", read_only=True)
    points = serializers.IntegerField(source="question.points", read_only=True)
    correct_option_text = serializers.SerializerMethodField()

    class Meta:
        model = QuizAttemptAnswer
        fields = (
            "question_id",
            "question_text",
            "selected_text",
            "is_correct",
            "points",
            "correct_option_text",
        )

    def get_correct_option_text(self, obj):
        if obj.is_correct:
            return None
        correct = obj.question.options.filter(is_correct=True).first()
        return correct.text if correct else None


class QuizAttemptSerializer(serializers.ModelSerializer):
    quiz_title = serializers.CharField(source="quiz.title", read_only=True)
    answers = QuizAttemptAnswerSerializer(many=True, read_only=True)

    class Meta:
        model = QuizAttempt
        fields = (
            "id",
            "quiz_id",
            "quiz_title",
            "score",
            "max_score",
            "created_at",
            "answers",
        )


class ProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    xp_progress = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = (
            "username",
            "clasa",
            "level",
            "xp",
            "avatar",
            "theme",
            "xp_progress",
        )
        read_only_fields = ("level", "xp")

    def get_xp_progress(self, obj):
        return xp_progress(obj)


class BattlePassTierSerializer(serializers.ModelSerializer):
    unlocked = serializers.SerializerMethodField()
    owned = serializers.SerializerMethodField()

    class Meta:
        model = BattlePassTier
        fields = (
            "level_req",
            "reward_name",
            "reward_type",
            "reward_value",
            "unlocked",
            "owned",
        )

    def get_unlocked(self, obj):
        profile = self.context.get("profile")
        return profile.level >= obj.level_req if profile else False

    def get_owned(self, obj):
        owned_keys = self.context.get("owned_keys", set())
        return obj.reward_value in owned_keys


class BattlePassSerializer(serializers.Serializer):
    season = serializers.SerializerMethodField()
    profile_level = serializers.SerializerMethodField()
    tiers = serializers.SerializerMethodField()

    def get_season(self, user):
        progress = get_battlepass_progress(user)
        season = progress["season"]
        if not season:
            return None
        return {
            "name": season.name,
            "start_date": season.start_date,
            "end_date": season.end_date,
        }

    def get_profile_level(self, user):
        return get_or_create_profile(user).level

    def get_tiers(self, user):
        progress = get_battlepass_progress(user)
        owned_keys = set(user.items.values_list("item_key", flat=True))
        return BattlePassTierSerializer(
            [item["tier"] for item in progress["tiers"]],
            many=True,
            context={"profile": progress["profile"], "owned_keys": owned_keys},
        ).data
