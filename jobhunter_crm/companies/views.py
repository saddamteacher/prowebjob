"""Company views."""

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Count

from .models import Company
from vacancies.models import Vacancy


@login_required(login_url='core:login')
def company_list(request):
    # Get vacancy counts per company name
    from django.db.models import Count, Value, IntegerField
    from django.db.models.functions import Coalesce
    companies = Company.objects.all().order_by('name')
    # Add vacancy count manually
    vacancy_counts = Vacancy.objects.values('company_name').annotate(
        cnt=Count('id')
    )
    count_map = {item['company_name']: item['cnt'] for item in vacancy_counts}
    for company in companies:
        company.vacancy_count = count_map.get(company.name, 0)
    # Sort by count descending
    companies = sorted(companies, key=lambda c: c.vacancy_count, reverse=True)
    return render(request, 'companies/list.html', {
        'companies': companies,
        'section': 'companies',
    })


@login_required(login_url='core:login')
def company_detail(request, pk):
    company = get_object_or_404(Company, pk=pk)
    vacancies = Vacancy.objects.filter(company_name=company.name).order_by('-created_at')[:20]
    return render(request, 'companies/detail.html', {
        'company': company,
        'vacancies': vacancies,
        'section': 'companies',
    })
