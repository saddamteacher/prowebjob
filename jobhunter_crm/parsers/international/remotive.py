"""Remotive parser using its public JSON endpoint."""

from bs4 import BeautifulSoup

from parsers.base import BaseParser

API_URL = "https://remotive.com/api/remote-jobs"


class RemotiveParser(BaseParser):
    def __init__(self):
        super().__init__()
        self.source_name = "remotive"
        self.display_name = "Remotive"

    def parse(self) -> list[dict]:
        response = self.get(
            API_URL,
            params={"category": "software-dev"},
            headers={"Accept": "application/json"},
        )
        payload = response.json()
        items = []
        for raw in payload.get("jobs", []):
            title = raw.get("title") or ""
            if not title:
                continue
            description = raw.get("description") or ""
            clean_description = BeautifulSoup(description, "lxml").get_text(" ", strip=True)
            items.append({
                "title": title,
                "company": raw.get("company_name") or "Remotive",
                "salary": raw.get("salary"),
                "city": "Remote",
                "url": raw.get("url") or "",
                "description": clean_description[:2000],
                "source": "Remotive",
            })
        return items[:50]
