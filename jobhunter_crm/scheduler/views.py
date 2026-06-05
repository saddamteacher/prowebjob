"""Scheduler management views."""

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django_apscheduler.models import DjangoJob, DjangoJobExecution


@login_required(login_url='core:login')
def scheduler_dashboard(request):
    jobs = DjangoJob.objects.all()
    recent_executions = DjangoJobExecution.objects.order_by('-run_time')[:30]
    return render(request, 'scheduler/index.html', {
        'jobs': jobs,
        'recent_executions': recent_executions,
        'section': 'scheduler',
    })


@login_required(login_url='core:login')
def run_parser_job(request):
    """Manually trigger parser job."""
    from parsers.engine import run_all_parsers
    result = run_all_parsers()
    messages.success(
        request,
        f"Parser run: {result['total_new']} new, {result['total_errors']} errors"
    )
    return redirect('scheduler:index')


@login_required(login_url='core:login')
def toggle_scheduler(request):
    """Enable/disable scheduler."""
    return redirect('scheduler:index')
