"""Vacancy views."""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q

from .models import Vacancy, Category
from services.category_icons import annotate_with_icons


@login_required(login_url='core:login')
def vacancy_list(request):
    """List vacancies with search and filters."""
    q = request.GET.get('q', '')
    category = request.GET.get('category', '')
    source = request.GET.get('source', '')
    sort = request.GET.get('sort', '-created_at')

    vacancies = Vacancy.objects.select_related('category').all()

    if q:
        vacancies = vacancies.filter(
            Q(title__icontains=q) |
            Q(company_name__icontains=q) |
            Q(description__icontains=q) |
            Q(city__icontains=q)
        )
    if category:
        vacancies = vacancies.filter(category__slug=category)
    if source:
        vacancies = vacancies.filter(source__iexact=source)

    order_fields = {
        '-created_at': '-created_at',
        '-score': '-score',
        'date': '-created_at',
        'score': '-score',
        'title': 'title',
        'company': 'company_name',
    }
    vacancies = vacancies.order_by(order_fields.get(sort, '-created_at'))

    categories = Category.objects.filter(is_active=True)
    sources = Vacancy.objects.values_list('source', flat=True).distinct().order_by('source')

    context = {
        'vacancies': vacancies,
        'categories': categories,
        'sources': sources,
        'q': q,
        'selected_category': category,
        'selected_source': source,
        'sort': sort,
        'section': 'vacancies',
    }
    return render(request, 'vacancies/list.html', context)


@login_required(login_url='core:login')
def vacancy_detail(request, pk):
    vacancy = get_object_or_404(Vacancy, pk=pk)
    from companies.models import Company
    from services.skill_detector import detect_skills
    company = Company.objects.filter(name=vacancy.company_name).first()
    skills  = detect_skills(vacancy.title, vacancy.description or '')
    return render(request, 'vacancies/detail.html', {
        'v':       vacancy,
        'company': company,
        'skills':  skills,
        'section': 'vacancies',
    })


@login_required(login_url='core:login')
def check_company_ai(request, pk):
    """AI bilan vakansiya kompaniyasini tekshirish."""
    if request.method != 'POST':
        return redirect('vacancies:detail', pk=pk)

    vacancy = get_object_or_404(Vacancy, pk=pk)
    from companies.models import Company
    from ai.views import _check_company_with_groq

    company, _ = Company.objects.get_or_create(name=vacancy.company_name)
    try:
        result = _check_company_with_groq(company.name)
        company.is_real      = result.get('is_real', True)
        company.company_type = result.get('company_type', 'Other')
        company.description  = result.get('description', '')
        company.is_top       = result.get('is_top', False)
        company.checked_by_ai = True
        company.save()
        messages.success(request, f"AI tekshiruvi tugadi: {company.company_type}")
    except Exception as e:
        messages.error(request, f"AI xatolik: {e}")

    return redirect('vacancies:detail', pk=pk)


@login_required(login_url='core:login')
def vacancy_delete(request, pk):
    vacancy = get_object_or_404(Vacancy, pk=pk)
    vacancy.delete()
    messages.success(request, "Vakansiya o'chirildi.")
    return redirect('vacancies:list')


@login_required(login_url='core:login')
def vacancy_clear(request):
    """Vakansiyalarni tozalash — filtrlangan yoki barchasini."""
    if request.method != 'POST':
        return redirect('vacancies:list')

    qs = Vacancy.objects.all()
    category = request.POST.get('category', '')
    source   = request.POST.get('source', '')
    scope    = request.POST.get('scope', 'all')

    # Faqat filtrlanganlarni tozalash
    if scope == 'filtered':
        if category:
            qs = qs.filter(category__slug=category)
        if source:
            qs = qs.filter(source__iexact=source)

    count = qs.count()
    qs.delete()

    # Loglarga yozish
    from logs_app.models import ActivityLog
    ActivityLog.objects.create(
        level='warning', source='system',
        message=f"{count} ta vakansiya tozalandi ({'filtrlangan' if scope == 'filtered' else 'barchasi'})",
        user=request.user,
    )
    messages.success(request, f"{count} ta vakansiya o'chirildi.")

    # Filtrlangan bo'lsa, filtrni saqlab qaytar
    if scope == 'filtered':
        params = []
        if category: params.append(f'category={category}')
        if source:   params.append(f'source={source}')
        qstr = '?' + '&'.join(params) if params else ''
        return redirect(f"{request.path.replace('clear/', '')}{qstr}")
    return redirect('vacancies:list')


@login_required(login_url='core:login')
def category_list(request):
    categories = Category.objects.annotate(
        vacancy_count=Count('vacancies')
    ).order_by('name')
    categories = annotate_with_icons(list(categories))
    return render(request, 'vacancies/categories.html', {
        'categories': categories,
        'section': 'categories',
    })


@login_required(login_url='core:login')
def category_toggle(request, pk):
    cat = get_object_or_404(Category, pk=pk)
    cat.is_active = not cat.is_active
    cat.save()
    messages.success(request, f"{cat.name} {'yoqildi' if cat.is_active else 'o\'chirildi'}.")
    return redirect('vacancies:categories')


@login_required(login_url='core:login')
def category_edit(request, pk):
    cat = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        daily_limit = request.POST.get('daily_limit')
        if daily_limit:
            cat.daily_limit = int(daily_limit)
            cat.save()
            messages.success(request, f"{cat.name} limiti {cat.daily_limit} ga o'zgartirildi.")
        return redirect('vacancies:categories')
    return render(request, 'vacancies/category_edit.html', {
        'cat': cat,
        'section': 'categories',
    })
