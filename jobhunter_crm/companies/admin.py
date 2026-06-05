from django.contrib import admin
from .models import Company


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ['name', 'company_type', 'checked_by_ai', 'is_top', 'created_at']
    list_filter = ['checked_by_ai', 'is_top', 'company_type']
    search_fields = ['name']
    readonly_fields = ['created_at', 'updated_at']
