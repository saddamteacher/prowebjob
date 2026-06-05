"""Parser monitoring views."""

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

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
    """Run all parsers manually."""
    from .engine import run_all_parsers
    result = run_all_parsers()
    messages.success(
        request,
        f"Parser yakunlandi: {result['total_new']} ta yangi, "
        f"{result['total_errors']} ta xatolik"
    )
    return redirect('parser:monitor')
