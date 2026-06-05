# JobHunter CRM Dockerfile
FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    TZ=Asia/Tashkent \
    DJANGO_SETTINGS_MODULE=jobhunter_crm.settings

# Install system deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libxml2-dev libxslt-dev nginx \
    && rm -rf /var/lib/apt/lists/*

# Install Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

WORKDIR /app/jobhunter_crm

# Create dirs
RUN mkdir -p logs staticfiles media

# Collect static files
RUN python manage.py collectstatic --noinput --clear

# Nginx config
COPY jobhunter_crm/nginx/nginx.conf /etc/nginx/sites-enabled/default

EXPOSE 80

CMD ["sh", "-c", "python manage.py migrate --noinput && \
    python manage.py init_data && \
    nginx && \
    gunicorn jobhunter_crm.wsgi:application -c gunicorn.conf.py"]
