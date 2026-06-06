"""Remotive parser using its public JSON endpoint."""

from bs4 import BeautifulSoup

from parsers.base import BaseParser

API_URL = "https://remotive.com/api/remote-jobs"


class RemotiveParser(BaseParser):
    def __init__(self):
        super().__init__()
        self.source_name = "remotive"
        self.display_name = "Remotive"

    # Bir nechta kategoriya — ko'proq vakansiya
    CATEGORIES = ["software-dev", "data", "design", "marketing", "product"]

    def parse(self) -> list[dict]:
        items = []
        seen: set[str] = set()
        for cat in self.CATEGORIES:
            try:
                response = self.get(
                    API_URL,
                    params={"category": cat},
                    headers={"Accept": "application/json"},
                )
                payload = response.json()
            except Exception:
                continue
            for raw in payload.get("jobs", []):
                title = raw.get("title") or ""
                url   = raw.get("url") or ""
                if not title or not url or url in seen:
                    continue
                seen.add(url)
                description = raw.get("description") or ""
                clean_description = BeautifulSoup(description, "lxml").get_text(" ", strip=True)
                items.append({
                    "title":       title,
                    "company":     raw.get("company_name") or "Remotive",
                    "salary":      raw.get("salary"),
                    "city":        "Remote",
                    "url":         url,
                    "description": clean_description[:2000],
                    "source":      "Remotive",
                })
        return items
