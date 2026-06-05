"""Activity log views."""

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import ActivityLog


@login_required(login_url='core:login')
def log_list(request):
    level = request.GET.get('level', '')
    source = request.GET.get('source', '')

    logs = ActivityLog.objects.all()
    if level:
        logs = logs.filter(level=level)
    if source:
        logs = logs.filter(source=source)

    logs = logs[:200]

    context = {
        'logs': logs,
        'selected_level': level,
        'selected_source': source,
        'section': 'logs',
    }
    return render(request, 'logs_app/list.html', context)


@login_required(login_url='core:login')
def log_clear(request):
    if request.user.is_superuser:
        ActivityLog.objects.all().delete()
        messages.success(request, "Loglar tozalandi.")
    return redirect('logs_app:list')
