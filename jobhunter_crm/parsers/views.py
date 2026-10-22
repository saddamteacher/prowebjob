"""Parser monitoring views."""

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from platforms.models import Platform
from vacancies.models import ParsedLog


@login_required(login_url='core:login')
def parser_monitor(request):
    platforms = Platform.objects.all().order_by('priority', 'name')
    recent_logs = ParsedLog.objects.select_related('vacancy').order_by('-created_at')[:50]
    return render(request, 'parsers/monitor.html', {
        'platforms': platforms,
        'recent_logs': recent_logs,
        'section': 'parser',
    })


@login_required(login_url='core:login')
def parser_run(request):
    """Old entry point: manual runs now go through the filtered search page,
    which works in the background instead of blocking the request."""
    return redirect('search:index')
