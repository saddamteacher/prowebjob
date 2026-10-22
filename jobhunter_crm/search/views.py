"""Filtered vacancy search: pick courses, platforms and levels, then fetch."""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from platforms.models import Platform
from services.category_icons import annotate_with_icons
from services.level_detector import LEVELS, LEVEL_LABELS
from services.platform_icons import get_platform_color, get_platform_icon_url
from vacancies.models import Category, Vacancy

from .models import SearchJob
from .runner import start_job

RESULTS_PER_PAGE = 50


def _active_job():
    """The currently running job, if any (stale ones are closed on the way)."""
    for job in SearchJob.objects.filter(status__in=['pending', 'running']):
        if job.is_stale:
            job.mark_stale()
        else:
            return job
    return None


@login_required(login_url='core:login')
def search_index(request):
    categories = annotate_with_icons(Category.objects.filter(is_active=True).order_by('name'))
    platforms = [
        {'obj': p, 'icon_url': get_platform_icon_url(p.slug, 64), 'color': get_platform_color(p.slug)}
        for p in Platform.objects.filter(is_enabled=True).order_by('priority', 'name')
    ]
    last = SearchJob.objects.first()
    return render(request, 'search/index.html', {
        'categories': categories,
        'platforms': platforms,
        'levels': [(lvl, LEVEL_LABELS[lvl]) for lvl in LEVELS],
        # Pre-tick the previous selection; everything on the first visit.
        'sel_categories': last.categories if last else [c.slug for c in categories],
        'sel_platforms': last.platforms if last else [p['obj'].slug for p in platforms],
        'sel_levels': last.levels if last else ['junior'],
        'active_job': _active_job(),
        'recent_jobs': SearchJob.objects.all()[:10],
        'section': 'search',
    })


@login_required(login_url='core:login')
@require_POST
def search_start(request):
    active = _active_job()
    if active:
        messages.error(request, "Boshqa qidiruv hali tugamagan.")
        return redirect('search:detail', pk=active.pk)

    valid_categories = set(Category.objects.filter(is_active=True).values_list('slug', flat=True))
    valid_platforms = set(Platform.objects.filter(is_enabled=True).values_list('slug', flat=True))
    categories = [c for c in request.POST.getlist('categories') if c in valid_categories]
    platforms = [p for p in request.POST.getlist('platforms') if p in valid_platforms]
    levels = [lvl for lvl in LEVELS if lvl in request.POST.getlist('levels')]

    if not (categories and platforms and levels):
        messages.error(request, "Kamida bitta kurs, platforma va daraja tanlang.")
        return redirect('search:index')

    job = SearchJob.objects.create(
        created_by=request.user,
        categories=categories,
        platforms=platforms,
        levels=levels,
    )
    start_job(job.pk)
    return redirect('search:detail', pk=job.pk)


def _job_vacancies(job):
    order = {pk: i for i, pk in enumerate(job.found_ids)}
    vacancies = list(
        Vacancy.objects.filter(pk__in=job.found_ids, level__in=job.levels,
                               category__slug__in=job.categories)
        .select_related('category')
    )
    vacancies.sort(key=lambda v: (-v.score, order[v.pk]))
    return vacancies


@login_required(login_url='core:login')
def search_detail(request, pk):
    job = get_object_or_404(SearchJob, pk=pk)
    if job.is_stale:
        job.mark_stale()

    vacancies = _job_vacancies(job)
    level = request.GET.get('level', '')
    if level in LEVELS:
        vacancies = [v for v in vacancies if v.level == level]
    page = Paginator(vacancies, RESULTS_PER_PAGE).get_page(request.GET.get('page'))

    names = dict(Platform.objects.filter(slug__in=job.platforms).values_list('slug', 'name'))
    platform_rows = [
        {'slug': slug, 'name': names.get(slug, slug), 'icon_url': get_platform_icon_url(slug, 32),
         **job.platform_status.get(slug, {'state': 'pending'})}
        for slug in job.platforms
    ]
    return render(request, 'search/detail.html', {
        'job': job,
        'page': page,
        'platform_rows': platform_rows,
        'levels': [(lvl, LEVEL_LABELS[lvl]) for lvl in job.levels],
        'selected_level': level,
        'section': 'search',
    })


@login_required(login_url='core:login')
def search_status(request, pk):
    job = get_object_or_404(SearchJob, pk=pk)
    if job.is_stale:
        job.mark_stale()
    return JsonResponse({
        'status': job.status,
        'progress': job.progress_percent,
        'done_platforms': job.done_platforms,
        'total_platforms': len(job.platforms),
        'found': len(job.found_ids),
        'new': job.new_count,
        'duration': job.duration_seconds,
        'platforms': job.platform_status,
    })
