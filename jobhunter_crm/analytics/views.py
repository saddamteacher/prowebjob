"""Analytics views — full chart data."""

import json, re
from datetime import timedelta

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Avg, Q
from django.utils import timezone

from vacancies.models import Vacancy, Category
from platforms.models import Platform
from services.platform_icons import get_platform_color


@login_required(login_url='core:login')
def analytics_index(request):
    today     = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
    month_ago = today - timedelta(days=30)
    week_ago  = today - timedelta(days=7)

    total     = Vacancy.objects.count()
    monthly   = Vacancy.objects.filter(created_at__gte=month_ago).count()
    avg_score = Vacancy.objects.aggregate(Avg('score'))['score__avg'] or 0
    remote    = Vacancy.objects.filter(is_remote=True).count()
    with_salary = Vacancy.objects.exclude(salary__isnull=True).exclude(salary='').count()

    # ── 30-day line chart ─────────────────────────────────────────────
    labels_30, data_30 = [], []
    for i in range(29, -1, -1):
        day = (today - timedelta(days=i)).date()
        c   = Vacancy.objects.filter(created_at__date=day).count()
        labels_30.append(day.strftime('%d %b'))
        data_30.append(c)

    # ── Platform donut ────────────────────────────────────────────────
    src_stats = (
        Vacancy.objects.values('source')
        .annotate(count=Count('id'))
        .order_by('-count')[:8]
    )
    slug_map = {
        'HH.UZ': 'hhuz', 'Job.uz': 'jobuz', 'Ishbor.uz': 'ishboruz',
        'LinkedIn': 'linkedin', 'RemoteOK': 'remoteok', 'Remotive': 'remotive',
        'OLX.uz': 'olxuz',
    }
    pie_labels  = [s['source'] for s in src_stats]
    pie_data    = [s['count']  for s in src_stats]
    pie_colors  = [get_platform_color(slug_map.get(lbl, '')) for lbl in pie_labels]

    # ── Category bar chart ────────────────────────────────────────────
    cats = (
        Category.objects.filter(is_active=True)
        .annotate(total=Count('vacancies'), week=Count('vacancies', filter=Q(vacancies__created_at__gte=week_ago)))
        .order_by('-total')
    )
    from core.translations import get_category_name
    _lang = request.session.get('lang', 'uz')
    cat_labels = [get_category_name(c.slug, _lang, c.name) for c in cats]
    cat_data   = [c.total for c in cats]
    cat_week   = [c.week  for c in cats]

    # ── Score distribution ────────────────────────────────────────────
    score_ranges = {
        '90-100': Vacancy.objects.filter(score__gte=90).count(),
        '70-89':  Vacancy.objects.filter(score__gte=70, score__lt=90).count(),
        '50-69':  Vacancy.objects.filter(score__gte=50, score__lt=70).count(),
        '<50':    Vacancy.objects.filter(score__lt=50).count(),
    }

    # ── Top cities ────────────────────────────────────────────────────
    cities = (
        Vacancy.objects.exclude(city__isnull=True).exclude(city='')
        .values('city').annotate(count=Count('id'))
        .order_by('-count')[:10]
    )
    city_labels = [c['city']  for c in cities]
    city_data   = [c['count'] for c in cities]

    # ── Weekly trend (7 days per-source) ─────────────────────────────
    top_sources = [s['source'] for s in src_stats[:4]]
    weekly_datasets = []
    w_labels = [(today - timedelta(days=i)).date().strftime('%d %b') for i in range(6, -1, -1)]
    colors_map = {'HH.UZ': '#c9f31c', 'LinkedIn': '#0077B5', 'RemoteOK': '#2CB67D', 'Remotive': '#6C63FF'}
    for src in top_sources:
        ds = []
        for i in range(6, -1, -1):
            day = (today - timedelta(days=i)).date()
            ds.append(Vacancy.objects.filter(source=src, created_at__date=day).count())
        weekly_datasets.append({'label': src, 'data': ds, 'color': colors_map.get(src, '#9299a5')})

    context = {
        'total': total, 'monthly': monthly,
        'avg_score': round(avg_score, 1),
        'remote': remote, 'with_salary': with_salary,
        'categories': cats,
        'platforms': Platform.objects.all().order_by('-total_vacancies'),
        # Chart.js JSON
        'labels_30_json':  json.dumps(labels_30),
        'data_30_json':    json.dumps(data_30),
        'pie_labels_json': json.dumps(pie_labels),
        'pie_data_json':   json.dumps(pie_data),
        'pie_colors_json': json.dumps(pie_colors),
        'cat_labels_json': json.dumps(cat_labels),
        'cat_data_json':   json.dumps(cat_data),
        'cat_week_json':   json.dumps(cat_week),
        'score_labels_json': json.dumps(list(score_ranges.keys())),
        'score_data_json':   json.dumps(list(score_ranges.values())),
        'city_labels_json':  json.dumps(city_labels),
        'city_data_json':    json.dumps(city_data),
        'w_labels_json':     json.dumps(w_labels),
        'weekly_datasets_json': json.dumps(weekly_datasets),
    }
    return render(request, 'analytics/index.html', context)


@login_required(login_url='core:login')
def analytics_data(request):
    from django.http import JsonResponse
    today    = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
    week_ago = today - timedelta(days=7)
    return JsonResponse({
        'source_stats':  list(Vacancy.objects.values('source').annotate(count=Count('id')).order_by('-count')[:10]),
        'top_companies': list(Vacancy.objects.values('company_name').annotate(count=Count('id')).order_by('-count')[:10]),
        'today_found':   Vacancy.objects.filter(created_at__gte=today).count(),
        'week_found':    Vacancy.objects.filter(created_at__gte=week_ago).count(),
    })
