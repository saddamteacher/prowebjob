"""Base parser class for all platforms."""

from abc import ABC, abstractmethod
from urllib.parse import urljoin

import httpx

from services.skill_mapper import SkillMapper
from services.scorer import VacancyScorer

skill_mapper = SkillMapper()
scorer = VacancyScorer()

DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "uz,en;q=0.9,ru;q=0.8",
}


class ParserError(RuntimeError):
    """Raised when a platform cannot be fetched or parsed."""


class BaseParser(ABC):
    """Abstract base parser. Subclass for each platform."""

    def __init__(self):
        self.source_name = ''
        self.display_name = ''
        self.timeout = 25

    def get(self, url: str, **kwargs) -> httpx.Response:
        """Fetch a URL with consistent headers and clear errors."""
        headers = DEFAULT_HEADERS | kwargs.pop("headers", {})
        try:
            response = httpx.get(
                url,
                headers=headers,
                timeout=kwargs.pop("timeout", self.timeout),
                follow_redirects=True,
                **kwargs,
            )
            response.raise_for_status()
            return response
        except httpx.HTTPStatusError as exc:
            raise ParserError(f"{self.display_name}: HTTP {exc.response.status_code}") from exc
        except httpx.RequestError as exc:
            raise ParserError(f"{self.display_name}: network error - {exc}") from exc

    def absolute_url(self, base_url: str, value: str | None) -> str:
        if not value:
            return ""
        return urljoin(base_url, value.strip())

    @abstractmethod
    def parse(self) -> list[dict]:
        """Parse vacancies. Returns list of dicts with keys:
        title, company, salary, city, url, description, source
        """
        ...

    def normalize(self, raw: dict) -> dict | None:
        """Normalize raw data into standard format with category and score.
        
        Returns None if no category matches (vacancy is ignored).
        """
        title = (raw.get('title') or '').strip()
        desc = raw.get('description') or ''
        
        # Detect category — return None if no match
        category_slug = skill_mapper.detect(title, desc)
        if category_slug is None:
            return None
        
        score = scorer.score(
            title=title,
            company=raw.get('company', ''),
            salary=raw.get('salary'),
            city=raw.get('city'),
            description=desc,
        )
        is_remote = False
        if raw.get('city') and 'remote' in raw['city'].lower():
            is_remote = True
        if desc and ('remote' in desc.lower() or 'masofaviy' in desc.lower()):
            is_remote = True

        return {
            'title': title,
            'company_name': (raw.get('company') or '').strip(),
            'salary': raw.get('salary'),
            'city': raw.get('city'),
            'url': (raw.get('url') or '').strip(),
            'description': desc.strip() if desc else None,
            'source': raw.get('source', self.display_name),
            'category_slug': category_slug,
            'score': score,
            'is_remote': is_remote,
        }
