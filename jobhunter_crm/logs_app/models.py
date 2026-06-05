"""Activity log model."""

from django.db import models
from django.contrib.auth.models import User


class ActivityLog(models.Model):
    """System-wide activity log."""
    LEVEL_CHOICES = [
        ('info', 'Info'),
        ('success', 'Success'),
        ('warning', 'Warning'),
        ('error', 'Error'),
        ('critical', 'Critical'),
    ]

    SOURCE_CHOICES = [
        ('parser', 'Parser'),
        ('scheduler', 'Scheduler'),
        ('ai', 'AI'),
        ('system', 'System'),
        ('user', 'User'),
    ]

    level = models.CharField(max_length=10, choices=LEVEL_CHOICES, default='info')
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES, default='system')
    message = models.TextField()
    details = models.TextField(blank=True, null=True)
    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        verbose_name = "Log"
        verbose_name_plural = "Loglar"
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.get_level_display()}] {self.message[:100]}"
