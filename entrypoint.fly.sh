#!/bin/sh
set -e

# Persistent volume papkasini tayyorlash
mkdir -p /data

# Migratsiya (DB /data/db.sqlite3 da yaratiladi)
python manage.py migrate --noinput

# Boshlang'ich ma'lumotlar (platformalar, kategoriyalar)
python manage.py init_data || true

# Admin foydalanuvchini avtomatik yaratish (agar yo'q bo'lsa)
# DJANGO_SUPERUSER_USERNAME / _PASSWORD / _EMAIL env'larini fly secrets'ga qo'ying
if [ -n "$DJANGO_SUPERUSER_USERNAME" ]; then
  python manage.py createsuperuser --noinput || true
fi

# Gunicorn — $PORT (Railway/Fly dinamik port beradi, default 8000)
exec gunicorn jobhunter_crm.wsgi:application \
  --bind "0.0.0.0:${PORT:-8000}" \
  --workers 2 \
  --timeout 120 \
  --access-logfile - \
  --error-logfile -
