"""Runs a SearchJob in a background thread.

Platforms are downloaded in parallel (network only); everything that touches
the database happens in the job thread, one platform at a time.
"""

import logging
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

from django.db import close_old_connections, connection
from django.utils import timezone

from logs_app.models import ActivityLog
from parsers.engine import fetch_platform, record_error, record_success, save_vacancies
from platforms.models import Platform

from .models import SearchJob

logger = logging.getLogger(__name__)

MAX_PARALLEL_PLATFORMS = 4


def start_job(job_id: int) -> threading.Thread:
    thread = threading.Thread(target=run_job, args=(job_id,), name=f"search-job-{job_id}", daemon=True)
    thread.start()
    return thread


def run_job(job_id: int) -> None:
    close_old_connections()
    job = SearchJob.objects.get(pk=job_id)
    try:
        _run(job)
    except Exception as exc:  # never leave a job "running"
        logger.exception("Search job %s failed", job_id)
        job.status = 'error'
        job.error = str(exc)
        job.finished_at = timezone.now()
        job.save(update_fields=['status', 'error', 'finished_at'])
    finally:
        connection.close()


def _run(job: SearchJob) -> None:
    platforms = list(Platform.objects.filter(slug__in=job.platforms))
    job.status = 'running'
    job.started_at = timezone.now()
    job.platform_status = {p.slug: {'state': 'running', 'found': 0, 'new': 0, 'error': ''} for p in platforms}
    job.save(update_fields=['status', 'started_at', 'platform_status'])

    found_ids = list(job.found_ids)
    with ThreadPoolExecutor(max_workers=MAX_PARALLEL_PLATFORMS) as pool:
        futures = {
            pool.submit(fetch_platform, p.slug, job.categories, job.levels): p
            for p in platforms
        }
        for future in as_completed(futures):
            plat = futures[future]
            state = job.platform_status[plat.slug]
            try:
                result = save_vacancies(plat.slug, future.result(), job.categories, job.levels)
            except Exception as exc:
                logger.warning("Search job %s: %s failed: %s", job.pk, plat.slug, exc)
                record_error(plat, exc)
                state.update(state='error', error=str(exc)[:300])
            else:
                record_success(plat, result['count'])
                found_ids.extend(i for i in result['ids'] if i not in found_ids)
                job.new_count += result['count']
                state.update(state='done', found=len(result['ids']), new=result['count'])
            job.found_ids = found_ids
            job.save(update_fields=['platform_status', 'found_ids', 'new_count'])

    job.status = 'done'
    job.finished_at = timezone.now()
    job.save(update_fields=['status', 'finished_at'])
    ActivityLog.objects.create(
        level='info', source='parser',
        message=f"Qidiruv #{job.pk}: {len(found_ids)} ta topildi, {job.new_count} ta yangi",
    )
