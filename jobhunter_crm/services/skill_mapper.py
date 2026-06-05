"""
PROWEB HR — Category detection + Skill extraction.
"""

import re


# ── Title patterns ─────────────────────────────────────────────────────────────
TITLE_PATTERNS = [
    ('data_analyst', re.compile(
        r'\b(data\s+anal|bi\s+anal|business\s+intel|reporting\s+anal|'
        r'analytics\s+eng|аналитик\s+данн|бизнес[\-\s]аналитик|bi[\-\s]аналитик|'
        r'power\s+bi\s+spec|tableau\s+spec|analytics\s+spec|аналитик\s+bi|'
        r'аналитик\s+баз|данные[\s]+аналит|data\s+engineer|etl\s+dev|'
        r'аналитик|analitik)\w*', re.IGNORECASE
    )),
    ('data_science', re.compile(
        r'\b(data\s+sci|ml\s+eng|machine\s+learn|deep\s+learn|ai\s+eng|'
        r'nlp\s+eng|computer\s+vision|data\s+mining|'
        r'специалист\s+по\s+данн|инженер\s+(?:по\s+)?машинн|'
        r'исследователь\s+данн|ml\s+разработч|ai\s+разработч)\w*', re.IGNORECASE
    )),
    ('python', re.compile(
        r'\b(python\s+dev|django\s+dev|fastapi\s+dev|backend\s+python|'
        r'python\s+(?:backend|engineer|разработч|dasturchi|programmer)|'
        r'django\s+(?:разработч|dasturchi)|бэкенд.{0,10}python|'
        r'python\s+программист|backend\s+dasturchi|'
        r'backend\s+engineer|backend\s+разработ)\w*', re.IGNORECASE
    )),
    ('frontend', re.compile(
        r'\b(front[\-\s]?end|react\s+dev|vue\s+dev|angular\s+dev|'
        r'javascript\s+dev|next\.?js\s+dev|full[\-\s]?stack|web\s+dev|'
        r'фронтенд|веб[\-\s]разработч|frontend\s+разработч|'
        r'web\s+dasturchi|frontend\s+dasturchi|'
        r'react\s+разработч|vue\s+разработч|js\s+разработч)\w*', re.IGNORECASE
    )),
    ('graphic_design', re.compile(
        r'\b(ui[\s/]ux|ux[\s/]ui|graphic\s+des|product\s+des|visual\s+des|'
        r'grafik\s+diz|визуальн\s+дизайн|ui\s+дизайн|ux\s+дизайн|'
        r'веб[\-\s]дизайн|графическ\s+дизайн|дизайнер|dizayner|'
        r'motion\s+des|brand\s+des|logo\s+des)\w*', re.IGNORECASE
    )),
    ('smm', re.compile(
        r'\b(smm|social\s+media\s+man|digital\s+market|content\s+man|'
        r'targetolog|таргетолог|smm[\-\s]менеджер|smm[\-\s]специалист|'
        r'маркетолог|маркетинг\s+менедж|контент[\-\s]менедж|'
        r'kontent\s+menejer|smm\s+mutaxassis|интернет[\-\s]маркетолог|'
        r'сео[\-\s]специалист|seo\s+spec|email\s+market)\w*', re.IGNORECASE
    )),
    ('mobilograf', re.compile(
        r'\b(mobilograf|videograf|видеограф|мобилограф|'
        r'content\s+creator|video\s+editor|монтажер|видеомонтаж|'
        r'оператор|film\s+maker|filmmaker|reels\s+editor)\w*', re.IGNORECASE
    )),
    ('3d_max', re.compile(
        r'\b(3ds?\s+max|autocad|archicad|interior\s+des|'
        r'3d[\-\s]визуализ|интерьер\s+дизайн|архитектор|'
        r'3d\s+моделир|визуализатор|revit\s+spec|archviz)\w*', re.IGNORECASE
    )),
    ('blender', re.compile(
        r'\b(blender\s+(?:art|dev|spec|3d)|3d\s+(?:art|model|animat)|'
        r'3d\s+аниматор|3d\s+моделлер|blender\s+аниматор|'
        r'game\s+(?:art|des)|vfx\s+art|cg\s+art)\w*', re.IGNORECASE
    )),
    ('ms_office', re.compile(
        r'\b(office\s+man|excel\s+spec|ms\s+office|оператор\s+пк|'
        r'оператор\s+1с|секретарь|офис[\-\s]менедж|делопроизводит|'
        r'administration\s+spec|ofis\s+menejer|operator\s+pk|'
        r'бухгалтер|accountant|финансов\s+аналитик|финансист)\w*', re.IGNORECASE
    )),
]


# ── Description keywords ───────────────────────────────────────────────────────
SKILL_CATEGORY_MAP = {

    'data_analyst': [
        # Job titles
        'data analyst', 'bi analyst', 'business intelligence analyst',
        'reporting analyst', 'analytics specialist', 'data analyst intern',
        'junior data analyst', 'аналитик данных', 'бизнес-аналитик',
        'bi-аналитик', 'аналитик би', 'аналитик отчетности',
        'data engineer', 'etl developer', 'аналитик', 'analitik',
        # BI Tools
        'power bi', 'power query', 'power pivot', 'dax', 'tableau',
        'looker studio', 'looker', 'metabase', 'qlik', 'qliksense',
        'google data studio', 'sisense', 'apache superset', 'grafana',
        # Data tools
        'sql', 'mysql', 'postgresql', 'sql server', 'sqlite',
        'oracle sql', 'nosql', 'etl', 'dwh', 'data warehouse',
        'clickhouse', 'google bigquery', 'amazon redshift', 'snowflake',
        'apache spark', 'hadoop', 'hive', 'airflow',
        # Analytics
        'data visualization', 'визуализация данных',
        'аналитика данных', 'анализ данных', 'статистический анализ',
        'a/b testing', 'cohort analysis', 'funnel analysis',
        'excel analytics', 'google sheets analytics',
        # Python for DA
        'pandas', 'numpy', 'matplotlib', 'seaborn', 'plotly', 'scipy',
    ],

    'data_science': [
        # Titles
        'data scientist', 'ml engineer', 'machine learning engineer',
        'ai engineer', 'nlp engineer', 'computer vision engineer',
        'ml разработчик', 'ai разработчик', 'data science',
        # ML/AI Frameworks
        'scikit-learn', 'sklearn', 'tensorflow', 'pytorch', 'keras',
        'xgboost', 'lightgbm', 'catboost', 'optuna', 'mlflow',
        'huggingface', 'transformers', 'langchain', 'openai api',
        # Techniques
        'machine learning', 'deep learning', 'nlp', 'computer vision',
        'neural network', 'neural networks', 'нейронные сети',
        'машинное обучение', 'глубокое обучение',
        'reinforcement learning', 'transfer learning',
        'natural language processing', 'object detection',
        'image segmentation', 'classification', 'regression',
        'clustering', 'feature engineering', 'model deployment',
        # Tools
        'jupyter', 'jupyter notebook', 'colab', 'kaggle',
        'docker', 'mlops', 'kubeflow', 'vertex ai', 'aws sagemaker',
    ],

    'python': [
        # Titles
        'python developer', 'django developer', 'fastapi developer',
        'python dasturchi', 'backend developer', 'backend engineer',
        'python разработчик', 'бэкенд разработчик',
        'software engineer python', 'python software engineer',
        # Frameworks
        'django', 'fastapi', 'flask', 'aiohttp', 'tornado', 'starlette',
        'celery', 'sqlalchemy', 'alembic', 'pydantic', 'uvicorn',
        # APIs & Architecture
        'rest api', 'restful api', 'graphql', 'grpc', 'microservices',
        'websocket', 'async python', 'asyncio',
        # DBs
        'postgresql', 'mysql', 'sqlite', 'mongodb', 'redis',
        'rabbitmq', 'kafka', 'elasticsearch',
        # DevOps / infra
        'docker', 'docker compose', 'kubernetes', 'nginx',
        'git', 'github', 'gitlab', 'linux', 'bash', 'ci/cd',
        'aws', 'gcp', 'azure',
        # Testing
        'pytest', 'unittest', 'tdd',
    ],

    'frontend': [
        # Titles
        'frontend developer', 'frontend разработчик',
        'react developer', 'vue developer', 'angular developer',
        'full stack developer', 'web developer', 'ui developer',
        'react разработчик', 'vue разработчик', 'js разработчик',
        # Frameworks / Libraries
        'react', 'react.js', 'vue', 'vue.js', 'angular',
        'next.js', 'nuxt.js', 'svelte', 'gatsby',
        'redux', 'vuex', 'zustand', 'pinia', 'recoil', 'mobx',
        # Core
        'javascript', 'typescript', 'html', 'css', 'html5', 'css3',
        'es6', 'es2015', 'dom', 'ajax', 'fetch api',
        # Styling
        'tailwindcss', 'tailwind', 'sass', 'scss', 'less',
        'styled-components', 'bootstrap', 'material ui', 'ant design',
        # Build tools
        'webpack', 'vite', 'rollup', 'parcel', 'babel',
        'npm', 'yarn', 'pnpm',
        # Testing
        'jest', 'cypress', 'playwright', 'vitest',
        # Others
        'rest api', 'graphql', 'websocket', 'pwa', 'spa',
        'responsive design', 'cross-browser', 'git',
    ],

    'smm': [
        # Titles
        'smm manager', 'smm специалист', 'social media manager',
        'digital marketing specialist', 'content manager',
        'таргетолог', 'targetolog', 'маркетолог',
        'интернет-маркетолог', 'seo специалист', 'email маркетолог',
        'brand manager', 'pr manager', 'community manager',
        'маркетинг специалист', 'маркетинговый менеджер',
        # Social Platforms
        'instagram', 'tiktok', 'youtube', 'facebook',
        'telegram', 'linkedin marketing', 'twitter', 'pinterest',
        'vkontakte', 'odnoklassniki',
        # Advertising
        'meta ads', 'facebook ads', 'instagram ads',
        'google ads', 'tiktok ads', 'yandex direct',
        'myTarget', 'targeted advertising', 'таргетированная реклама',
        'контекстная реклама', 'ppc', 'cpc', 'cpm', 'roas', 'roi',
        # Content
        'content plan', 'контент-план', 'копирайтинг', 'copywriting',
        'smm продвижение', 'lead generation', 'email marketing',
        'email рассылка', 'crm marketing', 'воронка продаж',
        'a/b тест', 'analytics', 'google analytics', 'pixel',
        # Tools
        'canva', 'adobe photoshop', 'capcut', 'hootsuite', 'buffer',
    ],

    'mobilograf': [
        # Titles
        'mobilograf', 'videograf', 'video editor', 'content creator',
        'видеограф', 'мобилограф', 'видеомонтажер',
        'оператор', 'filmmaker', 'reels creator', 'shorts creator',
        # Tools
        'capcut', 'premiere pro', 'adobe premiere', 'after effects',
        'davinci resolve', 'final cut', 'final cut pro',
        'imovie', 'inshot', 'kinemaster',
        # Skills
        'color grading', 'color correction', 'video production',
        'видеомонтаж', 'монтаж видео', 'съемка', 'видеосъемка',
        'reels', 'youtube shorts', 'tiktok video', 'shorts',
        'motion graphics', 'анимация', 'субтитры',
        'lighting', 'sound design',
    ],

    'graphic_design': [
        # Titles
        'graphic designer', 'ui designer', 'ux designer',
        'ui/ux designer', 'product designer', 'visual designer',
        'grafik dizayner', 'дизайнер', 'графический дизайнер',
        'motion designer', 'brand designer', 'logo designer',
        'web designer', 'веб-дизайнер', 'полиграфический дизайнер',
        # Tools
        'figma', 'adobe xd', 'sketch', 'framer',
        'photoshop', 'illustrator', 'indesign', 'after effects',
        'coreldraw', 'affinity designer', 'canva pro',
        # Skills
        'ui design', 'ux design', 'wireframe', 'prototype', 'mockup',
        'design system', 'брендинг', 'brand identity', 'typography',
        'color theory', 'grid system', 'user research',
        'usability testing', 'accessibility', 'responsive design',
        'логотип', 'фирменный стиль', 'баннер', 'лендинг',
    ],

    '3d_max': [
        # Titles
        '3d designer', 'interior designer', 'visualizer',
        'architect', 'интерьерный дизайнер', 'визуализатор',
        '3d визуализатор', 'архитектор', 'архвизуализатор',
        'interior architect', 'landscape architect',
        # Tools
        '3ds max', '3d max', 'autocad', 'archicad', 'revit',
        'corona render', 'v-ray', 'vray', 'arnold',
        'sketchup', 'lumion', 'rhino', 'rhinoceros',
        'solidworks', 'cinema 4d', '3d modeling',
        # Skills
        'interior design', 'интерьер', 'визуализация',
        'exterior design', '3d рендер', 'rendering',
        'architectural visualization', 'архитектурная визуализация',
        'планировка', 'floor plan',
    ],

    'blender': [
        # Titles
        '3d artist', '3d modeler', 'blender artist', '3d animator',
        '3d аниматор', '3d моделлер', 'vfx artist', 'cg artist',
        'game artist', 'character artist', 'environment artist',
        # Tools
        'blender', 'cycles', 'eevee', 'geometry nodes',
        'substance painter', 'substance designer', 'zbrush',
        'mari', 'houdini', 'maya', 'cinema4d',
        # Skills
        '3d modeling', 'rigging', 'sculpting', 'animation',
        'rendering', 'uv mapping', 'texturing',
        'character design', 'game ready assets', 'low poly',
        'high poly', 'photorealistic', 'stylized',
    ],

    'ms_office': [
        # Titles
        'office manager', 'excel specialist', 'оператор пк',
        'секретарь', 'делопроизводитель', 'офис-менеджер',
        'administrative assistant', 'office administrator',
        'бухгалтер', 'accountant', 'финансовый аналитик',
        '1с бухгалтер', 'экономист', 'финансист',
        # Tools
        'microsoft excel', 'advanced excel', 'excel', 'power query excel',
        'ms word', 'word', 'ms powerpoint', 'powerpoint',
        'ms outlook', 'microsoft office', 'ms office',
        '1с', '1c', '1с предприятие', '1c предприятие',
        'google sheets', 'google docs', 'google workspace',
        'data entry', 'ввод данных',
        # Skills
        'pivot table', 'vlookup', 'сводные таблицы', 'формулы excel',
        'финансовая отчетность', 'бухгалтерский учет',
        'налоговая отчетность', 'управленческий учет',
    ],
}


CATEGORY_LABELS = {
    'data_analyst':   'Data Analyst',
    'data_science':   'Data Science',
    'python':         'Python',
    'frontend':       'Frontend',
    'smm':            'Pro SMM',
    'mobilograf':     'Mobilograf',
    'graphic_design': 'Graphic Design',
    '3d_max':         '3DS Max & AutoCAD',
    'blender':        'Blender',
    'ms_office':      'MS Office',
}

CATEGORY_ICONS_MAP = {
    'data_analyst':   'Data Analyst 2.png',
    'data_science':   'Data Sciense.png',
    'python':         'python.png',
    'frontend':       'веб программирование.png',
    'smm':            'pro smm.png',
    'mobilograf':     'мобилография.png',
    'graphic_design': 'Motion design & Видеомонтаж.png',
    '3d_max':         '3ds max & autocad.png',
    'blender':        'blender.png',
    'ms_office':      'mc office.png',
}


class SkillMapper:
    def __init__(self):
        self._desc_patterns: dict[str, list[re.Pattern]] = {}
        for cat, keywords in SKILL_CATEGORY_MAP.items():
            self._desc_patterns[cat] = [
                re.compile(r'\b' + re.escape(kw) + r'\b', re.IGNORECASE)
                for kw in keywords
            ]

    def detect(self, title: str, description: str = '') -> str | None:
        title = (title or '').strip()
        description = (description or '').strip()

        for cat, pattern in TITLE_PATTERNS:
            if pattern.search(title):
                return cat

        full_text = f"{title} {description}"
        scores: dict[str, int] = {}
        for cat, patterns in self._desc_patterns.items():
            count = sum(len(p.findall(full_text)) for p in patterns)
            if count > 0:
                scores[cat] = count

        if not scores:
            return None

        best_cat = max(scores, key=scores.get)
        if scores[best_cat] < 2:
            return None

        return best_cat

    def get_label(self, slug: str) -> str:
        return CATEGORY_LABELS.get(slug, slug.replace('_', ' ').title())

    def get_all_categories(self) -> dict[str, str]:
        return dict(CATEGORY_LABELS)
