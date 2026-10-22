"""Filtered vacancy search runs (courses × platforms × levels)."""

from datetime import timedelta

from django.conf import settings
from django.db import models
from django.utils import timezone

# A run older than this that is still "running" died with its worker.
STALE_AFTER = timedelta(minutes=30)


class SearchJob(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Kutilmoqda'),
        ('running', 'Ishlamoqda'),
        ('done', 'Tugadi'),
        ('error', 'Xato'),
    ]

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    categories = models.JSONField(default=list, help_text="Category slugs")
    platforms = models.JSONField(default=list, help_text="Platform slugs")
    levels = models.JSONField(default=list, help_text="junior / middle / senior")

    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    # {platform_slug: {"state": pending|running|done|error, "found": n, "new": n, "error": str}}
    platform_status = models.JSONField(default=dict)
    found_ids = models.JSONField(default=list)
    new_count = models.PositiveIntegerField(default=0)
    error = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Qidiruv"
        verbose_name_plural = "Qidiruvlar"
        ordering = ['-created_at']

    def __str__(self):
        return f"Qidiruv #{self.pk} ({self.status})"

    @property
    def is_active(self) -> bool:
        return self.status in ('pending', 'running')

    @property
    def is_stale(self) -> bool:
        started = self.started_at or self.created_at
        return self.is_active and timezone.now() - started > STALE_AFTER

    @property
    def done_platforms(self) -> int:
        return sum(1 for s in self.platform_status.values() if s.get('state') in ('done', 'error'))

    @property
    def progress_percent(self) -> int:
        total = len(self.platforms)
        if not total:
            return 0
        return round(100 * self.done_platforms / total)

    @property
    def duration_seconds(self) -> int | None:
        if not self.started_at:
            return None
        end = self.finished_at or timezone.now()
        return int((end - self.started_at).total_seconds())

    def mark_stale(self) -> None:
        self.status = 'error'
        self.error = "Qidiruv to'xtab qoldi (server qayta ishga tushgan bo'lishi mumkin)."
        self.finished_at = timezone.now()
        self.save(update_fields=['status', 'error', 'finished_at'])
