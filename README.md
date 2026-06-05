# JobHunter CRM

Django asosidagi vacancy aggregator CRM. Tizim platformalardan vakansiyalarni yig'adi, kategoriya bo'yicha ajratadi, dublikatlarni tekshiradi va admin panel orqali boshqaradi.

## Stack

- Python 3.12
- Django 5.1
- SQLite development database
- Django Templates + Tailwind CDN + Alpine.js
- httpx, BeautifulSoup, feedparser
- APScheduler + django-apscheduler
- Groq AI integration

## Tez boshlash

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
cd jobhunter_crm
python manage.py migrate
python manage.py init_data
python manage.py createsuperuser
python manage.py runserver
```

Brauzerda ochish:

```text
http://127.0.0.1:8000
```

## Asosiy tuzilma

```text
jobhunter_ai/
  jobhunter_crm/
    jobhunter_crm/       settings, urls, wsgi/asgi
    core/                login, logout, global context
    dashboard/           asosiy monitoring paneli
    vacancies/           vakansiyalar va yo'nalishlar
    companies/           kompaniyalar
    platforms/           platforma holati va test
    parsers/             parser engine va platforma parserlari
    analytics/           statistika
    ai/                  Groq integratsiyasi
    settings_app/        tizim sozlamalari
    logs_app/            activity loglar
    scheduler/           scheduler sahifasi
    services/            scorer, duplicate checker, skill mapper
```

## Platformalar

Default ishlaydigan manbalar:

- LinkedIn public jobs
- RemoteOK API
- Remotive API

Qo'shimcha UZ manbalar mavjud, lekin ayrim saytlar vaqti-vaqti bilan bot/scraping so'rovlarini bloklaydi:

- HH.UZ
- Job.uz
- Ishbor.uz

Platformalarni `Platformalar` sahifasida yoqish/o'chirish va alohida test qilish mumkin.

## Muhim buyruqlar

```bash
cd jobhunter_crm
python manage.py init_data
python manage.py run_parsers
python manage.py check
python manage.py collectstatic
```

Test:

```bash
python -m pytest tests\test_skill_mapper.py
```

## Docker

```bash
copy .env.example .env
docker-compose up -d
```

Docker konteyner ishga tushganda migratsiyalarni yuritadi, boshlang'ich platforma/kategoriyalarni yaratadi va Gunicorn orqali Django appni beradi.
