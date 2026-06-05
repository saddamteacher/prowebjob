"""
Skill Detector — vakansiya tavsifidan kerakli skilllarni aniqlaydi.
Har bir skill uchun real icon (SimpleIcons CDN) qaytaradi.
"""

import re

# SimpleIcons CDN: https://cdn.simpleicons.org/{slug}/{hex-color}
_SI = "https://cdn.simpleicons.org"

# (kalit_so'zlar_regex, display_nomi, icon_url, rang)
SKILL_DEFINITIONS = [

    # ── PROGRAMMING LANGUAGES ─────────────────────────────────────────
    (r'\bpython\b',         'Python',       f'{_SI}/python/3776AB',         '#3776AB'),
    (r'\bjava(?:script)?\b','JavaScript',   f'{_SI}/javascript/F7DF1E',     '#F7DF1E'),
    (r'\btypescript\b|\bts\b', 'TypeScript',f'{_SI}/typescript/3178C6',     '#3178C6'),
    (r'\bphp\b',            'PHP',          f'{_SI}/php/777BB4',             '#777BB4'),
    (r'\bruby\b',           'Ruby',         f'{_SI}/ruby/CC342D',            '#CC342D'),
    (r'\bgolang\b|\bgo\b',  'Go',           f'{_SI}/go/00ADD8',              '#00ADD8'),
    (r'\brust\b',           'Rust',         f'{_SI}/rust/CE422B',            '#CE422B'),
    (r'\bc\+\+\b|\bcpp\b',  'C++',          f'{_SI}/cplusplus/00599C',       '#00599C'),
    (r'\bc#\b|\bcsharp\b',  'C#',           f'{_SI}/csharp/239120',          '#239120'),
    (r'\bswift\b',          'Swift',        f'{_SI}/swift/F05138',           '#F05138'),
    (r'\bkotlin\b',         'Kotlin',       f'{_SI}/kotlin/7F52FF',          '#7F52FF'),
    (r'\bdart\b',           'Dart',         f'{_SI}/dart/0175C2',            '#0175C2'),
    (r'\bscala\b',          'Scala',        f'{_SI}/scala/DC322F',           '#DC322F'),

    # ── PYTHON FRAMEWORKS ─────────────────────────────────────────────
    (r'\bdjango\b',         'Django',       f'{_SI}/django/092E20',          '#092E20'),
    (r'\bfastapi\b',        'FastAPI',      f'{_SI}/fastapi/009688',         '#009688'),
    (r'\bflask\b',          'Flask',        f'{_SI}/flask/000000',           '#555555'),
    (r'\baiohttp\b',        'aiohttp',      f'{_SI}/aiohttp/2C5BB4',         '#2C5BB4'),
    (r'\bcelery\b',         'Celery',       f'{_SI}/celery/37814A',          '#37814A'),
    (r'\bsqlalchemy\b',     'SQLAlchemy',   f'{_SI}/sqlalchemy/D71F00',      '#D71F00'),
    (r'\bpydantic\b',       'Pydantic',     f'{_SI}/pydantic/E92063',        '#E92063'),
    (r'\bpandas\b',         'Pandas',       f'{_SI}/pandas/150458',          '#150458'),
    (r'\bnumpy\b',          'NumPy',        f'{_SI}/numpy/013243',           '#013243'),
    (r'\bmatplotlib\b',     'Matplotlib',   f'{_SI}/matplotlib/11557C',      '#11557C'),
    (r'\bscikit[\-\s]?learn\b|\bsklearn\b', 'Scikit-learn', f'{_SI}/scikitlearn/F7931E', '#F7931E'),
    (r'\btensorflow\b',     'TensorFlow',   f'{_SI}/tensorflow/FF6F00',      '#FF6F00'),
    (r'\bpytorch\b',        'PyTorch',      f'{_SI}/pytorch/EE4C2C',         '#EE4C2C'),
    (r'\bkeras\b',          'Keras',        f'{_SI}/keras/D00000',           '#D00000'),
    (r'\bjupyter\b',        'Jupyter',      f'{_SI}/jupyter/F37626',         '#F37626'),

    # ── FRONTEND FRAMEWORKS ───────────────────────────────────────────
    (r'\breact(?:\.js)?\b', 'React',        f'{_SI}/react/61DAFB',          '#61DAFB'),
    (r'\bvue(?:\.js)?\b',   'Vue.js',       f'{_SI}/vuedotjs/4FC08D',       '#4FC08D'),
    (r'\bangular\b',        'Angular',      f'{_SI}/angular/DD0031',         '#DD0031'),
    (r'\bnext\.?js\b',      'Next.js',      f'{_SI}/nextdotjs/000000',       '#888888'),
    (r'\bnuxt\.?js\b',      'Nuxt.js',      f'{_SI}/nuxtdotjs/00DC82',       '#00DC82'),
    (r'\bsvelte\b',         'Svelte',       f'{_SI}/svelte/FF3E00',          '#FF3E00'),
    (r'\bredux\b',          'Redux',        f'{_SI}/redux/764ABC',           '#764ABC'),
    (r'\btailwind(?:css)?\b','Tailwind',    f'{_SI}/tailwindcss/06B6D4',    '#06B6D4'),
    (r'\bbootstrap\b',      'Bootstrap',    f'{_SI}/bootstrap/7952B3',       '#7952B3'),
    (r'\bsass\b|\bscss\b',  'Sass',         f'{_SI}/sass/CC6699',            '#CC6699'),
    (r'\bwebpack\b',        'Webpack',      f'{_SI}/webpack/8DD6F9',         '#8DD6F9'),
    (r'\bvite\b',           'Vite',         f'{_SI}/vite/646CFF',            '#646CFF'),

    # ── DATABASES ─────────────────────────────────────────────────────
    (r'\bpostgres(?:ql)?\b','PostgreSQL',   f'{_SI}/postgresql/336791',      '#336791'),
    (r'\bmysql\b',          'MySQL',        f'{_SI}/mysql/4479A1',           '#4479A1'),
    (r'\bmongodb\b',        'MongoDB',      f'{_SI}/mongodb/47A248',         '#47A248'),
    (r'\bredis\b',          'Redis',        f'{_SI}/redis/DC382D',           '#DC382D'),
    (r'\bsqlite\b',         'SQLite',       f'{_SI}/sqlite/003B57',          '#003B57'),
    (r'\belasticsearch\b',  'Elasticsearch',f'{_SI}/elasticsearch/005571',   '#005571'),
    (r'\bclickhouse\b',     'ClickHouse',   f'{_SI}/clickhouse/FFCC01',      '#FFCC01'),
    (r'\bbigquery\b',       'BigQuery',     f'{_SI}/googlebigquery/669DF6',  '#669DF6'),

    # ── DEVOPS / CLOUD ────────────────────────────────────────────────
    (r'\bdocker\b',         'Docker',       f'{_SI}/docker/2496ED',          '#2496ED'),
    (r'\bkubernetes\b|\bk8s\b', 'Kubernetes', f'{_SI}/kubernetes/326CE5',   '#326CE5'),
    (r'\bnginx\b',          'Nginx',        f'{_SI}/nginx/009639',           '#009639'),
    (r'\bgit\b',            'Git',          f'{_SI}/git/F05032',             '#F05032'),
    (r'\bgithub\b',         'GitHub',       f'{_SI}/github/181717',          '#888'),
    (r'\bgitlab\b',         'GitLab',       f'{_SI}/gitlab/FC6D26',          '#FC6D26'),
    (r'\baws\b',            'AWS',          f'{_SI}/amazonwebservices/232F3E','#FF9900'),
    (r'\bgcp\b|google\s+cloud', 'GCP',      f'{_SI}/googlecloud/4285F4',    '#4285F4'),
    (r'\bazure\b',          'Azure',        f'{_SI}/microsoftazure/0078D4',  '#0078D4'),
    (r'\bkafka\b',          'Kafka',        f'{_SI}/apachekafka/231F20',     '#888'),
    (r'\brabbitmq\b',       'RabbitMQ',     f'{_SI}/rabbitmq/FF6600',        '#FF6600'),
    (r'\blinux\b',          'Linux',        f'{_SI}/linux/FCC624',           '#FCC624'),
    (r'\bci[/\-]?cd\b',     'CI/CD',        f'{_SI}/githubactions/2088FF',   '#2088FF'),

    # ── DESIGN TOOLS ──────────────────────────────────────────────────
    (r'\bfigma\b',          'Figma',        f'{_SI}/figma/F24E1E',           '#F24E1E'),
    (r'\bphotoshop\b',      'Photoshop',    f'{_SI}/adobephotoshop/31A8FF',  '#31A8FF'),
    (r'\billustrator\b',    'Illustrator',  f'{_SI}/adobeillustrator/FF9A00','#FF9A00'),
    (r'\badobe\s+xd\b',     'Adobe XD',     f'{_SI}/adobexd/FF61F6',         '#FF61F6'),
    (r'\bcoreldraw\b',      'CorelDRAW',    f'{_SI}/coreldraw/229900',        '#229900'),
    (r'\bsketch\b',         'Sketch',       f'{_SI}/sketch/F7B500',          '#F7B500'),
    (r'\bcanva\b',          'Canva',        f'{_SI}/canva/00C4CC',           '#00C4CC'),
    (r'\bafter\s+effects\b','After Effects',f'{_SI}/adobeaftereffects/9999FF','#9999FF'),
    (r'\bpremiere\s+pro\b', 'Premiere Pro', f'{_SI}/adobepremierepro/9999FF','#9999FF'),

    # ── 3D / GAME ─────────────────────────────────────────────────────
    (r'\bblender\b',        'Blender',      f'{_SI}/blender/E87D0D',         '#E87D0D'),
    (r'\b3ds?\s+max\b',     '3ds Max',      f'{_SI}/autodesk/000000',        '#ff6d00'),
    (r'\bautocad\b',        'AutoCAD',      f'{_SI}/autodesk/000000',        '#ff6d00'),
    (r'\bunreal\s+engine\b','Unreal Engine',f'{_SI}/unrealengine/0E1128',    '#888'),
    (r'\bunity\b',          'Unity',        f'{_SI}/unity/000000',           '#888'),
    (r'\bzbrush\b',         'ZBrush',       f'{_SI}/pixologic/E84038',       '#E84038'),

    # ── BI / DATA TOOLS ───────────────────────────────────────────────
    (r'\bpower\s+bi\b',     'Power BI',     f'{_SI}/powerbi/F2C811',         '#F2C811'),
    (r'\btableau\b',        'Tableau',      f'{_SI}/tableau/E97627',         '#E97627'),
    (r'\bgrafana\b',        'Grafana',      f'{_SI}/grafana/F46800',         '#F46800'),
    (r'\bairflow\b',        'Airflow',      f'{_SI}/apacheairflow/017CEE',   '#017CEE'),
    (r'\bspark\b',          'Apache Spark', f'{_SI}/apachespark/E25A1C',     '#E25A1C'),
    (r'\bsql\b(?!\s*server)', 'SQL',        f'{_SI}/mysql/4479A1',           '#4479A1'),

    # ── MARKETING TOOLS ───────────────────────────────────────────────
    (r'\bgoogle\s+ads\b',   'Google Ads',   f'{_SI}/googleads/4285F4',       '#4285F4'),
    (r'\bfacebook\s+ads\b|meta\s+ads\b', 'Meta Ads', f'{_SI}/meta/0081FB', '#0081FB'),
    (r'\btiktok\s+ads\b|\btiktok\b', 'TikTok', f'{_SI}/tiktok/000000',     '#888'),
    (r'\byandex(?:\s+direct)?\b', 'Yandex', f'{_SI}/yandex/FF0000',        '#FF0000'),
    (r'\bgoogle\s+analytics\b', 'GA4',      f'{_SI}/googleanalytics/E37400','#E37400'),
    (r'\binstagram\b',      'Instagram',    f'{_SI}/instagram/E4405F',       '#E4405F'),

    # ── OFFICE / ACCOUNTING ───────────────────────────────────────────
    (r'\bexcel\b',          'Excel',        f'{_SI}/microsoftexcel/217346',  '#217346'),
    (r'\bword\b',           'Word',         f'{_SI}/microsoftword/2B579A',   '#2B579A'),
    (r'\bpowerpoint\b',     'PowerPoint',   f'{_SI}/microsoftpowerpoint/B7472A','#B7472A'),
    (r'\b1[cс]\b|\b1[cс]\s+предприятие\b', '1C',
                                            f'{_SI}/1c/DC2125',              '#DC2125'),
    (r'\bgraphql\b',        'GraphQL',      f'{_SI}/graphql/E10098',         '#E10098'),
]

# Pre-compile all patterns
_COMPILED = [
    (re.compile(pat, re.IGNORECASE), name, icon, color)
    for pat, name, icon, color in SKILL_DEFINITIONS
]


def detect_skills(title: str, description: str) -> list[dict]:
    """
    Vakansiya sarlavhasi va tavsifidan skilllarni aniqlaydi.
    Returns: [{'name': str, 'icon': str, 'color': str}, ...]
    """
    text = f"{title or ''} {description or ''}"
    found = {}

    for pattern, name, icon, color in _COMPILED:
        if name in found:
            continue
        if pattern.search(text):
            found[name] = {'name': name, 'icon': icon, 'color': color}

    return list(found.values())
