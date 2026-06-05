"""Telegram public channel parser — IT job channels in Uzbekistan."""

import re
from bs4 import BeautifulSoup

from parsers.base import BaseParser, ParserError

# Public IT job channels accessible via t.me/s/
CHANNELS = [
    ('it_jobs_uz',          'it_jobs_uz'),
    ('Uzbekistan_IT_Jobs',  'uzbekistan_it_jobs'),
]

BASE_URL = "https://t.me/s"


def _clean(text: str) -> str:
    """Remove emoji and extra whitespace."""
    emoji_pattern = re.compile(
        "[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF"
        "\U0001F680-\U0001F9FF\U0000200D\U00002702-\U000027B0"
        "\U0001F1E0-\U0001F1FF]+",
        flags=re.UNICODE,
    )
    return emoji_pattern.sub(' ', text).strip()


def _extract_field(text: str, *labels) -> str | None:
    """Extract value after any of the given labels."""
    for label in labels:
        m = re.search(
            rf'{re.escape(label)}\s*[:\-]?\s*(.+?)(?=\n|$)',
            text, re.IGNORECASE
        )
        if m:
            val = _clean(m.group(1)).strip()
            if len(val) > 2:
                return val[:250]
    return None


def _parse_title(text: str) -> str | None:
    """Extract job title from post text."""
    # Explicit labels
    for label in ['Vacancy:', 'Internship:', 'Position:', 'Вакансия:', 'Должность:', 'Роль:', 'Role:']:
        m = re.search(rf'{re.escape(label)}\s*(.+?)(?=\n)', text, re.IGNORECASE)
        if m:
            t = _clean(m.group(1)).strip()
            if len(t) > 4:
                return t[:200]

    # Hashtag + next meaningful line
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    for i, line in enumerate(lines):
        if line.startswith('#') and i + 1 < len(lines):
            candidate = _clean(lines[i + 1]).strip()
            if len(candidate) > 5 and not candidate.startswith('#'):
                return candidate[:200]

    # First non-hashtag non-emoji line
    for line in lines:
        clean = _clean(line).strip()
        if len(clean) > 8 and not clean.startswith('#'):
            return clean[:200]

    return None


class TelegramParser(BaseParser):
    def __init__(self):
        super().__init__()
        self.source_name = "telegram"
        self.display_name = "Telegram"

    def parse(self) -> list[dict]:
        items = []
        seen: set[str] = set()

        for channel_id, slug in CHANNELS:
            try:
                response = self.get(f"{BASE_URL}/{channel_id}")
                soup = BeautifulSoup(response.text, "lxml")
                messages = soup.select(".tgme_widget_message")

                for msg in messages:
                    text_el = msg.select_one(".tgme_widget_message_text")
                    if not text_el:
                        continue
                    text = text_el.get_text('\n', strip=True)
                    if len(text) < 30:
                        continue

                    # Get post URL
                    link_el = msg.select_one("a.tgme_widget_message_date")
                    url = link_el.get("href", "") if link_el else ""
                    msg_id = msg.get("data-post", "")
                    if not url:
                        url = f"https://t.me/{msg_id}" if msg_id else ""
                    if not url or url in seen:
                        continue
                    seen.add(url)

                    title = _parse_title(text)
                    if not title or len(title) < 5:
                        continue

                    company = _extract_field(
                        text,
                        'Company', 'Компания', 'Работодатель', 'Employer'
                    )
                    salary = _extract_field(
                        text,
                        'Salary', 'Зарплата', 'ЗП', 'Оплата', 'Доход', 'Compensation'
                    )
                    city = _extract_field(
                        text,
                        'Location', 'Город', 'Локация', 'Офис'
                    )

                    # Remote detection
                    if re.search(r'\b(remote|удалён|masofaviy|дистанц)\b', text, re.I):
                        city = city or "Remote"

                    items.append({
                        "title":       title,
                        "company":     company or f"@{slug}",
                        "salary":      salary,
                        "city":        city,
                        "url":         url,
                        "description": text[:2000],
                        "source":      f"Telegram @{slug}",
                    })

            except ParserError:
                continue

        return items
