"""Core views including login and main redirect."""

from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages


def _first_run() -> bool:
    """Desktop install with no account yet → the owner creates one in the browser."""
    return (settings.DESKTOP_MODE or settings.DEBUG) and not get_user_model().objects.exists()


def login_view(request):
    """User login page."""
    if request.user.is_authenticated:
        return redirect('dashboard:index')
    if _first_run():
        return redirect('core:setup')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard:index')
        messages.error(request, 'Login yoki parol xato!')
    return render(request, 'core/login.html')


def setup_view(request):
    """Create the first (admin) account. Only reachable while no user exists."""
    if not _first_run():
        return redirect('core:login')
    username = (request.POST.get('username') or '').strip()
    if request.method == 'POST':
        password = request.POST.get('password') or ''
        uz = request.session.get('lang', 'uz') != 'ru'
        if not username:
            messages.error(request, "Login kiriting." if uz else "Введите логин.")
        elif len(password) < 6:
            messages.error(request, "Parol kamida 6 belgi bo'lsin." if uz else "Пароль — минимум 6 символов.")
        elif password != request.POST.get('password2'):
            messages.error(request, "Parollar bir xil emas." if uz else "Пароли не совпадают.")
        else:
            user = get_user_model().objects.create_superuser(username=username, email='', password=password)
            login(request, user)
            return redirect('dashboard:index')
    return render(request, 'core/setup.html', {'username': username})


def logout_view(request):
    """Logout and redirect to login."""
    logout(request)
    return redirect('core:login')


@login_required(login_url='core:login')
def index(request):
    """Root redirect to dashboard."""
    return redirect('dashboard:index')


def set_language(request):
    """Switch UI language (uz / ru). Stores in session."""
    lang = request.GET.get('lang', 'uz')
    if lang not in ('uz', 'ru'):
        lang = 'uz'
    request.session['lang'] = lang
    next_url = request.GET.get('next', request.META.get('HTTP_REFERER', '/'))
    return redirect(next_url)
