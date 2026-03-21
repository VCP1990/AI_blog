import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

environment = os.getenv('DJANGO_ENVIRONMENT', 'development')

if environment == 'production':
    from .production import *
else:
    from .development import *
