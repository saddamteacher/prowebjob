"""OLX.uz jobs parser — web scraping /rabota section."""

from bs4 import BeautifulSoup
from urllib.parse import urljoin

from parsers.base import BaseParser, ParserError

BASE_URL = "https://www.olx.uz"
JOBS_URL = f"{BASE_URL}/rabota/"


class OLXUZParser(BaseParser):
    def __init__(self):
        super().__init__()
        self.source_name = "olxuz"
        self.display_name = "OLX.uz"

    def parse(self) -> list[dict]:
        items = []
        seen: set[str] = set()

        try:
            response = self.get(JOBS_URL)
        except ParserError:
            return []

        soup = BeautifulSoup(response.text, "lxml")
        cards = soup.select('[data-cy="l-card"]')

        for card in cards:
            # Title
            title_el = (
                card.find('h4') or card.find('h6') or
                card.find('strong') or card.select_one('[class*="title"]')
            )
            if not title_el:
                continue
            title = title_el.get_text(" ", strip=True)
            if len(title) < 4:
                continue

            # URL
            link_el = card.find('a', href=True)
            if not link_el:
                continue
            href = link_el.get('href', '')
            url = href if href.startswith('http') else urljoin(BASE_URL, href)
            if not url or url in seen:
                continue
            seen.add(url)

            # Price/salary
            price_el = (
                card.select_one('[data-testid="ad-price"]') or
                card.select_one('[class*="price"]')
            )
            salary = price_el.get_text(" ", strip=True) if price_el else None
            if salary and salary.strip() in ('', '-', '—'):
                salary = None

            # Location
            loc_el = (
                card.select_one('[data-testid="location-date"]') or
                card.select_one('[class*="location"]')
            )
            city = loc_el.get_text(" ", strip=True).split('-')[0].strip() if loc_el else None

            # Description from card text
            desc = card.get_text(" ", strip=True)[:1500]

            items.append({
                "title":       title,
                "company":     "OLX.uz",
                "salary":      salary,
                "city":        city,
                "url":         url,
                "description": desc,
                "source":      "OLX.uz",
            })

        return items
