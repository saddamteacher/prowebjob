#!/bin/sh
set -e

# Persistent volume papkasini tayyorlash
mkdir -p /data

# Migratsiya (DB /data/db.sqlite3 da yaratiladi)
python manage.py migrate --noinput

# Boshlang'ich ma'lumotlar (platformalar, kategoriyalar)
python manage.py init_data || true

# Admin foydalanuvchini yaratish YOKI parolini yangilash
# (env o'zgarsa — mavjud user ham yangilanadi)
if [ -n "$DJANGO_SUPERUSER_USERNAME" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ]; then
  python manage.py shell -c "
import os
from django.contrib.auth import get_user_model
U = get_user_model()
u = os.environ['DJANGO_SUPERUSER_USERNAME']
p = os.environ['DJANGO_SUPERUSER_PASSWORD']
e = os.environ.get('DJANGO_SUPERUSER_EMAIL', '')
obj, _ = U.objects.get_or_create(username=u, defaults={'email': e})
obj.email = e or obj.email
obj.is_staff = True
obj.is_superuser = True
obj.set_password(p)
obj.save()
print(f'Superuser ready: {u}')
" || true
fi

# Gunicorn — $PORT (Railway/Fly dinamik port beradi, default 8000)
# 1 worker — kam RAM (Railway $5 tarifiga sig'adi)
exec gunicorn jobhunter_crm.wsgi:application \
  --bind "0.0.0.0:${PORT:-8000}" \
  --workers "${WEB_WORKERS:-1}" \
  --timeout 120 \
  --max-requests 500 \
  --max-requests-jitter 50 \
  --access-logfile - \
  --error-logfile -
