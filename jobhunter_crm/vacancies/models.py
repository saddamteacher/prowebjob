"""Vacancy models."""

from django.db import models
from django.utils import timezone


class Category(models.Model):
    """Vacancy category / direction."""
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True, verbose_name="ON/OFF")
    daily_limit = models.PositiveIntegerField(default=10)
    icon = models.CharField(max_length=50, blank=True, help_text="Emoji or icon class")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Yo'nalish"
        verbose_name_plural = "Yo'nalishlar"
        ordering = ['name']

    def __str__(self):
        return self.name


class Skill(models.Model):
    """Skill mapped to a category."""
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name='skills'
    )
    name = models.CharField(max_length=100)
    aliases = models.TextField(
        blank=True,
        help_text="Comma-separated alternative names for matching"
    )

    class Meta:
        verbose_name = "Skill"
        verbose_name_plural = "Skilllar"
        unique_together = ('category', 'name')

    def __str__(self):
        return f"{self.name} → {self.category.name}"


class Vacancy(models.Model):
    """Vacancy from any source."""
    title = models.CharField(max_length=500)
    company_name = models.CharField(max_length=300, db_index=True)
    salary = models.CharField(max_length=200, blank=True, null=True)
    city = models.CharField(max_length=200, blank=True, null=True)
    source = models.CharField(max_length=100, db_index=True)
    url = models.URLField(max_length=2000, unique=True)
    description = models.TextField(blank=True, null=True)
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='vacancies'
    )
    score = models.IntegerField(default=0)
    is_remote = models.BooleanField(default=False)
    is_sent = models.BooleanField(default=False)
    sent_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Vakansiya"
        verbose_name_plural = "Vakansiyalar"
        ordering = ['-score', '-created_at']
        indexes = [
            models.Index(fields=['title', 'company_name']),
            models.Index(fields=['-created_at']),
        ]

    def __str__(self):
        return f"{self.title} @ {self.company_name}"


class ParsedLog(models.Model):
    """Log of parsed items for a run."""
    vacancy = models.ForeignKey(
        Vacancy, on_delete=models.CASCADE, related_name='parse_logs'
    )
    action = models.CharField(max_length=50, choices=[
        ('found', 'Topildi'),
        ('new', 'Yangi'),
        ('duplicate', 'Duplikat'),
        ('sent', 'Yuborilgan'),
        ('skipped', 'O\'tkazib yuborildi'),
    ])
    details = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Parser log"
        verbose_name_plural = "Parser loglari"
        ordering = ['-created_at']
