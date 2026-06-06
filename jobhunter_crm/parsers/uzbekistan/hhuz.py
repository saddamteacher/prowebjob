"""HH.UZ web parser — category-specific queries. API is blocked, uses web scraping."""

from urllib.parse import urlsplit, urlunsplit

from bs4 import BeautifulSoup

from parsers.base import BaseParser, ParserError

BASE_URL = "https://tashkent.hh.uz"

# Har kategoriya uchun bir nechta so'rov — barchasiga teng ko'p natija
CATEGORY_QUERIES = [
    # ── DATA ANALYST ──────────────────────────────────────
    "data analyst", "аналитик данных", "BI аналитик",
    "бизнес аналитик", "аналитик", "data analyst junior",
    "системный аналитик", "продуктовый аналитик",

    # ── DATA SCIENCE ──────────────────────────────────────
    "data scientist", "machine learning", "ml engineer",
    "data science", "специалист по данным", "ai engineer",

    # ── PYTHON / BACKEND ──────────────────────────────────
    "python developer", "python разработчик", "django developer",
    "backend developer", "бэкенд разработчик", "python программист",
    "fastapi developer",

    # ── FRONTEND ──────────────────────────────────────────
    "frontend developer", "react developer", "vue developer",
    "javascript разработчик", "фронтенд разработчик",
    "верстальщик", "web developer", "angular developer",

    # ── GRAPHIC / UI-UX DESIGN ────────────────────────────
    "ui ux designer", "графический дизайнер", "figma designer",
    "веб дизайнер", "дизайнер", "product designer",
    "motion designer", "брендинг дизайнер",

    # ── SMM / MARKETING ───────────────────────────────────
    "smm менеджер", "таргетолог", "контент менеджер",
    "smm специалист", "интернет маркетолог", "маркетолог",
    "digital marketing", "seo специалист", "контекстолог",

    # ── MOBILOGRAF / VIDEO ────────────────────────────────
    "видеограф", "мобилограф", "видеомонтажер",
    "video editor", "монтажер", "контент мейкер",

    # ── 3D MAX / AUTOCAD ──────────────────────────────────
    "3ds max", "интерьерный дизайнер", "визуализатор",
    "autocad", "архитектор", "3d визуализатор", "дизайнер интерьера",

    # ── BLENDER / 3D ART ──────────────────────────────────
    "blender", "3d artist", "3d моделлер",
    "3d аниматор", "game designer", "3d дизайнер",

    # ── MS OFFICE / ADMIN ─────────────────────────────────
    "офис менеджер", "оператор пк", "excel специалист",
    "секретарь", "администратор", "делопроизводитель",
    "1с оператор", "ассистент", "data entry",
]


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

        for query in CATEGORY_QUERIES:
            for page in range(self.MAX_PAGES):
                try:
                    response = self.get(
                        f"{BASE_URL}/search/vacancy",
                        params={
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
                        })

                    # Agar sahifada yangi vakansiya bo'lmasa — keyingi so'rovga
                    if new_on_page == 0:
                        break

                except ParserError:
                    break  # bu so'rov xato berdi, keyingisiga o't

        return items

    def _canonical_url(self, value: str | None) -> str:
        if not value:
            return ""
        absolute = self.absolute_url(BASE_URL, value)
        parts = urlsplit(absolute)
        return urlunsplit((parts.scheme, parts.netloc, parts.path, "", ""))
