"""ASGI config for jobhunter_crm."""

import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jobhunter_crm.settings')
application = get_asgi_application()
