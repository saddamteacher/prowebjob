"""Platform models for managing parser sources."""

from django.db import models
from django.utils import timezone


class Platform(models.Model):
    """A vacancy source platform (HH.UZ, LinkedIn, etc)."""
    PLATFORM_TYPES = [
        ('uz', "O'zbekiston"),
        ('intl', "Xalqaro"),
    ]

    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    platform_type = models.CharField(
        max_length=10, choices=PLATFORM_TYPES, default='uz'
    )
    base_url = models.URLField(blank=True)
    is_enabled = models.BooleanField(default=True, verbose_name="ON/OFF")
    priority = models.PositiveIntegerField(
        default=100,
        help_text="Lower number = higher priority"
    )

    # Monitoring fields
    last_check = models.DateTimeField(null=True, blank=True)
    last_success = models.DateTimeField(null=True, blank=True)
    last_error = models.DateTimeField(null=True, blank=True)
    last_error_message = models.TextField(blank=True)
    total_vacancies = models.PositiveIntegerField(default=0)
    last_fetch_count = models.PositiveIntegerField(default=0)
    consecutive_errors = models.PositiveIntegerField(default=0)

    is_working = models.BooleanField(default=True, verbose_name="Ishlamoqda")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Platforma"
        verbose_name_plural = "Platformalar"
        ordering = ['priority', 'name']

    def __str__(self):
        return self.name

    def mark_success(self, count: int):
        """Mark a successful parse run."""
        self.last_check = timezone.now()
        self.last_success = timezone.now()
        self.last_fetch_count = count
        self.total_vacancies += count
        self.consecutive_errors = 0
        self.is_working = True
        self.last_error_message = ''
        self.save(update_fields=[
            'last_check', 'last_success', 'last_fetch_count',
            'total_vacancies', 'consecutive_errors', 'is_working',
            'last_error_message',
        ])

    def mark_error(self, error_message: str):
        """Mark a failed parse run."""
        self.last_check = timezone.now()
        self.last_error = timezone.now()
        self.last_error_message = error_message
        self.consecutive_errors += 1
        if self.consecutive_errors >= 3:
            self.is_working = False
        self.save(update_fields=[
            'last_check', 'last_error', 'last_error_message',
            'consecutive_errors', 'is_working'
        ])
