"""Platform icon URLs — uses Google Favicon service for originals."""

PLATFORM_DOMAINS = {
    'hhuz':     'hh.uz',
    'jobuz':    'job.uz',
    'ishboruz': 'ishbor.uz',
    'telegram': 'telegram.org',
    'olxuz':    'olx.uz',
    'linkedin': 'linkedin.com',
    'remoteok': 'remoteok.com',
    'remotive': 'remotive.com',
}

# Brand colors for fallback chips
PLATFORM_COLORS = {
    'hhuz':     '#E3001B',
    'jobuz':    '#2E7D32',
    'ishboruz': '#FF6B00',
    'telegram': '#2AABEE',
    'olxuz':    '#3A9B42',
    'linkedin': '#0077B5',
    'remoteok': '#2CB67D',
    'remotive': '#6C63FF',
}


def get_platform_icon_url(slug: str, size: int = 64) -> str | None:
    """Return Google Favicon URL for platform logo."""
    domain = PLATFORM_DOMAINS.get(slug)
    if domain:
        return f"https://www.google.com/s2/favicons?domain={domain}&sz={size}"
    return None


def get_platform_color(slug: str) -> str:
    return PLATFORM_COLORS.get(slug, '#4b5162')
