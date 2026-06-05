"""Parser engine — runs all registered parsers."""

import logging
from typing import Optional

from django.utils import timezone

from vacancies.models import Vacancy, Category, ParsedLog
from platforms.models import Platform
from companies.models import Company
from services.duplicate_checker import DuplicateChecker
from logs_app.models import ActivityLog

logger = logging.getLogger(__name__)


def run_platform_parser(platform_slug: str) -> dict:
    """Run a specific platform parser by slug."""
    from platforms.models import Platform
    plat = Platform.objects.filter(slug=platform_slug).first()
    if not plat:
        return {'success': False, 'error': 'Platform not found'}

    parser = _get_parser(platform_slug)
    if not parser:
        return {'success': False, 'error': f'No parser for {platform_slug}'}

    try:
        raw_vacancies = parser.parse()
        count = 0
        for raw in raw_vacancies:
            norm = parser.normalize(raw)
            
            # Category check: skip if no category matches
            if norm is None:
                continue
            
            # Junior-level check: skip if score is 0 (senior/mid/lead)
            if norm.get('score', 0) == 0:
                continue
            if not norm.get('title') or not norm.get('url'):
                continue
            
            dup = DuplicateChecker().check(
                norm['title'], norm['company_name'],
                norm['url'], norm.get('description')
            )
            if dup:
                ParsedLog.objects.create(
                    vacancy=dup['existing'],
                    action='duplicate',
                    details=f"Stage {dup['stage']} ({dup['similarity']:.0f}%)",
                )
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
            if created:
                count += 1
                ParsedLog.objects.create(vacancy=vacancy, action='new')
            else:
                ParsedLog.objects.create(vacancy=vacancy, action='duplicate')

        plat.mark_success(count)
        ActivityLog.objects.create(
            level='success', source='parser',
            message=f"{plat.name}: {count} ta yangi vakansiya"
        )
        return {'success': True, 'count': count}

    except Exception as e:
        plat.mark_error(str(e))
        ActivityLog.objects.create(
            level='error', source='parser',
            message=f"{plat.name}: {e}"
        )
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
