from django.db import models
from django.contrib.auth.models import User

class Quiz(models.Model):
    title       = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    difficulty  = models.CharField(max_length=20, choices=[
        ("easy", "Easy"),
        ("medium", "Medium"),
        ("hard", "Hard"),
    ])

    def __str__(self):
        return self.title

class Question(models.Model):
    quiz   = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="questions")
    text   = models.TextField()
    points = models.IntegerField(default=10)

    def __str__(self):
        return self.text[:50]

class AnswerOption(models.Model):
    question   = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="options")
    text       = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.text

class QuizAttempt(models.Model):
    user      = models.ForeignKey(User, on_delete=models.CASCADE)
    quiz      = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    score     = models.IntegerField(default=0)
    max_score = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
