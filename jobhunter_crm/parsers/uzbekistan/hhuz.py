"""HH.UZ web parser — category-specific queries. API is blocked, uses web scraping."""

from urllib.parse import urlsplit, urlunsplit

from bs4 import BeautifulSoup

from parsers.base import BaseParser, ParserError

BASE_URL = "https://tashkent.hh.uz"

# One focused query per major category — title-field search for precision
CATEGORY_QUERIES = [
    # Data roles — high priority, often underrepresented
    "data analyst",
    "аналитик данных",
    "BI аналитик",
    "data scientist",

    # Dev roles
    "python developer",
    "python разработчик",
    "frontend developer",
    "react developer",
    "javascript разработчик",

    # Design
    "ui ux designer",
    "графический дизайнер",
    "figma designer",

    # Marketing
    "smm менеджер",
    "таргетолог",
    "контент менеджер",

    # Creative
    "видеограф",
    "мобилограф",
    "3ds max",
    "интерьерный дизайнер",

    # Office
    "офис менеджер",
    "оператор пк",
    "excel специалист",
]


class HHUZParser(BaseParser):
    def __init__(self):
        super().__init__()
        self.source_name = "hhuz"
        self.display_name = "HH.UZ"

    def parse(self) -> list[dict]:
        items = []
        seen: set[str] = set()

        for query in CATEGORY_QUERIES:
            try:
                response = self.get(
                    f"{BASE_URL}/search/vacancy",
                    params={
                        "text":           query,
                        "area":           97,        # Uzbekistan
                        "search_field":   "name",    # title only — precision
                        "order_by":       "publication_time",
                        "period":         7,         # last 7 days
                    },
                )
                soup = BeautifulSoup(response.text, "lxml")
                cards = soup.select("[data-qa='vacancy-serp__vacancy']")

                for card in cards:
                    title_el = card.select_one("[data-qa='serp-item__title']")
                    if not title_el:
                        continue
                    url = self._canonical_url(title_el.get("href"))
                    if not url or url in seen:
                        continue
                    seen.add(url)

                    employer_el = card.select_one("[data-qa='vacancy-serp__vacancy-employer']")
                    salary_el   = card.select_one("[data-qa='vacancy-serp__vacancy-compensation']")
                    city_el     = card.select_one("[data-qa='vacancy-serp__vacancy-address']")

                    # Get snippet for description
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
                    })

            except ParserError:
                continue  # skip failed queries

        return items

    def _canonical_url(self, value: str | None) -> str:
        if not value:
            return ""
        absolute = self.absolute_url(BASE_URL, value)
        parts = urlsplit(absolute)
        return urlunsplit((parts.scheme, parts.netloc, parts.path, "", ""))
