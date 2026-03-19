# config/settings/test.py

from .base import *

DATABASES['default']['NAME'] = os.getenv('TEST_DB_NAME', 'test_db')

DEBUG = True