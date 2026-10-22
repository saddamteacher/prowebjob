"""HH.UZ web parser — category-specific queries. API is blocked, uses web scraping."""

from urllib.parse import urlsplit, urlunsplit

from bs4 import BeautifulSoup

from parsers.base import BaseParser, ParserError
from services.level_detector import LEVELS, LEVEL_HH_EXPERIENCE

BASE_URL = "https://tashkent.hh.uz"

# Har kategoriya uchun bir nechta so'rov — barchasiga teng ko'p natija
QUERIES_BY_CATEGORY = {
    'data_analyst': [
        "data analyst", "аналитик данных", "BI аналитик",
        "бизнес аналитик", "аналитик", "data analyst junior",
        "системный аналитик", "продуктовый аналитик",
    ],
    'data_science': [
        "data scientist", "machine learning", "ml engineer",
        "data science", "специалист по данным", "ai engineer",
    ],
    'python': [
        "python developer", "python разработчик", "django developer",
        "backend developer", "бэкенд разработчик", "python программист",
        "fastapi developer",
    ],
    'frontend': [
        "frontend developer", "react developer", "vue developer",
        "javascript разработчик", "фронтенд разработчик",
        "верстальщик", "web developer", "angular developer",
    ],
    'graphic_design': [
        "ui ux designer", "графический дизайнер", "figma designer",
        "веб дизайнер", "дизайнер", "product designer",
        "motion designer", "брендинг дизайнер",
    ],
    'smm': [
        "smm менеджер", "таргетолог", "контент менеджер",
        "smm специалист", "интернет маркетолог", "маркетолог",
        "digital marketing", "seo специалист", "контекстолог",
    ],
    'mobilograf': [
        "видеограф", "мобилограф", "видеомонтажер",
        "video editor", "монтажер", "контент мейкер",
    ],
    '3d_max': [
        "3ds max", "интерьерный дизайнер", "визуализатор",
        "autocad", "архитектор", "3d визуализатор", "дизайнер интерьера",
    ],
    'blender': [
        "blender", "3d artist", "3d моделлер",
        "3d аниматор", "game designer", "3d дизайнер",
    ],
    'ms_office': [
        "офис менеджер", "оператор пк", "excel специалист",
        "секретарь", "администратор", "делопроизводитель",
        "1с оператор", "ассистент", "data entry",
    ],
}

CATEGORY_QUERIES = [q for queries in QUERIES_BY_CATEGORY.values() for q in queries]

EXPERIENCE_PREFIX = "vacancy-serp__vacancy-work-experience-"


class HHUZParser(BaseParser):
    def __init__(self):
        super().__init__()
        self.source_name = "hhuz"
        self.display_name = "HH.UZ"

    # Har so'rov uchun nechta sahifa olish (har sahifada ~20 ta)
    MAX_PAGES = 4

    def parse(self) -> list[dict]:
        items = []
        seen: set[str] = set()

        for query, experience in self._requests():
            for page in range(self.MAX_PAGES):
                try:
                    response = self.get(
                        f"{BASE_URL}/search/vacancy",
                        params={
                            **({"experience": experience} if experience else {}),
                            "text":         query,
                            "area":         97,        # Uzbekistan
                            "search_field": "name",    # sarlavhada — aniqlik
                            "order_by":     "publication_time",
                            "period":       30,        # oxirgi 30 kun (7 emas)
                            "page":         page,      # pagination
                            "items_on_page": 100,      # har sahifada ko'proq
                        },
                    )
                    soup = BeautifulSoup(response.text, "lxml")
                    cards = soup.select("[data-qa='vacancy-serp__vacancy']")

                    if not cards:
                        break  # bu so'rov tugadi, keyingisiga o't

                    new_on_page = 0
                    for card in cards:
                        title_el = card.select_one("[data-qa='serp-item__title']")
                        if not title_el:
                            continue
                        url = self._canonical_url(title_el.get("href"))
                        if not url or url in seen:
                            continue
                        seen.add(url)
                        new_on_page += 1

                        employer_el = card.select_one("[data-qa='vacancy-serp__vacancy-employer']")
                        salary_el   = card.select_one("[data-qa='vacancy-serp__vacancy-compensation']")
                        city_el     = card.select_one("[data-qa='vacancy-serp__vacancy-address']")

                        snippet_el = card.select_one("[data-qa='vacancy-serp__vacancy_snippet']")
                        description = snippet_el.get_text(" ", strip=True) if snippet_el else ""
                        if not description:
                            description = card.get_text(" ", strip=True)[:1500]

                        title = title_el.get_text(" ", strip=True)
                        if len(title) < 3:
                            continue

                        items.append({
                            "title":       title,
                            "company":     employer_el.get_text(" ", strip=True) if employer_el else "Unknown",
                            "salary":      salary_el.get_text(" ", strip=True) if salary_el else None,
                            "city":        city_el.get_text(" ", strip=True) if city_el else "Tashkent",
                            "url":         url,
                            "description": description[:2000],
                            "source":      "HH.UZ",
                            "experience_code": self._experience_code(card),
                        })

                    # Agar sahifada yangi vakansiya bo'lmasa — keyingi so'rovga
                    if new_on_page == 0:
                        break

                except ParserError:
                    break  # bu so'rov xato berdi, keyingisiga o't

        return items

    def _queries(self) -> list[str]:
        if not self.categories:
            return CATEGORY_QUERIES
        return [q for cat, queries in QUERIES_BY_CATEGORY.items()
                if cat in self.categories for q in queries]

    def _experience_filter(self) -> list[str]:
        """HH 'experience' values for the selected levels ([] = no filter).

        HH honours only one experience value per request, so each value is a
        separate pass; with 3+ values a single unfiltered pass is cheaper and
        the engine filters by level afterwards.
        """
        if not self.levels:
            return []
        codes = [code for level in LEVELS if level in self.levels
                 for code in LEVEL_HH_EXPERIENCE[level]]
        return codes if len(codes) <= 2 else []

    def _requests(self) -> list[tuple[str, str | None]]:
        """(query, experience code or None) pairs to fetch."""
        experiences = self._experience_filter() or [None]
        return [(query, exp) for exp in experiences for query in self._queries()]

    def _experience_code(self, card) -> str | None:
        el = card.select_one(f"[data-qa^='{EXPERIENCE_PREFIX}']")
        if not el:
            return None
        return el.get("data-qa", "")[len(EXPERIENCE_PREFIX):] or None

    def _canonical_url(self, value: str | None) -> str:
        if not value:
            return ""
        absolute = self.absolute_url(BASE_URL, value)
        parts = urlsplit(absolute)
        return urlunsplit((parts.scheme, parts.netloc, parts.path, "", ""))
