"""Job.uz parser — simple HTML format with bold field labels."""

import re
from bs4 import BeautifulSoup

from parsers.base import BaseParser, ParserError

BASE_URL = "https://job.uz"


class JobUZParser(BaseParser):
    def __init__(self):
        super().__init__()
        self.source_name = "jobuz"
        self.display_name = "Job.uz"

    def parse(self) -> list[dict]:
        try:
            response = self.get(BASE_URL)
        except ParserError:
            return []

        soup = BeautifulSoup(response.text, "lxml")
        items = []
        seen: set[str] = set()
        counter = 0

        # Each vacancy is in a <p> tag with bold labels
        for p in soup.find_all("p"):
            text = p.get_text(" ", strip=True)
            if "Position:" not in text and "Company:" not in text:
                continue

            # Extract fields with regex
            company  = self._field(text, "Company")
            position = self._field(text, "Position")
            salary   = self._field(text, "Salary")
            location = self._field(text, "Location")

            if not position or len(position) < 3:
                continue

            # Build a unique URL from company+position
            slug = re.sub(r'[^a-z0-9]+', '-', position.lower())[:40]
            counter += 1
            url = f"{BASE_URL}/vacancy/{counter}-{slug}"
            if url in seen:
                continue
            seen.add(url)

            # Full description — remove the structured part, keep the rest
            # Remove "Company: X Position: Y Salary: Z Location: W" prefix
            desc = re.sub(
                r'^(Company|Position|Salary|Location):.*?((?=\n[A-Z])|$)',
                '', text, flags=re.IGNORECASE | re.DOTALL
            ).strip()
            if len(desc) < 20:
                desc = text

            items.append({
                "title":       position[:300],
                "company":     company or "Job.uz",
                "salary":      salary,
                "city":        location,
                "url":         url,
                "description": desc[:2000],
                "source":      "Job.uz",
            })

        return items[:80]

    def _field(self, text: str, label: str) -> str | None:
        """Extract value after 'Label:' up to next label or newline."""
        pattern = rf'{label}:\s*(.+?)(?=\s+(?:Company|Position|Salary|Location|Skills|Main|If|Minimum|Preferred|Tech):|$)'
        m = re.search(pattern, text, re.IGNORECASE)
        if m:
            val = m.group(1).strip()
            return val[:200] if val else None
        return None
