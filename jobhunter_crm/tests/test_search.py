"""Tests for the filtered vacancy search (no network: parsers are mocked)."""

from unittest import mock

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from parsers.engine import save_vacancies
from platforms.models import Platform
from search import runner
from search.models import SearchJob
from vacancies.models import Category, Vacancy


def raw(title, company, url, description='', source='HH.UZ', **extra):
    return {'title': title, 'company': company, 'url': url, 'description': description,
            'city': 'Tashkent', 'salary': None, 'source': source, **extra}


RAWS = [
    raw('Junior Python Developer', 'Alpha LLC', 'https://example.com/v/1', 'Python Django'),
    raw('Python Developer', 'Beta LLC', 'https://example.com/v/2', 'Python Django',
        experience_code='between1And3'),
    raw('Senior Python Developer', 'Gamma LLC', 'https://example.com/v/3', 'Python Django'),
    raw('Python разработчик', 'Delta LLC', 'https://example.com/v/4', 'опыт работы от 3 лет'),
    raw('SMM менеджер', 'Epsilon LLC', 'https://example.com/v/5', 'Instagram SMM таргет'),
]


class BaseSearchTest(TestCase):
    def setUp(self):
        for slug in ('python', 'smm'):
            Category.objects.create(name=slug.title(), slug=slug)
        self.hh = Platform.objects.create(name='HH.UZ', slug='hhuz', priority=1)
        self.remotive = Platform.objects.create(name='Remotive', slug='remotive', priority=2)
        self.user = get_user_model().objects.create_user('tester', password='x')
        self.client.force_login(self.user)


class SaveVacanciesTest(BaseSearchTest):
    def test_filters_by_category_and_level(self):
        result = save_vacancies('hhuz', RAWS, categories=['python'], levels=['junior'])

        stored = Vacancy.objects.order_by('url')
        self.assertEqual([v.url[-1] for v in stored], ['1', '2'])
        self.assertTrue(all(v.level == 'junior' for v in stored))
        self.assertEqual(stored[1].experience, '1–3')
        self.assertEqual(result['count'], 2)
        self.assertEqual(sorted(result['ids']), sorted(stored.values_list('id', flat=True)))

    def test_middle_and_senior_are_kept_when_selected(self):
        save_vacancies('hhuz', RAWS, categories=['python'], levels=['middle', 'senior'])
        levels = dict(Vacancy.objects.values_list('company_name', 'level'))
        self.assertEqual(levels, {'Gamma LLC': 'senior', 'Delta LLC': 'middle'})

    def test_no_filters_keeps_every_level(self):
        save_vacancies('hhuz', RAWS)
        self.assertEqual(Vacancy.objects.count(), 5)

    def test_known_vacancy_gets_fresh_level(self):
        save_vacancies('hhuz', [raw('Старший аналитик', 'Zeta LLC', 'https://example.com/v/9', 'SQL Power BI')])
        self.assertEqual(Vacancy.objects.get().level, 'senior')

        fresh = raw('Старший аналитик', 'Zeta LLC', 'https://example.com/v/9', 'SQL Power BI',
                    experience_code='between1And3')
        result = save_vacancies('hhuz', [fresh], levels=['junior'])

        vacancy = Vacancy.objects.get()
        self.assertEqual((vacancy.level, vacancy.experience), ('junior', '1–3'))
        self.assertEqual(result['ids'], [vacancy.id])

    def test_already_known_vacancy_is_returned_not_duplicated(self):
        save_vacancies('hhuz', RAWS[:1])
        result = save_vacancies('hhuz', RAWS[:1])
        self.assertEqual(result['count'], 0)
        self.assertEqual(result['ids'], [Vacancy.objects.get().id])


class RunnerTest(BaseSearchTest):
    def test_run_collects_results_and_survives_a_failing_platform(self):
        job = SearchJob.objects.create(categories=['python'], platforms=['hhuz', 'remotive'],
                                       levels=['junior', 'middle'])

        def fake_fetch(slug, categories, levels):
            if slug == 'remotive':
                raise RuntimeError('HTTP 503')
            return RAWS

        with mock.patch.object(runner, 'fetch_platform', side_effect=fake_fetch):
            runner._run(job)

        job.refresh_from_db()
        self.assertEqual(job.status, 'done')
        self.assertEqual(job.new_count, 3)
        self.assertEqual(len(job.found_ids), 3)
        self.assertEqual(job.platform_status['hhuz']['state'], 'done')
        self.assertEqual(job.platform_status['remotive']['state'], 'error')
        self.assertIn('503', job.platform_status['remotive']['error'])
        self.assertEqual(job.progress_percent, 100)
        self.remotive.refresh_from_db()
        self.assertEqual(self.remotive.consecutive_errors, 1)


class SearchViewsTest(BaseSearchTest):
    def test_index_lists_courses_platforms_levels(self):
        response = self.client.get(reverse('search:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'value="python"')
        self.assertContains(response, 'value="remotive"')
        self.assertContains(response, 'value="senior"')

    def test_start_creates_job_and_runs_it_in_background(self):
        with mock.patch('search.views.start_job') as start:
            response = self.client.post(reverse('search:start'), {
                'categories': ['python', 'unknown'],
                'platforms': ['hhuz'],
                'levels': ['junior', 'bogus'],
            })
        job = SearchJob.objects.get()
        self.assertRedirects(response, reverse('search:detail', args=[job.pk]), fetch_redirect_response=False)
        start.assert_called_once_with(job.pk)
        self.assertEqual((job.categories, job.platforms, job.levels), (['python'], ['hhuz'], ['junior']))

    def test_start_requires_every_filter(self):
        with mock.patch('search.views.start_job') as start:
            response = self.client.post(reverse('search:start'), {'categories': ['python'], 'platforms': ['hhuz']})
        self.assertRedirects(response, reverse('search:index'), fetch_redirect_response=False)
        start.assert_not_called()
        self.assertFalse(SearchJob.objects.exists())

    def test_only_one_job_at_a_time(self):
        active = SearchJob.objects.create(categories=['python'], platforms=['hhuz'],
                                          levels=['junior'], status='running')
        with mock.patch('search.views.start_job') as start:
            response = self.client.post(reverse('search:start'), {
                'categories': ['python'], 'platforms': ['hhuz'], 'levels': ['junior']})
        self.assertRedirects(response, reverse('search:detail', args=[active.pk]), fetch_redirect_response=False)
        start.assert_not_called()

    def test_start_rejects_get(self):
        self.assertEqual(self.client.get(reverse('search:start')).status_code, 405)

    def test_detail_shows_results_and_filters_by_level(self):
        save_vacancies('hhuz', RAWS)
        job = SearchJob.objects.create(categories=['python', 'smm'], platforms=['hhuz'],
                                       levels=['junior', 'senior'], status='done',
                                       found_ids=list(Vacancy.objects.values_list('id', flat=True)))
        response = self.client.get(reverse('search:detail', args=[job.pk]))
        self.assertContains(response, 'Gamma LLC')
        self.assertContains(response, 'Alpha LLC')

        response = self.client.get(reverse('search:detail', args=[job.pk]), {'level': 'senior'})
        self.assertContains(response, 'Gamma LLC')
        self.assertNotContains(response, 'Alpha LLC')

    def test_status_json(self):
        job = SearchJob.objects.create(categories=['python'], platforms=['hhuz', 'remotive'], levels=['junior'],
                                       status='running', found_ids=[1, 2], new_count=2,
                                       platform_status={'hhuz': {'state': 'done'}, 'remotive': {'state': 'running'}})
        data = self.client.get(reverse('search:status', args=[job.pk])).json()
        self.assertEqual(data['status'], 'running')
        self.assertEqual((data['found'], data['new'], data['done_platforms'], data['progress']), (2, 2, 1, 50))

    def test_login_required(self):
        self.client.logout()
        for url in (reverse('search:index'), reverse('search:detail', args=[1])):
            self.assertEqual(self.client.get(url).status_code, 302)

    def test_old_run_parser_url_redirects_to_search(self):
        response = self.client.get(reverse('parser:run'))
        self.assertRedirects(response, reverse('search:index'), fetch_redirect_response=False)


class VacancyListLevelTest(BaseSearchTest):
    def setUp(self):
        super().setUp()
        save_vacancies('hhuz', RAWS)

    def test_level_filter(self):
        response = self.client.get(reverse('vacancies:list'), {'level': 'senior'})
        self.assertContains(response, 'Gamma LLC')
        self.assertNotContains(response, 'Alpha LLC')

    def test_clear_filtered_respects_search_query_and_level(self):
        self.client.post(reverse('vacancies:clear'), {'scope': 'filtered', 'q': 'Gamma', 'level': ''})
        self.assertEqual(Vacancy.objects.count(), 4)
        self.client.post(reverse('vacancies:clear'), {'scope': 'filtered', 'level': 'middle'})
        self.assertEqual(sorted(Vacancy.objects.values_list('level', flat=True)), ['junior', 'junior', 'junior'])
