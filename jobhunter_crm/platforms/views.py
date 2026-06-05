"""Platform management views."""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .models import Platform
from services.platform_icons import get_platform_icon_url, get_platform_color


@login_required(login_url='core:login')
def platform_list(request):
    platforms = Platform.objects.all().order_by('priority', 'name')
    platform_data = [
        {'obj': p, 'icon_url': get_platform_icon_url(p.slug, 64), 'color': get_platform_color(p.slug)}
        for p in platforms
    ]
    return render(request, 'platforms/list.html', {
        'platform_data': platform_data,
        'platforms': platforms,
        'section': 'platforms',
    })


@login_required(login_url='core:login')
def platform_toggle(request, pk):
    plat = get_object_or_404(Platform, pk=pk)
    plat.is_enabled = not plat.is_enabled
    plat.save(update_fields=['is_enabled'])
    status = "yoqildi" if plat.is_enabled else "o'chirildi"
    messages.success(request, f"{plat.name} {status}")
    return redirect('platforms:list')


@login_required(login_url='core:login')
def platform_test(request, pk):
    """Run one parser manually from the platform card."""
    plat = get_object_or_404(Platform, pk=pk)
    try:
        from parsers.engine import run_platform_parser

        result = run_platform_parser(plat.slug)
        if result['success']:
            messages.success(
                request,
                f"{plat.name}: {result.get('count', 0)} ta yangi vakansiya saqlandi."
            )
        else:
            messages.error(request, f"{plat.name}: {result.get('error', 'Xatolik')}")
    except Exception as exc:
        plat.mark_error(str(exc))
        messages.error(request, f"{plat.name}: {exc}")

    return redirect('platforms:list')
