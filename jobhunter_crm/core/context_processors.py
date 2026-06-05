"""Context processors for all templates."""

from django.conf import settings
from .translations import get_translations


def site_settings(request):
    """Inject site-wide settings and translations into template context."""
    from vacancies.models import Vacancy
    from settings_app.models import Setting

    lang = request.session.get('lang', 'uz')

    ctx = {
        'DEBUG':        settings.DEBUG,
        'APP_NAME':     'PROWEB HR',
        'APP_VERSION':  '2.0.0',
        'current_lang': lang,
        't':            get_translations(lang),
    }
    try:
        ctx['DAILY_LIMIT'] = Setting.objects.get(key='daily_total_limit').value
    except Exception:
        ctx['DAILY_LIMIT'] = settings.DAILY_TOTAL_LIMIT
    try:
        ctx['total_vacancies'] = Vacancy.objects.count()
    except Exception:
        ctx['total_vacancies'] = 0
    return ctx
