from django.conf import settings
from django.db import models


class ErrorReport(models.Model):
    KIND_USER = "user"
    KIND_SERVER = "server"
    KIND_CHOICES = [
        (KIND_USER, "Raport utilizator"),
        (KIND_SERVER, "Eroare server"),
    ]

    STATUS_NEW = "new"
    STATUS_REVIEWED = "reviewed"
    STATUS_RESOLVED = "resolved"
    STATUS_CHOICES = [
        (STATUS_NEW, "Nou"),
        (STATUS_REVIEWED, "Revizuit"),
        (STATUS_RESOLVED, "Rezolvat"),
    ]

    kind = models.CharField(max_length=10, choices=KIND_CHOICES, db_index=True)
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default=STATUS_NEW,
        db_index=True,
    )
    description = models.TextField(blank=True)
    page_url = models.CharField(max_length=500, blank=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="error_reports",
    )
    email = models.EmailField(blank=True)
    user_agent = models.CharField(max_length=500, blank=True)
    exception_type = models.CharField(max_length=200, blank=True)
    traceback = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["kind", "status", "created_at"]),
        ]

    def __str__(self):
        return f"#{self.pk} [{self.get_kind_display()}] {self.created_at:%Y-%m-%d %H:%M}"
