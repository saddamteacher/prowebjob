"""LinkedIn public search parser — multi-category queries."""

from bs4 import BeautifulSoup

from parsers.base import BaseParser, ParserError

BASE_URL = "https://www.linkedin.com"

SEARCH_QUERIES = [
    "data analyst",
    "data scientist",
    "python developer",
    "frontend developer",
    "ui ux designer",
    "smm manager",
]


class LinkedInParser(BaseParser):
    def __init__(self):
        super().__init__()
        self.source_name = "linkedin"
        self.display_name = "LinkedIn"

    def parse(self) -> list[dict]:
        items = []
        seen: set[str] = set()

        for query in SEARCH_QUERIES:
            try:
                response = self.get(
                    f"{BASE_URL}/jobs/search",
                    params={
                        "keywords": query,
                        "location": "Uzbekistan",
                        "f_TPR": "r604800",  # last 7 days
                    },
                )
                if "authwall" in response.text.lower():
                    raise ParserError("LinkedIn authwall; platforma vaqtincha bloklangan")

                soup = BeautifulSoup(response.text, "lxml")
                for card in soup.select(".base-card, li"):
                    link = card.select_one("a[href*='/jobs/view']")
                    if not link:
                        continue
                    url = self.absolute_url(BASE_URL, link.get("href"))
                    if not url or url in seen:
                        continue
                    seen.add(url)

                    title_el    = card.select_one(".base-search-card__title, h3") or link
                    company_el  = card.select_one(".base-search-card__subtitle, h4")
                    location_el = card.select_one(".job-search-card__location")
                    title = title_el.get_text(" ", strip=True)
                    if len(title) < 4:
                        continue

                    items.append({
                        "title":       title,
                        "company":     company_el.get_text(" ", strip=True) if company_el else "LinkedIn",
                        "salary":      None,
                        "city":        location_el.get_text(" ", strip=True) if location_el else None,
                        "url":         url,
                        "description": card.get_text(" ", strip=True)[:1500],
                        "source":      "LinkedIn",
                    })
            except ParserError:
                continue

        return items[:80]
