"""Company models."""

from django.db import models


class Company(models.Model):
    """Employer company."""
    name = models.CharField(max_length=300, unique=True, db_index=True)
    company_type = models.CharField(
        max_length=100, blank=True, null=True,
        help_text="IT Company, Education Center, Fintech, etc."
    )
    is_real = models.BooleanField(default=True, verbose_name="Haqiqiy kompaniya")
    description = models.TextField(blank=True, verbose_name="Faoliyat tavsifi")
    checked_by_ai = models.BooleanField(default=False)
    website = models.URLField(blank=True, null=True)
    logo = models.ImageField(upload_to='companies/', blank=True, null=True)
    is_top = models.BooleanField(default=False, verbose_name="TOP kompaniya")
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Kompaniya"
        verbose_name_plural = "Kompaniyalar"
        ordering = ['name']

    def __str__(self):
        return self.name
