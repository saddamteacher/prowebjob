"""Template filters for localization."""

from django import template
from core.translations import get_category_name

register = template.Library()


@register.filter
def cat_name(category, lang='uz'):
    """
    Kategoriya nomini joriy tilda qaytaradi.
    Ishlatish: {{ vacancy.category|cat_name:current_lang }}
              {{ cat|cat_name:current_lang }}
    """
    if category is None:
        return ''
    slug = getattr(category, 'slug', None)
    fallback = getattr(category, 'name', '') or str(category)
    if not slug:
        return fallback
    return get_category_name(slug, lang, fallback)


@register.filter
def cat_name_by_slug(slug, lang='uz'):
    """Slug bo'yicha to'g'ridan-to'g'ri."""
    if not slug:
        return ''
    return get_category_name(slug, lang)
