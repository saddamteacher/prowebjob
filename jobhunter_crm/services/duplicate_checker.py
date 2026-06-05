"""3-stage duplicate detection."""

import logging
from typing import Optional
from rapidfuzz import fuzz
from django.conf import settings

from vacancies.models import Vacancy

logger = logging.getLogger(__name__)
SIMILARITY_THRESHOLD = 90


class DuplicateChecker:
    """Three-stage duplicate check."""

    def __init__(self, groq_client=None):
        self.groq = groq_client

    def check(self, title: str, company: str, url: str,
              description: str = None) -> Optional[dict]:
        """Run all stages. Returns duplicate info or None."""
        # Stage 1: title + company exact
        existing = Vacancy.objects.filter(
            title__iexact=title,
            company_name__iexact=company
        ).first()
        if existing:
            logger.info(f"Stage 1 duplicate: '{title}' @ {company}")
            return {'stage': 1, 'existing': existing, 'similarity': 100.0}

        # Stage 2: description similarity
        if description and len(description) > 50:
            for vac in Vacancy.objects.exclude(description__isnull=True).exclude(description='')[:200]:
                ratio = fuzz.token_sort_ratio(description, vac.description)
                if ratio > SIMILARITY_THRESHOLD:
                    logger.info(f"Stage 2 duplicate: '{title}' ~ '{vac.title}' ({ratio:.1f}%)")
                    return {'stage': 2, 'existing': vac, 'similarity': ratio}

        # Stage 3: exact URL
        existing = Vacancy.objects.filter(url=url).first()
        if existing:
            logger.info(f"Stage 1 (URL) duplicate: {url}")
            return {'stage': 1, 'existing': existing, 'similarity': 100.0}

        return None
