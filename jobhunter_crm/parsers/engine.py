"""Parser engine — runs all registered parsers."""

import logging

from vacancies.models import Vacancy, Category, ParsedLog
from platforms.models import Platform
from companies.models import Company
from services.duplicate_checker import DuplicateChecker
from logs_app.models import ActivityLog

logger = logging.getLogger(__name__)


def fetch_platform(platform_slug: str, categories=None, levels=None) -> list[dict]:
    """Download raw vacancies from one platform. Network only — no DB access,
    so several platforms can be fetched in parallel threads."""
    parser = _get_parser(platform_slug)
    if not parser:
        raise ValueError(f'No parser for {platform_slug}')
    parser.configure(categories=categories, levels=levels)
    return parser.parse()


def save_vacancies(platform_slug: str, raw_vacancies: list[dict],
                   categories=None, levels=None) -> dict:
    """Normalize, filter and store raw vacancies.

    Returns {'count': new vacancies, 'ids': ids of every stored or already
    known vacancy that matches the filters}.
    """
    parser = _get_parser(platform_slug)
    categories = set(categories) if categories else None
    levels = set(levels) if levels else None
    count = 0
    ids: list[int] = []

    for raw in raw_vacancies:
        norm = parser.normalize(raw)

        # Category check: skip if no category matches
        if norm is None:
            continue
        if not norm.get('title') or not norm.get('url'):
            continue
        if categories and norm['category_slug'] not in categories:
            continue
        if levels and norm['level'] not in levels:
            continue

        dup = DuplicateChecker().check(
            norm['title'], norm['company_name'],
            norm['url'], norm.get('description')
        )
        if dup:
            existing = dup['existing']
            ParsedLog.objects.create(
                vacancy=existing,
                action='duplicate',
                details=f"Stage {dup['stage']} ({dup['similarity']:.0f}%)",
            )
            if dup['stage'] == 1:
                # Same posting (same URL, or same title + company): the fresh
                # level is the most accurate one (HH gives it explicitly).
                _refresh_level(existing, norm)
            existing_cat = existing.category.slug if existing.category else None
            if (not levels or existing.level in levels) and (not categories or existing_cat in categories):
                ids.append(existing.id)
            continue

        # Get or create category
        cat_slug = norm.pop('category_slug')
        category = Category.objects.filter(slug=cat_slug).first()
        if not category:
            category, _ = Category.objects.get_or_create(
                slug=cat_slug,
                defaults={'name': cat_slug.replace('_', ' ').title(), 'is_active': True}
            )

        Company.objects.get_or_create(name=norm['company_name'] or 'Unknown')
        vacancy, created = Vacancy.objects.get_or_create(
            url=norm['url'],
            defaults={**norm, 'category': category}
        )
        ids.append(vacancy.id)
        if created:
            count += 1
            ParsedLog.objects.create(vacancy=vacancy, action='new')
        else:
            _refresh_level(vacancy, norm)
            ParsedLog.objects.create(vacancy=vacancy, action='duplicate')

    return {'count': count, 'ids': list(dict.fromkeys(ids))}


def _refresh_level(vacancy: Vacancy, norm: dict) -> None:
    if (vacancy.level, vacancy.experience) != (norm['level'], norm['experience']):
        vacancy.level = norm['level']
        vacancy.experience = norm['experience']
        vacancy.save(update_fields=['level', 'experience', 'updated_at'])


def record_success(plat: Platform, count: int) -> None:
    plat.mark_success(count)
    ActivityLog.objects.create(
        level='success', source='parser',
        message=f"{plat.name}: {count} ta yangi vakansiya"
    )


def record_error(plat: Platform, error: Exception | str) -> None:
    plat.mark_error(str(error))
    ActivityLog.objects.create(
        level='error', source='parser',
        message=f"{plat.name}: {error}"
    )


def run_platform_parser(platform_slug: str, categories=None, levels=None) -> dict:
    """Run a specific platform parser by slug (fetch + save)."""
    plat = Platform.objects.filter(slug=platform_slug).first()
    if not plat:
        return {'success': False, 'error': 'Platform not found'}
    if not _get_parser(platform_slug):
        return {'success': False, 'error': f'No parser for {platform_slug}'}

    try:
        raw_vacancies = fetch_platform(platform_slug, categories, levels)
        result = save_vacancies(platform_slug, raw_vacancies, categories, levels)
        record_success(plat, result['count'])
        return {'success': True, **result}

    except Exception as e:
        record_error(plat, e)
        return {'success': False, 'error': str(e)}


def run_all_parsers() -> dict:
    """Run all enabled platform parsers."""
    results = {'total_new': 0, 'total_errors': 0, 'details': []}
    platforms = Platform.objects.filter(is_enabled=True)

    for plat in platforms:
        result = run_platform_parser(plat.slug)
        if result['success']:
            results['total_new'] += result.get('count', 0)
        else:
            results['total_errors'] += 1
        results['details'].append({
            'platform': plat.name,
            'success': result['success'],
            'count': result.get('count', 0),
            'error': result.get('error'),
        })

    ActivityLog.objects.create(
        level='info', source='parser',
        message=f"Parser run: {results['total_new']} new, {results['total_errors']} errors"
    )
    return results


def _get_parser(platform_slug: str):
    """Get parser instance for a platform slug."""
    from .uzbekistan.hhuz import HHUZParser
    from .uzbekistan.jobuz import JobUZParser
    from .uzbekistan.ishboruz import IshborUZParser
    from .uzbekistan.telegram import TelegramParser
    from .uzbekistan.olxuz import OLXUZParser
    from .international.linkedin import LinkedInParser
    from .international.remoteok import RemoteOKParser
    from .international.remotive import RemotiveParser

    parsers = {
        'hhuz':     HHUZParser(),
        'jobuz':    JobUZParser(),
        'ishboruz': IshborUZParser(),
        'telegram': TelegramParser(),
        'olxuz':    OLXUZParser(),
        'linkedin': LinkedInParser(),
        'remoteok': RemoteOKParser(),
        'remotive': RemotiveParser(),
    }
    return parsers.get(platform_slug)
