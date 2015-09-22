from django.test import TestCase
from django.core.management import call_command

from shutil import rmtree
from subprocess import call
import os

from denis import Denis

from .models import SomeData


class TestDenis(TestCase):
    fixtures = ['testdata.json']

    def test_dump_and_load(self):
       appdir = os.path.abspath(os.path.dirname(__file__))
       fixtures = os.path.join(appdir, 'fixtures', 'testdata.json')
       # load fixtures into backup db
       call_command('loaddata', fixtures, database='backup')

       SomeData.objects.get(pk=1).delete()
       have_somedata = SomeData.objects.filter(pk=1).exists()
       self.assertEqual(have_somedata, False)
       qs = SomeData.objects.using('backup').filter(pk=1)
       self.assertEqual(qs.exists(), True)

       outdir = os.path.join(appdir, '..', 'some-data-restore')
       denis = Denis(qs, using='backup', outdir=outdir)
       denis.dump()

       have_dir = os.path.isdir(outdir)
       self.assertEqual(have_dir, True)

       denis_script_path = os.path.join(outdir, 'denis.sh')
       have_script = os.path.exists(denis_script_path)
       self.assertEqual(have_script, True)

       call(['sh', denis_script_path])

       somedata_isback = SomeData.objects.filter(pk=1).exists()
       self.assertEqual(somedata_isback, True)

       shutil.rmtree(outdir)
