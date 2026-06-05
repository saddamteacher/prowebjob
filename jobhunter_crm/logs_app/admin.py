from django.contrib import admin
from .models import ActivityLog


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ['level', 'source', 'message', 'user', 'created_at']
    list_filter = ['level', 'source']
    search_fields = ['message', 'details']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'
