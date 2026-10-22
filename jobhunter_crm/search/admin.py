from django.contrib import admin

from .models import SearchJob


@admin.register(SearchJob)
class SearchJobAdmin(admin.ModelAdmin):
    list_display = ['id', 'status', 'new_count', 'created_by', 'created_at', 'finished_at']
    list_filter = ['status']
    readonly_fields = ['platform_status', 'found_ids']
