from django.contrib import admin
from .models import Category, Skill, Vacancy, ParsedLog


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'daily_limit', 'created_at']
    list_filter = ['is_active']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ['name', 'category']
    list_filter = ['category']
    search_fields = ['name', 'category__name']


@admin.register(Vacancy)
class VacancyAdmin(admin.ModelAdmin):
    list_display = ['title', 'company_name', 'category', 'source', 'score', 'created_at']
    list_filter = ['source', 'category', 'is_sent', 'is_remote']
    search_fields = ['title', 'company_name', 'description']
    date_hierarchy = 'created_at'
    readonly_fields = ['created_at', 'updated_at']


@admin.register(ParsedLog)
class ParsedLogAdmin(admin.ModelAdmin):
    list_display = ['vacancy', 'action', 'created_at']
    list_filter = ['action']
    readonly_fields = ['created_at']
