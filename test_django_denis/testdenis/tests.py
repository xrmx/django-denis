from django.test import TestCase
from django.core.management import call_command

import os

from denis import Denis

from .models import School, Class, Student, Teacher, Course


class TestDenis(TestCase):

    def test_recover(self):
       appdir = os.path.abspath(os.path.dirname(__file__))
       fixtures = os.path.join(appdir, 'fixtures', 'testdata.json')
       auth = os.path.join(appdir, 'fixtures', 'auth.json')
       # load fixtures into backup db
       call_command('loaddata', auth, database='backup')
       call_command('loaddata', fixtures, database='backup')
       call_command('loaddata', auth, database='test')
       call_command('loaddata', fixtures, database='test')

       School.objects.using('test').get(pk=1).delete()
       have_somedata = School.objects.using('test').filter(pk=1).exists()
       self.assertEqual(have_somedata, False)
       qs = School.objects.using('backup').filter(pk=1)
       self.assertEqual(qs.exists(), True)

       denis = Denis(qs, using='backup')
       denis.recover(using='test')

       school_isback = School.objects.using('test').filter(pk=1).exists()
       self.assertEqual(school_isback, True)
