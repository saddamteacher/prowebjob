"""Dashboard views."""

import re, json
from datetime import timedelta, date

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.utils import timezone

from vacancies.models import Vacancy, Category
from platforms.models import Platform
from companies.models import Company
from logs_app.models import ActivityLog
from services.category_icons import CATEGORY_ICONS, get_category_icon_url
from services.platform_icons import get_platform_icon_url, get_platform_color, PLATFORM_DOMAINS


def _extract_salary_usd(salary_str: str) -> int | None:
    if not salary_str:
        return None
    s = salary_str.lower()
    nums = [int(n.replace(' ', '').replace(',', '')) for n in re.findall(r'[\d\s,]{3,}', salary_str) if n.strip().replace(' ','').replace(',','').isdigit()]
    if not nums:
        return None
    avg = sum(nums) / len(nums)
    if 'uzs' in s or 'сум' in s or avg > 100_000:
        return int(avg / 12700)
    if avg < 100:
        return int(avg * 1000)
    return int(avg)


@login_required(login_url='core:login')
def index(request):
    today    = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
    week_ago  = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)

    total_vacancies  = Vacancy.objects.count()
    today_found      = Vacancy.objects.filter(created_at__gte=today).count()
    week_found       = Vacancy.objects.filter(created_at__gte=week_ago).count()
    active_platforms = Platform.objects.filter(is_enabled=True).count()
    total_companies  = Company.objects.count()
    remote_count     = Vacancy.objects.filter(is_remote=True).count()

    # ── 30-day line chart data ───────────────────────────────────────
    chart_labels, chart_data = [], []
    for i in range(29, -1, -1):
        day = (today - timedelta(days=i)).date()
        count = Vacancy.objects.filter(
            created_at__date=day
        ).count()
        chart_labels.append(day.strftime('%d %b'))
        chart_data.append(count)

    # ── Platform donut data ──────────────────────────────────────────
    source_stats = (
        Vacancy.objects.values('source')
        .annotate(count=Count('id'))
        .order_by('-count')[:8]
    )
    platform_labels = [s['source'] for s in source_stats]
    platform_data   = [s['count'] for s in source_stats]

    # Platform colors for donut
    slug_by_source = {v: k for k, v in {
        'hhuz': 'HH.UZ', 'jobuz': 'Job.uz', 'ishboruz': 'Ishbor.uz',
        'telegram': 'Telegram', 'olxuz': 'OLX.uz',
        'linkedin': 'LinkedIn', 'remoteok': 'RemoteOK', 'remotive': 'Remotive',
    }.items()}
    donut_colors = []
    for lbl in platform_labels:
        slug = slug_by_source.get(lbl, lbl.lower().replace('.', '').replace(' ', ''))
        donut_colors.append(get_platform_color(slug))

    # ── Per-category stats ───────────────────────────────────────────
    cat_raw = (
        Category.objects.filter(is_active=True)
        .annotate(
            total=Count('vacancies'),
            week=Count('vacancies', filter=Q(vacancies__created_at__gte=week_ago)),
        )
        .order_by('-total')
    )
    max_count = max((c.total for c in cat_raw), default=1)
    category_stats = []
    for cat in cat_raw:
        icon_url = get_category_icon_url(cat.slug)
        sample = (
            Vacancy.objects.filter(category=cat, salary__isnull=False)
            .exclude(salary='').values_list('salary', flat=True)[:30]
        )
        usd_vals = [v for v in (_extract_salary_usd(s) for s in sample) if v and 100 < v < 20000]
        avg_salary = int(sum(usd_vals) / len(usd_vals)) if usd_vals else None
        pct = int(cat.total / max_count * 100) if max_count else 0
        demand = 'high' if pct >= 70 else ('medium' if pct >= 35 else 'low')
        category_stats.append({
            'slug': cat.slug, 'name': cat.name,
            'icon_url': icon_url, 'total': cat.total,
            'week': cat.week, 'pct': pct,
            'demand': demand, 'avg_salary': avg_salary,
        })

    # ── Platform cards with icons ─────────────────────────────────────
    platforms_db = Platform.objects.all().order_by('priority')
    platform_cards = []
    for p in platforms_db:
        platform_cards.append({
            'obj':       p,
            'icon_url':  get_platform_icon_url(p.slug, 32),
            'color':     get_platform_color(p.slug),
        })

    # ── Recent & logs ─────────────────────────────────────────────────
    recent_vacancies = Vacancy.objects.select_related('category').order_by('-created_at')[:8]
    recent_logs      = ActivityLog.objects.order_by('-created_at')[:6]
    top_companies    = Vacancy.objects.values('company_name').annotate(count=Count('id')).order_by('-count')[:5]

    context = {
        'total_vacancies':  total_vacancies,
        'today_found':      today_found,
        'week_found':       week_found,
        'active_platforms': active_platforms,
        'total_companies':  total_companies,
        'remote_count':     remote_count,
        'category_stats':   category_stats,
        'platform_cards':   platform_cards,
        'recent_vacancies': recent_vacancies,
        'recent_logs':      recent_logs,
        'top_companies':    top_companies,
        # Chart.js data
        'chart_labels_json':   json.dumps(chart_labels),
        'chart_data_json':     json.dumps(chart_data),
        'platform_labels_json': json.dumps(platform_labels),
        'platform_data_json':  json.dumps(platform_data),
        'donut_colors_json':   json.dumps(donut_colors),
    }
    return render(request, 'dashboard/index.html', context)
