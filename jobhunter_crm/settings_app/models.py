"""Application settings model."""

from django.db import models


class Setting(models.Model):
    """Key-value settings store."""
    key = models.CharField(max_length=200, unique=True, db_index=True)
    value = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Sozlama"
        verbose_name_plural = "Sozlamalar"

    def __str__(self):
        return self.key
