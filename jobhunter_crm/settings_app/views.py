"""Settings views."""

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings as django_settings

from .models import Setting


@login_required(login_url='core:login')
def settings_index(request):
    """View all settings."""
    all_settings = Setting.objects.all().order_by('key')
    default_limit = django_settings.DAILY_TOTAL_LIMIT
    return render(request, 'settings_app/index.html', {
        'settings': all_settings,
        'daily_limit': default_limit,
        'section': 'settings',
    })


@login_required(login_url='core:login')
def settings_update(request):
    """Update a setting via HTMX/POST."""
    if request.method == 'POST':
        key = request.POST.get('key', '')
        value = request.POST.get('value', '')
        if key:
            Setting.objects.update_or_create(key=key, defaults={'value': value})
            messages.success(request, f"Sozlama yangilandi: {key}")
    return redirect('settings_app:index')
