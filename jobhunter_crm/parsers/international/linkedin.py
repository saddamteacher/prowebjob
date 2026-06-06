"""LinkedIn guest jobs API parser — pagination + 30 kun."""

from bs4 import BeautifulSoup

from parsers.base import BaseParser, ParserError

# LinkedIn ochiq (guest) jobs API — pagination'ni qo'llab-quvvatlaydi
API_URL = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"

SEARCH_QUERIES = [
    "data analyst", "business analyst", "data scientist",
    "python developer", "backend developer",
    "frontend developer", "react developer", "fullstack developer",
    "ui ux designer", "product designer", "graphic designer",
    "smm manager", "digital marketing", "marketing specialist",
    "qa engineer", "devops engineer", "project manager",
]


class LinkedInParser(BaseParser):
    MAX_PAGES = 4        # har so'rov uchun 4 sahifa (25 tadan = 100)
    PER_PAGE  = 25

    def __init__(self):
        super().__init__()
        self.source_name = "linkedin"
        self.display_name = "LinkedIn"

    def parse(self) -> list[dict]:
        items = []
        seen: set[str] = set()

        for query in SEARCH_QUERIES:
            for page in range(self.MAX_PAGES):
                try:
                    response = self.get(
                        API_URL,
                        params={
                            "keywords": query,
                            "location": "Uzbekistan",
                            "f_TPR":    "r2592000",   # oxirgi 30 kun (7 emas)
                            "start":    page * self.PER_PAGE,
                        },
                    )
                except ParserError:
                    break

                if "authwall" in response.text.lower():
                    break

                soup  = BeautifulSoup(response.text, "lxml")
                cards = soup.select(".base-card, li")
                if not cards:
                    break

                new_on_page = 0
                for card in cards:
                    link = card.select_one("a[href*='/jobs/view']")
                    if not link:
                        continue
                    url = self.absolute_url("https://www.linkedin.com", link.get("href"))
                    if not url or url in seen:
                        continue
                    seen.add(url)
                    new_on_page += 1

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

                if new_on_page == 0:
                    break

        return items
