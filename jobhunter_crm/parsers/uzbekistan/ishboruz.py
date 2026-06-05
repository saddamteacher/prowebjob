"""Ishbor.uz parser — uses public JSON API at api.ishbor.uz."""

from parsers.base import BaseParser, ParserError

API_BASE = "https://api.ishbor.uz"


class IshborUZParser(BaseParser):
    def __init__(self):
        super().__init__()
        self.source_name = "ishboruz"
        self.display_name = "Ishbor.uz"

    def parse(self) -> list[dict]:
        items = []
        seen: set[str] = set()

        # Fetch first 3 pages (80 items each → up to 240 vacancies)
        for page in range(1, 4):
            try:
                response = self.get(
                    f"{API_BASE}/vacancies",
                    params={"page": page},
                    headers={"Accept": "application/json"},
                )
                data = response.json()
                raw_list = data.get("items") or []
                if not raw_list:
                    break

                for raw in raw_list:
                    vac_id = raw.get("id")
                    title  = (raw.get("title") or "").strip()
                    if not title or not vac_id:
                        continue

                    url = f"https://ishbor.uz/vacancy/{vac_id}"
                    if url in seen:
                        continue
                    seen.add(url)

                    # Salary
                    sal_min = raw.get("salary_min")
                    sal_max = raw.get("salary_max")
                    cur     = raw.get("salary_currency") or "UZS"
                    if sal_min and sal_max:
                        salary = f"{int(sal_min):,} - {int(sal_max):,} {cur}"
                    elif sal_min:
                        salary = f"from {int(sal_min):,} {cur}"
                    elif raw.get("negotiable"):
                        salary = "Kelishiladi"
                    else:
                        salary = None

                    # City
                    city = raw.get("city") or None

                    # Description — prefer full, fallback to short
                    desc = (
                        raw.get("description") or
                        raw.get("short_description") or ""
                    ).strip()

                    # Company
                    company = (raw.get("company_name") or "").strip()
                    if not company:
                        customer = raw.get("customer") or {}
                        company = (customer.get("full_name") or "Ishbor.uz").strip()

                    # Remote detection
                    job_modes = raw.get("job_modes") or []
                    if isinstance(job_modes, list):
                        is_remote_hint = any("remote" in str(m).lower() for m in job_modes)
                    else:
                        is_remote_hint = False

                    items.append({
                        "title":       title,
                        "company":     company,
                        "salary":      salary,
                        "city":        "Remote" if is_remote_hint else city,
                        "url":         url,
                        "description": desc[:2000],
                        "source":      "Ishbor.uz",
                    })

            except (ParserError, Exception):
                break

        return items
