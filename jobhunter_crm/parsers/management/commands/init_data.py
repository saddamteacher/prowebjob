"""Initialize database with default platforms and categories."""

from django.core.management.base import BaseCommand
from platforms.models import Platform
from vacancies.models import Category, Skill


class Command(BaseCommand):
    help = 'Initialize default data (platforms, categories, skills)'

    def handle(self, *args, **options):
        self._create_platforms()
        self._create_categories_and_skills()
        self.stdout.write(self.style.SUCCESS('Default data initialized'))

    def _create_platforms(self):
        platforms = [
            # name, slug, type, url, priority, enabled
            # O'zbekiston platformalari
            ('HH.UZ',           'hhuz',     'uz',   'https://hh.uz',                1, True),
            ('Job.uz',          'jobuz',    'uz',   'https://job.uz',               2, True),
            ('Ishbor.uz',       'ishboruz', 'uz',   'https://ishbor.uz',            3, True),
            ('Telegram IT',     'telegram', 'uz',   'https://t.me/it_jobs_uz',      4, True),
            ('OLX.uz',          'olxuz',    'uz',   'https://www.olx.uz/rabota/',   5, True),
            # Xalqaro platformalar
            ('LinkedIn',        'linkedin', 'intl', 'https://www.linkedin.com/jobs/', 6, True),
            ('RemoteOK',        'remoteok', 'intl', 'https://remoteok.com',           7, True),
            ('Remotive',        'remotive', 'intl', 'https://remotive.com',           8, True),
        ]
        for name, slug, ptype, url, priority, enabled in platforms:
            Platform.objects.update_or_create(
                slug=slug,
                defaults={
                    'name': name, 'platform_type': ptype,
                    'base_url': url, 'priority': priority,
                    'is_enabled': enabled,
                }
            )
        self.stdout.write(f"  Created {len(platforms)} platforms")

    def _create_categories_and_skills(self):
        categories_skills = {
            'data_analyst': ['SQL', 'Power BI', 'Excel', 'Tableau', 'Python', 'Pandas'],
            'data_science': ['Python', 'Machine Learning', 'TensorFlow', 'PyTorch', 'Scikit-learn'],
            'mobilograf': ['CapCut', 'Premiere Pro', 'After Effects', 'DaVinci Resolve', 'TikTok'],
            'smm': ['Meta Ads', 'Google Ads', 'Facebook Ads', 'Instagram Ads', 'SMM'],
            'graphic_design': ['Figma', 'Photoshop', 'Illustrator', 'CorelDRAW', 'Adobe XD'],
            '3d_max': ['3ds Max', 'AutoCAD', 'Corona Render', 'V-Ray', 'ArchiCAD'],
            'blender': ['Blender', '3D Modeling', 'Animation', 'Cycles', 'Rendering'],
            'python': ['Python', 'Django', 'FastAPI', 'Flask', 'PostgreSQL', 'Docker'],
            'frontend': ['HTML', 'CSS', 'JavaScript', 'React', 'Vue', 'TypeScript', 'Node.js', 'PHP'],
            'ms_office': ['Excel', 'Word', 'PowerPoint', 'Access', 'Outlook', 'Google Sheets'],
        }

        for slug, skills in categories_skills.items():
            name_map = {
                'data_analyst': 'Data Analyst',
                'data_science': 'Data Science',
                'mobilograf': 'Mobilograf',
                'smm': 'Pro SMM',
                'graphic_design': 'Pro Design',
                '3d_max': '3DS Max & AutoCAD',
                'blender': 'Blender',
                'python': 'Python',
                'frontend': 'Web Dasturlash',
                'ms_office': 'MS Office',
            }
            cat, created = Category.objects.get_or_create(
                slug=slug,
                defaults={
                    'name': name_map.get(slug, slug.replace('_', ' ').title()),
                    'is_active': True,
                    'daily_limit': 10,
                }
            )
            for skill_name in skills:
                Skill.objects.get_or_create(category=cat, name=skill_name)

        self.stdout.write(f"  Created {len(categories_skills)} categories with skills")
