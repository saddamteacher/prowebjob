from django.contrib import admin
from .models import Platform


@admin.register(Platform)
class PlatformAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'platform_type', 'is_enabled', 'is_working',
        'last_check', 'consecutive_errors', 'total_vacancies'
    ]
    list_filter = ['platform_type', 'is_enabled', 'is_working']
    search_fields = ['name']
    readonly_fields = [
        'last_check', 'last_success', 'last_error',
        'total_vacancies', 'consecutive_errors'
    ]
    prepopulated_fields = {'slug': ('name',)}
