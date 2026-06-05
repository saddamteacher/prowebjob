"""Core views including login and main redirect."""

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages


def login_view(request):
    """User login page."""
    if request.user.is_authenticated:
        return redirect('dashboard:index')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard:index')
        messages.error(request, 'Login yoki parol xato!')
    return render(request, 'core/login.html')


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
