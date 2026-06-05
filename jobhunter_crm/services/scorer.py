"""Smart priority scoring for vacancies."""

import re
from django.conf import settings

TOP_COMPANIES = {
    'uzum', 'yandex', 'google', 'microsoft', 'amazon', 'meta', 'apple',
    'epam', 'pdp', 'najot ta\'lim', 'tbc', 'artel', 'beeline', 'ucell',
    'agrobank', 'kapitalbank', 'click', 'payme', 'apelsin', 'goodzone',
    'humans', 'myid', 'uzcard', 'humo', 'zood', 'aliif', 'anor bank',
    'ipoteka bank', 'hamkorbank', 'soliq', 'davr bank',
}

# Only these seniority levels are hard-rejected (lead/director level)
SENIOR_ONLY_BLOCKLIST = re.compile(
    r'\b(team\s*lead|tech\s*lead|lead\s+developer|lead\s+engineer|'
    r'principal|staff\s+engineer|head\s+of|director|'
    r'vp\s+of|vice\s+president|chief\s+\w+\s+officer|cto|ceo|coo)\b',
    re.IGNORECASE
)

# These boost score (entry/junior level)
JUNIOR_BOOST = re.compile(
    r'\b(junior|intern|trainee|assistant|entry\s*level|beginner|'
    r'начинающ|стажер|помощник|kichik|yordamchi|stajyor)\b',
    re.IGNORECASE
)

# Experience requirement patterns — reject only if 3+ years required
EXPERIENCE_STRICT = re.compile(
    r'(?:опыт|experience|tajriba)\s*(?:от|from|of)?\s*([3-9]|\d{2,})\s*'
    r'(?:лет|года|years?|yil)',
    re.IGNORECASE
)


class VacancyScorer:
    """
    Calculate priority score for vacancies.

    Scoring:
      Base:          20 (all passing vacancies)
      Junior bonus:  +15
      Salary:        +20 (present), +5 (numeric)
      Top company:   +30
      Remote:        +20
      Full desc:     +10

    Rejected (score=0):
      - Team lead / head of / director in title
      - Requires 3+ years experience explicitly
    """

    def score(self, title: str, company: str, salary: str = None,
              city: str = None, description: str = None) -> int:

        title_lower = (title or '').lower()
        desc_lower  = (description or '').lower()
        full_text   = f"{title_lower} {desc_lower}"

        # ── Hard reject: lead/director roles ───────────────────────
        if SENIOR_ONLY_BLOCKLIST.search(title):
            return 0

        # ── Hard reject: 3+ years experience explicitly required ────
        if description and EXPERIENCE_STRICT.search(description):
            return 0

        # ── Base score ──────────────────────────────────────────────
        total = 20

        # Junior/intern/trainee boost
        if JUNIOR_BOOST.search(full_text):
            total += 15

        # Salary present
        if salary and salary.strip():
            total += getattr(settings, 'SCORE_SALARY', 20)
            if re.search(r'\d', salary):
                total += 5

        # Top company
        comp_clean = (company or '').lower().strip()
        if any(tc in comp_clean for tc in TOP_COMPANIES):
            total += getattr(settings, 'SCORE_TOP_COMPANY', 30)

        # Remote work
        remote_pattern = re.compile(
            r'\b(remote|masofaviy|wfh|masofadan|удаленн|дистанцион)\b',
            re.IGNORECASE
        )
        if (city and 'remote' in city.lower()) or remote_pattern.search(full_text):
            total += getattr(settings, 'SCORE_REMOTE', 20)

        # Full description (quality signal)
        if description and len(description.strip()) > 150:
            total += getattr(settings, 'SCORE_FULL_DESCRIPTION', 10)

        return min(total, 100)  # cap at 100
