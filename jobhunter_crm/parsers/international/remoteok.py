"""RemoteOK parser using its public JSON endpoint."""

from parsers.base import BaseParser

API_URL = "https://remoteok.com/api"


class RemoteOKParser(BaseParser):
    def __init__(self):
        super().__init__()
        self.source_name = "remoteok"
        self.display_name = "RemoteOK"

    def parse(self) -> list[dict]:
        response = self.get(API_URL, headers={"Accept": "application/json"})
        payload = response.json()
        items = []
        for raw in payload:
            if not isinstance(raw, dict) or not raw.get("position"):
                continue
            tags = " ".join(raw.get("tags") or [])
            description = " ".join(part for part in [raw.get("description"), tags] if part)
            items.append({
                "title": raw.get("position") or "",
                "company": raw.get("company") or "RemoteOK",
                "salary": self._salary(raw),
                "city": "Remote",
                "url": raw.get("url") or f"https://remoteok.com/remote-jobs/{raw.get('id')}",
                "description": description[:2000],
                "source": "RemoteOK",
            })
        return items[:50]

    def _salary(self, raw: dict) -> str | None:
        minimum = raw.get("salary_min")
        maximum = raw.get("salary_max")
        if not minimum and not maximum:
            return None
        if minimum and maximum:
            return f"${minimum} - ${maximum}"
        if minimum:
            return f"from ${minimum}"
        return f"up to ${maximum}"
