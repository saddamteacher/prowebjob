"""Seniority level detection (junior / middle / senior).

Rule of thumb used everywhere in the app:
  junior — no experience, up to 1 year, 1–3 years
  middle — 3–6 years
  senior — 6+ years, or lead / head / principal roles
"""

import re

JUNIOR = 'junior'
MIDDLE = 'middle'
SENIOR = 'senior'
LEVELS = (JUNIOR, MIDDLE, SENIOR)

LEVEL_LABELS = {
    JUNIOR: 'Junior',
    MIDDLE: 'Middle',
    SENIOR: 'Senior',
}

# HH.UZ "work experience" codes → level
HH_EXPERIENCE_LEVELS = {
    'noExperience':  JUNIOR,
    'between1And3':  JUNIOR,
    'between3And6':  MIDDLE,
    'moreThan6':     SENIOR,
}

# HH.UZ codes to request for each level (search filter)
LEVEL_HH_EXPERIENCE = {
    JUNIOR: ['noExperience', 'between1And3'],
    MIDDLE: ['between3And6'],
    SENIOR: ['moreThan6'],
}

SENIOR_TITLE = re.compile(
    r'\b(senior|sr\.?|lead(?!\s*gen)|team\s*lead|tech\s*lead|principal|staff\s+engineer|'
    r'head\s+of|director|architect|vp\s+of|vice\s+president|cto|ceo|coo|'
    r'старш\w*|ведущ\w*|главн\w*|руководител\w*|директор\w*|'
    r'тимлид\w*|начальник\w*|katta)\b',
    re.IGNORECASE,
)

MIDDLE_TITLE = re.compile(r'\b(middle|mid|mid-level)\b', re.IGNORECASE)

JUNIOR_TITLE = re.compile(
    r'\b(junior|jr\.?|intern|internship|trainee|entry[\s-]*level|graduate|assistant|'
    r'младш\w*|стаж[её]р\w*|начинающ\w*|без\s+опыта|ассистент\w*|помощник\w*|'
    r'kichik|stajyor|amaliyotchi|tajribasiz|yordamchi)\b',
    re.IGNORECASE,
)

NO_EXPERIENCE = re.compile(
    r'(без\s+опыта|опыт\s+не\s+(?:требуется|обязателен|нужен)|'
    r'no\s+experience|experience\s+not\s+required|tajriba\s+shart\s+emas|'
    r'tajribasiz)',
    re.IGNORECASE,
)

_YEARS = r'(?:лет|года|год|years?|yrs?|yil)'
_NUM = r'(\d{1,2})'

# Explicit required-experience phrases; group(1) = minimum years.
EXPERIENCE_PATTERNS = [
    # "опыт работы от 3 лет", "опыт 1-3 года", "experience: 2+ years", "tajriba 1 yil"
    re.compile(
        r'(?:опыт\w*|experience|tajriba\w*)\D{0,25}?(?:от|from|at\s+least|min(?:imum)?\.?|kamida)?\s*'
        + _NUM + r'\s*(?:[-–—]\s*\d{1,2}\s*)?\+?\s*' + _YEARS,
        re.IGNORECASE,
    ),
    # "3+ years of experience", "от 3 лет опыта", "2 yillik tajriba"
    re.compile(
        r'(?:от|from|at\s+least)?\s*' + _NUM + r'\s*(?:[-–—]\s*\d{1,2}\s*)?\+?\s*'
        + _YEARS + r'\w*\s+(?:of\s+)?(?:опыт\w*|experience|tajriba\w*|commercial|работы)',
        re.IGNORECASE,
    ),
]


def level_from_years(years: int) -> str:
    """Minimum required years → level (0–2 junior, 3–5 middle, 6+ senior)."""
    if years < 3:
        return JUNIOR
    if years < 6:
        return MIDDLE
    return SENIOR


def required_years(text: str) -> int | None:
    """Smallest explicit 'N years of experience' requirement found in text."""
    if not text:
        return None
    found = []
    for pattern in EXPERIENCE_PATTERNS:
        for match in pattern.finditer(text):
            years = int(match.group(1))
            if years <= 20:
                found.append(years)
    return min(found) if found else None


def detect_level(title: str, description: str = '', experience_code: str | None = None) -> str:
    """Detect seniority. Priority: platform field → title → description → junior."""
    if experience_code in HH_EXPERIENCE_LEVELS:
        return HH_EXPERIENCE_LEVELS[experience_code]

    # Titles like "Junior/Middle" or "Помощник руководителя" → lowest level wins.
    title = title or ''
    if JUNIOR_TITLE.search(title):
        return JUNIOR
    if MIDDLE_TITLE.search(title):
        return MIDDLE
    if SENIOR_TITLE.search(title):
        return SENIOR

    description = description or ''
    if NO_EXPERIENCE.search(description):
        return JUNIOR
    years = required_years(description)
    if years is not None:
        return level_from_years(years)

    # No requirement stated — open to beginners.
    return JUNIOR


def experience_label(title: str, description: str = '', experience_code: str | None = None) -> str:
    """Short human label of the experience requirement, '' if unknown."""
    hh_labels = {
        'noExperience': '0',
        'between1And3': '1–3',
        'between3And6': '3–6',
        'moreThan6':    '6+',
    }
    if experience_code in hh_labels:
        return hh_labels[experience_code]
    if NO_EXPERIENCE.search(description or ''):
        return '0'
    years = required_years(description or '')
    if years is not None:
        return f'{years}+'
    return ''
