import os
import sys

os.environ['DJANGO_SETTINGS_MODULE'] = 'test_django_denis.settings'
test_dir = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(test_dir, 'denis'))
sys.path.insert(0, os.path.join(test_dir, 'test_django_denis'))

import django
from django.test.utils import get_runner
from django.conf import settings

def runtests():
    TestRunner = get_runner(settings)
    test_runner = TestRunner(verbosity=1, interactive=True)
    if hasattr(django, 'setup'):
        django.setup()
    failures = test_runner.run_tests(['testdenis'])
    sys.exit(bool(failures))

if __name__ == '__main__':
    runtests()

